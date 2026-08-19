#include <Arduino.h>

const uint8_t DEC_PIN = A1;
const uint8_t INC_PIN = A2;
uint8_t indexValue = 2;

uint16_t intervalMs() {
  return (uint16_t)(125U << indexValue);
}

bool previousDec = HIGH;
bool previousInc = HIGH;

void setup() {
  Serial.begin(115200);
  pinMode(DEC_PIN, INPUT_PULLUP);
  pinMode(INC_PIN, INPUT_PULLUP);
  Serial.println(F("TEST 04: A1/A2 interval buttons"));
  Serial.println(intervalMs());
}

void loop() {
  const bool dec = digitalRead(DEC_PIN);
  const bool inc = digitalRead(INC_PIN);

  if (previousDec == HIGH && dec == LOW && indexValue > 0) {
    --indexValue;
    Serial.print(F("interval = "));
    Serial.println(intervalMs());
  }
  if (previousInc == HIGH && inc == LOW && indexValue < 5) {
    ++indexValue;
    Serial.print(F("interval = "));
    Serial.println(intervalMs());
  }

  previousDec = dec;
  previousInc = inc;
  delay(20);
}
