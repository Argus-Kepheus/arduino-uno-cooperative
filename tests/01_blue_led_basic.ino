#include <Arduino.h>

const uint8_t LED_PIN = 2;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);
  Serial.println(F("TEST 01: D2 blue LED"));
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  Serial.println(F("ON"));
  delay(700);
  digitalWrite(LED_PIN, LOW);
  Serial.println(F("OFF"));
  delay(700);
}
