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

## Reproducible Arduino build

Wave 7 pins the integrated build to:

```text
Arduino CLI      1.5.1
Arduino AVR Core 1.8.8
FQBN             arduino:avr:uno
warnings         all
```

The exact library versions remain in `config/toolchain.json`.

The repository root intentionally keeps `sketch.ino` for Wokwi. Arduino's
sketch specification requires the primary `.ino` file to match the sketch
folder name, so `build_firmware.py` creates a temporary valid sketch under
`build/staging/`, copies the integrated root headers, renames the staged
primary file, and writes a pinned `sketch.yaml` build profile.

Inspect the generated profile without compiling:

```text
python tools/build_firmware.py --print-profile
```

Prepare the staging sketch only:

```text
python tools/build_firmware.py --prepare-only
```

Compile with the pinned Arduino CLI installed:

```text
python tools/build_firmware.py
```

The profile-based build excludes globally installed cores/libraries and uses
the exact platform/library versions declared in `config/toolchain.json`.
Build staging and binaries remain under ignored `build/`.

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
- neutral button-class defaults and generated runtime debounce/TFT rotation consumption;
- Wokwi project URL consistency;
- exact Arduino CLI/core pinning and deterministic reproducible build-profile rendering;
- multilingual documentation parity from `docs/metadata.json` (document IDs,
  language markers, shared revisions and semantic-section sequence);
- byte-exact generated documentation regions from canonical `config/` data;
- manual-diagnostic inventory/order under `diagnostics/` and separation from
  automated host-side `tests/`;
- automated-test inventory/runner contract under `tests/metadata.json`.

A successful result is a **static consistency result**. It does not prove that
the integrated sketch has executed successfully in Wokwi or on physical
hardware. Standalone manual hardware checks live under `diagnostics/`; the
`tests/` namespace is reserved for future non-interactive automated tests.

## Automated host tests

The host regression suite is standard-library-only:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

Its machine-readable inventory is `tests/metadata.json`. The suite covers
positive and negative generator cases, documentation parity/generated regions,
AVR/source boundaries, diagnostic/test separation and the CI regression
contract itself.

## Continuous integration

`.github/workflows/repository-validation.yml` mirrors the local validation
boundary on GitHub-hosted Ubuntu runners.

For pushes to `main`, pull requests and manual dispatch it:

1. checks out the repository;
2. installs Python;
3. reads the pinned Arduino CLI version from `config/toolchain.json`;
4. installs that exact Arduino CLI version with the official Arduino action;
5. checks every generated artifact/region;
6. runs the automated host regression suite;
7. runs `tools/validate_repository.py`;
8. runs `tools/build_firmware.py`, producing a real isolated Uno compilation.

The workflow has `contents: read` permissions and concurrency cancellation so
obsolete runs for the same ref do not waste runner time.

A green workflow is stronger than static validation because it proves a clean
GitHub-hosted environment can resolve the pinned build profile and compile the
integrated firmware. It still does not prove Wokwi runtime behavior or physical
Arduino Uno behavior.

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
