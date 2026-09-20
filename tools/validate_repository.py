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
AVR_CONTRACTS_PATH = ROOT / "avr_contracts.h"
AVR_FAST_IO_PATH = ROOT / "avr_fast_io.h"
LIBRARIES_PATH = ROOT / "libraries.txt"
DIAGRAM_PATH = ROOT / "diagram.json"
SKETCH_PATH = ROOT / "sketch.ino"
SCHEDULER_PATH = ROOT / "cooperative_scheduler.h"
BUTTON_PATH = ROOT / "button_debounce.h"
TFT_PATH = ROOT / "tft_dashboard.h"
WOKWI_PROJECT_PATH = ROOT / "wokwi-project.txt"
DOCS_METADATA_PATH = ROOT / "docs" / "metadata.json"
DIAGNOSTICS_METADATA_PATH = ROOT / "diagnostics" / "metadata.json"
TESTS_README_PATH = ROOT / "tests" / "README.md"
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "repository-validation.yml"

sys.path.insert(0, str(ROOT / "tools"))
from build_firmware import render_build_profile  # noqa: E402
from generate_avr_contracts import render_avr_contracts  # noqa: E402
from generate_docs import render_file, target_files  # noqa: E402
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
        AVR_CONTRACTS_PATH,
        AVR_FAST_IO_PATH,
        LIBRARIES_PATH,
        DIAGRAM_PATH,
        SKETCH_PATH,
        SCHEDULER_PATH,
        BUTTON_PATH,
        TFT_PATH,
        DOCS_METADATA_PATH,
        DIAGNOSTICS_METADATA_PATH,
        TESTS_README_PATH,
        CI_WORKFLOW_PATH,
        ROOT / "tools" / "build_firmware.py",
        ROOT / "tools" / "generate_project_config.py",
        ROOT / "tools" / "generate_avr_contracts.py",
        ROOT / "tools" / "generate_docs.py",
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
        expected_avr_contracts = render_avr_contracts(hardware, runtime, avr)
        actual_avr_contracts = AVR_CONTRACTS_PATH.read_text(encoding="utf-8")
        if actual_avr_contracts != expected_avr_contracts:
            fail(
                "avr_contracts.h is stale; run "
                "python tools/generate_avr_contracts.py --write"
            )
    except Exception as exc:
        fail(f"Cannot render avr_contracts.h: {exc}")

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
    fast_io_h = AVR_FAST_IO_PATH.read_text(encoding="utf-8")
    contracts_h = AVR_CONTRACTS_PATH.read_text(encoding="utf-8")

    if '#include "avr_fast_io.h"' not in sketch:
        fail("sketch.ino must include avr_fast_io.h")
    if '#include "avr_contracts.h"' not in sketch:
        fail("sketch.ino must include avr_contracts.h")

    for register in ("PORTD", "PINC", "PORTC"):
        if register in sketch:
            fail(
                f"sketch.ino directly references {register}; "
                "AVR register access belongs in avr_fast_io.h"
            )

    required_fast_io_fragments = (
        "namespace AvrFastIo",
        "PORTD ^=",
        "PINC;",
        "PORTC ^=",
        "AvrContracts::BLUE_LED_PORT_FIRST_BIT",
        "AvrContracts::MAIN_BUTTON_PORT_BIT",
        "AvrContracts::DECREASE_BUTTON_PORT_BIT",
        "AvrContracts::INCREASE_BUTTON_PORT_BIT",
        "AvrContracts::HEARTBEAT_PORT_BIT",
    )
    for fragment in required_fast_io_fragments:
        if fragment not in fast_io_h:
            fail(f"avr_fast_io.h missing required fragment: {fragment}")

    if "AvrFastIo::toggleBlueLed(index)" not in sketch:
        fail("sketch.ino does not route blue LED toggles through AvrFastIo")
    if "AvrFastIo::sampleButtons(" not in sketch:
        fail("sketch.ino does not route button sampling through AvrFastIo")
    if "AvrFastIo::toggleSchedulerHeartbeat()" not in sketch:
        fail("sketch.ino does not route heartbeat through AvrFastIo")

    if (
        "AvrContracts::BLUE_TASK_FIRST_ID" not in sketch
        or "AvrContracts::BLUE_TASK_COUNT" not in sketch
    ):
        fail("sketch.ino does not consume generated blue-task ID contracts")

    if '#include "avr_contracts.h"' not in scheduler_h:
        fail("cooperative_scheduler.h must include avr_contracts.h")
    if "AvrContracts::SCHEDULER_MAX_TASKS" not in scheduler_h:
        fail("Scheduler capacity is not bound to generated AVR contracts")
    if scheduler_h.count("AvrContracts::SCHEDULER_HALF_RANGE_MS") < 3:
        fail("Scheduler half-range guards are not fully bound to AVR contracts")
    if re.search(r"\b32768U?\b", scheduler_h):
        fail("cooperative_scheduler.h still contains a manual 32768 half-range literal")
    if not re.search(
        r"static_assert\s*\(\s*sizeof\(TickMs\)\s*==\s*2",
        scheduler_h,
    ):
        fail("Scheduler is missing its 16-bit TickMs compile-time assertion")

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
        if len(callbacks) != avr["scheduler"]["expected_registered_tasks"]:
            fail(
                "Scheduler registered-task count differs from avr.json: "
                f"{len(callbacks)}"
            )

    expected_contract_literals = (
        f"SCHEDULER_MAX_TASKS = {avr['scheduler']['maximum_tasks']}",
        f"SCHEDULER_HALF_RANGE_MS = {avr['scheduler']['signed_comparison_half_range_ms']}U",
        f"BLUE_TASK_FIRST_ID = {avr['scheduler']['first_blue_task_id']}",
        f"BLUE_TASK_COUNT = {avr['scheduler']['blue_task_count']}",
        f"BLINK_INTERVAL_SCALE_BASE = {runtime['blinking_leds']['shared_interval']['scale_base']}",
    )
    for fragment in expected_contract_literals:
        if fragment not in contracts_h:
            fail(f"avr_contracts.h missing canonical contract: {fragment}")

    if not re.search(r"debounceMs_\s*\(\s*0\s*\)", button_h):
        fail(
            "DebouncedButton constructor must use a neutral zero default; "
            "runtime debounce belongs to Config::BUTTON_DEBOUNCE_MS"
        )
    if sketch.count("Config::BUTTON_DEBOUNCE_MS") < 3:
        fail(
            "All three integrated buttons must consume Config::BUTTON_DEBOUNCE_MS"
        )

    if "setRotation(\n        Config::TFT_ROTATION);" not in tft_h:
        fail("TFT rotation must be consumed from Config::TFT_ROTATION")
    if re.search(r"setRotation\(\s*\d+\s*\)", tft_h):
        fail("tft_dashboard.h still contains a literal TFT rotation")



