#ifndef COOPERATIVE_SCHEDULER_H
#define COOPERATIVE_SCHEDULER_H

#include <Arduino.h>

#include "avr_contracts.h"


class CooperativeScheduler {

 public:

  typedef void (*TaskCallback)();


  struct WindowCounters {

    uint32_t callbackBusyUs;

    uint32_t passes;
  };


  // Capacity is generated from the canonical AVR scheduler contract.
  static const uint8_t MAX_TASKS =
      AvrContracts::SCHEDULER_MAX_TASKS;


  static const uint8_t INVALID_TASK =
      0xFF;


  /*
   * Only the lower 16 bits of millis() are needed.
   *
   * Signed modular differences are unambiguous while every scheduled
   * interval remains below AvrContracts::SCHEDULER_HALF_RANGE_MS and the
   * scheduler is not prevented from executing for that long.
   *
   * The maximum currently configured period is generated in avr_contracts.h.
   */

  typedef uint16_t TickMs;

  static_assert(sizeof(TickMs) == 2,
                "Scheduler TickMs must remain 16-bit");


  CooperativeScheduler()
      :
        taskCount_(0),

        callbackBusyUsWindow_(0),

        passesWindow_(0),

        maxCallbackUs_(0),

        maxLateMs_(0),

        overruns_(0) {
  }


  // ---------------------------------------------------------------------------
  // Register task
  // ---------------------------------------------------------------------------

  uint8_t add(
      TaskCallback callback,
      uint16_t periodMs,
      uint16_t firstDelayMs = 0) {


    if (
        callback == 0 ||

        periodMs == 0 ||

        periodMs >= AvrContracts::SCHEDULER_HALF_RANGE_MS ||

        firstDelayMs >= AvrContracts::SCHEDULER_HALF_RANGE_MS ||

        taskCount_ >= MAX_TASKS) {


      return INVALID_TASK;
    }


    Task &task =
        tasks_[taskCount_];


    task.callback =
        callback;


    task.periodMs =
        periodMs;


    task.nextRunMs =
        (TickMs)(
            (TickMs)millis() +
            (TickMs)firstDelayMs);


    return taskCount_++;
  }


  // ---------------------------------------------------------------------------
  // Execute one scheduler pass
  // ---------------------------------------------------------------------------

  void execute() {

    ++passesWindow_;


    /*
     * Read once per pass, not once per task.
     *
     * Most passes find no task due, so this is the hottest line in the
     * firmware. A task whose release lands while an earlier callback in
     * this same pass is still running simply gets picked up on the next
     * pass, which follows immediately since loop() calls execute() back
     * to back.
     */

    const TickMs nowMs =
        (TickMs)millis();


    for (
        uint8_t i = 0;
        i < taskCount_;
        ++i) {


      Task &task =
          tasks_[i];


      /*
       * Overflow-safe comparison in the 16-bit modular time domain.
       */

      if (
          (int16_t)(
              nowMs -
              task.nextRunMs) < 0) {


        continue;
      }


      const TickMs scheduledMs =
          task.nextRunMs;


      const uint16_t latenessMs =
          (uint16_t)(
              nowMs -
              scheduledMs);


      if (
          (uint32_t)latenessMs >
          maxLateMs_) {


        maxLateMs_ =
            latenessMs;
      }


      // Measure callback -------------------------------------------------------

      const uint32_t startedUs =
          micros();


      task.callback();


      const uint32_t durationUs =
          micros() -
          startedUs;


      callbackBusyUsWindow_ +=
          durationUs;


      if (
          durationUs >
          maxCallbackUs_) {


        maxCallbackUs_ =
            durationUs;
      }


      /*
       * Fixed-rate scheduling:
       *
       * schedule from the intended release time, not from callback completion.
       */

      task.nextRunMs =
          (TickMs)(
              scheduledMs +
              task.periodMs);


      /*
       * Controlled degradation.
       *
       * If releases were missed while another callback was blocking, skip the
       * missed releases instead of performing a burst of catch-up executions.
       */

      const TickMs afterMs =
          (TickMs)millis();


      if (
          (int16_t)(
              afterMs -
              task.nextRunMs) >= 0) {


        const uint16_t behindMs =
            (uint16_t)(
                afterMs -
                task.nextRunMs);


        const uint16_t missed =
            (uint16_t)(
                behindMs /
                task.periodMs)
            + 1U;


        task.nextRunMs =
            (TickMs)(
                task.nextRunMs +

                (uint32_t)missed *
                task.periodMs);


        overruns_ +=
            missed;
      }
    }
  }


  // ---------------------------------------------------------------------------
  // Change period while preserving current phase
  // ---------------------------------------------------------------------------

  void setPeriodPreservePhase(
      uint8_t taskId,
      uint16_t newPeriodMs) {


    if (
        taskId >= taskCount_ ||

        newPeriodMs == 0 ||

        newPeriodMs >= AvrContracts::SCHEDULER_HALF_RANGE_MS) {


      return;
    }


    Task &task =
        tasks_[taskId];


    const uint16_t oldPeriodMs =
        task.periodMs;


    const TickMs nowMs =
        (TickMs)millis();


    uint16_t remainingOldMs =
        0;


    const int16_t remainingSigned =
        (int16_t)(
            task.nextRunMs -
            nowMs);


    if (remainingSigned > 0) {

      remainingOldMs =
          (uint16_t)remainingSigned;


      if (
          remainingOldMs >
          oldPeriodMs) {


        remainingOldMs =
            oldPeriodMs;
      }
    }


    const uint16_t remainingNewMs =
        (uint16_t)(
            (
                (uint32_t)remainingOldMs *
                newPeriodMs
            )
            /
            oldPeriodMs);


    task.periodMs =
        newPeriodMs;


    task.nextRunMs =
        (TickMs)(
            nowMs +
            remainingNewMs);
  }


  // ---------------------------------------------------------------------------
  // Window metrics
  // ---------------------------------------------------------------------------

  WindowCounters takeWindowCounters() {

    WindowCounters counters;


    counters.callbackBusyUs =
        callbackBusyUsWindow_;


    counters.passes =
        passesWindow_;


    callbackBusyUsWindow_ =
        0;


    passesWindow_ =
        0;


    return counters;
  }


  // ---------------------------------------------------------------------------
  // Lifetime metrics
  // ---------------------------------------------------------------------------

  uint32_t maxCallbackUs() const {

    return maxCallbackUs_;
  }


  uint32_t maxLateMs() const {

    return maxLateMs_;
  }


  uint32_t overruns() const {

    return overruns_;
  }


  uint8_t taskCount() const {

    return taskCount_;
  }


 private:

  /*
   * AVR layout:
   *
   * function pointer  2 B
   * next-run tick     2 B
   * period            2 B
   * ---------------------
   * task descriptor   6 B
   */

  struct Task {

    TaskCallback callback;

    TickMs nextRunMs;

    uint16_t periodMs;
  };


  Task tasks_[MAX_TASKS];


  uint8_t taskCount_;


  uint32_t callbackBusyUsWindow_;

  uint32_t passesWindow_;

  uint32_t maxCallbackUs_;

  uint32_t maxLateMs_;

  uint32_t overruns_;
};


#endif