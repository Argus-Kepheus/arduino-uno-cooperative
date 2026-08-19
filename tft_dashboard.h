#ifndef TFT_DASHBOARD_H
#define TFT_DASHBOARD_H

#include <Arduino.h>

#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

#include "display_activity.h"
#include "metrics.h"
#include "project_config.h"


class TftDashboard {

 public:

  enum EventCode : uint8_t {

    EVENT_STARTUP = 0,

    EVENT_BUTTON_PRESSED,

    EVENT_BUTTON_RELEASED,

    EVENT_INTERVAL_CHANGED,

    EVENT_OLED_OK,

    EVENT_OLED_FAIL
  };


  TftDashboard()
      :
        /*
         * Four mandatory arguments select Adafruit software SPI:
         *
         * CS, DC, MOSI, SCK
         */
        tft_(
            Config::TFT_CS_PIN,
            Config::TFT_DC_PIN,
            Config::TFT_MOSI_PIN,
            Config::TFT_SCK_PIN),

        busyGraphX_(0),

        ramGraphX_(0),

        consoleRow_(0),

        eventHead_(0),

        eventTail_(0),

        eventCount_(0),

        cacheValid_(false),

        cachedIntervalMs_(0),

        cachedButtonPressed_(false),

        cachedBusyPercent_(0),

        cachedFreeRam_(0),

        cachedMinFreeRam_(0),

        cachedPassesPerSecond_(0),

        cachedMaxCallbackUs_(0),

        cachedMaxLateMs_(0),

        cachedOverruns_(0) {
  }


  // ---------------------------------------------------------------------------
  // Initialization
  // ---------------------------------------------------------------------------

  void begin() {

    /*
     * D12 is a completely independent GPIO in this revision.
     *
     * Software SPI touches only CS, DC, MOSI/D11 and SCK/D13.
     */

    DisplayActivity::begin();


    DisplayActivity::busyBegin();


    tft_.begin();


    tft_.setRotation(
        1);


    tft_.fillScreen(
        ILI9341_BLACK);


    tft_.setTextWrap(
        false);


    tft_.setTextSize(
        1);


    drawStaticLayout();


    DisplayActivity::busyEnd();
  }


  // ---------------------------------------------------------------------------
  // Event queue
  // ---------------------------------------------------------------------------

  void log(
      EventCode code,
      int16_t value = 0) {


    /*
     * Serial remains the authoritative diagnostic channel.
     */

    printEventToSerial(
        code,
        value);


    /*
     * Fixed-size circular queue.
     *
     * No String, malloc, new or dynamic container.
     */

    if (
        eventCount_ ==
        EVENT_QUEUE_SIZE) {


      eventTail_ =
          (
              eventTail_ +
              1
          )
          %
          EVENT_QUEUE_SIZE;


      --eventCount_;
    }


    events_[eventHead_].code =
        code;


    events_[eventHead_].value =
        value;


    eventHead_ =
        (
            eventHead_ +
            1
        )
        %
        EVENT_QUEUE_SIZE;


    ++eventCount_;
  }


  // ---------------------------------------------------------------------------
  // APP BUSY graph
  // -----------------------------------------------------------------------------

  void updateBusyGraph(
      uint8_t percent) {


    if (percent > 100) {

      percent =
          100;
    }


    const int16_t x =
        BUSY_GRAPH_X +
        busyGraphX_;


    const int16_t usableHeight =
        GRAPH_H -
        2;


    const int16_t barHeight =
        (
            (int32_t)percent *
            usableHeight
        )
        /
        100;


    DisplayActivity::busyBegin();


    /*
     * Erase only one history column.
     */

    tft_.drawFastVLine(
        x,
        GRAPH_Y + 1,
        usableHeight,
        ILI9341_BLACK);


    if (barHeight > 0) {

      tft_.drawFastVLine(
          x,

          GRAPH_Y +
              GRAPH_H -
              1 -
              barHeight,

          barHeight,

          ILI9341_RED);
    }


    DisplayActivity::busyEnd();


    busyGraphX_ =
        (
            busyGraphX_ +
            1
        )
        %
        GRAPH_W;
  }


  // ---------------------------------------------------------------------------
  // SRAM graph
  // ---------------------------------------------------------------------------

