#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

const uint8_t TFT_DC = 9;
const uint8_t TFT_CS = 10;
const uint8_t TFT_MOSI = 11;
const uint8_t TFT_SCK = 13;

Adafruit_ILI9341 tft(TFT_CS, TFT_DC, TFT_MOSI, TFT_SCK);

void setup() {
  Serial.begin(115200);
  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);
  tft.setCursor(20, 30);
  tft.print(F("UNO COOPERATIVE"));
  tft.setTextSize(1);
  tft.setCursor(20, 65);
  tft.print(F("Software SPI D11/D13"));
  tft.drawRect(20, 90, 250, 80, ILI9341_CYAN);
  Serial.println(F("TEST 07: TFT software SPI initialized"));
}

void loop() {}