HEADER_PATTERNS = {
    "doc_id": re.compile(r"<!--\\s*doc-id:\\s*([^>]+?)\\s*-->"),
    "language": re.compile(r"<!--\\s*language:\\s*([^>]+?)\\s*-->"),
    "revision": re.compile(r"<!--\\s*content-revision:\\s*([^>]+?)\\s*-->"),
}
SECTION_PATTERN = re.compile(r"<!--\\s*section:\\s*([^>]+?)\\s*-->")



def check_generated_documentation(
    hardware: dict, runtime: dict, avr: dict, toolchain: dict
) -> None:
    for relative, language, names in target_files():
        path = ROOT / relative
        if not path.exists():
            fail(f"Missing generated-document target: {relative}")
            continue
        try:
            actual = path.read_text(encoding="utf-8")
            expected = render_file(
                path,
                language,
                names,
                hardware,
                runtime,
                avr,
                toolchain,
            )
        except Exception as exc:
            fail(f"Cannot render generated documentation {relative}: {exc}")
            continue
        if actual != expected:
            fail(
                f"{relative} contains stale generated regions; run "
                "python tools/generate_docs.py --write"
            )


def check_documentation_parity(metadata: dict) -> None:
    if metadata.get("schema_version") != "1.0":
        fail("docs/metadata.json: expected schema_version 1.0")

    languages = metadata.get("languages", {})
    canonical = metadata.get("canonical_language")

    if canonical not in languages:
        fail("docs/metadata.json canonical_language is not registered")
    elif languages.get(canonical, {}).get("role") != "canonical":
        fail("Canonical documentation language must declare role=canonical")

    if set(languages) != {"EN", "PT"}:
        fail("Wave 4 documentation contract must contain exactly EN and PT")

    if languages.get("PT", {}).get("role") != "translation":
        fail("PT documentation language must declare role=translation")

    documents = metadata.get("documents", {})
    if not documents:
        fail("docs/metadata.json contains no document contracts")
        return

    seen_paths: set[str] = set()

    for doc_id, spec in documents.items():
        revision = spec.get("content_revision")
        required = spec.get("required_sections", [])
        paths = spec.get("paths", {})

        if not isinstance(revision, int) or revision < 1:
            fail(f"{doc_id}: content_revision must be a positive integer")
        if not required or len(required) != len(set(required)):
            fail(f"{doc_id}: required_sections must be non-empty and unique")

        if set(paths) != set(languages):
            fail(f"{doc_id}: paths must cover every registered language")
            continue

        for language in languages:
            relative = paths.get(language)
            if not isinstance(relative, str):
                fail(f"{doc_id}/{language}: invalid document path")
                continue
            if relative in seen_paths:
                fail(f"Duplicate documentation path in metadata: {relative}")
            seen_paths.add(relative)

            path = ROOT / relative
            if not path.exists():
                fail(f"Missing documentation file: {relative}")
                continue

            text = path.read_text(encoding="utf-8")

            headers: dict[str, str | None] = {}
            for key, pattern in HEADER_PATTERNS.items():
                match = pattern.search(text)
                headers[key] = match.group(1).strip() if match else None

            if headers["doc_id"] != doc_id:
                fail(
                    f"{relative}: doc-id {headers['doc_id']!r} "
                    f"does not match {doc_id!r}"
                )
            if headers["language"] != language:
                fail(
                    f"{relative}: language {headers['language']!r} "
                    f"does not match {language!r}"
                )
            if headers["revision"] != str(revision):
                fail(
                    f"{relative}: content-revision {headers['revision']!r} "
                    f"does not match metadata revision {revision}"
                )

            sections = [
                match.group(1).strip()
                for match in SECTION_PATTERN.finditer(text)
            ]
            if sections != required:
                fail(
                    f"{relative}: semantic section sequence differs from "
                    f"metadata; expected {required}, found {sections}"
                )



