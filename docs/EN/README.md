<!-- doc-id: project-overview -->
<!-- language: EN -->
<!-- content-revision: 2 -->

# arduino-uno-cooperative

**Language:** [English](README.md) | [Português](../PT/README.md)

Arduino Uno R3 / ATmega328P project exploring cooperative concurrency without
an RTOS, threads, or `TaskScheduler`. The application preserves six independent
blue-LED tasks, three non-blocking debounced buttons, a green LED, two activity
indicators, a diagnostic SSD1306 OLED, a primary ILI9341 TFT, and timing/SRAM
instrumentation.

The initial simulation target is **Wokwi in the web browser**.

<!-- section: baseline-architecture -->
## Baseline architecture

<!-- BEGIN GENERATED: baseline-summary -->
| Property | Canonical value |
|---|---|
| Board | Arduino Uno R3 |
| MCU / clock | ATmega328P / 16 MHz |
| Registered tasks | 11 |
| Blue LEDs | D2–D7 (6) |
| Buttons | A0 / A1 / A2 |
| Green LED | D8 |
| Display-activity LED | D12 |
| Scheduler heartbeat | A3 |
| TFT | software SPI: D9/D10/D11/D13 |
| OLED | hardware I2C: A4/SDA, A5/SCL |
| UART | D0/RX, D1/TX |
| Libraries | Adafruit GFX Library 1.12.6, Adafruit ILI9341 1.6.3, Adafruit BusIO 1.17.4, SSD1306Ascii 1.3.5 |
<!-- END GENERATED: baseline-summary -->

The generated table owns the current board, pin, bus, task-count and library-version facts. The architectural policies remain manual:

- C++ / Arduino framework;
- native static cooperative scheduler;
- no `delay()` during normal operation;
- no deliberate dynamic allocation during normal operation.

<!-- section: documents -->
## Documents

- [`technical-specification.md`](technical-specification.md) - requirements and acceptance criteria;
- [`architecture.md`](architecture.md) - firmware organization and execution flow;
- [`pinout.md`](pinout.md) - official pin assignment;
- [`scheduler.md`](scheduler.md) - native scheduler behavior;
- [`displays.md`](displays.md) - TFT/OLED strategy;
- [`validation-checklist.md`](validation-checklist.md) - validation procedure.

<!-- section: baseline-status -->
## Baseline status

The project intentionally keeps the baseline readable and instrumentable.
Aggressive AVR optimizations, `TaskScheduler`, hardware SPI with reassigned
GPIO, watchdog support, and more sophisticated timing measurements remain
future work so they can be compared against this baseline.
