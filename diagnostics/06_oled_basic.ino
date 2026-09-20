#include <Arduino.h>
#include <Wire.h>
#include <SSD1306Ascii.h>
#include <SSD1306AsciiWire.h>

SSD1306AsciiWire oled;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000UL);

  Wire.beginTransmission(0x3C);
  if (Wire.endTransmission() != 0) {
    Serial.println(F("OLED 0x3C not detected"));
    return;
  }

  oled.begin(&Adafruit128x64, 0x3C);
  oled.setFont(System5x7);
  oled.clear();
  oled.println(F("UNO COOPERATIVE"));
  oled.println(F("OLED TEST OK"));
  oled.println(F("A4 SDA"));
  oled.println(F("A5 SCL"));
  Serial.println(F("TEST 06 OK"));
}

void loop() {}
