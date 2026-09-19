#!/usr/bin/env python3
"""Static repository consistency validator.

This validator is intentionally host-side. Passing it proves canonical/
derived consistency and AVR/Wokwi structural invariants; it does not prove
successful Wokwi execution or physical-hardware behavior.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
HARDWARE_PATH = CONFIG_DIR / "hardware.json"
RUNTIME_PATH = CONFIG_DIR / "runtime.json"
AVR_PATH = CONFIG_DIR / "avr.json"
TOOLCHAIN_PATH = CONFIG_DIR / "toolchain.json"
PROJECT_CONFIG_PATH = ROOT / "project_config.h"
LIBRARIES_PATH = ROOT / "libraries.txt"
DIAGRAM_PATH = ROOT / "diagram.json"
SKETCH_PATH = ROOT / "sketch.ino"
SCHEDULER_PATH = ROOT / "cooperative_scheduler.h"
BUTTON_PATH = ROOT / "button_debounce.h"
TFT_PATH = ROOT / "tft_dashboard.h"
WOKWI_PROJECT_PATH = ROOT / "wokwi-project.txt"

sys.path.insert(0, str(ROOT / "tools"))
from generate_libraries import render_libraries  # noqa: E402
from generate_project_config import render_project_config  # noqa: E402

ERRORS: list[str] = []
WARNINGS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Cannot load {path.relative_to(ROOT)}: {exc}")
        return {}


def digital_pin_number(pin: str) -> int | None:
    if isinstance(pin, str) and pin.startswith("D") and pin[1:].isdigit():
        return int(pin[1:])
    return None


class NetGraph:
    def __init__(self, connections: list[list]) -> None:
        self.adj: dict[str, set[str]] = {}
        for connection in connections:
            if len(connection) < 2:
                continue
            self.connect(connection[0], connection[1])

    def connect(self, left: str, right: str) -> None:
        self.adj.setdefault(left, set()).add(right)
        self.adj.setdefault(right, set()).add(left)

    def connected(self, start: str, target: str) -> bool:
        if start == target:
            return True
        seen = {start}
        stack = [start]
        while stack:
            node = stack.pop()
            for nxt in self.adj.get(node, ()):
                if nxt == target:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return False


def check_required_files() -> None:
    for path in (
        HARDWARE_PATH,
        RUNTIME_PATH,
        AVR_PATH,
        TOOLCHAIN_PATH,
        PROJECT_CONFIG_PATH,
        LIBRARIES_PATH,
        DIAGRAM_PATH,
        SKETCH_PATH,
        SCHEDULER_PATH,
        BUTTON_PATH,
        TFT_PATH,
        ROOT / "tools" / "generate_project_config.py",
        ROOT / "tools" / "generate_libraries.py",
    ):
        if not path.exists():
            fail(f"Missing required repository file: {path.relative_to(ROOT)}")


def check_schema(config: dict, name: str) -> None:
    if config.get("schema_version") != "1.0":
        fail(f"{name}: expected schema_version 1.0")
    if config.get("authority", {}).get("status") != "canonical":
        fail(f"{name}: authority.status must be canonical")


def check_generated_files(
    hardware: dict, runtime: dict, avr: dict, toolchain: dict
) -> None:
    try:
        expected_header = render_project_config(hardware, runtime, avr)
        actual_header = PROJECT_CONFIG_PATH.read_text(encoding="utf-8")
        if actual_header != expected_header:
            fail(
                "project_config.h is stale; run "
                "python tools/generate_project_config.py --write"
            )
    except Exception as exc:
        fail(f"Cannot render project_config.h: {exc}")

    try:
        expected_libraries = render_libraries(toolchain)
        actual_libraries = LIBRARIES_PATH.read_text(encoding="utf-8")
        if actual_libraries != expected_libraries:
            fail(
                "libraries.txt is stale; run "
                "python tools/generate_libraries.py --write"
            )
    except Exception as exc:
        fail(f"Cannot render libraries.txt: {exc}")


def check_internal_config(
    hardware: dict, runtime: dict, avr: dict, toolchain: dict
) -> None:
    components = hardware.get("components", {})
    leds = components.get("blinking_leds", [])
    scheduler = avr.get("scheduler", {})
    blink = runtime.get("blinking_leds", {}).get("shared_interval", {})

    ids: list[str] = []
    for led in leds:
        ids.extend([led.get("id"), led.get("resistor_id")])
    green = components.get("green_led", {})
    ids.extend([green.get("id"), green.get("resistor_id")])
    for item in components.get("status_leds", {}).values():
        ids.extend([item.get("id"), item.get("resistor_id")])
    for item in components.get("buttons", {}).values():
        ids.append(item.get("id"))
    for item in components.get("displays", {}).values():
        ids.append(item.get("id"))
    ids = [item for item in ids if isinstance(item, str)]
    if len(ids) != len(set(ids)):
        fail("config/hardware.json contains duplicate component/resistor IDs")

    if len(leds) != scheduler.get("blue_task_count"):
        fail("Blue LED count differs from AVR scheduler blue_task_count")
    if len(leds) != blink.get("count"):
        fail("Blue LED count differs from runtime blink interval count")

    led_numbers = [digital_pin_number(item.get("arduino_pin", "")) for item in leds]
    if any(value is None for value in led_numbers):
        fail("All blue LEDs must use digital Dn pins")
    elif led_numbers != list(range(led_numbers[0], led_numbers[0] + len(led_numbers))):
        fail(f"Blue LED pins must remain contiguous, found {led_numbers}")

    expected_fast_pins = avr.get("fast_io", {}).get("blue_leds", {}).get(
        "arduino_pins", []
    )
    if [item.get("arduino_pin") for item in leds] != expected_fast_pins:
        fail("Blue LED hardware pins disagree with AVR fast-I/O contract")

    button_order = [
        components.get("buttons", {}).get("main", {}).get("arduino_pin"),
        components.get("buttons", {}).get("decrease_interval", {}).get("arduino_pin"),
        components.get("buttons", {}).get("increase_interval", {}).get("arduino_pin"),
    ]
    if button_order != avr.get("fast_io", {}).get("buttons", {}).get(
        "arduino_pins"
    ):
        fail("Button pins disagree with AVR PINC fast-I/O contract")

    heartbeat = components.get("status_leds", {}).get("scheduler_heartbeat", {})
    if heartbeat.get("arduino_pin") != avr.get("fast_io", {}).get(
        "scheduler_heartbeat", {}
    ).get("arduino_pin"):
        fail("Scheduler heartbeat pin disagrees with AVR PORTC fast path")

    tft = hardware.get("buses", {}).get("tft_spi", {})
    if tft.get("mode") != "software" or tft.get("miso") is not None:
        fail("TFT bus must remain write-only software SPI in current architecture")

    hardware_spi = avr.get("spi_relationships", {}).get("hardware_spi_pins", {})
    display_idle_pin = components.get("status_leds", {}).get(
        "display_idle", {}
    ).get("arduino_pin")
    if display_idle_pin != hardware_spi.get("miso"):
        fail("Display-idle LED must occupy the hardware-MISO/D12 pin")
    if display_idle_pin in {
        tft.get(signal, {}).get("arduino_pin")
        for signal in ("dc", "cs", "mosi", "sck")
    }:
        fail("Display-idle LED pin conflicts with TFT software-SPI signals")

    derived = [
        blink.get("base_ms", 0) * (blink.get("scale_base", 0) ** index)
        for index in range(blink.get("count", 0))
    ]
    if derived != blink.get("derived_values_ms"):
        fail("Runtime derived_values_ms does not match base/scale/count")
    if not (0 <= blink.get("initial_index", -1) < blink.get("count", 0)):
        fail("Blink initial_index is outside the configured interval range")

    half_range = scheduler.get("signed_comparison_half_range_ms", 0)
    scheduler_periods = derived + [
        runtime.get("buttons", {}).get("scan_period_ms", 0),
        runtime.get("metrics", {}).get("sample_period_ms", 0),
        runtime.get("displays", {}).get("service_period_ms", 0),
        runtime.get("serial", {}).get("status_period_ms", 0),
        runtime.get("scheduler", {}).get("heartbeat_period_ms", 0),
    ]
    for period in scheduler_periods:
        if not isinstance(period, int) or period <= 0 or period >= half_range:
            fail(
                f"Scheduler period {period!r} violates 16-bit half-range "
                f"constraint (< {half_range})"
            )

    if runtime.get("sram_policy", {}).get("minimum_free_bytes", 0) > runtime.get(
        "sram_policy", {}
    ).get("target_free_bytes", 0):
        fail("SRAM minimum_free_bytes cannot exceed target_free_bytes")
    if runtime.get("sram_policy", {}).get("target_free_bytes", 0) >= avr.get(
        "microcontroller", {}
    ).get("sram_bytes", 0):
        fail("SRAM target_free_bytes must be below physical SRAM size")

    libraries = toolchain.get("libraries", [])
    names = [item.get("name") for item in libraries]
    if len(names) != len(set(names)):
        fail("config/toolchain.json contains duplicate library names")
    if toolchain.get("build_target", {}).get("fqbn") != "arduino:avr:uno":
        fail("Current build target must remain arduino:avr:uno")


def check_diagram(hardware: dict) -> None:
    diagram = load_json(DIAGRAM_PATH)
    if not diagram:
        return

    parts = {part.get("id"): part for part in diagram.get("parts", [])}
    graph = NetGraph(diagram.get("connections", []))
    # The two Uno GND headers are the same electrical reference.
    graph.connect("uno:GND.1", "uno:GND.2")

    board = hardware["board"]
    if parts.get(board["id"], {}).get("type") != board["wokwi_type"]:
        fail("diagram.json board type/id differs from hardware.json")

    for led in hardware["components"]["blinking_leds"]:
        part = parts.get(led["id"], {})
        resistor = parts.get(led["resistor_id"], {})
        if part.get("type") != "wokwi-led":
            fail(f"diagram.json missing LED {led['id']}")
        if part.get("attrs", {}).get("color") != led["color"]:
            fail(f"{led['id']}: diagram color differs from hardware.json")
        if resistor.get("type") != "wokwi-resistor":
            fail(f"diagram.json missing resistor {led['resistor_id']}")
        if resistor.get("attrs", {}).get("value") != "1k":
            fail(f"{led['resistor_id']}: expected 1k in diagram.json")
        pin = led["arduino_pin"][1:]
        if not graph.connected(f"uno:{pin}", f"{led['resistor_id']}:1"):
            fail(f"{led['id']}: GPIO-to-resistor connection mismatch")
        if not graph.connected(f"{led['resistor_id']}:2", f"{led['id']}:A"):
            fail(f"{led['id']}: resistor-to-anode connection mismatch")
        if not graph.connected(f"{led['id']}:C", "uno:GND.2"):
            fail(f"{led['id']}: cathode is not connected to board ground")

    simple_leds = [
        hardware["components"]["green_led"],
        hardware["components"]["status_leds"]["display_idle"],
        hardware["components"]["status_leds"]["scheduler_heartbeat"],
    ]
    for led in simple_leds:
        if parts.get(led["id"], {}).get("attrs", {}).get("color") != led["color"]:
            fail(f"{led['id']}: diagram color differs from hardware.json")
        if parts.get(led["resistor_id"], {}).get("attrs", {}).get("value") != "1k":
            fail(f"{led['resistor_id']}: expected 1k in diagram.json")
        pin = led["arduino_pin"].replace("D", "")
        if not graph.connected(f"uno:{pin}", f"{led['resistor_id']}:1"):
            fail(f"{led['id']}: board-pin connection mismatch")
        if not graph.connected(f"{led['resistor_id']}:2", f"{led['id']}:A"):
            fail(f"{led['id']}: resistor-to-anode connection mismatch")
        if not graph.connected(f"{led['id']}:C", "uno:GND.2"):
            fail(f"{led['id']}: cathode is not connected to board ground")

    for button in hardware["components"]["buttons"].values():
        part = parts.get(button["id"], {})
        if part.get("type") != "wokwi-pushbutton":
            fail(f"diagram.json missing pushbutton {button['id']}")
            continue
        if part.get("attrs", {}).get("key") != button["wokwi_key"]:
            fail(f"{button['id']}: Wokwi key differs from hardware.json")
        if not graph.connected(
            f"uno:{button['arduino_pin']}", f"{button['id']}:1.l"
        ):
            fail(f"{button['id']}: signal pin connection mismatch")
        if not graph.connected(f"{button['id']}:2.l", "uno:GND.2"):
            fail(f"{button['id']}: pressed side is not connected to GND")

    oled = hardware["components"]["displays"]["oled"]
    oled_part = parts.get(oled["id"], {})
    if oled_part.get("type") != oled["wokwi_type"]:
        fail("OLED type differs from hardware.json")
    if oled_part.get("attrs", {}).get("i2cAddress", "").upper() != oled[
        "address_hex"
    ].upper():
        fail("OLED address differs from hardware.json")
    i2c = hardware["buses"]["oled_i2c"]
    if not graph.connected(
        f"uno:{i2c['sda']['arduino_pin']}", f"{oled['id']}:SDA"
    ):
        fail("OLED SDA connection mismatch")
    if not graph.connected(
        f"uno:{i2c['scl']['arduino_pin']}", f"{oled['id']}:SCL"
    ):
        fail("OLED SCL connection mismatch")
    if not graph.connected("uno:5V", f"{oled['id']}:VCC"):
        fail("OLED VCC connection mismatch")
    if not graph.connected(f"{oled['id']}:GND", "uno:GND.2"):
        fail("OLED GND connection mismatch")

    tft = hardware["components"]["displays"]["tft"]
    tft_part = parts.get(tft["id"], {})
    if tft_part.get("type") != tft["wokwi_type"]:
        fail("TFT type differs from hardware.json")
    spi = hardware["buses"]["tft_spi"]
    for signal, endpoint in (
        ("dc", "D/C"),
        ("cs", "CS"),
        ("mosi", "MOSI"),
        ("sck", "SCK"),
    ):
        pin = spi[signal]["arduino_pin"].replace("D", "")
        if not graph.connected(f"uno:{pin}", f"{tft['id']}:{endpoint}"):
            fail(f"TFT {signal.upper()} connection mismatch")
    if not graph.connected("uno:5V", f"{tft['id']}:VCC"):
        fail("TFT VCC connection mismatch")
    if not graph.connected(f"{tft['id']}:GND", "uno:GND.2"):
        fail("TFT GND connection mismatch")


def check_firmware_contracts(runtime: dict, avr: dict, hardware: dict) -> None:
    sketch = SKETCH_PATH.read_text(encoding="utf-8")
    scheduler_h = SCHEDULER_PATH.read_text(encoding="utf-8")
    button_h = BUTTON_PATH.read_text(encoding="utf-8")
    tft_h = TFT_PATH.read_text(encoding="utf-8")

    match = re.search(r"MAX_TASKS\s*=\s*(\d+)", scheduler_h)
    if not match or int(match.group(1)) != avr["scheduler"]["maximum_tasks"]:
        fail("cooperative_scheduler.h MAX_TASKS differs from avr.json")

    register_match = re.search(
        r"void\s+registerTasks\s*\(\s*\)\s*\{(.*?)\n\}",
        sketch,
        re.DOTALL,
    )
    if not register_match:
        fail("Cannot locate registerTasks() in sketch.ino")
    else:
        callbacks = re.findall(
            r"scheduler\.add\(\s*([A-Za-z_][A-Za-z0-9_]*)",
            register_match.group(1),
        )
        if callbacks != avr["scheduler"]["registration_order"]:
            fail(
                "Scheduler registration order differs from avr.json: "
                f"{callbacks}"
            )

    if (
        "PORTD ^=" not in sketch
        or "(uint8_t)(1U << pin)" not in sketch
    ):
        fail("Blue-LED AVR direct PORTD fast path is missing")

    required_button_fragments = (
        "const uint8_t pinc =",
        "PINC;",
        "!(pinc & (1U << 0))",
        "!(pinc & (1U << 1))",
        "!(pinc & (1U << 2))",
    )
    for fragment in required_button_fragments:
        if fragment not in sketch:
            fail(f"Button AVR fast path missing fragment: {fragment}")

    if "PORTC ^=" not in sketch or "(uint8_t)(1U << 3)" not in sketch:
        fail("Scheduler-heartbeat AVR PORTC fast path is missing")

    debounce = runtime["buttons"]["debounce_ms"]
    match = re.search(r"debounceMs_\s*\(\s*(\d+)\s*\)", button_h)
    if match and int(match.group(1)) != debounce:
        fail(
            "DebouncedButton constructor default differs from canonical "
            f"debounce ({match.group(1)} vs {debounce})"
        )

    rotation = hardware["components"]["displays"]["tft"]["configured_rotation"]
    rotations = [int(value) for value in re.findall(r"setRotation\(\s*(\d+)\s*\)", tft_h)]
    if rotations and any(value != rotation for value in rotations):
        fail(
            f"TFT setRotation values {rotations} differ from canonical "
            f"rotation {rotation}"
        )


def check_toolchain(toolchain: dict) -> None:
    if WOKWI_PROJECT_PATH.exists():
        text = WOKWI_PROJECT_PATH.read_text(encoding="utf-8")
        url = toolchain.get("simulator", {}).get("project_url")
        if url and url not in text:
            fail("wokwi-project.txt URL differs from config/toolchain.json")


def main() -> int:
    check_required_files()

    hardware = load_json(HARDWARE_PATH)
    runtime = load_json(RUNTIME_PATH)
    avr = load_json(AVR_PATH)
    toolchain = load_json(TOOLCHAIN_PATH)

    for config, name in (
        (hardware, "hardware.json"),
        (runtime, "runtime.json"),
        (avr, "avr.json"),
        (toolchain, "toolchain.json"),
    ):
        if config:
            check_schema(config, name)

    if hardware and runtime and avr and toolchain:
        check_generated_files(hardware, runtime, avr, toolchain)
        check_internal_config(hardware, runtime, avr, toolchain)
        check_diagram(hardware)
        check_firmware_contracts(runtime, avr, hardware)
        check_toolchain(toolchain)

    print("arduino-uno-cooperative repository validation")
    print(f"Errors: {len(ERRORS)}")
    for message in ERRORS:
        print(f"  ERROR: {message}")
    print(f"Warnings: {len(WARNINGS)}")
    for message in WARNINGS:
        print(f"  WARN: {message}")

    if ERRORS:
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