def check_diagnostics_semantics() -> None:
    metadata = load_json(DIAGNOSTICS_METADATA_PATH)
    if not metadata:
        return

    if metadata.get("schema_version") != "1.0":
        fail("diagnostics/metadata.json: expected schema_version 1.0")
    if metadata.get("mode") != "manual":
        fail("diagnostics/metadata.json must declare mode=manual")

    entries = metadata.get("ordered_diagnostics", [])
    expected_ids = [f"DIAG-{index:02d}" for index in range(1, 11)]
    ids = [entry.get("id") for entry in entries]
    if ids != expected_ids:
        fail(
            "diagnostics/metadata.json must contain ordered IDs "
            "DIAG-01 through DIAG-10"
        )

    filenames = [entry.get("file") for entry in entries]
    if len(filenames) != len(set(filenames)):
        fail("diagnostics/metadata.json contains duplicate filenames")

    diagnostic_dir = ROOT / "diagnostics"
    actual_ino = sorted(path.name for path in diagnostic_dir.glob("*.ino"))
    expected_ino = sorted(
        name for name in filenames if isinstance(name, str)
    )
    if actual_ino != expected_ino:
        fail(
            "diagnostics/*.ino inventory differs from metadata; "
            f"expected {expected_ino}, found {actual_ino}"
        )

    for index, entry in enumerate(entries, 1):
        filename = entry.get("file")
        expected_prefix = f"{index:02d}_"
        if not isinstance(filename, str) or not filename.startswith(expected_prefix):
            fail(
                f"{entry.get('id')}: filename must start with "
                f"{expected_prefix!r}"
            )
            continue
        path = diagnostic_dir / filename
        if not path.exists():
            fail(f"Missing diagnostic file: diagnostics/{filename}")

    tests_ino = sorted((ROOT / "tests").glob("*.ino"))
    if tests_ino:
        fail(
            "Manual Arduino diagnostics must not live under tests/: "
            + ", ".join(path.name for path in tests_ino)
        )

    if TESTS_README_PATH.exists():
        text = TESTS_README_PATH.read_text(encoding="utf-8").lower()
        if "automated" not in text or "diagnostics" not in text:
            fail(
                "tests/README.md must reserve tests for automated tests "
                "and point manual checks to diagnostics/"
            )

    operational_files = [
        ROOT / "README.md",
        ROOT / "tools" / "README.md",
        ROOT / "docs" / "README.md",
        ROOT / "config" / "README.md",
    ]
    stale_manual_path = re.compile(
        r"tests/(?:0[1-9]|10)_[A-Za-z0-9_]+\.ino"
    )
    for path in operational_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if stale_manual_path.search(text):
            fail(
                f"{path.relative_to(ROOT)} still references the former "
                "tests/ manual-diagnostic path"
            )



