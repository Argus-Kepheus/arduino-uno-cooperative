#ifndef PROJECT_CONFIG_H
#define PROJECT_CONFIG_H

#include <Arduino.h>


namespace Config {


// -----------------------------------------------------------------------------
// Serial
// -----------------------------------------------------------------------------

static const uint32_t SERIAL_BAUD =
    115200UL;


// -----------------------------------------------------------------------------
// Six independent blue LEDs
// -----------------------------------------------------------------------------

/*
 * D2 through D7 form one contiguous pin range.
 *
 * Storing only the first pin avoids a lookup table in SRAM.
 */

static const uint8_t BLUE_LED_FIRST_PIN =
    2;


static const uint8_t BLUE_LED_COUNT =
    6;


// -----------------------------------------------------------------------------
// Main-button LED
// -----------------------------------------------------------------------------

static const uint8_t GREEN_LED_PIN =
    8;


// -----------------------------------------------------------------------------
// TFT ILI9341 -- SOFTWARE SPI by design
// -----------------------------------------------------------------------------

/*
 * The TFT keeps the same physical wiring:
 *
 * D9  = D/C
 * D10 = CS
 * D11 = MOSI
 * D13 = SCK
 *
 * However, D11/D13 are driven by Adafruit's software-SPI path rather than
 * by the ATmega328P SPI peripheral.
 *
 * This is deliberate: it leaves D12/MISO available as a normal GPIO for
 * the orange display-activity LED.
 */

static const uint8_t TFT_DC_PIN =
    9;


static const uint8_t TFT_CS_PIN =
    10;


static const uint8_t TFT_MOSI_PIN =
    11;


static const uint8_t TFT_SCK_PIN =
    13;


/*
 * D13 is also connected to the Arduino Uno built-in LED L.
 *
 * Therefore TFT clock activity is physically observable on LED L.
 */


// -----------------------------------------------------------------------------
// Display activity indicator
// -----------------------------------------------------------------------------

/*
 * D12 is now an ordinary GPIO because hardware SPI is not enabled.
 *
 * HIGH = display subsystem idle
 * LOW  = instrumented TFT/OLED operation in progress
 */

static const uint8_t DISPLAY_IDLE_LED_PIN =
    12;


// -----------------------------------------------------------------------------
// Buttons
// -----------------------------------------------------------------------------

/*
 * INPUT_PULLUP:
 *
 * released = HIGH
 * pressed  = LOW
 */

static const uint8_t MAIN_BUTTON_PIN =
    A0;


static const uint8_t DECREASE_INTERVAL_BUTTON_PIN =
    A1;


static const uint8_t INCREASE_INTERVAL_BUTTON_PIN =
    A2;


// -----------------------------------------------------------------------------
// Scheduler heartbeat
// -----------------------------------------------------------------------------

static const uint8_t SCHEDULER_HEARTBEAT_LED_PIN =
    A3;


// -----------------------------------------------------------------------------
// OLED SSD1306 -- hardware I2C
// -----------------------------------------------------------------------------

/*
 * A4 = SDA
 * A5 = SCL
 */

static const uint8_t OLED_I2C_ADDRESS =
    0x3C;


static const uint32_t OLED_I2C_CLOCK_HZ =
    400000UL;


static const uint16_t OLED_REFRESH_PERIOD_MS =
    1000;


// -----------------------------------------------------------------------------
// Shared blue-LED blink interval
// -----------------------------------------------------------------------------

/*
 * The valid intervals are powers of two of 125 ms:
 *
 * 125
 * 250
 * 500
 * 1000
 * 2000
 * 4000
 *
 * Calculating them removes the need for a six-element uint16_t table.
 */

static const uint16_t BLINK_INTERVAL_BASE_MS =
    125;


static const uint8_t BLINK_INTERVAL_COUNT =
    6;


static const uint8_t BLINK_INTERVAL_INITIAL_INDEX =
    2;


// -----------------------------------------------------------------------------
// Cooperative task periods
// -----------------------------------------------------------------------------

static const uint16_t BUTTON_SCAN_PERIOD_MS =
    5;


static const uint16_t BUTTON_DEBOUNCE_MS =
    30;


static const uint16_t METRICS_SAMPLE_PERIOD_MS =
    250;


static const uint16_t DISPLAY_SERVICE_PERIOD_MS =
    20;


static const uint16_t SERIAL_STATUS_PERIOD_MS =
    1000;


static const uint16_t SCHEDULER_HEARTBEAT_PERIOD_MS =
    100;


// -----------------------------------------------------------------------------
// SRAM limits
// -----------------------------------------------------------------------------

static const uint16_t SRAM_TOTAL_BYTES =
    2048;


static const uint16_t SRAM_TARGET_FREE_BYTES =
    512;


static const uint16_t SRAM_MIN_FREE_BYTES =
    400;


}  // namespace Config


#endif