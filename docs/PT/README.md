# arduino-uno-cooperative

**Idioma:** [English](../EN/README.md) | [Português](README.md)

Projeto para Arduino Uno R3 / ATmega328P que explora concorrência cooperativa
sem RTOS, sem threads e sem `TaskScheduler`. A aplicação preserva seis tarefas
independentes para LEDs azuis, três botões com debounce não bloqueante, um LED
verde, dois indicadores de atividade, um OLED SSD1306 diagnóstico, uma TFT
ILI9341 principal e instrumentação de tempo e SRAM.

A simulação inicial é destinada ao **Wokwi no navegador**.

## Arquitetura-base

- Arduino Uno R3, ATmega328P, 16 MHz;
- C++ / framework Arduino;
- escalonador cooperativo nativo e estático;
- 11 tarefas registradas;
- seis LEDs azuis em D2-D7, com uma tarefa por LED;
- botão principal em A0 e botões de intervalo em A1/A2;
- LED verde em D8;
- LED laranja de atividade dos displays em D12;
- LED amarelo de heartbeat do escalonador em A3;
- TFT ILI9341 em SPI por software: D9/D10/D11/D13;
- OLED SSD1306 no I2C de hardware: A4/SDA e A5/SCL;
- UART preservada em D0/RX e D1/TX;
- nenhum `delay()` durante a operação normal;
- nenhuma alocação dinâmica deliberada durante a operação normal.

## Documentos

- [`technical-specification.md`](technical-specification.md) - requisitos e critérios técnicos;
- [`architecture.md`](architecture.md) - organização do firmware e fluxo de execução;
- [`pinout.md`](pinout.md) - pinagem oficial;
- [`scheduler.md`](scheduler.md) - funcionamento do escalonador nativo;
- [`displays.md`](displays.md) - TFT, OLED e estratégia de atualização;
- [`validation-checklist.md`](validation-checklist.md) - roteiro de validação.

## Estado da versão-base

O projeto deliberadamente preserva uma implementação legível e instrumentável.
Otimizações agressivas de AVR, uso de `TaskScheduler`, SPI de hardware com nova
pinagem, watchdog e medições temporais mais sofisticadas permanecem como
trabalhos futuros, para permitir comparação com a versão-base.
