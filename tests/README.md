# Testes diagnósticos para Wokwi web

Esta pasta contém sketches Arduino independentes destinados a isolar partes do
hardware e da arquitetura do `arduino-uno-cooperative`.

Eles **não são compilados em conjunto** com o firmware principal. Para executar
um teste no Wokwi web, copie temporariamente o conteúdo do arquivo desejado para
`sketch.ino`, execute a simulação, registre o resultado e depois restaure o
firmware real.

## Ordem sugerida

| # | Arquivo | Verificação |
|---:|---|---|
| 1 | `01_blue_led_basic.ino` | D2 e primeiro LED azul |
| 2 | `02_all_blue_leds_basic.ino` | D2-D7 e seis LEDs |
| 3 | `03_green_button_led.ino` | A0, debounce simples e D8 |
| 4 | `04_interval_buttons.ino` | A1/A2 e limites 125-4000 ms |
| 5 | `05_status_leds.ino` | D12 laranja e A3 amarelo |
| 6 | `06_oled_basic.ino` | SSD1306 em A4/A5, `0x3C` |
| 7 | `07_tft_basic_software_spi.ino` | ILI9341 por SPI de software |
| 8 | `08_tft_oled_together.ino` | TFT + OLED simultaneamente |
| 9 | `09_native_scheduler_basic.ino` | seis callbacks independentes |
| 10 | `10_scheduler_rollover.ino` | aritmética modular de 16 bits |

## Dependências

Os testes 6 e 8 usam `SSD1306Ascii`. Os testes 7 e 8 usam `Adafruit GFX` e
`Adafruit ILI9341`.

## Observação

Os testes de hardware podem usar `delay()` deliberadamente quando o objetivo é
isolar uma ligação física. A proibição de `delay()` aplica-se ao firmware
integrado, não a um diagnóstico isolado de bancada.

Para aceitação completa do projeto, use também
`docs/PT/validation-checklist.md`.
