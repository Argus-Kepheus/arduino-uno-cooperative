#ifndef METRICS_H
#define METRICS_H

#include <Arduino.h>

#include "cooperative_scheduler.h"


struct MetricsSnapshot {

  uint8_t appBusyPercent;

  int16_t freeRamBytes;

  int16_t minFreeRamBytes;

  uint32_t passesPerSecond;

  uint32_t maxCallbackUs;

  uint32_t maxLateMs;

  uint32_t overruns;
};


// -----------------------------------------------------------------------------
// Estimated free SRAM
// -----------------------------------------------------------------------------

inline int16_t estimateFreeRamBytes() {

#if defined(__AVR__)

  extern char __heap_start;

  extern char *__brkval;


  char stackTop;


  char *heapTop =
      (__brkval == 0)
          ? &__heap_start
          : __brkval;


  return
      (int16_t)(
          &stackTop -
          heapTop);

#else

  return -1;

#endif
}


// -----------------------------------------------------------------------------
// Metrics sampler
// -----------------------------------------------------------------------------

class MetricsSampler {

 public:

  MetricsSampler()
      :
        windowStartedUs_(0),

        minFreeRamBytes_(32767) {
  }


  void begin() {

    windowStartedUs_ =
        micros();


    minFreeRamBytes_ =
        estimateFreeRamBytes();
  }


  void sample(
      CooperativeScheduler &scheduler,
      MetricsSnapshot &snapshot) {


    const uint32_t nowUs =
        micros();


    const uint32_t elapsedUs =
        nowUs -
        windowStartedUs_;


    windowStartedUs_ =
        nowUs;


    const CooperativeScheduler::WindowCounters counters =
        scheduler.takeWindowCounters();


    // APP BUSY ----------------------------------------------------------------

    if (elapsedUs > 0) {

      uint32_t busy =
          (
              counters.callbackBusyUs *
              100UL
          )
          /
          elapsedUs;


      if (busy > 100UL) {

        busy =
            100UL;
      }


      snapshot.appBusyPercent =
          (uint8_t)busy;


      const uint32_t elapsedMs =
          elapsedUs /
          1000UL;


      snapshot.passesPerSecond =
          elapsedMs > 0
              ?
              (
                  counters.passes *
                  1000UL
              )
              /
              elapsedMs

              :
              0;
    }

    else {

      snapshot.appBusyPercent =
          0;


      snapshot.passesPerSecond =
          0;
    }


    // SRAM --------------------------------------------------------------------

    snapshot.freeRamBytes =
        estimateFreeRamBytes();


    if (
        snapshot.freeRamBytes <
        minFreeRamBytes_) {


      minFreeRamBytes_ =
          snapshot.freeRamBytes;
    }


    snapshot.minFreeRamBytes =
        minFreeRamBytes_;


    // Scheduler lifetime metrics ----------------------------------------------

    snapshot.maxCallbackUs =
        scheduler.maxCallbackUs();


    snapshot.maxLateMs =
        scheduler.maxLateMs();


    snapshot.overruns =
        scheduler.overruns();
  }


 private:

  uint32_t windowStartedUs_;

  int16_t minFreeRamBytes_;
};


#endif