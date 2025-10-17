#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>

#define DHTPIN 4
#define DHTTYPE DHT11
#define MQ3_PIN 32
#define BUZZER_PIN 5
#define LED_PIN 13
#define NUM_LEDS 144

LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHTPIN, DHTTYPE);
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

unsigned long previousMillis = 0;
const unsigned long displayInterval = 3000;  // 3 seconds
int displayMode = 0;  // 0 = Temp, 1 = Humidity, 2 = Gas

float temperature = 0.0;
float humidity = 0.0;
int gasValue = 0;
bool buzzerState = false;

bool messageMode = false;
String incomingMessage = "";
unsigned long messageStartTime = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  dht.begin();
  strip.begin();
  strip.show();

  lcd.init();
  lcd.backlight();
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Starting");
  lcd.setCursor(0, 1);
  lcd.print("Team Phoenix");
  delay(2000);
  lcd.clear();
}

void loop() {
  unsigned long currentMillis = millis();

  // ---------- HANDLE INCOMING SERIAL ----------
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.equalsIgnoreCase("true")) {
      buzzerState = true;
      beepBuzzer();
    } 
    else if (input.equalsIgnoreCase("false")) {
      buzzerState = false;
    } 
    else if (input.startsWith("color:")) {
      setColorFromSerial(input);
    } 
    else {
      // Any other text input → display it with blinking
      incomingMessage = input;
      messageMode = true;
      messageStartTime = millis();
    }
  }

  // ---------- MESSAGE DISPLAY MODE ----------
  if (messageMode) {
    unsigned long elapsed = millis() - messageStartTime;
    if (elapsed < 10000) {  // 10 seconds
      static bool blinkState = false;
      static unsigned long lastBlink = 0;

      if (millis() - lastBlink >= 500) { // toggle every 0.5s
        lastBlink = millis();
        blinkState = !blinkState;

        lcd.clear();
        if (blinkState) {
          lcd.setCursor(0, 0);
          lcd.print(incomingMessage.substring(0, 16));  // limit to 16 chars
        }
        lcd.setCursor(0, 1);
        lcd.print("Team Phoenix");
      }
      return;  // skip sensor display while message blinking
    } else {
      messageMode = false;
      lcd.clear();
    }
  }

  // ---------- SENSOR DISPLAY MODE ----------
  if (currentMillis - previousMillis >= displayInterval) {
    previousMillis = currentMillis;
    displayMode = (displayMode + 1) % 3;

    temperature = dht.readTemperature();
    humidity = dht.readHumidity();
    gasValue = analogRead(MQ3_PIN);

    lcd.clear();
    if (displayMode == 0) {
      lcd.setCursor(0, 0);
      lcd.print("Temp: ");
      lcd.print(temperature, 1);
      lcd.print(" C");
    } else if (displayMode == 1) {
      lcd.setCursor(0, 0);
      lcd.print("Humidity: ");
      lcd.print(humidity, 1);
      lcd.print("%");
    } else {
      lcd.setCursor(0, 0);
      lcd.print("Gas: ");
      lcd.print(gasValue);
    }

    lcd.setCursor(0, 1);
    lcd.print("Team Phoenix");

    Serial.print("Temp: ");
    Serial.print(temperature, 1);
    Serial.print(" C\tHumidity: ");
    Serial.print(humidity, 1);
    Serial.print("%\tGas: ");
    Serial.print(gasValue);
    Serial.print("\tBuzzer: ");
    Serial.println(buzzerState ? "ON" : "OFF");
  }
}

// ---------- HELPER FUNCTIONS ----------
void beepBuzzer() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(150);
    digitalWrite(BUZZER_PIN, LOW);
    delay(150);
  }
}

void setColorFromSerial(String input) {
  input.replace("color:", "");
  int firstComma = input.indexOf(',');
  int secondComma = input.indexOf(',', firstComma + 1);
  if (firstComma == -1 || secondComma == -1) return;

  int r = input.substring(0, firstComma).toInt();
  int g = input.substring(firstComma + 1, secondComma).toInt();
  int b = input.substring(secondComma + 1).toInt();
  setStripColor(r, g, b);
}

void setStripColor(int r, int g, int b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}
