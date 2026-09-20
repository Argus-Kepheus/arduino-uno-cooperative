# Manual diagnostics

This directory contains standalone Arduino sketches used to isolate hardware and
architecture elements of `arduino-uno-cooperative`.

They are **manual diagnostics**, not automated software tests and not part of
the integrated firmware build. Each sketch is intentionally self-contained so
it can diagnose a circuit or subsystem without depending on
`project_config.h` or the complete application.

To run one in Wokwi web, temporarily use the selected diagnostic as the active
`sketch.ino`, execute the simulation, record the observed result, and then
restore the integrated firmware.

The ordered diagnostic inventory is machine-readable in
[`metadata.json`](metadata.json).

## Recommended order

| ID | File | Verification |
|---|---|---|
| DIAG-01 | `01_blue_led_basic.ino` | D2 and first blue LED |
| DIAG-02 | `02_all_blue_leds_basic.ino` | D2-D7 and all six blue LEDs |
| DIAG-03 | `03_green_button_led.ino` | A0, simple debounce and D8 |
| DIAG-04 | `04_interval_buttons.ino` | A1/A2 and interval limits |
| DIAG-05 | `05_status_leds.ino` | orange display indicator and yellow heartbeat |
| DIAG-06 | `06_oled_basic.ino` | SSD1306 / hardware I2C |
| DIAG-07 | `07_tft_basic_software_spi.ino` | ILI9341 / software SPI |
| DIAG-08 | `08_tft_oled_together.ino` | TFT and OLED together |
| DIAG-09 | `09_native_scheduler_basic.ino` | six independent scheduler callbacks |
| DIAG-10 | `10_scheduler_rollover.ino` | 16-bit modular scheduler arithmetic |

## Dependencies

Diagnostics 6 and 8 use `SSD1306Ascii`. Diagnostics 7 and 8 use
`Adafruit GFX` and `Adafruit ILI9341`.

## Boundary

A diagnostic may deliberately use `delay()` when isolating a physical
connection. The integrated firmware's non-blocking rule does not apply to these
standalone bench/simulator diagnostics.

A successful diagnostic is evidence about the subsystem observed during that
run; it is not proof that the integrated application passes.

For integrated acceptance, also use
[`docs/EN/validation-checklist.md`](../docs/EN/validation-checklist.md) or
[`docs/PT/validation-checklist.md`](../docs/PT/validation-checklist.md).
