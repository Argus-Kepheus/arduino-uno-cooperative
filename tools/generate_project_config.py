#!/usr/bin/env python3
"""Generate project_config.h from canonical repository configuration.

Usage:
    python tools/generate_project_config.py          # print generated content
    python tools/generate_project_config.py --write  # update project_config.h
    python tools/generate_project_config.py --check  # fail if stale
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_PATH = ROOT / "config" / "hardware.json"
RUNTIME_PATH = ROOT / "config" / "runtime.json"
AVR_PATH = ROOT / "config" / "avr.json"
OUTPUT_PATH = ROOT / "project_config.h"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def digital_pin_number(pin: str) -> int:
    if not pin.startswith("D") or not pin[1:].isdigit():
        raise ValueError(f"Expected digital Arduino pin like D2, got {pin!r}")
    return int(pin[1:])


def require_contiguous_blue_leds(hardware: dict, avr: dict) -> list[dict]:
    leds = hardware["components"]["blinking_leds"]
    expected_count = avr["scheduler"]["blue_task_count"]
    if len(leds) != expected_count:
        raise ValueError(
            f"Expected {expected_count} blue LEDs from AVR contract, found {len(leds)}"
        )

    numbers = [digital_pin_number(led["arduino_pin"]) for led in leds]
    if numbers != list(range(numbers[0], numbers[0] + len(numbers))):
        raise ValueError(f"Blue LED pins are not contiguous: {numbers}")
    return leds


def render_project_config(hardware: dict, runtime: dict, avr: dict) -> str:
    leds = require_contiguous_blue_leds(hardware, avr)
    components = hardware["components"]
    buses = hardware["buses"]

    tft = buses["tft_spi"]
    buttons = components["buttons"]
    status = components["status_leds"]
    oled = components["displays"]["oled"]

    blink = runtime["blinking_leds"]["shared_interval"]
    serial = runtime["serial"]
    timings = {
        "BUTTON_SCAN_PERIOD_MS": runtime["buttons"]["scan_period_ms"],
        "BUTTON_DEBOUNCE_MS": runtime["buttons"]["debounce_ms"],
        "METRICS_SAMPLE_PERIOD_MS": runtime["metrics"]["sample_period_ms"],
        "DISPLAY_SERVICE_PERIOD_MS": runtime["displays"]["service_period_ms"],
        "SERIAL_STATUS_PERIOD_MS": serial["status_period_ms"],
        "SCHEDULER_HEARTBEAT_PERIOD_MS": runtime["scheduler"]["heartbeat_period_ms"],
    }

    derived = [
        blink["base_ms"] * (blink["scale_base"] ** index)
        for index in range(blink["count"])
    ]
    if derived != blink["derived_values_ms"]:
        raise ValueError(
            "runtime.json derived_values_ms does not match base/scale/count"
        )

    def digital(component: dict) -> int:
        return digital_pin_number(component["arduino_pin"])

    lines = [
        "// GENERATED FILE — DO NOT EDIT DIRECTLY.",
        "// Source: config/hardware.json + config/runtime.json + config/avr.json",
        "// Regenerate with: python tools/generate_project_config.py --write",
        "",
        "#ifndef PROJECT_CONFIG_H",
        "#define PROJECT_CONFIG_H",
        "",
        "#include <Arduino.h>",
        "",
        "namespace Config {",
        "",
        "// Serial",
        f"static const uint32_t SERIAL_BAUD = {serial['baud']}UL;",
        "",
        "// Six independent blue LEDs. The AVR fast path requires a contiguous range.",
        f"static const uint8_t BLUE_LED_FIRST_PIN = {digital_pin_number(leds[0]['arduino_pin'])};",
        f"static const uint8_t BLUE_LED_COUNT = {len(leds)};",
        "",
        "// Main-button LED",
        f"static const uint8_t GREEN_LED_PIN = {digital(components['green_led'])};",
        "",
        "// TFT ILI9341 — software SPI by design",
        f"static const uint8_t TFT_DC_PIN = {digital_pin_number(tft['dc']['arduino_pin'])};",
        f"static const uint8_t TFT_CS_PIN = {digital_pin_number(tft['cs']['arduino_pin'])};",
        f"static const uint8_t TFT_MOSI_PIN = {digital_pin_number(tft['mosi']['arduino_pin'])};",
        f"static const uint8_t TFT_SCK_PIN = {digital_pin_number(tft['sck']['arduino_pin'])};",
        f"static const uint8_t TFT_ROTATION = {components['displays']['tft']['configured_rotation']};",
        "",
        "// Display activity indicator",
        f"static const uint8_t DISPLAY_IDLE_LED_PIN = {digital(status['display_idle'])};",
        "",
        "// Buttons",
        f"static const uint8_t MAIN_BUTTON_PIN = {buttons['main']['arduino_pin']};",
        f"static const uint8_t DECREASE_INTERVAL_BUTTON_PIN = {buttons['decrease_interval']['arduino_pin']};",
        f"static const uint8_t INCREASE_INTERVAL_BUTTON_PIN = {buttons['increase_interval']['arduino_pin']};",
        "",
        "// Scheduler heartbeat",
        f"static const uint8_t SCHEDULER_HEARTBEAT_LED_PIN = {status['scheduler_heartbeat']['arduino_pin']};",
        "",
        "// OLED SSD1306 — hardware I2C",
        f"static const uint8_t OLED_I2C_ADDRESS = {oled['address_hex']};",
        f"static const uint32_t OLED_I2C_CLOCK_HZ = {buses['oled_i2c']['frequency_hz']}UL;",
        f"static const uint16_t OLED_REFRESH_PERIOD_MS = {runtime['displays']['oled_refresh_period_ms']};",
        "",
        "// Shared blue-LED blink interval",
        f"static const uint16_t BLINK_INTERVAL_BASE_MS = {blink['base_ms']};",
        f"static const uint8_t BLINK_INTERVAL_COUNT = {blink['count']};",
        f"static const uint8_t BLINK_INTERVAL_INITIAL_INDEX = {blink['initial_index']};",
        "",
        "// Cooperative task periods",
    ]
    for name, value in timings.items():
        lines.append(f"static const uint16_t {name} = {value};")

    lines.extend(
        [
            "",
            "// SRAM limits",
            f"static const uint16_t SRAM_TOTAL_BYTES = {avr['microcontroller']['sram_bytes']};",
            f"static const uint16_t SRAM_TARGET_FREE_BYTES = {runtime['sram_policy']['target_free_bytes']};",
            f"static const uint16_t SRAM_MIN_FREE_BYTES = {runtime['sram_policy']['minimum_free_bytes']};",
            "",
            "}  // namespace Config",
            "",
            "#endif",
            "",
        ]
    )
    return "\n".join(lines)


def render_from_repository() -> str:
    return render_project_config(
        load_json(HARDWARE_PATH),
        load_json(RUNTIME_PATH),
        load_json(AVR_PATH),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = render_from_repository()

    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Updated {OUTPUT_PATH.relative_to(ROOT)}")
        return 0

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"Missing generated file: {OUTPUT_PATH.relative_to(ROOT)}")
            return 1
        actual = OUTPUT_PATH.read_text(encoding="utf-8")
        if actual != expected:
            print(
                "Generated project configuration is stale. Run: "
                "python tools/generate_project_config.py --write"
            )
            return 1
        print("project_config.h is up to date.")
        return 0

    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
