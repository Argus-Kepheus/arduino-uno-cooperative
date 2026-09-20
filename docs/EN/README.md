<!-- doc-id: project-overview -->
<!-- language: EN -->
<!-- content-revision: 1 -->

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

- Arduino Uno R3, ATmega328P, 16 MHz;
- C++ / Arduino framework;
- native static cooperative scheduler;
- 11 registered tasks;
- six blue LEDs on D2-D7, one task per LED;
- main button on A0 and interval buttons on A1/A2;
- green LED on D8;
- orange display-activity LED on D12;
- yellow scheduler-heartbeat LED on A3;
- ILI9341 TFT using software SPI: D9/D10/D11/D13;
- SSD1306 OLED on hardware I2C: A4/SDA and A5/SCL;
- UART preserved on D0/RX and D1/TX;
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