def check_ci_workflow(toolchain: dict) -> None:
    if not CI_WORKFLOW_PATH.exists():
        fail("Missing GitHub Actions repository validation workflow")
        return

    text = CI_WORKFLOW_PATH.read_text(encoding="utf-8")
    required_fragments = (
        "name: Repository validation",
        "push:",
        "pull_request:",
        "workflow_dispatch:",
        "permissions:",
        "contents: read",
        "concurrency:",
        "cancel-in-progress: true",
        "uses: actions/checkout@v7.0.1",
        "uses: actions/setup-python@v7.0.0",
        "uses: arduino/setup-arduino-cli@v2",
        "steps.toolchain.outputs.arduino_cli",
        "python tools/generate_project_config.py --check",
        "python tools/generate_avr_contracts.py --check",
        "python tools/generate_libraries.py --check",
        "python tools/generate_docs.py --check",
        "python tools/validate_repository.py",
        "python tools/build_firmware.py",
    )
    for fragment in required_fragments:
        if fragment not in text:
            fail(f"CI workflow missing required fragment: {fragment}")

    if toolchain.get("arduino_cli", {}).get("version") not in text:
        # The workflow intentionally reads the version dynamically rather than
        # embedding it. Require the config-read path if no literal is present.
        if 'toolchain["arduino_cli"]["version"]' not in text:
            fail(
                "CI workflow neither embeds nor reads the canonical "
                "Arduino CLI version"
            )

    if "version: ${{ steps.toolchain.outputs.arduino_cli }}" not in text:
        fail("CI Arduino CLI action must consume the canonical version output")


def check_toolchain(toolchain: dict) -> None:
    if WOKWI_PROJECT_PATH.exists():
        text = WOKWI_PROJECT_PATH.read_text(encoding="utf-8")
        url = toolchain.get("simulator", {}).get("project_url")
        if url and url not in text:
            fail("wokwi-project.txt URL differs from config/toolchain.json")

    cli = toolchain.get("arduino_cli", {})
    core = toolchain.get("arduino_avr_core", {})
    build = toolchain.get("build", {})

    semver = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
    if cli.get("pinned") is not True or not semver.match(str(cli.get("version", ""))):
        fail("Arduino CLI must be pinned to an exact semantic version")
    if core.get("pinned") is not True or not semver.match(str(core.get("version", ""))):
        fail("Arduino AVR core must be pinned to an exact semantic version")
    if core.get("package") != "arduino:avr":
        fail("Reproducible build must use the arduino:avr core package")

    if build.get("profile_name") != "reproducible":
        fail("Build profile name must remain reproducible")
    if build.get("warnings") != "all":
        fail("Reproducible build must compile with warnings=all")

    primary = build.get("primary_sketch_name", "")
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,62}$", primary):
        fail("Build staging primary sketch name violates Arduino sketch naming rules")

    for key in ("staging_directory", "output_directory"):
        value = build.get(key)
        if not isinstance(value, str) or not value.startswith("build/"):
            fail(f"toolchain build.{key} must remain under ignored build/")

    try:
        profile = render_build_profile(toolchain)
    except Exception as exc:
        fail(f"Cannot render reproducible Arduino build profile: {exc}")
    else:
        required_profile_fragments = (
            f"fqbn: {toolchain['build_target']['fqbn']}",
            f"platform: {core['package']} ({core['version']})",
            f"default_profile: {build['profile_name']}",
        )
        for fragment in required_profile_fragments:
            if fragment not in profile:
                fail(f"Generated Arduino build profile missing: {fragment}")
        for library in toolchain.get("libraries", []):
            fragment = f"{library['name']} ({library['version']})"
            if fragment not in profile:
                fail(f"Generated Arduino build profile missing library: {fragment}")

    gitignore = ROOT / ".gitignore"
    if not gitignore.exists() or "build/" not in gitignore.read_text(encoding="utf-8"):
        fail("Reproducible build staging/output must remain ignored under build/")


def main() -> int:
    check_required_files()

    hardware = load_json(HARDWARE_PATH)
    runtime = load_json(RUNTIME_PATH)
    avr = load_json(AVR_PATH)
    toolchain = load_json(TOOLCHAIN_PATH)
    docs_metadata = load_json(DOCS_METADATA_PATH)

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
        check_ci_workflow(toolchain)
        check_generated_documentation(hardware, runtime, avr, toolchain)

    if docs_metadata:
        check_documentation_parity(docs_metadata)

    check_diagnostics_semantics()

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
