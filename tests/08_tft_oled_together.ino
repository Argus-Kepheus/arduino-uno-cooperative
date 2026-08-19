#include <Arduino.h>
#include <Wire.h>
#include <SSD1306Ascii.h>
#include <SSD1306AsciiWire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

SSD1306AsciiWire oled;
Adafruit_ILI9341 tft(10, 9, 11, 13);

void setup() {
  Serial.begin(115200);

  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_GREEN);
  tft.setCursor(10, 10);
  tft.print(F("TFT + OLED TEST"));

  Wire.begin();
  Wire.setClock(400000UL);
  oled.begin(&Adafruit128x64, 0x3C);
  oled.setFont(System5x7);
  oled.clear();
  oled.println(F("TFT + OLED"));
  oled.println(F("TOGETHER OK"));

  Serial.println(F("TEST 08 initialized"));
}

void loop() {
  static uint32_t n = 0;
  static uint32_t last = 0;
  if ((uint32_t)(millis() - last) >= 1000) {
    last = millis();
    ++n;
    tft.fillRect(10, 30, 150, 12, ILI9341_BLACK);
    tft.setCursor(10, 30);
    tft.setTextColor(ILI9341_YELLOW);
    tft.print(n);
    oled.setCursor(0, 3);
    oled.print(F("COUNT "));
    oled.print(n);
    oled.print(F("   "));
    Serial.println(n);
  }
}
