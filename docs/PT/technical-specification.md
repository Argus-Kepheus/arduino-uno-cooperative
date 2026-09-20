<!-- doc-id: technical-specification -->
<!-- language: PT -->
<!-- content-revision: 2 -->

# Especificação Técnica

<!-- section: purpose -->
## 1. Objetivo

O `arduino-uno-cooperative` demonstra concorrência cooperativa em um Arduino
Uno R3, preservando conceitos do projeto `esp32-asyncio` sem tentar reproduzir
o `asyncio` do MicroPython. A restrição do ATmega328P - 8 bits, 16 MHz e apenas
2 KiB de SRAM - faz parte do experimento.

<!-- section: baseline-principles -->
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

<!-- section: tasks -->
## 3. Tarefas

<!-- BEGIN GENERATED: task-periods -->
| Tarefa | Período nominal | Função |
|---|---:|---|
| blinkLed1 ... blinkLed6 | 125–4000 ms | seis LEDs independentes |
| scanButtons | 5 ms | leitura/debounce de três botões |
| sampleMetrics | 250 ms | consolidar métricas |
| serviceDisplays | 20 ms | pipeline incremental TFT/OLED |
| printStatus | 1000 ms | status serial |
| schedulerHeartbeat | 100 ms | heartbeat do escalonador |

Total: **11 tarefas**.
<!-- END GENERATED: task-periods -->

<!-- section: blue-led-intervals -->
## 4. Intervalos dos LEDs

Os seis LEDs compartilham o mesmo período configurado, mantendo tarefas independentes.

<!-- BEGIN GENERATED: blink-intervals -->
| Índice | Intervalo |
|---:|---:|
| 0 | 125 ms |
| 1 | 250 ms |
| 2 | 500 ms |
| 3 | 1000 ms |
| 4 | 2000 ms |
| 5 | 4000 ms |

Valor inicial: **500 ms**.
<!-- END GENERATED: blink-intervals -->

<!-- section: inputs-debounce -->
## 5. Entradas e debounce

Os valores operacionais atuais são gerados a partir de
`config/runtime.json`, `config/hardware.json` e `config/avr.json`:

<!-- BEGIN GENERATED: runtime-summary -->
| Propriedade de runtime | Valor canônico |
|---|---|
| Modo de entrada | INPUT_PULLUP |
| Pressionado / solto | LOW / HIGH |
| Varredura dos botões | 5 ms |
| Debounce | 30 ms |
| Auto-repeat | desativado |
| SRAM física | 2048 bytes |
| Meta de SRAM livre | >= 512 bytes |
| Mínimo de SRAM livre | >= 400 bytes |
| Baud serial | 115200 |
| Período de status serial | 1000 ms |
| UART | D0/RX, D1/TX |
<!-- END GENERATED: runtime-summary -->

O botão principal reage às bordas de pressão e liberação. Os botões de
intervalo reagem somente à borda de pressão; a política de auto-repeat acima
permanece autoritativa.

<!-- section: displays -->
## 6. Displays

<!-- section: ili9341 -->
### ILI9341

Display principal em orientação horizontal. Sua pinagem e geometria canônicas
são geradas em [`displays.md`](displays.md). Funções: gráficos `APP BUSY` e
SRAM livre, métricas, estado dos botões e console circular de eventos.

<!-- section: ssd1306 -->
### SSD1306

Display diagnóstico compacto usando a configuração canônica de I2C de hardware
gerada em [`displays.md`](displays.md). Utiliza `SSD1306Ascii`, evitando um
framebuffer de 1024 bytes.

<!-- section: metrics -->
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

<!-- section: sram -->
## 8. SRAM

O tamanho físico da SRAM e os limiares operacionais de SRAM livre são gerados
no resumo de runtime acima. Abaixo do mínimo configurado, a configuração
integrada não deve ser aprovada sem nova revisão.

Devem ser evitados `String`, `new`, `malloc`, containers dinâmicos e grandes
buffers gráficos durante a operação normal.

<!-- section: communication -->
## 9. Comunicação

A taxa UART e os pinos reservados são gerados no resumo de runtime acima. O
monitor serial deve continuar funcionando mesmo quando os displays apresentarem
limitações ou falhas.

<!-- section: acceptance-criteria -->
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

<!-- section: future-work -->
## 11. Trabalhos futuros

Ficam abertos: `TaskScheduler`, AceRoutine, SPI de hardware com nova pinagem,
acesso direto a `PORT`, watchdog, prioridades, jitter por tarefa, high-water
mark real de pilha, persistência em EEPROM e outras otimizações específicas do
AVR.
