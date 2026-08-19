# Official Pin Assignment

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
| D11 | TFT MOSI - software SPI |
| D12 | orange display idle/activity LED |
| D13 | TFT SCK - software SPI + built-in `L` LED |
| A0 | main button |
| A1 | decrease interval |
| A2 | increase interval |
| A3 | yellow scheduler heartbeat LED |
| A4 / SDA | OLED SDA |
| A5 / SCL | OLED SCL |

## TFT

```text
D9  -> D/C
D10 -> CS
D11 -> MOSI
D13 -> SCK
5V  -> VCC
GND -> GND
```

The TFT is write-only. The baseline uses software SPI so D12 can remain a normal
GPIO.

## Orange D12 LED

Logical meaning:

```text
HIGH -> display subsystem idle
LOW  -> instrumented display operation in progress
```

The indicator does not attempt to reproduce every electrical bus transition.

## Built-in L LED on D13

D13 is also the TFT clock, so the built-in `L` LED may show activity during
ILI9341 transfers. This is expected.

## OLED

```text
A4 -> SDA
A5 -> SCL
5V -> VCC
GND -> GND
address -> 0x3C
```

A4/A5 use the ATmega328P hardware I2C/TWI peripheral.

## Buttons

A0, A1, and A2 use `INPUT_PULLUP` and connect to GND when pressed.

## UART

D0 and D1 remain reserved exclusively for serial communication.