  void updateRamGraph(
      int16_t freeRamBytes) {


    int16_t bounded =
        freeRamBytes;


    if (bounded < 0) {

      bounded =
          0;
    }


    if (
        bounded >
        (int16_t)
            Config::SRAM_TOTAL_BYTES) {


      bounded =
          Config::SRAM_TOTAL_BYTES;
    }


    const uint8_t percent =
        (uint8_t)(
            (
                (int32_t)bounded *
                100L
            )
            /
            Config::SRAM_TOTAL_BYTES);


    const int16_t x =
        RAM_GRAPH_X +
        ramGraphX_;


    const int16_t usableHeight =
        GRAPH_H -
        2;


    const int16_t barHeight =
        (
            (int32_t)percent *
            usableHeight
        )
        /
        100;


    DisplayActivity::busyBegin();


    tft_.drawFastVLine(
        x,
        GRAPH_Y + 1,
        usableHeight,
        ILI9341_BLACK);


    if (barHeight > 0) {

      tft_.drawFastVLine(
          x,

          GRAPH_Y +
              GRAPH_H -
              1 -
              barHeight,

          barHeight,

          ILI9341_MAGENTA);
    }


    DisplayActivity::busyEnd();


    ramGraphX_ =
        (
            ramGraphX_ +
            1
        )
        %
        GRAPH_W;
  }


  // ---------------------------------------------------------------------------
  // TFT row 1
  // ---------------------------------------------------------------------------

  void updateStatusRow(
      const MetricsSnapshot &metrics,
      uint16_t blinkIntervalMs,
      bool mainButtonPressed) {


    const bool dirty =
        !cacheValid_ ||

        cachedIntervalMs_ !=
            blinkIntervalMs ||

        cachedButtonPressed_ !=
            mainButtonPressed ||

        cachedBusyPercent_ !=
            metrics.appBusyPercent;


    if (!dirty) {

      return;
    }


    DisplayActivity::busyBegin();


    if (
        !cacheValid_ ||

        cachedIntervalMs_ !=
            blinkIntervalMs) {


      printValue(
          32,
          99,
          58,
          blinkIntervalMs,
          ILI9341_CYAN);


      cachedIntervalMs_ =
          blinkIntervalMs;
    }


    if (
        !cacheValid_ ||

        cachedButtonPressed_ !=
            mainButtonPressed) {


      printValue(
          137,
          99,
          28,

          mainButtonPressed
              ? 1
              : 0,

          mainButtonPressed
              ? ILI9341_GREEN
              : ILI9341_WHITE);


      cachedButtonPressed_ =
          mainButtonPressed;
    }


    if (
        !cacheValid_ ||

        cachedBusyPercent_ !=
            metrics.appBusyPercent) {


      printValue(
          249,
          99,
          40,
          metrics.appBusyPercent,
          ILI9341_RED);


      cachedBusyPercent_ =
          metrics.appBusyPercent;
    }


    DisplayActivity::busyEnd();
  }


  // ---------------------------------------------------------------------------
  // TFT row 2
  // ---------------------------------------------------------------------------

  void updateResourceRow(
      const MetricsSnapshot &metrics) {


    const bool dirty =
        !cacheValid_ ||

        cachedFreeRam_ !=
            metrics.freeRamBytes ||

        cachedPassesPerSecond_ !=
            metrics.passesPerSecond ||

        cachedMaxCallbackUs_ !=
            metrics.maxCallbackUs;


    if (!dirty) {

      return;
    }


    DisplayActivity::busyBegin();


    if (
        !cacheValid_ ||

        cachedFreeRam_ !=
            metrics.freeRamBytes) {


      printValueSigned(
          32,
          113,
          58,
          metrics.freeRamBytes,
          ILI9341_MAGENTA);


      cachedFreeRam_ =
          metrics.freeRamBytes;
    }


    if (
        !cacheValid_ ||

        cachedPassesPerSecond_ !=
            metrics.passesPerSecond) {


      printValue(
          137,
          113,
          70,
          metrics.passesPerSecond,
          ILI9341_YELLOW);


      cachedPassesPerSecond_ =
          metrics.passesPerSecond;
    }


    if (
        !cacheValid_ ||

        cachedMaxCallbackUs_ !=
            metrics.maxCallbackUs) {


      printValue(
          254,
          113,
          60,
          metrics.maxCallbackUs,
          ILI9341_ORANGE);


      cachedMaxCallbackUs_ =
          metrics.maxCallbackUs;
    }


    DisplayActivity::busyEnd();
  }


  // ---------------------------------------------------------------------------
  // TFT row 3
  // ---------------------------------------------------------------------------

