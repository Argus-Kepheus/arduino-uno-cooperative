from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class SourceContractTests(unittest.TestCase):
    def test_avr_register_access_stays_out_of_sketch(self) -> None:
        sketch = (ROOT / "sketch.ino").read_text(encoding="utf-8")
        fast_io = (ROOT / "avr_fast_io.h").read_text(encoding="utf-8")

        for register in ("PORTD", "PINC", "PORTC"):
            self.assertNotIn(register, sketch)
            self.assertIn(register, fast_io)

    def test_scheduler_consumes_generated_contracts(self) -> None:
        scheduler = (ROOT / "cooperative_scheduler.h").read_text(encoding="utf-8")
        self.assertIn("AvrContracts::SCHEDULER_MAX_TASKS", scheduler)
        self.assertGreaterEqual(
            scheduler.count("AvrContracts::SCHEDULER_HALF_RANGE_MS"),
            3,
        )
        self.assertIsNone(re.search(r"\b32768U?\b", scheduler))

    def test_integrated_sources_consume_runtime_configuration(self) -> None:
        sketch = (ROOT / "sketch.ino").read_text(encoding="utf-8")
        button = (ROOT / "button_debounce.h").read_text(encoding="utf-8")
        tft = (ROOT / "tft_dashboard.h").read_text(encoding="utf-8")

        self.assertGreaterEqual(sketch.count("Config::BUTTON_DEBOUNCE_MS"), 3)
        self.assertRegex(button, r"debounceMs_\s*\(\s*0\s*\)")
        self.assertIn("Config::TFT_ROTATION", tft)
        self.assertIsNone(re.search(r"setRotation\(\s*\d+\s*\)", tft))

    def test_manual_diagnostics_match_metadata_and_tests_contain_no_ino(self) -> None:
        metadata = load_json(ROOT / "diagnostics" / "metadata.json")
        expected = sorted(
            item["file"]
            for item in metadata["ordered_diagnostics"]
        )
        actual = sorted(path.name for path in (ROOT / "diagnostics").glob("*.ino"))
        self.assertEqual(expected, actual)
        self.assertEqual([], list((ROOT / "tests").glob("*.ino")))

    def test_generated_headers_are_marked_generated(self) -> None:
        for filename in ("project_config.h", "avr_contracts.h"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertTrue(
                text.startswith("// GENERATED FILE — DO NOT EDIT DIRECTLY."),
                filename,
            )

    def test_ci_runs_host_tests_before_repository_validation(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "repository-validation.yml"
        ).read_text(encoding="utf-8")
        test_command = (
            'python -m unittest discover -s tests -p "test_*.py" -v'
        )
        self.assertIn(test_command, workflow)
        self.assertLess(
            workflow.index(test_command),
            workflow.index("python tools/validate_repository.py"),
        )


if __name__ == "__main__":
    unittest.main()
