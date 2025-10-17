import serial
import serial.tools.list_ports
import threading
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from werkzeug.serving import make_server
import cv2
from ultralytics import YOLO
import torch
import time

# ----------------------- FLASK SERVER CLASS -----------------------
class FlaskServer(threading.Thread):
    def __init__(self, shared_data, send_func_a, send_func_b, camera_index=0, yolo_model=None):
        threading.Thread.__init__(self)
        self.shared_data = shared_data
        self.send_func_a = send_func_a
        self.send_func_b = send_func_b
        self.daemon = True
        self.server = None
        self.app = Flask(__name__)
        CORS(self.app)

        # Camera
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # YOLO model
        self.yolo_model = yolo_model
        self.yolo_frame = None
        self.raw_frame = None
        self.running = True

        # Start YOLO thread if model exists
        if self.yolo_model:
            threading.Thread(target=self.yolo_loop, daemon=True).start()

        # -------------------- ROUTES --------------------
        @self.app.route('/sensors')
        def sensors():
            return jsonify(self.shared_data)

        # Send to Port A
        @self.app.route('/portA', methods=['POST'])
        def port_a():
            try:
                cmd = request.json.get("cmd")
                if not cmd:
                    return jsonify({"error": "Missing cmd"}), 400
                self.send_func_a(cmd)
                return jsonify({"status": "sent to Port A", "cmd": cmd})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Send to Port B
        @self.app.route('/portB', methods=['POST'])
        def port_b():
            try:
                cmd = request.json.get("cmd")
                if not cmd:
                    return jsonify({"error": "Missing cmd"}), 400
                self.send_func_b(cmd)
                return jsonify({"status": "sent to Port B", "cmd": cmd})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/video_raw')
        def video_raw():
            return Response(self.generate_frames(raw=True),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/video_yolo')
        def video_yolo():
            return Response(self.generate_frames(raw=False),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

    # -------------------- YOLO THREAD --------------------
    def yolo_loop(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    continue
                self.raw_frame = frame.copy()

                # YOLO inference
                results = self.yolo_model(frame, verbose=False)
                annotated = frame.copy()
                for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
                    x1, y1, x2, y2 = map(int, box)
                    cls_id = int(cls)
                    label = self.yolo_model.names[cls_id]
                    color = (0, 255, 0) if not label.startswith("NO-") else (0, 0, 255)
                    label_text = label.replace("NO-", "") if label.startswith("NO-") else label
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(annotated, label_text, (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                self.yolo_frame = annotated
            else:
                time.sleep(0.1)

    # -------------------- FRAME GENERATOR --------------------
    def generate_frames(self, raw=True):
        while self.running:
            frame = self.raw_frame if raw else self.yolo_frame
            if frame is None:
                time.sleep(0.01)
                continue
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    # -------------------- RUN / STOP SERVER --------------------
    def run(self):
        self.server = make_server("0.0.0.0", 5000, self.app)
        self.server.serve_forever()

    def stop(self):
        self.running = False
        if self.server:
            self.server.shutdown()
        if self.cap.isOpened():
            self.cap.release()


# ----------------------- MAIN APP -----------------------
class DualSerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Serial + HTTP Endpoint + YOLO Stream")
        self.root.geometry("950x800")
        self.root.resizable(False, False)

        self.serA = None
        self.serB = None
        self.http_thread = None
        self.http_running = False

        self.shared_data = {
            "m5stack": {"distance": None, "rfid": None, "door": None, "raw": ""},
            "esp32": {"temp": None, "gas": None, "buzzer": None, "raw": ""}
        }

        # YOLO model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.yolo_model = YOLO("ppe.pt").to(device)

        self.create_widgets()
        self.refresh_ports()
        self.available_cams = self.list_cameras()
        self.camera_menu['values'] = self.available_cams
        if self.available_cams:
            self.camera_menu.current(0)

    # ----------------------- GUI -----------------------
    def create_widgets(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        # Port A/B
        tk.Label(frame_top, text="Port A:").grid(row=0, column=0)
        self.portA_var = tk.StringVar()
        self.portA_menu = ttk.Combobox(frame_top, textvariable=self.portA_var, width=15)
        self.portA_menu.grid(row=0, column=1)
        tk.Button(frame_top, text="Connect A", command=self.connect_a).grid(row=0, column=2)

        tk.Label(frame_top, text="Port B:").grid(row=0, column=3)
        self.portB_var = tk.StringVar()
        self.portB_menu = ttk.Combobox(frame_top, textvariable=self.portB_var, width=15)
        self.portB_menu.grid(row=0, column=4)
        tk.Button(frame_top, text="Connect B", command=self.connect_b).grid(row=0, column=5)

        tk.Button(frame_top, text="↻ Refresh Ports", command=self.refresh_ports).grid(row=0, column=6)

        # Camera selection
        tk.Label(frame_top, text="Camera:").grid(row=1, column=0)
        self.camera_var = tk.StringVar()
        self.camera_menu = ttk.Combobox(frame_top, textvariable=self.camera_var, width=10)
        self.camera_menu.grid(row=1, column=1)

        # HTTP start/stop
        self.http_btn = tk.Button(frame_top, text="▶ Start HTTP Endpoint", command=self.toggle_http, bg="#b3ffb3")
        self.http_btn.grid(row=1, column=2)

        # Endpoint display
        tk.Label(frame_top, text="Endpoint URLs:").grid(row=2, column=0, sticky='e')
        self.endpoint_entry = tk.Entry(frame_top, width=70)
        self.endpoint_entry.grid(row=2, column=1, columnspan=5)
        self.endpoint_entry.insert(0, "Not running")
        self.endpoint_entry.config(state='readonly')

        # Serial displays
        frame_mid = tk.Frame(self.root)
        frame_mid.pack(pady=10, fill='both', expand=True)
        tk.Label(frame_mid, text="M5Stack / Port A Output").grid(row=0, column=0)
        self.textA = scrolledtext.ScrolledText(frame_mid, width=50, height=25)
        self.textA.grid(row=1, column=0)
        tk.Label(frame_mid, text="ESP32 / Port B Output").grid(row=0, column=1)
        self.textB = scrolledtext.ScrolledText(frame_mid, width=50, height=25)
        self.textB.grid(row=1, column=1)

        # Send entries
        frame_bottom = tk.Frame(self.root)
        frame_bottom.pack(pady=10)
        tk.Label(frame_bottom, text="Send to Port A:").grid(row=0, column=0)
        self.sendA_entry = tk.Entry(frame_bottom, width=40)
        self.sendA_entry.grid(row=0, column=1)
        tk.Button(frame_bottom, text="Send A", command=self.send_to_a).grid(row=0, column=2)

        tk.Label(frame_bottom, text="Send to Port B:").grid(row=1, column=0)
        self.sendB_entry = tk.Entry(frame_bottom, width=40)
        self.sendB_entry.grid(row=1, column=1)
        tk.Button(frame_bottom, text="Send B", command=self.send_to_b).grid(row=1, column=2)

    # ----------------------- SERIAL -----------------------
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.portA_menu['values'] = ports
        self.portB_menu['values'] = ports

    def connect_a(self):
        port = self.portA_var.get()
        if not port: return messagebox.showwarning("Warning", "Select Port A first.")
        self.serA = serial.Serial(port, 115200, timeout=1)
        threading.Thread(target=self.read_serial_a, daemon=True).start()
        self.textA.insert(tk.END, f"✅ Connected to {port}\n")

    def connect_b(self):
        port = self.portB_var.get()
        if not port: return messagebox.showwarning("Warning", "Select Port B first.")
        self.serB = serial.Serial(port, 115200, timeout=1)
        threading.Thread(target=self.read_serial_b, daemon=True).start()
        self.textB.insert(tk.END, f"✅ Connected to {port}\n")

    def read_serial_a(self):
        while True:
            try:
                if self.serA and self.serA.in_waiting:
                    line = self.serA.readline().decode(errors='ignore').strip()
                    if line:
                        self.textA.insert(tk.END, line + "\n")
                        self.textA.see(tk.END)
                        self.shared_data["m5stack"]["raw"] = line
            except:
                break

    def read_serial_b(self):
        while True:
            try:
                if self.serB and self.serB.in_waiting:
                    line = self.serB.readline().decode(errors='ignore').strip()
                    if line:
                        self.textB.insert(tk.END, line + "\n")
                        self.textB.see(tk.END)
                        self.shared_data["esp32"]["raw"] = line
            except:
                break

    # ----------------------- SEND -----------------------
    def send_to_a(self, msg=None):
        if msg is None:
            msg = self.sendA_entry.get().strip()
        if self.serA and msg:
            self.serA.write((msg + "\n").encode())
            self.textA.insert(tk.END, f"> Sent: {msg}\n")
            self.textA.see(tk.END)
            self.sendA_entry.delete(0, tk.END)

    def send_to_b(self, msg=None):
        if msg is None:
            msg = self.sendB_entry.get().strip()
        if self.serB and msg:
            self.serB.write((msg + "\n").encode())
            self.textB.insert(tk.END, f"> Sent: {msg}\n")
            self.textB.see(tk.END)
            self.sendB_entry.delete(0, tk.END)

    # ----------------------- CAMERA -----------------------
    def list_cameras(self, max_cams=5):
        available = []
        for i in range(max_cams):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                available.append(i)
            cap.release()
        return available

    # ----------------------- HTTP -----------------------
    def toggle_http(self):
        if not self.http_running:
            cam_idx = int(self.camera_var.get()) if self.camera_var.get() else 0
            self.http_thread = FlaskServer(
                self.shared_data,
                self.send_to_a,
                self.send_to_b,
                camera_index=cam_idx,
                yolo_model=self.yolo_model
            )
            self.http_thread.start()
            self.http_running = True

            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            urls = (
                f"Sensors: http://{local_ip}:5000/sensors | "
                f"PortA: http://{local_ip}:5000/portA | "
                f"PortB: http://{local_ip}:5000/portB | "
                f"Raw Video: http://{local_ip}:5000/video_raw | "
                f"YOLO Video: http://{local_ip}:5000/video_yolo"
            )
            self.http_btn.config(text="■ Stop HTTP Endpoint", bg="#ff9999")
            self.endpoint_entry.config(state='normal')
            self.endpoint_entry.delete(0, tk.END)
            self.endpoint_entry.insert(0, urls)
            self.endpoint_entry.config(state='readonly')
            self.textA.insert(tk.END, f"🌐 HTTP Endpoint started at:\n{urls}\n")
        else:
            self.http_thread.stop()
            self.http_thread = None
            self.http_running = False
            self.http_btn.config(text="▶ Start HTTP Endpoint", bg="#b3ffb3")
            self.endpoint_entry.config(state='normal')
            self.endpoint_entry.delete(0, tk.END)
            self.endpoint_entry.insert(0, "Not running")
            self.endpoint_entry.config(state='readonly')
            self.textA.insert(tk.END, "🛑 HTTP Endpoint stopped\n")


# ----------------------- RUN -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DualSerialApp(root)
    root.mainloop()
