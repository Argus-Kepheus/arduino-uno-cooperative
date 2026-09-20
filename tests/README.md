# Automated host tests

This directory contains the repository's **non-interactive CPython regression
suite**. These tests complement, but do not replace, the manual sketches under
[`diagnostics/`](../diagnostics/).

Run the full suite from the repository root:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

The suite uses only the Python standard library.

## Coverage

- `test_config_generation.py` checks deterministic generated artifacts,
  pinned build-profile rendering, and negative configuration cases that must be
  rejected.
- `test_documentation_contract.py` checks EN/PT semantic metadata and
  byte-exact generated documentation regions.
- `test_source_contracts.py` checks AVR/source boundaries, canonical runtime
  consumption, the diagnostics/tests split, generated-header markers, and the
  CI test step.

The machine-readable inventory is [`metadata.json`](metadata.json).

## Evidence boundary

A green host suite proves repository/configuration/source invariants on CPython.
The GitHub Actions compile step separately proves that the integrated sketch
builds for the pinned Arduino Uno toolchain. Manual Wokwi and physical-board
behavior remain under `diagnostics/` and the validation checklist.
