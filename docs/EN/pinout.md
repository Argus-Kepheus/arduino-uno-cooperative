<!-- doc-id: pinout -->
<!-- language: EN -->
<!-- content-revision: 2 -->

# Official Pin Assignment

<!-- BEGIN GENERATED: pin-map -->
| Pin | Function |
|---|---|
| D0 / RX | serial receive |
| D1 / TX | serial transmit |
| D2 | blue LED 1 |
| D3 | blue LED 2 |
| D4 | blue LED 3 |
| D5 | blue LED 4 |
| D6 | blue LED 5 |
| D7 | blue LED 6 |
| D8 | green LED |
| D9 | TFT D/C |
| D10 | TFT CS |
| D11 | TFT MOSI — software SPI |
| D12 | orange display-activity LED |
| D13 | TFT SCK — software SPI + built-in L LED |
| A0 | main button |
| A1 | decrease interval |
| A2 | increase interval |
| A3 | yellow scheduler heartbeat LED |
| A4 / SDA | OLED SDA |
| A5 / SCL | OLED SCL |
<!-- END GENERATED: pin-map -->

<!-- section: tft -->
## TFT

Canonical signal pins are generated in the pin map above. The TFT is write-only
and uses software SPI so the hardware-MISO pin remains available to the
display-activity indicator.

<!-- section: display-activity-led -->
## Orange display-activity LED

Logical meaning:

```text
HIGH -> display subsystem idle
LOW  -> instrumented display operation in progress
```

Its current pin is generated in the map above. The indicator does not attempt
to reproduce every electrical bus transition.

<!-- section: builtin-led -->
## Built-in L LED

The pin used as TFT SCK also drives the board's built-in `L` LED, so display
clock activity may be visible there. This is expected; the current pin is
generated above.

<!-- section: oled -->
## OLED

The canonical SDA/SCL pins are generated above. Address, bus frequency and
supply are owned by `config/hardware.json` and summarized in
[`displays.md`](displays.md).

<!-- section: buttons -->
## Buttons

The three application buttons use `INPUT_PULLUP` and connect to GND when
pressed. Their current pins and roles are generated above.

<!-- section: uart -->
## UART

The pins shown above remain reserved exclusively for serial communication.
