#ifndef DISPLAY_ACTIVITY_H
#define DISPLAY_ACTIVITY_H

#include <Arduino.h>

#include "project_config.h"


namespace DisplayActivity {


/*
 * D12 is fixed by the project hardware.
 *
 * HIGH = display subsystem idle
 * LOW  = instrumented display operation in progress
 */

inline void begin() {

  pinMode(
      Config::DISPLAY_IDLE_LED_PIN,
      OUTPUT);


  digitalWrite(
      Config::DISPLAY_IDLE_LED_PIN,
      HIGH);
}


inline void busyBegin() {

  digitalWrite(
      Config::DISPLAY_IDLE_LED_PIN,
      LOW);
}


inline void busyEnd() {

  digitalWrite(
      Config::DISPLAY_IDLE_LED_PIN,
      HIGH);
}


}  // namespace DisplayActivity


#endif