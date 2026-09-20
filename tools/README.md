# Repository tooling

The tools in this directory are development-time CPython utilities. They use
only the Python standard library and do not run on the Arduino Uno.

## Generate project configuration

```text
python tools/generate_project_config.py
python tools/generate_project_config.py --write
python tools/generate_project_config.py --check
```

Inputs:

- `config/hardware.json`
- `config/runtime.json`
- `config/avr.json`

Output:

- `project_config.h`

The generated header preserves the public `Config::...` names consumed by the
existing firmware. The Uno does not parse JSON at runtime.

## Generate AVR contracts

```text
python tools/generate_avr_contracts.py
python tools/generate_avr_contracts.py --write
python tools/generate_avr_contracts.py --check
```

Inputs:

- `config/hardware.json`
- `config/runtime.json`
- `config/avr.json`

Output:

- `avr_contracts.h`

The generated header exposes scheduler limits and fast-I/O bit contracts and
adds compile-time assertions for the ATmega328P/16 MHz target, D2–D7 blue-LED
mapping, A0–A2 button mapping, A3 heartbeat mapping and D11/D12/D13 SPI
relationship.

`avr_fast_io.h` consumes those contracts and is the single implementation
boundary for direct `PORTD`, `PINC` and `PORTC` accesses.

## Generate library list

```text
python tools/generate_libraries.py
python tools/generate_libraries.py --write
python tools/generate_libraries.py --check
```

Input:

- `config/toolchain.json`

Output:

- `libraries.txt`

The Wokwi library-list format does not support comments, so the generated-file
status is documented here and enforced by validation rather than embedded in
`libraries.txt`.

## Generate documentation

```text
python tools/generate_docs.py
python tools/generate_docs.py --write
python tools/generate_docs.py --check
```

Inputs:

- `config/hardware.json`
- `config/runtime.json`
- `config/avr.json`
- `config/toolchain.json`

Outputs are generated regions inside selected EN/PT Markdown documents. The
generator owns only repeated technical facts; explanatory prose remains manual.

The current generated regions cover baseline technical inventory, pin mapping,
display configuration, scheduler contracts/registration order, task periods,
blink intervals and runtime/SRAM/UART values.

## Validate repository

```text
python tools/validate_repository.py
```

The validator checks:

- canonical JSON schema/status;
- byte-exact `project_config.h` generation;
- byte-exact `libraries.txt` generation;
- internal hardware/runtime/AVR/toolchain consistency;
- AVR fast-I/O contracts for D2–D7, A0–A2 and A3;
- 16-bit scheduler half-range constraints;
- scheduler registration order and `MAX_TASKS`;
- Wokwi component IDs, colors, resistor values, keys and electrical
  connectivity;
- OLED/TFT buses, supply and address;
- TFT software-SPI relationship with D12;
- the current button debounce default and TFT rotation;
- Wokwi project URL consistency;
- multilingual documentation parity from `docs/metadata.json` (document IDs,
  language markers, shared revisions and semantic-section sequence);
- byte-exact generated documentation regions from canonical `config/` data.

A successful result is a **static consistency result**. It does not prove that
the integrated sketch has executed successfully in Wokwi or on physical
hardware. The standalone sketches currently under `tests/` remain manual
diagnostics until the later diagnostics wave.

## Normal edit workflow

For a configuration change:

```text
edit config/*.json
python tools/generate_project_config.py --write
python tools/generate_avr_contracts.py --write
python tools/generate_libraries.py --write
python tools/generate_docs.py --write
python tools/validate_repository.py
```

Only run the generator whose inputs actually changed. Generated artifacts
should not be edited independently.
