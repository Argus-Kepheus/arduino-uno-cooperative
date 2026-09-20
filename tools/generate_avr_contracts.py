#!/usr/bin/env python3
"""Generate avr_contracts.h from canonical AVR/runtime/hardware configuration.

Usage:
    python tools/generate_avr_contracts.py          # print generated content
    python tools/generate_avr_contracts.py --write  # update avr_contracts.h
    python tools/generate_avr_contracts.py --check  # fail if stale
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_PATH = ROOT / "config" / "hardware.json"
RUNTIME_PATH = ROOT / "config" / "runtime.json"
AVR_PATH = ROOT / "config" / "avr.json"
OUTPUT_PATH = ROOT / "avr_contracts.h"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def digital_pin_number(pin: str) -> int:
    if not pin.startswith("D") or not pin[1:].isdigit():
        raise ValueError(f"Expected Dn Arduino pin, got {pin!r}")
    return int(pin[1:])


def analog_pin_index(pin: str) -> int:
    if not pin.startswith("A") or not pin[1:].isdigit():
        raise ValueError(f"Expected An Arduino pin, got {pin!r}")
    return int(pin[1:])


def render_avr_contracts(hardware: dict, runtime: dict, avr: dict) -> str:
    scheduler = avr["scheduler"]
    fast = avr["fast_io"]
    components = hardware["components"]
    blink = runtime["blinking_leds"]["shared_interval"]

    led_pins = [item["arduino_pin"] for item in components["blinking_leds"]]
    if led_pins != fast["blue_leds"]["arduino_pins"]:
        raise ValueError("Hardware blue LED pins disagree with AVR fast-I/O contract")

    button_pins = [
        components["buttons"]["main"]["arduino_pin"],
        components["buttons"]["decrease_interval"]["arduino_pin"],
        components["buttons"]["increase_interval"]["arduino_pin"],
    ]
    if button_pins != fast["buttons"]["arduino_pins"]:
        raise ValueError("Hardware button pins disagree with AVR fast-I/O contract")

    heartbeat_pin = components["status_leds"]["scheduler_heartbeat"]["arduino_pin"]
    if heartbeat_pin != fast["scheduler_heartbeat"]["arduino_pin"]:
        raise ValueError("Heartbeat pin disagrees with AVR fast-I/O contract")

    spi = hardware["buses"]["tft_spi"]
    hardware_spi = avr["spi_relationships"]["hardware_spi_pins"]
    if spi["mode"] != "software" or spi["miso"] is not None:
        raise ValueError("Current AVR contract requires write-only software SPI")
    if spi["mosi"]["arduino_pin"] != hardware_spi["mosi"]:
        raise ValueError("TFT MOSI disagrees with ATmega328P hardware-SPI mapping")
    if spi["sck"]["arduino_pin"] != hardware_spi["sck"]:
        raise ValueError("TFT SCK disagrees with ATmega328P hardware-SPI mapping")
    if components["status_leds"]["display_idle"]["arduino_pin"] != hardware_spi["miso"]:
        raise ValueError("Display-idle LED must occupy hardware-MISO/D12")

    i2c = hardware["buses"]["oled_i2c"]
    twi = avr["i2c_relationships"]["hardware_twi_pins"]
    if i2c["sda"]["arduino_pin"] != twi["sda"]:
        raise ValueError("OLED SDA disagrees with ATmega328P TWI mapping")
    if i2c["scl"]["arduino_pin"] != twi["scl"]:
        raise ValueError("OLED SCL disagrees with ATmega328P TWI mapping")

    led_bits = fast["blue_leds"]["avr_bits"]
    if led_bits != list(range(led_bits[0], led_bits[0] + len(led_bits))):
        raise ValueError("Blue LED AVR bits must be contiguous")

    button_bits = fast["buttons"]["avr_bits"]
    if len(button_bits) != 3:
        raise ValueError("Exactly three AVR button bits are required")

    derived_blink = [
        blink["base_ms"] * (blink["scale_base"] ** index)
        for index in range(blink["count"])
    ]
    if derived_blink != blink["derived_values_ms"]:
        raise ValueError("Blink derived_values_ms is stale")

    scheduled_periods = derived_blink + [
        runtime["buttons"]["scan_period_ms"],
        runtime["metrics"]["sample_period_ms"],
        runtime["displays"]["service_period_ms"],
        runtime["serial"]["status_period_ms"],
        runtime["scheduler"]["heartbeat_period_ms"],
    ]
    max_period = max(scheduled_periods)

    lines = [
        "// GENERATED FILE — DO NOT EDIT DIRECTLY.",
        "// Source: config/hardware.json + config/runtime.json + config/avr.json",
        "// Regenerate with: python tools/generate_avr_contracts.py --write",
        "",
        "#ifndef AVR_CONTRACTS_H",
        "#define AVR_CONTRACTS_H",
        "",
        "#include <Arduino.h>",
        '#include "project_config.h"',
        "",
        "namespace AvrContracts {",
        "",
        f"static const uint8_t SCHEDULER_MAX_TASKS = {scheduler['maximum_tasks']};",
        f"static const uint16_t SCHEDULER_HALF_RANGE_MS = {scheduler['signed_comparison_half_range_ms']}U;",
        f"static const uint16_t MAX_CONFIGURED_SCHEDULER_PERIOD_MS = {max_period}U;",
        "",
        f"static const uint8_t BLUE_TASK_FIRST_ID = {scheduler['first_blue_task_id']};",
        f"static const uint8_t BLUE_TASK_COUNT = {scheduler['blue_task_count']};",
        f"static const uint8_t BLINK_INTERVAL_SCALE_BASE = {blink['scale_base']};",
        "",
        f"static const uint8_t BLUE_LED_PORT_FIRST_BIT = {led_bits[0]};",
        f"static const uint8_t MAIN_BUTTON_PORT_BIT = {button_bits[0]};",
        f"static const uint8_t DECREASE_BUTTON_PORT_BIT = {button_bits[1]};",
        f"static const uint8_t INCREASE_BUTTON_PORT_BIT = {button_bits[2]};",
        f"static const uint8_t HEARTBEAT_PORT_BIT = {fast['scheduler_heartbeat']['avr_bit']};",
        "",
        "}  // namespace AvrContracts",
        "",
        "#if defined(__AVR__)",
        "#if !defined(__AVR_ATmega328P__)",
        '#error "AVR fast paths are validated only for ATmega328P"',
        "#endif",
        "",
        f"static_assert(F_CPU == {avr['microcontroller']['clock_hz']}UL,",
        '              "AVR clock differs from config/avr.json");',
        f"static_assert(Config::BLUE_LED_FIRST_PIN == {digital_pin_number(led_pins[0])},",
        '              "Blue LED first pin violates AVR PORTD contract");',
        f"static_assert(Config::BLUE_LED_COUNT == {len(led_pins)},",
        '              "Blue LED count violates AVR fast-I/O contract");',
        f"static_assert(Config::MAIN_BUTTON_PIN == A{analog_pin_index(button_pins[0])},",
        '              "Main button pin violates AVR PINC contract");',
        f"static_assert(Config::DECREASE_INTERVAL_BUTTON_PIN == A{analog_pin_index(button_pins[1])},",
        '              "Decrease button pin violates AVR PINC contract");',
        f"static_assert(Config::INCREASE_INTERVAL_BUTTON_PIN == A{analog_pin_index(button_pins[2])},",
        '              "Increase button pin violates AVR PINC contract");',
        f"static_assert(Config::SCHEDULER_HEARTBEAT_LED_PIN == A{analog_pin_index(heartbeat_pin)},",
        '              "Heartbeat pin violates AVR PORTC contract");',
        f"static_assert(Config::TFT_MOSI_PIN == {digital_pin_number(spi['mosi']['arduino_pin'])},",
        '              "TFT MOSI violates AVR SPI relationship");',
        f"static_assert(Config::DISPLAY_IDLE_LED_PIN == {digital_pin_number(hardware_spi['miso'])},",
        '              "Display-idle LED must remain on hardware MISO/D12");',
        f"static_assert(Config::TFT_SCK_PIN == {digital_pin_number(spi['sck']['arduino_pin'])},",
        '              "TFT SCK violates AVR SPI relationship");',
        "static_assert(AvrContracts::BLINK_INTERVAL_SCALE_BASE == 2,",
        '              "currentBlinkIntervalMs() requires a power-of-two x2 scale");',
        "static_assert(AvrContracts::MAX_CONFIGURED_SCHEDULER_PERIOD_MS <",
        "                  AvrContracts::SCHEDULER_HALF_RANGE_MS,",
        '              "Configured scheduler period violates modular-time half range");',
        "#endif",
        "",
        "#endif",
        "",
    ]
    return "\n".join(lines)


def render_from_repository() -> str:
    return render_avr_contracts(
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
                "Generated AVR contracts are stale. Run: "
                "python tools/generate_avr_contracts.py --write"
            )
            return 1
        print("avr_contracts.h is up to date.")
        return 0

    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
