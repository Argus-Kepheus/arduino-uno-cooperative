#include <Arduino.h>

bool due(uint16_t now, uint16_t deadline) {
  return (int16_t)(now - deadline) >= 0;
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("TEST 10: 16-bit modular timing"));

  const uint16_t deadline = 4; // after rollover
  const uint16_t samples[] = {65530U, 65535U, 0U, 3U, 4U, 5U};

  for (uint8_t i=0; i<6; ++i) {
    Serial.print(samples[i]);
    Serial.print(F(" -> "));
    Serial.println(due(samples[i], deadline) ? F("DUE") : F("WAIT"));
  }

  Serial.println(F("Expected: WAIT WAIT WAIT WAIT DUE DUE"));
}

void loop() {}
