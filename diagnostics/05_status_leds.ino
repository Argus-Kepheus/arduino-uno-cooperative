#include <Arduino.h>

const uint8_t ORANGE_PIN = 12;
const uint8_t YELLOW_PIN = A3;

void setup() {
  Serial.begin(115200);
  pinMode(ORANGE_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  digitalWrite(ORANGE_PIN, LOW);
  digitalWrite(YELLOW_PIN, LOW);
  Serial.println(F("TEST 05: orange D12 / yellow A3"));
}

void loop() {
  digitalWrite(ORANGE_PIN, HIGH);
  digitalWrite(YELLOW_PIN, LOW);
  Serial.println(F("orange ON"));
  delay(700);
  digitalWrite(ORANGE_PIN, LOW);
  digitalWrite(YELLOW_PIN, HIGH);
  Serial.println(F("yellow ON"));
  delay(700);
}
