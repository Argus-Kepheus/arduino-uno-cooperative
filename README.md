# Arduino Uno Cooperative

![Circuito simulado: Arduino Uno R3, seis LEDs azuis, LED verde do botão principal, três botões, LED laranja de atividade dos displays, LED amarelo de heartbeat do escalonador, OLED SSD1306 e TFT ILI9341](report/figures/front-cover.png)

Firmware para Arduino Uno R3 que explora concorrência cooperativa sem RTOS,
threads ou `TaskScheduler`. Deriva conceitualmente do projeto `esp32-asyncio`
(MicroPython/`asyncio`), mas usa um escalonador cooperativo nativo e estático
em C++, adequado às restrições do ATmega328P. Onze tarefas cooperativas
controlam seis LEDs azuis independentes, três botões com debounce não
bloqueante, um LED verde, dois indicadores de atividade, um OLED SSD1306
diagnóstico, uma TFT ILI9341 principal e instrumentação de tempo e SRAM.

**Documentação completa:** [Português](docs/PT/README.md) · [English](docs/EN/README.md)

**Relatório técnico (Português):** [`report/relatorio.pdf`](report/relatorio.pdf)

**Simulação no Wokwi:** <https://wokwi.com/projects/472743544463123457>

## Execução rápida

1. Abra o link do Wokwi ou importe `diagram.json`, `sketch.ino`, os arquivos
   `.h` e `libraries.txt` em um projeto Arduino Uno.
2. Inicie a simulação.
3. Use os botões para alternar o LED verde e ajustar o intervalo compartilhado
   dos seis LEDs azuis.
4. Acompanhe métricas em tempo real na TFT, no OLED e no monitor serial.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `sketch.ino` + módulos `*.h` | Firmware Arduino/C++ (escalonador, botões, métricas, displays) |
| `config/` | Fontes canônicas de hardware, runtime, contratos AVR e toolchain |
| `project_config.h` | Header gerado de configuração consumido pelo firmware |
| `avr_contracts.h` | Contratos AVR gerados e `static_assert` de segurança arquitetural |
| `avr_fast_io.h` | Única camada de implementação com acessos diretos `PORTD`/`PINC`/`PORTC` |
| `diagram.json` | Circuito e geometria/layout do Wokwi; semântica elétrica validada contra `config/hardware.json` |
| `libraries.txt` | Lista gerada de dependências do Wokwi |
| `tools/` | Geração determinística e validação estática do repositório |
| `docs/EN/` e `docs/PT/` | Documentação técnica bilíngue sob contrato semântico em `docs/metadata.json` |
| `diagnostics/` | Diagnósticos manuais isolados para Wokwi/hardware, governados por `diagnostics/metadata.json` |
| `tests/` | Reservado para futuros testes automatizados host-side |
| `report/` | Relatório técnico em LaTeX e PDF |

## Validação

A consistência estática entre `config/`, artefatos gerados, firmware, circuito e paridade EN/PT pode ser verificada com:

```text
python tools/generate_project_config.py --check
python tools/generate_avr_contracts.py --check
python tools/generate_libraries.py --check
python tools/generate_docs.py --check
python tools/validate_repository.py
```

A pasta `diagnostics/` contém sketches independentes que isolam partes do
hardware (LEDs, botões, displays, escalonador). Eles são diagnósticos manuais e
não substituem a validação integrada. O namespace `tests/` fica reservado para
futura automação host-side. Para aceitação completa, use
`docs/PT/validation-checklist.md` (ou `docs/EN/validation-checklist.md`).

## Limitações

Não há RTOS, `TaskScheduler` ou alocação dinâmica após `setup()`. A versão-base
prioriza legibilidade e observabilidade em vez de desempenho máximo; ver
"Trabalhos futuros" em `docs/PT/technical-specification.md`.

**Licença:** CC0 1.0 Universal — consulte [`LICENSE`](LICENSE).
