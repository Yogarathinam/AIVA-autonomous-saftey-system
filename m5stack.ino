#include <M5Unified.h>
#include <MFRC522.h>
#include <SPI.h>

// --- Pins ---
#define SS_PIN    21
#define RST_PIN   22
#define TRIG_PIN  26
#define ECHO_PIN  36
#define OUT_PIN   2   // instead of servo

MFRC522 mfrc522(SS_PIN, RST_PIN);

String lastUID = "";            // last scanned UID
bool waitForResponse = false;   // waiting for OK from webpage
bool rfidSent = false;
bool pinActive = false;
unsigned long pinTimer = 0;

void setup() {
    auto cfg = M5.config();
    cfg.clear_display = true;
    M5.begin(cfg);
    M5.Display.setBrightness(80);

    Serial.begin(115200);
    delay(200);

    SPI.begin(18, 19, 23, 21); 
    mfrc522.PCD_Init();

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(OUT_PIN, OUTPUT);
    digitalWrite(OUT_PIN, LOW);

    M5.Display.clear();
    M5.Display.setTextSize(2);
    M5.Display.setTextColor(GREEN, BLACK);
    M5.Display.setCursor(10, 20);
    M5.Display.println("M5Stack Ready");
}

void loop() {
    M5.update();

    // --- 1️⃣ Check RFID ---
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
        String uid = "";
        for (byte i = 0; i < mfrc522.uid.size; i++) {
            if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
            uid += String(mfrc522.uid.uidByte[i], HEX);
        }
        uid.toUpperCase();

        if (uid != lastUID) {
            lastUID = uid;
            waitForResponse = true;
            rfidSent = false;
        }

        mfrc522.PICC_HaltA();
    }

    // --- 2️⃣ Send Serial Data ---
    float distance = readDistance();

    Serial.print("DIST:");
    if (distance > 0) Serial.print(distance, 1);
    else Serial.print("NULL");
    Serial.print("\t");

    Serial.print("RFID:");
    if (waitForResponse && !rfidSent) {
        Serial.print(lastUID);
        rfidSent = true;
    } else {
        Serial.print("NULL");
    }
    Serial.print("\t");

    Serial.print("Door:");
    Serial.println(pinActive ? "OPEN" : "CLOSED");

    // --- 3️⃣ Check Serial for OK ---
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.equalsIgnoreCase("OK") && waitForResponse) {
            digitalWrite(OUT_PIN, HIGH); // set pin HIGH
            pinActive = true;
            pinTimer = millis();
            waitForResponse = false;
            Serial.println("Pin HIGH activated!");
            M5.Display.fillRect(0, 100, 320, 40, BLACK);
            M5.Display.setCursor(10, 100);
            M5.Display.setTextColor(YELLOW, BLACK);
            M5.Display.println("Pin ACTIVE");
        }
    }

    // --- 4️⃣ Turn pin LOW after 2 seconds ---
    if (pinActive && millis() - pinTimer >= 2000) {
        digitalWrite(OUT_PIN, LOW);
        pinActive = false;
        lastUID = ""; // allow same card again
        rfidSent = false;
        M5.Display.fillRect(0, 100, 320, 40, BLACK);
        M5.Display.setCursor(10, 100);
        M5.Display.setTextColor(RED, BLACK);
        M5.Display.println("Pin INACTIVE");
    }

    delay(100);
}

float readDistance() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    if (duration == 0) return -1;
    return duration * 0.034 / 2;
}
