#ifndef OLED_STATUS_H
#define OLED_STATUS_H

#include <Arduino.h>
#include <Wire.h>

#include <SSD1306Ascii.h>
#include <SSD1306AsciiWire.h>

#include "display_activity.h"
#include "metrics.h"
#include "project_config.h"


class OledStatus {

 public:

  OledStatus()
      :
        available_(false),

        lastRefreshMs_(0) {
  }


  // ---------------------------------------------------------------------------
  // Initialization
  // ---------------------------------------------------------------------------

  bool begin() {

    Wire.begin();


    Wire.setClock(
        Config::OLED_I2C_CLOCK_HZ);


    /*
     * Probe address 0x3C before initializing the controller.
     */

    Wire.beginTransmission(
        Config::OLED_I2C_ADDRESS);


    if (
        Wire.endTransmission() !=
        0) {


      available_ =
          false;


      return false;
    }


    DisplayActivity::busyBegin();


    oled_.begin(
        &Adafruit128x64,
        Config::OLED_I2C_ADDRESS);


    oled_.setFont(
        System5x7);


    oled_.clear();


    DisplayActivity::busyEnd();


    available_ =
        true;


    lastRefreshMs_ =
        0;


    return true;
  }


  bool available() const {

    return available_;
  }


  // ---------------------------------------------------------------------------
  // Rate-limited refresh
  // ---------------------------------------------------------------------------

  void refreshIfDue(
      const MetricsSnapshot &metrics,
      uint16_t blinkIntervalMs,
      uint32_t nowMs) {


    if (!available_) {

      return;
    }


    if (
        lastRefreshMs_ != 0 &&

        (uint32_t)(
            nowMs -
            lastRefreshMs_) <
            Config::OLED_REFRESH_PERIOD_MS) {


      return;
    }


    lastRefreshMs_ =
        nowMs;


    refresh(
        metrics,
        blinkIntervalMs);
  }


 private:

  // ---------------------------------------------------------------------------
  // Diagnostic panel
  // ---------------------------------------------------------------------------

  void refresh(
      const MetricsSnapshot &metrics,
      uint16_t blinkIntervalMs) {


    char line[24];


    DisplayActivity::busyBegin();


    printLine(
        0,
        "UNO COOPERATIVE");


    snprintf_P(
        line,
        sizeof(line),
        PSTR("INT %4u ms"),
        blinkIntervalMs);


    printLine(
        1,
        line);


    snprintf_P(
        line,
        sizeof(line),
        PSTR("BUSY %3u %%"),
        metrics.appBusyPercent);


    printLine(
        2,
        line);


    snprintf_P(
        line,
        sizeof(line),
        PSTR("RAM %5d B"),
        metrics.freeRamBytes);


    printLine(
        3,
        line);


    snprintf_P(
        line,
        sizeof(line),
        PSTR("LOW %5d B"),
        metrics.minFreeRamBytes);


    printLine(
        4,
        line);


    snprintf_P(
        line,
        sizeof(line),
        PSTR("PASS %7lu"),
        (unsigned long)
            metrics.passesPerSecond);


    printLine(
        5,
        line);


    snprintf_P(
        line,
        sizeof(line),
        PSTR("LATE %5lu ms"),
        (unsigned long)
            metrics.maxLateMs);


    printLine(
        6,
        line);


    snprintf_P(
        line,
        sizeof(line),
        PSTR("OVR %8lu"),
        (unsigned long)
            metrics.overruns);


    printLine(
        7,
        line);


    DisplayActivity::busyEnd();
  }


  // ---------------------------------------------------------------------------
  // Fixed-width OLED row
  // ---------------------------------------------------------------------------

  void printLine(
      uint8_t row,
      const char *text) {


    /*
     * Sixteen columns are sufficient for the diagnostic fields and reduce
     * I2C traffic compared with rewriting the full 21-character width.
     */

    char padded[17];


    uint8_t i =
        0;


    while (
        i < 16 &&
        text[i] != '\0') {


      padded[i] =
          text[i];


      ++i;
    }


    while (i < 16) {

      padded[i++] =
          ' ';
    }


    padded[16] =
        '\0';


    oled_.setCursor(
        0,
        row);


    oled_.print(
        padded);
  }


  SSD1306AsciiWire oled_;

  bool available_;

  uint32_t lastRefreshMs_;
};


#endif