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

## Generated artifacts after Wave 2

Wave 2 makes the configuration model executable:

```text
config/hardware.json ─┐
config/runtime.json ──┼──> tools/generate_project_config.py ──> project_config.h
config/avr.json ──────┘

config/hardware.json ─┐
config/runtime.json ──┼──> tools/generate_avr_contracts.py ──> avr_contracts.h
config/avr.json ──────┘

config/toolchain.json ───> tools/generate_libraries.py ──> libraries.txt

config/*.json ────────────> tools/generate_docs.py ──> generated EN/PT regions
```

`project_config.h` is now a generated artifact and contains an explicit
generated-file header. `libraries.txt` is also generated; its format cannot
carry comments, so its generated status is enforced by
`tools/validate_repository.py`.

The Arduino firmware continues to consume the same `Config::...` interface;
the Uno never parses the JSON files at runtime.

To change configuration, edit the canonical JSON first, regenerate the affected
artifact, and run:

```text
python tools/validate_repository.py
```

The validator also checks the current Wokwi circuit and AVR fast-path
assumptions so a pin/configuration change cannot silently leave
`diagram.json` or direct-port code inconsistent.

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

After Wave 2:

1. edit canonical values under `config/`;
2. regenerate `project_config.h`, `avr_contracts.h`, `libraries.txt`
   and/or generated documentation regions as appropriate;
3. never maintain generated values independently in those artifacts/regions;
4. keep `diagram.json` as the authority for Wokwi geometry, but validate its
   electrical semantics against `config/hardware.json`;
5. preserve narrative documentation manually while generated numeric/technical
   regions remain owned by `config/`;
6. run `python tools/validate_repository.py` before committing.


## AVR contract layer after Wave 3

AVR-specific assumptions are now enforced through two explicit headers:

```text
config/hardware.json ─┐
config/runtime.json ──┼──> tools/generate_avr_contracts.py
config/avr.json ──────┘                  │
                                         ▼
                                avr_contracts.h
                                         │
                     ┌───────────────────┴───────────────────┐
                     ▼                                       ▼
               avr_fast_io.h                    cooperative_scheduler.h
                     │                                       │
                     └───────────────────┬───────────────────┘
                                         ▼
                                     sketch.ino
```

`avr_contracts.h` is generated and contains compile-time assertions for the
ATmega328P target, 16 MHz clock, direct-port pin assumptions, software-SPI
D11/D12/D13 relationship and scheduler half-range.

`avr_fast_io.h` is hand-written implementation code. It is the only
application header allowed to know the direct AVR registers used by the fast
paths (`PORTD`, `PINC`, `PORTC`). It also provides portable
`digitalRead()/digitalWrite()` fallbacks for non-ATmega328P builds.

Changing a pin involved in a fast path therefore requires a coherent canonical
configuration update; otherwise generation, static validation or compilation
will reject the change.