  void updateTimingRow(
      const MetricsSnapshot &metrics) {


    const bool dirty =
        !cacheValid_ ||

        cachedMaxLateMs_ !=
            metrics.maxLateMs ||

        cachedOverruns_ !=
            metrics.overruns ||

        cachedMinFreeRam_ !=
            metrics.minFreeRamBytes;


    if (!dirty) {

      cacheValid_ =
          true;


      return;
    }


    DisplayActivity::busyBegin();


    if (
        !cacheValid_ ||

        cachedMaxLateMs_ !=
            metrics.maxLateMs) {


      printValue(
          32,
          127,
          70,
          metrics.maxLateMs,
          ILI9341_WHITE);


      cachedMaxLateMs_ =
          metrics.maxLateMs;
    }


    if (
        !cacheValid_ ||

        cachedOverruns_ !=
            metrics.overruns) {


      printValue(
          137,
          127,
          70,
          metrics.overruns,
          ILI9341_WHITE);


      cachedOverruns_ =
          metrics.overruns;
    }


    if (
        !cacheValid_ ||

        cachedMinFreeRam_ !=
            metrics.minFreeRamBytes) {


      printValueSigned(
          254,
          127,
          60,
          metrics.minFreeRamBytes,

          metrics.minFreeRamBytes >=
                  (int16_t)
                      Config::SRAM_MIN_FREE_BYTES

              ? ILI9341_GREEN
              : ILI9341_RED);


      cachedMinFreeRam_ =
          metrics.minFreeRamBytes;
    }


    cacheValid_ =
        true;


    DisplayActivity::busyEnd();
  }


  // ---------------------------------------------------------------------------
  // Render one queued event
  // ---------------------------------------------------------------------------

  void renderNextEvent() {

    if (eventCount_ == 0) {

      return;
    }


    const Event event =
        events_[eventTail_];


    eventTail_ =
        (
            eventTail_ +
            1
        )
        %
        EVENT_QUEUE_SIZE;


    --eventCount_;


    char line[41];


    formatEvent(
        event.code,
        event.value,
        line,
        sizeof(line));


    const int16_t y =
        CONSOLE_Y +
        consoleRow_ *
            8;


    DisplayActivity::busyBegin();


    /*
     * Clear only the text area, not all 318 pixels of the screen width.
     */

    tft_.fillRect(
        1,
        y,
        CONSOLE_CLEAR_W,
        8,
        ILI9341_BLACK);


    tft_.setCursor(
        2,
        y);


    tft_.setTextColor(
        eventColor(event.code),
        ILI9341_BLACK);


    tft_.print(
        line);


    DisplayActivity::busyEnd();


    consoleRow_ =
        (
            consoleRow_ +
            1
        )
        %
        CONSOLE_ROWS;
  }


 private:

  struct Event {

    EventCode code;

    int16_t value;
  };


  static const uint8_t EVENT_QUEUE_SIZE =
      6;


  static const int16_t GRAPH_Y =
      29;


  static const int16_t GRAPH_H =
      56;


  static const int16_t GRAPH_W =
      148;


  static const int16_t BUSY_GRAPH_X =
      4;


  static const int16_t RAM_GRAPH_X =
      168;


  static const int16_t CONSOLE_Y =
      148;


  static const uint8_t CONSOLE_ROWS =
      11;


  static const int16_t CONSOLE_CLEAR_W =
      240;


  // ---------------------------------------------------------------------------
  // Static screen
  // ---------------------------------------------------------------------------

  void drawStaticLayout() {

    tft_.drawRect(
        0,
        0,
        320,
        240,
        ILI9341_DARKGREY);


    tft_.setTextColor(
        ILI9341_WHITE,
        ILI9341_BLACK);


    tft_.setCursor(
        6,
        6);


    tft_.print(
        F("ARDUINO UNO COOPERATIVE"));


    // APP BUSY ----------------------------------------------------------------

    tft_.setTextColor(
        ILI9341_RED,
        ILI9341_BLACK);


    tft_.setCursor(
        BUSY_GRAPH_X,
        19);


    tft_.print(
        F("APP BUSY"));


    tft_.drawRect(
        BUSY_GRAPH_X - 1,
        GRAPH_Y,
        GRAPH_W + 2,
        GRAPH_H,
        ILI9341_DARKGREY);


    // SRAM --------------------------------------------------------------------

    tft_.setTextColor(
        ILI9341_MAGENTA,
        ILI9341_BLACK);


    tft_.setCursor(
        RAM_GRAPH_X,
        19);


    tft_.print(
        F("SRAM FREE"));


    tft_.drawRect(
        RAM_GRAPH_X - 1,
        GRAPH_Y,
        GRAPH_W + 2,
        GRAPH_H,
        ILI9341_DARKGREY);


    // Text rows ---------------------------------------------------------------

    tft_.setTextColor(
        ILI9341_WHITE,
        ILI9341_BLACK);


    // Row 1
    tft_.setCursor(4, 99);
    tft_.print(F("INT:"));

    tft_.setCursor(105, 99);
    tft_.print(F("BTN:"));

    tft_.setCursor(211, 99);
    tft_.print(F("BUSY:"));


    // Row 2
    tft_.setCursor(4, 113);
    tft_.print(F("RAM:"));

    tft_.setCursor(105, 113);
    tft_.print(F("PASS:"));

    tft_.setCursor(211, 113);
    tft_.print(F("CBMAX:"));


    // Row 3
    tft_.setCursor(4, 127);
    tft_.print(F("LATE:"));

    tft_.setCursor(105, 127);
    tft_.print(F("OVR:"));

    tft_.setCursor(211, 127);
    tft_.print(F("RAM LOW:"));


    // Event console ------------------------------------------------------------

    tft_.drawFastHLine(
        0,
        140,
        320,
        ILI9341_DARKGREY);


    tft_.setCursor(
        4,
        141);


    tft_.print(
        F("EVENTS"));
  }


