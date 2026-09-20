<!-- doc-id: displays -->
<!-- language: EN -->
<!-- content-revision: 1 -->

# Display Subsystem

<!-- section: strategy -->
## Strategy

The architecture fixes option A:

- **ILI9341**: primary visual interface;
- **SSD1306**: compact diagnostic panel.

<!-- section: ili9341 -->
## ILI9341

The TFT uses D9 (D/C), D10 (CS), D11 (MOSI), and D13 (SCK). The baseline uses
the Adafruit software-SPI path so D12 remains available for the orange LED.

To compensate for CPU cost, the firmware keeps no TFT framebuffer, avoids
`fillScreen()` during normal operation, advances each graph by only one column,
splits updates into stages, caches text values to avoid unnecessary redraws,
and uses a fixed circular event queue.

<!-- section: ssd1306 -->
## SSD1306

The OLED uses A4/SDA and A5/SCL at address `0x3C` through hardware I2C.
`SSD1306Ascii` avoids a 1024-byte framebuffer. It presents a compact diagnostic
view and refreshes at approximately 1 Hz.

<!-- section: visual-snapshot -->
## Visual snapshot

A metric sample is copied into `displaySnapshot`. All stages in the same visual
cycle use that immutable copy; newer samples wait until the cycle completes.

<!-- section: display-activity-led -->
## Orange LED

D12 is HIGH while the display subsystem is logically idle and LOW inside
operations delimited by `busyBegin()`/`busyEnd()`. It is a software activity
indicator, not a bus analyzer.

<!-- section: builtin-led -->
## Built-in L LED

D13 also drives the board's built-in `L` LED, so TFT clock activity may be
visible there.

<!-- section: functional-priority -->
## Functional priority

Under resource pressure, scheduler, buttons, LEDs, and serial take priority.
The visual interface should be simplified before those core functions are
compromised.
