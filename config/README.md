# Canonical configuration

This directory is the canonical configuration layer introduced in **Wave 1**.

The repository deliberately separates configuration ownership by domain so the
same fact does not acquire multiple authoritative definitions.

## Ownership

| File | Canonical responsibility |
|---|---|
| `hardware.json` | board identity, components, GPIO assignments, buses, passive values, electrical roles and Wokwi identifiers |
| `runtime.json` | serial/runtime timing, debounce, blink-speed policy, scheduler periods and operational SRAM margins |
| `avr.json` | ATmega328P architectural facts, direct-port fast paths, modular scheduler constraints and task-order invariants |
| `toolchain.json` | Arduino build target, simulator identity, dependency versions and toolchain pinning status |

Other files remain authoritative only for information outside these domains:

- `diagram.json` owns **Wokwi geometry and visual routing**;
- `sketch.ino` and the project headers own **implementation behavior**;
- `docs/EN/` currently owns the canonical technical narrative;
- `report/` is a historical/academic snapshot, not an operational source of truth.

## Wave 1 transitional state

Wave 1 is intentionally behavior-neutral.

`project_config.h` and `libraries.txt` are still the files consumed by the
current firmware/Wokwi workflow. They are **not generated yet** in this wave.

The new JSON files therefore mirror and formalize the verified baseline. Do not
assume that editing `config/` changes firmware behavior yet.

Wave 2 will establish deterministic generation and repository validation:

```text
config/hardware.json ─┐
config/runtime.json ──┼──> project_config.h
config/avr.json ──────┘

config/toolchain.json ───> libraries.txt
```

At that point, generated artifacts can stop being independently maintained.

## Why AVR has its own configuration file

Some Arduino pin assignments are architectural contracts, not freely
interchangeable numbers.

The current AVR fast paths rely on:

```text
D2..D7  <-> PORTD bits 2..7
A0..A2  <-> PINC bits 0..2
A3      <-> PORTC bit 3
```

Likewise, the scheduler relies on 16-bit modular-time arithmetic and the first
six task IDs being the six blue-LED callbacks.

Those relationships live in `avr.json` so a future pin change cannot silently
leave optimized direct-port code or scheduler assumptions inconsistent.

## Unknown or unpinned toolchain values

Wave 1 records uncertainty explicitly.

The repository currently does **not** pin:

- the `arduino-cli` version;
- the Arduino AVR Core version.

They remain `null` with `pinned: false` in `toolchain.json`. A later wave
may pin them if reproducible CI requires it.

## Editing policy

Until Wave 2 is complete:

1. treat the JSON files as the intended canonical model;
2. do not remove the existing values from `project_config.h` or
   `libraries.txt`;
3. do not alter firmware behavior merely to consume the new files;
4. keep `diagram.json` unchanged unless a real hardware change is intended.

After generation is introduced, edits should flow from `config/` to generated
artifacts rather than the reverse.
