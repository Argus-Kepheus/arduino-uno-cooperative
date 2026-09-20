from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from build_firmware import render_build_profile
from generate_avr_contracts import render_avr_contracts
from generate_libraries import render_libraries
from generate_project_config import render_project_config


def load_json(name: str) -> dict:
    with (ROOT / "config" / name).open(encoding="utf-8") as handle:
        return json.load(handle)


class ConfigGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hardware = load_json("hardware.json")
        cls.runtime = load_json("runtime.json")
        cls.avr = load_json("avr.json")
        cls.toolchain = load_json("toolchain.json")

    def test_project_config_matches_repository_artifact(self) -> None:
        expected = render_project_config(self.hardware, self.runtime, self.avr)
        actual = (ROOT / "project_config.h").read_text(encoding="utf-8")
        self.assertEqual(expected, actual)

    def test_avr_contracts_match_repository_artifact(self) -> None:
        expected = render_avr_contracts(self.hardware, self.runtime, self.avr)
        actual = (ROOT / "avr_contracts.h").read_text(encoding="utf-8")
        self.assertEqual(expected, actual)

    def test_libraries_match_repository_artifact(self) -> None:
        expected = render_libraries(self.toolchain)
        actual = (ROOT / "libraries.txt").read_text(encoding="utf-8")
        self.assertEqual(expected, actual)

    def test_build_profile_contains_every_pinned_dependency(self) -> None:
        profile = render_build_profile(self.toolchain)
        self.assertIn(
            f"fqbn: {self.toolchain['build_target']['fqbn']}",
            profile,
        )
        core = self.toolchain["arduino_avr_core"]
        self.assertIn(
            f"platform: {core['package']} ({core['version']})",
            profile,
        )
        for library in self.toolchain["libraries"]:
            self.assertIn(
                f"{library['name']} ({library['version']})",
                profile,
            )

    def test_project_config_rejects_noncontiguous_blue_led_pins(self) -> None:
        hardware = copy.deepcopy(self.hardware)
        hardware["components"]["blinking_leds"][2]["arduino_pin"] = "D8"
        with self.assertRaisesRegex(ValueError, "not contiguous"):
            render_project_config(hardware, self.runtime, self.avr)

    def test_project_config_rejects_stale_derived_blink_values(self) -> None:
        runtime = copy.deepcopy(self.runtime)
        runtime["blinking_leds"]["shared_interval"]["derived_values_ms"][0] = 126
        with self.assertRaisesRegex(ValueError, "derived_values_ms"):
            render_project_config(self.hardware, runtime, self.avr)

    def test_avr_contracts_reject_button_fast_path_drift(self) -> None:
        hardware = copy.deepcopy(self.hardware)
        hardware["components"]["buttons"]["main"]["arduino_pin"] = "A3"
        with self.assertRaisesRegex(ValueError, "button pins disagree"):
            render_avr_contracts(hardware, self.runtime, self.avr)

    def test_library_generator_rejects_duplicate_names(self) -> None:
        toolchain = copy.deepcopy(self.toolchain)
        toolchain["libraries"].append(copy.deepcopy(toolchain["libraries"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate library"):
            render_libraries(toolchain)


if __name__ == "__main__":
    unittest.main()
