#ifndef BUTTON_DEBOUNCE_H
#define BUTTON_DEBOUNCE_H

#include <Arduino.h>


class DebouncedButton {

 public:

  enum Event : uint8_t {

    NONE = 0,

    PRESSED,

    RELEASED
  };


  DebouncedButton()
      :
        pin_(0),

        debounceMs_(30),

        stablePressed_(false),

        candidatePressed_(false),

        candidateSinceMs_(0) {
  }


  void begin(
      uint8_t pin,
      uint8_t debounceMs) {


    pin_ =
        pin;


    debounceMs_ =
        debounceMs;


    pinMode(
        pin_,
        INPUT_PULLUP);


    stablePressed_ =
        readPressed();


    candidatePressed_ =
        stablePressed_;


    candidateSinceMs_ =
        (uint16_t)millis();
  }


  /*
   * rawPressed is sampled by the caller rather than read here, so that a
   * caller polling several buttons on the same port can take one port
   * read and share it instead of paying a digitalRead() per button.
   */

  Event poll(
      uint16_t nowMs,
      bool rawPressed) {


    if (
        rawPressed !=
        candidatePressed_) {


      candidatePressed_ =
          rawPressed;


      candidateSinceMs_ =
          nowMs;


      return NONE;
    }


    if (
        candidatePressed_ !=
            stablePressed_ &&

        (uint16_t)(
            nowMs -
            candidateSinceMs_) >=
            debounceMs_) {


      stablePressed_ =
          candidatePressed_;


      return stablePressed_
          ? PRESSED
          : RELEASED;
    }


    return NONE;
  }


  bool isPressed() const {

    return stablePressed_;
  }


 private:

  bool readPressed() const {

    return
        digitalRead(pin_) ==
        LOW;
  }


  uint8_t pin_;

  uint8_t debounceMs_;

  bool stablePressed_;

  bool candidatePressed_;

  uint16_t candidateSinceMs_;
};


#endif