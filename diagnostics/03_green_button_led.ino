#include <Arduino.h>

const uint8_t BUTTON_PIN = A0;
const uint8_t GREEN_LED_PIN = 8;
const uint16_t DEBOUNCE_MS = 30;

bool stablePressed = false;
bool candidatePressed = false;
uint32_t candidateSince = 0;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(GREEN_LED_PIN, OUTPUT);
  stablePressed = digitalRead(BUTTON_PIN) == LOW;
  candidatePressed = stablePressed;
  digitalWrite(GREEN_LED_PIN, stablePressed ? HIGH : LOW);
  Serial.println(F("TEST 03: A0 button -> D8 green LED"));
}

void loop() {
  const bool raw = digitalRead(BUTTON_PIN) == LOW;
  const uint32_t now = millis();

  if (raw != candidatePressed) {
    candidatePressed = raw;
    candidateSince = now;
  }

  if (candidatePressed != stablePressed &&
      (uint32_t)(now - candidateSince) >= DEBOUNCE_MS) {
    stablePressed = candidatePressed;
    digitalWrite(GREEN_LED_PIN, stablePressed ? HIGH : LOW);
    Serial.println(stablePressed ? F("PRESSED") : F("RELEASED"));
  }
}