  // ---------------------------------------------------------------------------
  // Numeric fields
  // ---------------------------------------------------------------------------

  void printValue(
      int16_t x,
      int16_t y,
      int16_t width,
      uint32_t value,
      uint16_t color) {


    tft_.fillRect(
        x,
        y,
        width,
        8,
        ILI9341_BLACK);


    tft_.setCursor(
        x,
        y);


    tft_.setTextColor(
        color,
        ILI9341_BLACK);


    tft_.print(
        value);
  }


  void printValueSigned(
      int16_t x,
      int16_t y,
      int16_t width,
      int32_t value,
      uint16_t color) {


    tft_.fillRect(
        x,
        y,
        width,
        8,
        ILI9341_BLACK);


    tft_.setCursor(
        x,
        y);


    tft_.setTextColor(
        color,
        ILI9341_BLACK);


    tft_.print(
        value);
  }


  // ---------------------------------------------------------------------------
  // Event formatting
  // ---------------------------------------------------------------------------

  uint16_t eventColor(
      EventCode code) const {


    switch (code) {

      case EVENT_BUTTON_PRESSED:

      case EVENT_BUTTON_RELEASED:

        return ILI9341_GREEN;


      case EVENT_INTERVAL_CHANGED:

        return ILI9341_BLUE;


      case EVENT_OLED_OK:

        return ILI9341_CYAN;


      case EVENT_OLED_FAIL:

        return ILI9341_RED;


      case EVENT_STARTUP:

      default:

        return ILI9341_WHITE;
    }
  }


  void formatEvent(
      EventCode code,
      int16_t value,
      char *buffer,
      size_t size) const {


    switch (code) {

      case EVENT_BUTTON_PRESSED:

        strncpy_P(
            buffer,
            PSTR("Button pressed -> green ON"),
            size);

        break;


      case EVENT_BUTTON_RELEASED:

        strncpy_P(
            buffer,
            PSTR("Button released -> green OFF"),
            size);

        break;


      case EVENT_INTERVAL_CHANGED:

        snprintf_P(
            buffer,
            size,
            PSTR("Blue LEDs interval -> %d ms"),
            value);

        break;


      case EVENT_OLED_OK:

        strncpy_P(
            buffer,
            PSTR("OLED diagnostic online"),
            size);

        break;


      case EVENT_OLED_FAIL:

        strncpy_P(
            buffer,
            PSTR("OLED diagnostic not detected"),
            size);

        break;


      case EVENT_STARTUP:

      default:

        strncpy_P(
            buffer,
            PSTR("System starting"),
            size);

        break;
    }


    buffer[size - 1] =
        '\0';
  }


  void printEventToSerial(
      EventCode code,
      int16_t value) const {


    char line[41];


    formatEvent(
        code,
        value,
        line,
        sizeof(line));


    Serial.println(
        line);
  }


  // ---------------------------------------------------------------------------
  // Display object
  // ---------------------------------------------------------------------------

  Adafruit_ILI9341 tft_;


  // Graph cursors
  uint16_t busyGraphX_;

  uint16_t ramGraphX_;


  // Console
  uint8_t consoleRow_;


  Event events_[EVENT_QUEUE_SIZE];

  uint8_t eventHead_;

  uint8_t eventTail_;

  uint8_t eventCount_;


  // TFT value cache -----------------------------------------------------------

  bool cacheValid_;

  uint16_t cachedIntervalMs_;

  bool cachedButtonPressed_;

  uint8_t cachedBusyPercent_;

  int16_t cachedFreeRam_;

  int16_t cachedMinFreeRam_;

  uint32_t cachedPassesPerSecond_;

  uint32_t cachedMaxCallbackUs_;

  uint32_t cachedMaxLateMs_;

  uint32_t cachedOverruns_;
};


#endif