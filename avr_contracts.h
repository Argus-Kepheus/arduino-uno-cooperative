// GENERATED FILE — DO NOT EDIT DIRECTLY.
// Source: config/hardware.json + config/runtime.json + config/avr.json
// Regenerate with: python tools/generate_avr_contracts.py --write

#ifndef AVR_CONTRACTS_H
#define AVR_CONTRACTS_H

#include <Arduino.h>
#include "project_config.h"

namespace AvrContracts {

static const uint8_t SCHEDULER_MAX_TASKS = 11;
static const uint16_t SCHEDULER_HALF_RANGE_MS = 32768U;
static const uint16_t MAX_CONFIGURED_SCHEDULER_PERIOD_MS = 4000U;

static const uint8_t BLUE_TASK_FIRST_ID = 0;
static const uint8_t BLUE_TASK_COUNT = 6;
static const uint8_t BLINK_INTERVAL_SCALE_BASE = 2;

static const uint8_t BLUE_LED_PORT_FIRST_BIT = 2;
static const uint8_t MAIN_BUTTON_PORT_BIT = 0;
static const uint8_t DECREASE_BUTTON_PORT_BIT = 1;
static const uint8_t INCREASE_BUTTON_PORT_BIT = 2;
static const uint8_t HEARTBEAT_PORT_BIT = 3;

}  // namespace AvrContracts

#if defined(__AVR__)
#if !defined(__AVR_ATmega328P__)
#error "AVR fast paths are validated only for ATmega328P"
#endif

static_assert(F_CPU == 16000000UL,
              "AVR clock differs from config/avr.json");
static_assert(Config::BLUE_LED_FIRST_PIN == 2,
              "Blue LED first pin violates AVR PORTD contract");
static_assert(Config::BLUE_LED_COUNT == 6,
              "Blue LED count violates AVR fast-I/O contract");
static_assert(Config::MAIN_BUTTON_PIN == A0,
              "Main button pin violates AVR PINC contract");
static_assert(Config::DECREASE_INTERVAL_BUTTON_PIN == A1,
              "Decrease button pin violates AVR PINC contract");
static_assert(Config::INCREASE_INTERVAL_BUTTON_PIN == A2,
              "Increase button pin violates AVR PINC contract");
static_assert(Config::SCHEDULER_HEARTBEAT_LED_PIN == A3,
              "Heartbeat pin violates AVR PORTC contract");
static_assert(AvrContracts::BLINK_INTERVAL_SCALE_BASE == 2,
              "currentBlinkIntervalMs() requires a power-of-two x2 scale");
static_assert(AvrContracts::MAX_CONFIGURED_SCHEDULER_PERIOD_MS <
                  AvrContracts::SCHEDULER_HALF_RANGE_MS,
              "Configured scheduler period violates modular-time half range");
#endif

#endif
