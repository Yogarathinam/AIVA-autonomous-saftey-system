# 🏭 AIVA – AI-Powered Industrial Vision & Alert System

> **Theme:** Smart Manufacturing & Industry 4.0  
> **Event:** Dev Arena 2025 — TechSaavy Club, Easwari Engineering College  
> **Team:** Team Phoenix
> **Developed by:** Yogarathinam T.L

---

## 🚀 Overview

**AIVA (Autonomous Industrial Vision & Alert System)** is an **AI-powered safety monitoring and control system** designed for **smart factories and industrial environments**.

It integrates **computer vision, IoT sensors, and voice-based AI** to ensure a safe and efficient shop floor.  
AIVA monitors **workers, environment, and machinery**, provides **real-time alerts**, and interacts through **voice & dashboard** to report issues or answer operator queries.

---

## 🎯 Problem Statement

**PS Title:** AI-Powered Safety Monitoring for Smarter Shop Floor  

Factories face increasing risks — gas leaks, overheating, human errors, and unsafe equipment operation.  
Most existing systems are reactive or expensive. AIVA aims to provide an **affordable, AI-driven, multi-sensor solution** that can **detect, prevent, and communicate** potential hazards intelligently.

---

## 💡 Solution Overview

| Component | Description |
|------------|-------------|
| **Vision Intelligence** | Detects human presence, PPE usage, and hazardous conditions via camera (YOLOv8 + OpenCV). |
| **IoT Sensing** | Tracks temperature, gas levels, and proximity using DHT11, MQ3, and ultrasonic sensors. |
| **Access Control** | RFID-based restricted area entry and servo-controlled smart doors. |
| **Visual Alerts** | ARGB strips and machine indicators signal alert levels (Green–Safe, Red–Danger). |
| **Voice Interaction** | Gemini AI with TTS/STT provides verbal alerts, responds to safety queries, and logs incidents. |
| **Dashboard** | Displays live readings, alerts, camera feed, and AI logs from both MCUs. |

---

## ⚙️ System Architecture

┌────────────────────────────────────────────┐
│ Laptop / AI Node │
│--------------------------------------------│
│ Gemini AI | YOLO Vision | Dashboard | TTS │
│ Communicates via Wi-Fi (JSON) │
└───────────────▲────────────────────────────┘
│
│ Wi-Fi / Serial JSON
▼
┌────────────────────────────────────────────┐
│ M5Stack Core (AI Node) │
│--------------------------------------------│
│ Controls Pan-Tilt Camera (2x MG996R) │
│ Plays Audio via Speaker + Amp │
│ Sends data to Laptop │
└───────────────▲────────────────────────────┘
│
│ Serial / I2C / Wi-Fi
▼
┌────────────────────────────────────────────┐
│ ESP32 (Sensor Node) │
│--------------------------------------------│
│ DHT11 | MQ3 | Ultrasonic | RFID | LCD │
│ SG90 Door Servo | Buzzer | ARGB Strips │
│ Sends Real-time Data to M5Stack/Laptop │
└────────────────────────────────────────────┘

yaml
Copy code

---

## 🔩 Hardware Components

| Component | Quantity | Purpose |
|------------|-----------|----------|
| ESP32 Dev Module | 1 | IoT sensor controller |
| M5Stack Core | 1 | AI & visualization node |
| Webcam | 1 | Visual detection |
| MG996R Servo | 2 | Pan-tilt camera control |
| SG90 Servo | 1 | Door access mechanism |
| DHT11 Sensor | 1 | Temperature & humidity |
| MQ3 Gas Sensor | 1 | Gas / smoke detection |
| Ultrasonic Sensor | 1 | Motion / worker detection |
| RFID RC522 + Tags | 1 | Access control |
| Buzzer | 1 | Alert notification |
| LCD Display (16x2 / I2C) | 1 | Local status display |
| ARGB Strip | 1 | Wall-mounted alert lights |
| ARGB Sticks (3) | 1 set | Machine status indicators |
| Touch Sensors | 2 | Manual override / reset |
| Speaker + Amp | 1 | Audio output |
| Power Supply | - | Battery / adapter |

---

## 🧠 Software Stack

| Layer | Technologies |
|-------|---------------|
| **AI / CV** | YOLOv8, OpenCV |
| **Voice** | Gemini API, Edge TTS, SpeechRecognition (Python) |
| **IoT Firmware** | ESP32 (Arduino / MicroPython) |
| **Dashboard** | Flask / React + WebSocket for real-time updates |
| **Communication** | JSON over Wi-Fi / Serial |
| **Data Logging** | SQLite / CSV |

---

## 🧩 Key Features

- 🧍 **Human Detection & PPE Monitoring**
- 🌡️ **Environmental Tracking (Temp, Gas)**
- 🪫 **Alert LEDs & Buzzer on Critical Events**
- 🎙️ **Voice Alerts via Gemini AI**
- 🎛️ **Dashboard with Real-Time Sensor Data**
- 🔐 **RFID Access Control System**
- 📷 **Pan-Tilt AI Camera Tracking**
- 🧩 **Modular Dual-MCU Architecture (ESP32 + M5Stack)**

---

## 📊 Dashboard Overview

- **Live Camera Feed:** Real-time vision analysis.  
- **Sensor Status Panel:** Displays temperature, gas level, humidity, proximity.  
- **Event Logs:** All alerts, warnings, and AI interactions are logged.  
- **Access Logs:** RFID entries with timestamps.  
- **System Control:** Manual override for door, lights, and buzzer.  
- **Voice Query Panel:** Ask AIVA status questions (“Is everything safe?”, “Who entered last?”).

---

## 🧰 Project Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/<yourusername>/AIVA-Safety-System.git
cd AIVA-Safety-System
2️⃣ Flash ESP32
Upload /firmware/esp32_safety.ino using Arduino IDE.

Configure Wi-Fi credentials and MQTT/serial connection.

3️⃣ Setup M5Stack Core
Upload /firmware/m5_ai_node.ino or /scripts/m5_core.py.

Verify pan-tilt servo and speaker connections.

4️⃣ Run AI + Dashboard on Laptop
bash
Copy code
cd dashboard
python app.py
Open browser at http://localhost:5000

💬 Example Voice Interaction
User: “AIVA, is the shop floor safe?”
AIVA: “Temperature is 27°C, gas levels are normal, and all workers are detected wearing safety gear.”

User: “Who entered the restricted zone?”
AIVA: “Access granted to Employee ID-32 at 10:42 AM.”

🧭 Future Enhancements
Cloud dashboard with analytics

Integration with industrial PLCs via Modbus

Predictive maintenance using sensor history

Multi-factory deployment with central monitoring

Edge TPU-based vision for faster PPE detection

💼 Market & Impact
Target Users
SMEs, manufacturing units, and training labs

Safety managers and industrial operators

Competitive Edge
Combines AI vision + IoT + voice at low cost

Fully modular and demonstrable

Real-time safety alerts & analytics

Monetization & Scalability
Hardware kits for educational & factory use

SaaS-based dashboard subscription

Custom integrations for large industries

🤝 Contributors
Yogarathinam T.L – Hardware integration & AI System Design
Sanjay Kumar K -- Frontend
Goutham -- miniature prototype
Saravan kumar -- System specs manager and Embedded Systems
📜 License
This project is licensed under the MIT License — see LICENSE for details.

🌟 Acknowledgements
Thanks to TechSaavy Club, Easwari Engineering College for organizing Dev Arena 2025
and for inspiring innovation in smart manufacturing.

“Safety isn’t expensive — it’s priceless.
AIVA ensures it’s also intelligent.”

yaml
Copy code
