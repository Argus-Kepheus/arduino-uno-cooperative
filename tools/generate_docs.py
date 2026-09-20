#!/usr/bin/env python3
"""Generate canonical technical regions inside EN/PT documentation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_PATH = ROOT / "config" / "hardware.json"
RUNTIME_PATH = ROOT / "config" / "runtime.json"
AVR_PATH = ROOT / "config" / "avr.json"
TOOLCHAIN_PATH = ROOT / "config" / "toolchain.json"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def region(name: str, body: str) -> str:
    return (
        f"<!-- BEGIN GENERATED: {name} -->\n"
        f"{body.rstrip()}\n"
        f"<!-- END GENERATED: {name} -->"
    )


def replace_region(text: str, name: str, body: str) -> str:
    begin = f"<!-- BEGIN GENERATED: {name} -->"
    end = f"<!-- END GENERATED: {name} -->"
    start = text.find(begin)
    finish = text.find(end)
    if start < 0 or finish < 0 or finish < start:
        raise ValueError(f"Missing generated region {name}")
    finish += len(end)
    return text[:start] + region(name, body) + text[finish:]


def baseline_summary(language: str, h: dict, r: dict, a: dict, t: dict) -> str:
    c = h["components"]
    b = h["buses"]
    labels = {
        "EN": ("Property", "Canonical value", "Board", "MCU / clock", "Registered tasks",
               "Blue LEDs", "Buttons", "Green LED", "Display-activity LED",
               "Scheduler heartbeat", "TFT", "OLED", "UART", "Libraries"),
        "PT": ("Propriedade", "Valor canônico", "Placa", "MCU / clock", "Tarefas registradas",
               "LEDs azuis", "Botões", "LED verde", "LED de atividade dos displays",
               "Heartbeat do escalonador", "TFT", "OLED", "UART", "Bibliotecas"),
    }[language]
    lib_text = ", ".join(f"{item['name']} {item['version']}" for item in t["libraries"])
    rows = [
        (labels[2], h["board"]["board_name"]),
        (labels[3], f"{h['board']['microcontroller']} / {a['microcontroller']['clock_hz'] // 1000000} MHz"),
        (labels[4], str(a["scheduler"]["expected_registered_tasks"])),
        (labels[5], f"{c['blinking_leds'][0]['arduino_pin']}–{c['blinking_leds'][-1]['arduino_pin']} ({len(c['blinking_leds'])})"),
        (labels[6], f"{c['buttons']['main']['arduino_pin']} / {c['buttons']['decrease_interval']['arduino_pin']} / {c['buttons']['increase_interval']['arduino_pin']}"),
        (labels[7], c["green_led"]["arduino_pin"]),
        (labels[8], c["status_leds"]["display_idle"]["arduino_pin"]),
        (labels[9], c["status_leds"]["scheduler_heartbeat"]["arduino_pin"]),
        (labels[10], f"software SPI: {b['tft_spi']['dc']['arduino_pin']}/{b['tft_spi']['cs']['arduino_pin']}/{b['tft_spi']['mosi']['arduino_pin']}/{b['tft_spi']['sck']['arduino_pin']}"),
        (labels[11], f"hardware I2C: {b['oled_i2c']['sda']['arduino_pin']}/SDA, {b['oled_i2c']['scl']['arduino_pin']}/SCL"),
        (labels[12], f"{b['uart0']['rx']['arduino_pin']}/RX, {b['uart0']['tx']['arduino_pin']}/TX"),
        (labels[13], lib_text),
    ]
    lines = [f"| {labels[0]} | {labels[1]} |", "|---|---|"]
    lines.extend(f"| {key} | {value} |" for key, value in rows)
    return "\n".join(lines)


def pin_map(language: str, h: dict) -> str:
    c = h["components"]
    b = h["buses"]
    rows = [
        ("D0 / RX", "serial receive" if language == "EN" else "recepção serial"),
        ("D1 / TX", "serial transmit" if language == "EN" else "transmissão serial"),
    ]
    for index, led in enumerate(c["blinking_leds"], 1):
        role = f"blue LED {index}" if language == "EN" else f"LED azul {index}"
        rows.append((led["arduino_pin"], role))
    rows.extend([
        (c["green_led"]["arduino_pin"], "green LED" if language == "EN" else "LED verde"),
        (b["tft_spi"]["dc"]["arduino_pin"], "TFT D/C"),
        (b["tft_spi"]["cs"]["arduino_pin"], "TFT CS"),
        (b["tft_spi"]["mosi"]["arduino_pin"], "TFT MOSI — software SPI" if language == "EN" else "TFT MOSI — SPI por software"),
        (c["status_leds"]["display_idle"]["arduino_pin"], "orange display-activity LED" if language == "EN" else "LED laranja de atividade dos displays"),
        (b["tft_spi"]["sck"]["arduino_pin"], "TFT SCK — software SPI + built-in L LED" if language == "EN" else "TFT SCK — SPI por software + LED L integrado"),
        (c["buttons"]["main"]["arduino_pin"], "main button" if language == "EN" else "botão principal"),
        (c["buttons"]["decrease_interval"]["arduino_pin"], "decrease interval" if language == "EN" else "diminuir intervalo"),
        (c["buttons"]["increase_interval"]["arduino_pin"], "increase interval" if language == "EN" else "aumentar intervalo"),
        (c["status_leds"]["scheduler_heartbeat"]["arduino_pin"], "yellow scheduler heartbeat LED" if language == "EN" else "LED amarelo de heartbeat do escalonador"),
        (f"{b['oled_i2c']['sda']['arduino_pin']} / SDA", "OLED SDA"),
        (f"{b['oled_i2c']['scl']['arduino_pin']} / SCL", "OLED SCL"),
    ])
    header = ("Pin", "Function") if language == "EN" else ("Pino", "Função")
    lines = [f"| {header[0]} | {header[1]} |", "|---|---|"]
    lines.extend(f"| {pin} | {role} |" for pin, role in rows)
    return "\n".join(lines)


def display_summary(language: str, h: dict, r: dict) -> str:
    c = h["components"]["displays"]
    b = h["buses"]
    tft = c["tft"]
    oled = c["oled"]
    h1 = ("Display", "Interface", "Canonical wiring", "Geometry / timing") if language == "EN" else ("Display", "Interface", "Ligações canônicas", "Geometria / temporização")
    tft_geometry = (
        f"{tft['native_resolution_px']['width']}×{tft['native_resolution_px']['height']} native; "
        f"rotation {tft['configured_rotation']} -> "
        f"{tft['logical_resolution_px']['width']}×{tft['logical_resolution_px']['height']} logical"
        if language == "EN"
        else
        f"{tft['native_resolution_px']['width']}×{tft['native_resolution_px']['height']} nativo; "
        f"rotação {tft['configured_rotation']} -> "
        f"{tft['logical_resolution_px']['width']}×{tft['logical_resolution_px']['height']} lógico"
    )
    oled_geometry = (
        f"{oled['resolution_px']['width']}×{oled['resolution_px']['height']}; "
        f"address {oled['address_hex']}; refresh {r['displays']['oled_refresh_period_ms']} ms"
        if language == "EN"
        else
        f"{oled['resolution_px']['width']}×{oled['resolution_px']['height']}; "
        f"endereço {oled['address_hex']}; atualização {r['displays']['oled_refresh_period_ms']} ms"
    )
    tft_wiring = f"D/C {b['tft_spi']['dc']['arduino_pin']}, CS {b['tft_spi']['cs']['arduino_pin']}, MOSI {b['tft_spi']['mosi']['arduino_pin']}, SCK {b['tft_spi']['sck']['arduino_pin']}"
    oled_wiring = f"SDA {b['oled_i2c']['sda']['arduino_pin']}, SCL {b['oled_i2c']['scl']['arduino_pin']}"
    return "\n".join([
        f"| {h1[0]} | {h1[1]} | {h1[2]} | {h1[3]} |",
        "|---|---|---|---|",
        f"| ILI9341 | {tft['interface']} | {tft_wiring} | {tft_geometry} |",
        f"| SSD1306 | {oled['interface']} ({b['oled_i2c']['mode']}) | {oled_wiring} | {oled_geometry} |",
    ])


def scheduler_summary(language: str, r: dict, a: dict) -> str:
    s = a["scheduler"]
    periods = r["blinking_leds"]["shared_interval"]["derived_values_ms"] + [
        r["buttons"]["scan_period_ms"],
        r["metrics"]["sample_period_ms"],
        r["displays"]["service_period_ms"],
        r["serial"]["status_period_ms"],
        r["scheduler"]["heartbeat_period_ms"],
    ]
    rows = [
        ("Capacity" if language == "EN" else "Capacidade", f"{s['maximum_tasks']}"),
        ("Tick" if language == "EN" else "Tick", f"{s['tick_type']} / {s['tick_bits']} bit"),
        ("Modular range" if language == "EN" else "Faixa modular", f"{s['modular_range_ms']} ms"),
        ("Signed half-range" if language == "EN" else "Meia-faixa assinada", f"{s['signed_comparison_half_range_ms']} ms"),
        ("Longest configured period" if language == "EN" else "Maior período configurado", f"{max(periods)} ms"),
        ("Scheduling policy" if language == "EN" else "Política de escalonamento", r["scheduler"]["scheduling_policy"]),
        ("Missed-release policy" if language == "EN" else "Política de liberações perdidas", r["scheduler"]["missed_release_policy"]),
    ]
    header = ("Contract", "Canonical value") if language == "EN" else ("Contrato", "Valor canônico")
    lines = [f"| {header[0]} | {header[1]} |", "|---|---|"]
    lines.extend(f"| {key} | {value} |" for key, value in rows)
    return "\n".join(lines)


def registration_order(language: str, a: dict) -> str:
    header = ("Task ID", "Callback") if language == "EN" else ("ID da tarefa", "Callback")
    lines = [f"| {header[0]} | {header[1]} |", "|---:|---|"]
    lines.extend(f"| {index} | {name} |" for index, name in enumerate(a["scheduler"]["registration_order"]))
    return "\n".join(lines)


def task_periods(language: str, r: dict, a: dict) -> str:
    blink = r["blinking_leds"]["shared_interval"]
    rows = [
        ("blinkLed1 ... blinkLed6", f"{min(blink['derived_values_ms'])}–{max(blink['derived_values_ms'])} ms", "six independent LEDs" if language == "EN" else "seis LEDs independentes"),
        ("scanButtons", f"{r['buttons']['scan_period_ms']} ms", "read/debounce three buttons" if language == "EN" else "leitura/debounce de três botões"),
        ("sampleMetrics", f"{r['metrics']['sample_period_ms']} ms", "consolidate metrics" if language == "EN" else "consolidar métricas"),
        ("serviceDisplays", f"{r['displays']['service_period_ms']} ms", "incremental TFT/OLED pipeline" if language == "EN" else "pipeline incremental TFT/OLED"),
        ("printStatus", f"{r['serial']['status_period_ms']} ms", "serial status" if language == "EN" else "status serial"),
        ("schedulerHeartbeat", f"{r['scheduler']['heartbeat_period_ms']} ms", "scheduler heartbeat" if language == "EN" else "heartbeat do escalonador"),
    ]
    header = ("Task", "Nominal period", "Responsibility") if language == "EN" else ("Tarefa", "Período nominal", "Função")
    lines = [f"| {header[0]} | {header[1]} | {header[2]} |", "|---|---:|---|"]
    lines.extend(f"| {name} | {period} | {role} |" for name, period, role in rows)
    total = f"Total: **{a['scheduler']['expected_registered_tasks']} tasks**." if language == "EN" else f"Total: **{a['scheduler']['expected_registered_tasks']} tarefas**."
    lines.extend(["", total])
    return "\n".join(lines)


def blink_intervals(language: str, r: dict) -> str:
    b = r["blinking_leds"]["shared_interval"]
    header = ("Index", "Interval") if language == "EN" else ("Índice", "Intervalo")
    lines = [f"| {header[0]} | {header[1]} |", "|---:|---:|"]
    lines.extend(f"| {index} | {value} ms |" for index, value in enumerate(b["derived_values_ms"]))
    initial = b["derived_values_ms"][b["initial_index"]]
    lines.extend(["", f"Initial value: **{initial} ms**." if language == "EN" else f"Valor inicial: **{initial} ms**."])
    return "\n".join(lines)


def runtime_summary(language: str, h: dict, r: dict, a: dict) -> str:
    buttons = h["components"]["buttons"]
    bus = h["buses"]["uart0"]
    labels = (
        ("Input mode", "Pressed / released", "Button scan", "Debounce", "Auto-repeat",
         "Physical SRAM", "Target free SRAM", "Minimum free SRAM", "Serial baud",
         "Serial status period", "disabled")
        if language == "EN" else
        ("Modo de entrada", "Pressionado / solto", "Varredura dos botões", "Debounce", "Auto-repeat",
         "SRAM física", "Meta de SRAM livre", "Mínimo de SRAM livre", "Baud serial",
         "Período de status serial", "desativado")
    )
    rows = [
        (labels[0], buttons["main"]["input_mode"]),
        (labels[1], f"{buttons['main']['pressed_level']} / {buttons['main']['released_level']}"),
        (labels[2], f"{r['buttons']['scan_period_ms']} ms"),
        (labels[3], f"{r['buttons']['debounce_ms']} ms"),
        (labels[4], labels[10] if not r["buttons"]["auto_repeat"] else "enabled"),
        (labels[5], f"{a['microcontroller']['sram_bytes']} bytes"),
        (labels[6], f">= {r['sram_policy']['target_free_bytes']} bytes"),
        (labels[7], f">= {r['sram_policy']['minimum_free_bytes']} bytes"),
        (labels[8], str(r["serial"]["baud"])),
        (labels[9], f"{r['serial']['status_period_ms']} ms"),
        ("UART", f"{bus['rx']['arduino_pin']}/RX, {bus['tx']['arduino_pin']}/TX"),
    ]
    header = ("Runtime property", "Canonical value") if language == "EN" else ("Propriedade de runtime", "Valor canônico")
    lines = [f"| {header[0]} | {header[1]} |", "|---|---|"]
    lines.extend(f"| {key} | {value} |" for key, value in rows)
    return "\n".join(lines)


def target_files() -> list[tuple[str, str, tuple[str, ...]]]:
    targets = []
    for language in ("EN", "PT"):
        targets.extend([
            (f"docs/{language}/README.md", language, ("baseline-summary",)),
            (f"docs/{language}/pinout.md", language, ("pin-map",)),
            (f"docs/{language}/displays.md", language, ("display-summary",)),
            (f"docs/{language}/scheduler.md", language, ("scheduler-summary", "registration-order")),
            (f"docs/{language}/technical-specification.md", language, ("task-periods", "blink-intervals", "runtime-summary")),
        ])
    return targets


def render_body(name: str, language: str, h: dict, r: dict, a: dict, t: dict) -> str:
    if name == "baseline-summary":
        return baseline_summary(language, h, r, a, t)
    if name == "pin-map":
        return pin_map(language, h)
    if name == "display-summary":
        return display_summary(language, h, r)
    if name == "scheduler-summary":
        return scheduler_summary(language, r, a)
    if name == "registration-order":
        return registration_order(language, a)
    if name == "task-periods":
        return task_periods(language, r, a)
    if name == "blink-intervals":
        return blink_intervals(language, r)
    if name == "runtime-summary":
        return runtime_summary(language, h, r, a)
    raise KeyError(name)


def render_file(path: Path, language: str, names: tuple[str, ...], h: dict, r: dict, a: dict, t: dict) -> str:
    text = path.read_text(encoding="utf-8")
    for name in names:
        text = replace_region(text, name, render_body(name, language, h, r, a, t))
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    h = load_json(HARDWARE_PATH)
    r = load_json(RUNTIME_PATH)
    a = load_json(AVR_PATH)
    t = load_json(TOOLCHAIN_PATH)

    stale = []
    for relative, language, names in target_files():
        path = ROOT / relative
        expected = render_file(path, language, names, h, r, a, t)
        actual = path.read_text(encoding="utf-8")
        if args.write:
            path.write_text(expected, encoding="utf-8")
            print(f"Updated {relative}")
        elif args.check:
            if actual != expected:
                stale.append(relative)
        else:
            print(f"--- {relative} ---")
            print(expected, end="" if expected.endswith("\n") else "\n")

    if args.check:
        if stale:
            print("Generated documentation is stale:")
            for relative in stale:
                print(f"  {relative}")
            print("Run: python tools/generate_docs.py --write")
            return 1
        print("Generated documentation is up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
