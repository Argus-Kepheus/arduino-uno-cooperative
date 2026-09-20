<!-- doc-id: technical-specification -->
<!-- language: EN -->
<!-- content-revision: 2 -->

# Technical Specification

<!-- section: purpose -->
## 1. Purpose

`arduino-uno-cooperative` demonstrates cooperative concurrency on an Arduino
Uno R3 while preserving concepts from `esp32-asyncio` without attempting to
reproduce MicroPython `asyncio`. The constraints of the ATmega328P - 8 bit,
16 MHz, and only 2 KiB of SRAM - are part of the experiment.

<!-- section: baseline-principles -->
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

<!-- section: tasks -->
## 3. Tasks

<!-- BEGIN GENERATED: task-periods -->
| Task | Nominal period | Responsibility |
|---|---:|---|
| blinkLed1 ... blinkLed6 | 125–4000 ms | six independent LEDs |
| scanButtons | 5 ms | read/debounce three buttons |
| sampleMetrics | 250 ms | consolidate metrics |
| serviceDisplays | 20 ms | incremental TFT/OLED pipeline |
| printStatus | 1000 ms | serial status |
| schedulerHeartbeat | 100 ms | scheduler heartbeat |

Total: **11 tasks**.
<!-- END GENERATED: task-periods -->

<!-- section: blue-led-intervals -->
## 4. Blue-LED intervals

All six tasks share the same configured period while remaining independent.

<!-- BEGIN GENERATED: blink-intervals -->
| Index | Interval |
|---:|---:|
| 0 | 125 ms |
| 1 | 250 ms |
| 2 | 500 ms |
| 3 | 1000 ms |
| 4 | 2000 ms |
| 5 | 4000 ms |

Initial value: **500 ms**.
<!-- END GENERATED: blink-intervals -->

<!-- section: inputs-debounce -->
## 5. Inputs and debounce

The current operational values are generated from `config/runtime.json`,
`config/hardware.json` and `config/avr.json`:

<!-- BEGIN GENERATED: runtime-summary -->
| Runtime property | Canonical value |
|---|---|
| Input mode | INPUT_PULLUP |
| Pressed / released | LOW / HIGH |
| Button scan | 5 ms |
| Debounce | 30 ms |
| Auto-repeat | disabled |
| Physical SRAM | 2048 bytes |
| Target free SRAM | >= 512 bytes |
| Minimum free SRAM | >= 400 bytes |
| Serial baud | 115200 |
| Serial status period | 1000 ms |
| UART | D0/RX, D1/TX |
<!-- END GENERATED: runtime-summary -->

The main button reacts to press and release edges. The interval buttons react
only to the press edge; the auto-repeat policy above remains authoritative.

<!-- section: displays -->
## 6. Displays

<!-- section: ili9341 -->
### ILI9341

Primary display in landscape orientation. Its canonical wiring and geometry
are generated in [`displays.md`](displays.md). It shows `APP BUSY`,
free-SRAM history, metrics, button state, and a circular event console.

<!-- section: ssd1306 -->
### SSD1306

Compact diagnostic display using the canonical hardware-I2C configuration
generated in [`displays.md`](displays.md). `SSD1306Ascii` avoids a
1024-byte framebuffer.

<!-- section: metrics -->
## 7. Metrics

- **APP BUSY:** fraction of the measurement window spent inside instrumented
  callbacks. It is not absolute CPU utilization.
- **SRAM FREE:** sampled heap-to-stack distance estimate.
- **RAM LOW:** lowest sampled `SRAM FREE` since boot.
- **PASS/s:** scheduler passes per second.
- **MAX CALLBACK:** largest observed callback duration.
- **MAX LATE:** largest observed release-to-execution delay.
- **OVR:** missed releases skipped by the controlled-degradation policy.

<!-- section: sram -->
## 8. SRAM

The physical SRAM size and operational free-SRAM thresholds are generated in
the runtime summary above. Falling below the configured minimum means the
integrated baseline should not be accepted without redesign.

Avoid `String`, `new`, `malloc`, dynamic containers, and large graphical buffers
during normal operation.

<!-- section: communication -->
## 9. Communication

UART rate and reserved pins are generated in the runtime summary above. Serial
diagnostics should remain available even when a display is unavailable or
limited.

<!-- section: acceptance-criteria -->
## 10. Acceptance criteria

The baseline must compile for Uno R3, run eleven cooperative tasks, preserve six
independent LEDs and all six periods, keep non-blocking debounce, operate TFT,
OLED, and serial simultaneously, expose the specified metrics, remain above the
SRAM threshold, stay responsive at 125 ms, survive modular-clock rollover, and
remain stable during an extended integrated run.

<!-- section: future-work -->
## 11. Future work

Open extensions include `TaskScheduler`, AceRoutine, hardware SPI with revised
pin assignment, direct `PORT` access, watchdog support, priorities, per-task
jitter, true stack high-water measurement, EEPROM persistence, and other
AVR-specific optimizations.
