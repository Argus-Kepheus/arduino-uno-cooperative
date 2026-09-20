<!-- doc-id: project-overview -->
<!-- language: PT -->
<!-- content-revision: 2 -->

# arduino-uno-cooperative

**Idioma:** [English](../EN/README.md) | [Português](README.md)

Projeto para Arduino Uno R3 / ATmega328P que explora concorrência cooperativa
sem RTOS, sem threads e sem `TaskScheduler`. A aplicação preserva seis tarefas
independentes para LEDs azuis, três botões com debounce não bloqueante, um LED
verde, dois indicadores de atividade, um OLED SSD1306 diagnóstico, uma TFT
ILI9341 principal e instrumentação de tempo e SRAM.

A simulação inicial é destinada ao **Wokwi no navegador**.

<!-- section: baseline-architecture -->
## Arquitetura-base

<!-- BEGIN GENERATED: baseline-summary -->
| Propriedade | Valor canônico |
|---|---|
| Placa | Arduino Uno R3 |
| MCU / clock | ATmega328P / 16 MHz |
| Tarefas registradas | 11 |
| LEDs azuis | D2–D7 (6) |
| Botões | A0 / A1 / A2 |
| LED verde | D8 |
| LED de atividade dos displays | D12 |
| Heartbeat do escalonador | A3 |
| TFT | software SPI: D9/D10/D11/D13 |
| OLED | hardware I2C: A4/SDA, A5/SCL |
| UART | D0/RX, D1/TX |
| Bibliotecas | Adafruit GFX Library 1.12.6, Adafruit ILI9341 1.6.3, Adafruit BusIO 1.17.4, SSD1306Ascii 1.3.5 |
<!-- END GENERATED: baseline-summary -->

A tabela gerada mantém os fatos atuais de placa, pinagem, buses, quantidade de tarefas e versões de bibliotecas. As políticas arquiteturais permanecem manuais:

- C++ / framework Arduino;
- escalonador cooperativo nativo e estático;
- nenhum `delay()` durante a operação normal;
- nenhuma alocação dinâmica deliberada durante a operação normal.

<!-- section: documents -->
## Documentos

- [`technical-specification.md`](technical-specification.md) - requisitos e critérios técnicos;
- [`architecture.md`](architecture.md) - organização do firmware e fluxo de execução;
- [`pinout.md`](pinout.md) - pinagem oficial;
- [`scheduler.md`](scheduler.md) - funcionamento do escalonador nativo;
- [`displays.md`](displays.md) - TFT, OLED e estratégia de atualização;
- [`validation-checklist.md`](validation-checklist.md) - roteiro de validação.

<!-- section: baseline-status -->
## Estado da versão-base

O projeto deliberadamente preserva uma implementação legível e instrumentável.
Otimizações agressivas de AVR, uso de `TaskScheduler`, SPI de hardware com nova
pinagem, watchdog e medições temporais mais sofisticadas permanecem como
trabalhos futuros, para permitir comparação com a versão-base.
