# Technical Specification

## 1. Purpose

`arduino-uno-cooperative` demonstrates cooperative concurrency on an Arduino
Uno R3 while preserving concepts from `esp32-asyncio` without attempting to
reproduce MicroPython `asyncio`. The constraints of the ATmega328P - 8 bit,
16 MHz, and only 2 KiB of SRAM - are part of the experiment.

## 2. Baseline principles

1. No RTOS, threads, or `TaskScheduler`.
2. No `delay()` during normal operation.
3. Preserve six independent blue-LED tasks.
4. Use a native static observable cooperative scheduler.
5. Handle all three buttons in one scan/debounce task.
6. Avoid dynamic allocation after `setup()`.
7. Keep serial output as the authoritative diagnostic channel.
8. Split graphical work into cooperative stages.
9. Instrument callback duration, lateness, overruns, scheduler passes, and SRAM.
10. Skip missed releases rather than executing catch-up bursts.

## 3. Tasks

| Task | Nominal period | Responsibility |
|---|---:|---|
| `blinkLed1` ... `blinkLed6` | 125-4000 ms | six independent LEDs |
| `scanButtons` | 5 ms | read/debounce three buttons |
| `sampleMetrics` | 250 ms | consolidate metrics |
| `serviceDisplays` | 20 ms | incremental TFT/OLED pipeline |
| `printStatus` | 1000 ms | serial status |
| `schedulerHeartbeat` | 100 ms | heartbeat on A3 |

Total: **11 tasks**.

## 4. Blue-LED intervals

All six tasks share the same configured period while remaining independent:
125, 250, 500, 1000, 2000, and 4000 ms. Initial value: **500 ms**.

## 5. Inputs and debounce

All buttons use `INPUT_PULLUP`: pressed = LOW, released = HIGH. Nominal debounce
is 30 ms with a 5 ms scan period. The main button reacts to press and release;
the interval buttons react only to the press edge and do not auto-repeat.

## 6. Displays

### ILI9341

Primary display in landscape orientation. It uses software SPI so D12 remains a
GPIO. It shows `APP BUSY`, free-SRAM history, metrics, button state, and a
circular event console.

### SSD1306

Compact diagnostic display on hardware I2C at `0x3C`. `SSD1306Ascii` avoids a
1024-byte framebuffer. Refresh is rate-limited to about 1 Hz.

## 7. Metrics

- **APP BUSY:** fraction of the measurement window spent inside instrumented
  callbacks. It is not absolute CPU utilization.
- **SRAM FREE:** sampled heap-to-stack distance estimate.
- **RAM LOW:** lowest sampled `SRAM FREE` since boot.
- **PASS/s:** scheduler passes per second.
- **MAX CALLBACK:** largest observed callback duration.
- **MAX LATE:** largest observed release-to-execution delay.
- **OVR:** missed releases skipped by the controlled-degradation policy.

## 8. SRAM

Desired margin: **>= 512 estimated free bytes**. Minimum accepted margin:
**400 bytes**. Below 400 bytes, the integrated baseline should not be accepted
without redesign.

Avoid `String`, `new`, `malloc`, dynamic containers, and large graphical buffers
during normal operation.

## 9. Communication

UART: 115200 baud, D0/RX and D1/TX reserved. Serial diagnostics should remain
available even when a display is unavailable or limited.

## 10. Acceptance criteria

The baseline must compile for Uno R3, run eleven cooperative tasks, preserve six
independent LEDs and all six periods, keep non-blocking debounce, operate TFT,
OLED, and serial simultaneously, expose the specified metrics, remain above the
SRAM threshold, stay responsive at 125 ms, survive modular-clock rollover, and
remain stable during an extended integrated run.

## 11. Future work

Open extensions include `TaskScheduler`, AceRoutine, hardware SPI with revised
pin assignment, direct `PORT` access, watchdog support, priorities, per-task
jitter, true stack high-water measurement, EEPROM persistence, and other
AVR-specific optimizations.
