#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  for (uint8_t pin = 2; pin <= 7; ++pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  Serial.println(F("TEST 02: D2-D7 blue LEDs one at a time"));
}

void loop() {
  for (uint8_t pin = 2; pin <= 7; ++pin) {
    digitalWrite(pin, HIGH);
    Serial.print(F("LED on pin D"));
    Serial.println(pin);
    delay(400);
    digitalWrite(pin, LOW);
  }
}
