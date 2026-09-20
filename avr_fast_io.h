#ifndef AVR_FAST_IO_H
#define AVR_FAST_IO_H

#include <Arduino.h>

#include "project_config.h"
#include "avr_contracts.h"


namespace AvrFastIo {


inline void toggleBlueLed(
    uint8_t index) {

#if defined(__AVR_ATmega328P__)

  PORTD ^=
      (uint8_t)(
          1U <<
          (AvrContracts::BLUE_LED_PORT_FIRST_BIT + index));

#else

  const uint8_t pin =
      (uint8_t)(
          Config::BLUE_LED_FIRST_PIN +
          index);


  digitalWrite(
      pin,
      digitalRead(pin)
          ? LOW
          : HIGH);

#endif
}


inline void sampleButtons(
    bool &mainPressed,
    bool &decreasePressed,
    bool &increasePressed) {

#if defined(__AVR_ATmega328P__)

  const uint8_t pinc =
      PINC;


  mainPressed =
      !(pinc &
        (1U << AvrContracts::MAIN_BUTTON_PORT_BIT));

  decreasePressed =
      !(pinc &
        (1U << AvrContracts::DECREASE_BUTTON_PORT_BIT));

  increasePressed =
      !(pinc &
        (1U << AvrContracts::INCREASE_BUTTON_PORT_BIT));

#else

  mainPressed =
      digitalRead(
          Config::MAIN_BUTTON_PIN) == LOW;

  decreasePressed =
      digitalRead(
          Config::DECREASE_INTERVAL_BUTTON_PIN) == LOW;

  increasePressed =
      digitalRead(
          Config::INCREASE_INTERVAL_BUTTON_PIN) == LOW;

#endif
}


inline void toggleSchedulerHeartbeat() {

#if defined(__AVR_ATmega328P__)

  PORTC ^=
      (uint8_t)(
          1U <<
          AvrContracts::HEARTBEAT_PORT_BIT);

#else

  digitalWrite(
      Config::SCHEDULER_HEARTBEAT_LED_PIN,

      digitalRead(
          Config::SCHEDULER_HEARTBEAT_LED_PIN)
          ? LOW
          : HIGH);

#endif
}


}  // namespace AvrFastIo


#endif
