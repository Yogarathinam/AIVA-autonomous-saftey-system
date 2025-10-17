#include <Servo.h>

Servo myServo;

const int inputPin = 2;   // Pin receiving signal from other microcontroller
const int servoPin = 9;   // Servo signal pin
bool hasMoved = false;    // To prevent repeated triggers

void setup() {
  pinMode(inputPin, INPUT);   // Input from another microcontroller
  myServo.attach(servoPin);   // Attach servo to pin 9
  myServo.write(0);           // Start at 0 degrees
}

void loop() {
  int signal = digitalRead(inputPin);

  if (signal == HIGH && !hasMoved) {
    hasMoved = true;

    // Rotate servo from 0 to 180 smoothly
    for (int pos = 0; pos <= 180; pos++) {
      myServo.write(pos);
      delay(10); // Smooth motion
    }

    // Hold at 180 degrees for 15 seconds
    delay(15000);

    // Return servo back to 0 degrees
    for (int pos = 180; pos >= 0; pos--) {
      myServo.write(pos);
      delay(15);
    }

    // Small delay to avoid retriggering too fast
    delay(1000);
  }

  // Reset trigger when signal goes low
  if (signal == LOW) {
    hasMoved = false;
  }
}
