<!-- doc-id: displays -->
<!-- language: EN -->
<!-- content-revision: 2 -->

# Display Subsystem

<!-- section: strategy -->
## Strategy

The architecture fixes option A:

- **ILI9341**: primary visual interface;
- **SSD1306**: compact diagnostic panel.

<!-- BEGIN GENERATED: display-summary -->
| Display | Interface | Canonical wiring | Geometry / timing |
|---|---|---|---|
| ILI9341 | software SPI | D/C D9, CS D10, MOSI D11, SCK D13 | 240×320 native; rotation 1 -> 320×240 logical |
| SSD1306 | I2C (hardware) | SDA A4, SCL A5 | 128×64; address 0x3C; refresh 1000 ms |
<!-- END GENERATED: display-summary -->

<!-- section: ili9341 -->
## ILI9341

The TFT follows the software-SPI path summarized above, preserving the
hardware-MISO pin for the orange activity LED.

To compensate for CPU cost, the firmware keeps no TFT framebuffer, avoids
`fillScreen()` during normal operation, advances each graph by only one
column, splits updates into stages, caches text values to avoid unnecessary
redraws, and uses a fixed circular event queue.

<!-- section: ssd1306 -->
## SSD1306

The OLED uses the hardware-I2C configuration summarized above.
`SSD1306Ascii` avoids a 1024-byte framebuffer and presents a compact
diagnostic view.

<!-- section: visual-snapshot -->
## Visual snapshot

A metric sample is copied into `displaySnapshot`. All stages in the same visual
cycle use that immutable copy; newer samples wait until the cycle completes.

<!-- section: display-activity-led -->
## Orange LED

The display-activity indicator is HIGH while the display subsystem is
logically idle and LOW inside operations delimited by
`busyBegin()`/`busyEnd()`. Its current pin is owned by
`config/hardware.json`; this is a software activity indicator, not a bus
analyzer.

<!-- section: builtin-led -->
## Built-in L LED

The TFT clock pin also drives the board's built-in `L` LED, so clock activity
may be visible there. The current pin relationship is generated from the
canonical hardware configuration.

<!-- section: functional-priority -->
## Functional priority

Under resource pressure, scheduler, buttons, LEDs, and serial take priority.
The visual interface should be simplified before those core functions are
compromised.
