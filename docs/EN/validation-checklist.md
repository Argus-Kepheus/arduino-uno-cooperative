# Validation Checklist

## Build and startup

- [ ] Builds for Arduino Uno R3 in Wokwi web.
- [ ] All `libraries.txt` dependencies resolve.
- [ ] Flash and static SRAM usage are recorded.
- [ ] Serial opens at 115200 baud.
- [ ] Exactly 11 tasks are registered.
- [ ] TFT and OLED initialize.
- [ ] Yellow heartbeat LED is visible.
- [ ] Orange LED returns HIGH after startup.

## Blue LEDs

- [ ] LEDs 1 through 6 blink.
- [ ] Each remains associated with its own callback.
- [ ] Initial interval is 500 ms.
- [ ] 125, 250, 500, 1000, 2000, and 4000 ms all work.
- [ ] Lower and upper limits are enforced.

## Buttons

- [ ] Main button controls green LED after debounce.
- [ ] Press and release generate single events.
- [ ] Interval buttons produce one change per press.
- [ ] Holding an interval button does not auto-repeat.
- [ ] Debounce contains no `delay()`.

## Scheduler

- [ ] A3 heartbeat remains visible.
- [ ] `PASS/s`, `MAX CALLBACK`, `MAX LATE`, and `OVR` update.
- [ ] The system crosses `65535 ms -> 0 ms` without stopping or bursting tasks.

## TFT

- [ ] Uses D9/D10/D11/D13 with software SPI.
- [ ] Both graphs are displayed.
- [ ] Interval, button, BUSY, RAM, PASS, CBMAX, LATE, OVR, and RAM LOW appear.
- [ ] Circular event console works.
- [ ] Unchanged values are not continuously redrawn.
- [ ] No `fillScreen()` occurs during normal operation.

## OLED

- [ ] Uses A4/SDA and A5/SCL at `0x3C`.
- [ ] Shows compact diagnostics.
- [ ] Refreshes at about 1 Hz.
- [ ] Missing OLED does not stop the application.

## Indicators

- [ ] D12 drives the orange LED.
- [ ] Orange HIGH = display idle, LOW = instrumented display operation.
- [ ] A3 drives the yellow heartbeat.
- [ ] Built-in D13 `L` activity may reflect TFT clock without being treated as an error.

## SRAM

Record compiled static SRAM, initial `SRAM FREE`, and `RAM LOW`.

- [ ] RAM LOW remains >= 400 bytes.
- [ ] Preferably RAM LOW remains >= 512 bytes.
- [ ] No unexplained progressive loss occurs.

## Integrated stress

- [ ] 125 ms interval with TFT, OLED, and serial active.
- [ ] Rapid use of all three buttons.
- [ ] Repeated 125 <-> 4000 ms changes.
- [ ] Enough events to wrap the console.
- [ ] At least 15 minutes without reset or lockup.
- [ ] Serial remains usable under graphics load.
- [ ] Heartbeat remains continuous.

## Result record

Date:

Version/commit:

Wokwi URL:

Flash used:

Static SRAM:

RAM LOW:

MAX CALLBACK:

MAX LATE:

OVR:

Notes:
