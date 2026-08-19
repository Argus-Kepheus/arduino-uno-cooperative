# Especificação Técnica

## 1. Objetivo

O `arduino-uno-cooperative` demonstra concorrência cooperativa em um Arduino
Uno R3, preservando conceitos do projeto `esp32-asyncio` sem tentar reproduzir
o `asyncio` do MicroPython. A restrição do ATmega328P - 8 bits, 16 MHz e apenas
2 KiB de SRAM - faz parte do experimento.

## 2. Princípios da versão-base

1. Não utilizar RTOS, threads ou `TaskScheduler`.
2. Não utilizar `delay()` na operação normal.
3. Preservar seis tarefas independentes para os LEDs azuis.
4. Usar um escalonador cooperativo nativo, estático e observável.
5. Tratar os três botões em uma única tarefa de varredura/debounce.
6. Evitar alocação dinâmica após `setup()`.
7. Manter o serial como canal diagnóstico autoritativo.
8. Dividir operações gráficas em etapas cooperativas.
9. Instrumentar duração de callbacks, atraso, overruns, passagens e SRAM.
10. Descartar liberações perdidas em vez de executar rajadas de recuperação.

## 3. Tarefas

| Tarefa | Período nominal | Função |
|---|---:|---|
| `blinkLed1` ... `blinkLed6` | 125-4000 ms | seis LEDs independentes |
| `scanButtons` | 5 ms | leitura e debounce dos três botões |
| `sampleMetrics` | 250 ms | consolidação das métricas |
| `serviceDisplays` | 20 ms | pipeline incremental TFT/OLED |
| `printStatus` | 1000 ms | status serial |
| `schedulerHeartbeat` | 100 ms | heartbeat em A3 |

Total: **11 tarefas**.

## 4. Intervalos dos LEDs

Os seis LEDs compartilham o mesmo valor de período, mas mantêm tarefas próprias:

| Índice | Intervalo |
|---:|---:|
| 0 | 125 ms |
| 1 | 250 ms |
| 2 | 500 ms |
| 3 | 1000 ms |
| 4 | 2000 ms |
| 5 | 4000 ms |

Valor inicial: **500 ms**.

## 5. Entradas e debounce

Os três botões utilizam `INPUT_PULLUP`, portanto pressionado = LOW e solto =
HIGH. O debounce nominal é de 30 ms, com amostragem a cada 5 ms. O botão
principal reage a pressão e liberação; os dois botões de intervalo reagem
somente à borda de pressão e não repetem automaticamente ao permanecerem
pressionados.

## 6. Displays

### ILI9341

Display principal, em orientação horizontal. Utiliza SPI por software para
preservar D12 como GPIO. Funções: gráficos `APP BUSY` e SRAM livre, métricas,
estado dos botões e console circular de eventos.

### SSD1306

Display diagnóstico compacto em I2C de hardware, endereço `0x3C`. Utiliza
`SSD1306Ascii`, evitando um framebuffer de 1024 bytes. Atualização limitada a
aproximadamente 1 Hz.

## 7. Métricas

- **APP BUSY:** fração da janela de amostragem consumida dentro dos callbacks
  instrumentados. Não é uso absoluto de CPU.
- **SRAM FREE:** estimativa da distância entre heap e pilha no instante da
  amostragem.
- **RAM LOW:** menor `SRAM FREE` amostrada desde a inicialização.
- **PASS/s:** passagens do escalonador por segundo.
- **MAX CALLBACK:** maior duração observada de callback.
- **MAX LATE:** maior atraso entre liberação programada e execução real.
- **OVR:** liberações perdidas e descartadas pela política de degradação.

## 8. SRAM

Meta desejável: **>= 512 bytes livres estimados**.

Mínimo aceitável: **400 bytes**.

Abaixo de 400 bytes, a configuração integrada não deve ser aprovada sem nova
revisão.

Devem ser evitados `String`, `new`, `malloc`, containers dinâmicos e grandes
buffers gráficos durante a operação normal.

## 9. Comunicação

UART: 115200 baud, D0/RX e D1/TX reservados. O monitor serial deve continuar
funcionando mesmo quando os displays apresentarem limitações ou falhas.

## 10. Critérios de aceitação

A versão-base deve:

- compilar para Arduino Uno R3;
- executar onze tarefas cooperativas;
- manter os seis LEDs independentes;
- respeitar os seis intervalos;
- manter debounce sem bloqueio;
- manter TFT, OLED e serial simultaneamente;
- expor todas as métricas previstas;
- manter SRAM acima do limite mínimo;
- permanecer responsiva no intervalo de 125 ms;
- atravessar overflow do relógio modular sem falha;
- permanecer estável em ensaio integrado prolongado.

## 11. Trabalhos futuros

Ficam abertos: `TaskScheduler`, AceRoutine, SPI de hardware com nova pinagem,
acesso direto a `PORT`, watchdog, prioridades, jitter por tarefa, high-water
mark real de pilha, persistência em EEPROM e outras otimizações específicas do
AVR.
