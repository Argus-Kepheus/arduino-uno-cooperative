# Firmware Architecture

## Overview

The firmware has one physical execution flow. `loop()` continuously calls
`scheduler.execute()`, which scans a static task table and invokes only ready
callbacks.

```text
loop()
  |
  v
CooperativeScheduler::execute()
  |
  +-- blinkLed1 ... blinkLed6
  +-- scanButtons
  +-- sampleMetrics
  +-- serviceDisplays
  +-- printStatus
  +-- schedulerHeartbeat
```

Tasks have no private stacks and normal tasks do not preempt one another.
Interrupts used internally by the Arduino core still support facilities such as
timekeeping and UART, but they are not the application architecture.

## Layers

- **Application (`sketch.ino`)**: initialization, composition, functional logic.
- **Scheduling (`cooperative_scheduler.h`)**: releases, callbacks, lateness,
  overruns, and pass counters.
- **Inputs (`button_debounce.h`)**: debouncing and edge events.
- **Instrumentation (`metrics.h`)**: APP BUSY, SRAM, PASS/s, MAX CALLBACK,
  MAX LATE, and OVR.
- **Presentation**: `display_activity.h`, `oled_status.h`, `tft_dashboard.h`.

## Six independent LEDs

The six callbacks `blinkLed1` ... `blinkLed6` intentionally remain separate.
A single task could update all LEDs more compactly, but would remove the
observation of six independent timing entities from the experiment.

## Display pipeline

`serviceDisplays` never redraws the full interface in one call. When a new
metric sample appears, the firmware freezes it in `displaySnapshot` and spreads
presentation across stages:

```text
0 APP BUSY graph
1 SRAM graph
2 TFT status row
3 TFT resource row
4 TFT timing row
5 OLED diagnostic
```

The sample is marked displayed only after all stages complete, avoiding mixed
samples on the same visual update.

## Event console

Events use a fixed-size circular queue. If full, the oldest event is dropped.
No `String`, `malloc`, or dynamic lists are used.

## Fault isolation

A missing OLED must not prevent LEDs, buttons, scheduler, TFT, or serial from
operating. Serial remains the primary diagnostic path.

## Evolution policy

The baseline favors clarity, observability, and low SRAM use. Aggressive
optimizations remain separate so future implementations can be compared against
this baseline.
