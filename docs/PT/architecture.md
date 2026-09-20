<!-- doc-id: architecture -->
<!-- language: PT -->
<!-- content-revision: 1 -->

# Arquitetura do Firmware

<!-- section: overview -->
## Visão geral

O firmware possui um único fluxo físico de execução. `loop()` chama
continuamente `scheduler.execute()`, que percorre uma tabela estática de tarefas
e executa apenas callbacks prontos.

```text
loop()
  |
  v
CooperativeScheduler::execute()
  |
  +-- blinkLed1 ... blinkLed6
  +-- scanButtons
  +-- sampleMetrics
  +-- serviceDisplays
  +-- printStatus
  +-- schedulerHeartbeat
```

Nenhuma tarefa possui pilha própria e nenhuma tarefa normal preempta outra.
Interrupções usadas internamente pelo core Arduino continuam existindo para
recursos como temporização e UART, mas não constituem a arquitetura da
aplicação.

<!-- section: layers -->
## Camadas

- **Aplicação (`sketch.ino`)**: inicialização, composição e lógica funcional.
- **Escalonamento (`cooperative_scheduler.h`)**: deadlines, chamada de callbacks,
  atraso, overrun e passagens.
- **Entradas (`button_debounce.h`)**: debounce e eventos de borda.
- **Instrumentação (`metrics.h`)**: APP BUSY, SRAM, PASS/s, MAX CALLBACK,
  MAX LATE e OVR.
- **Apresentação**: `display_activity.h`, `oled_status.h` e `tft_dashboard.h`.

<!-- section: blue-leds -->
## Independência dos seis LEDs

Os seis callbacks `blinkLed1` ... `blinkLed6` são deliberadamente separados.
Uma única tarefa atualizando todos os LEDs seria mais compacta, porém retiraria
do experimento a observação de seis entidades temporais independentes.

<!-- section: display-pipeline -->
## Pipeline visual

`serviceDisplays` não redesenha toda a interface. Ao surgir nova amostra, o
firmware cria `displaySnapshot` e distribui a atualização em etapas:

```text
0 APP BUSY graph
1 SRAM graph
2 TFT status row
3 TFT resource row
4 TFT timing row
5 OLED diagnostic
```

Somente depois dessas etapas a amostra é considerada exibida. Isso evita
misturar valores de amostras diferentes na mesma atualização visual.

<!-- section: event-console -->
## Console de eventos

Eventos são colocados em fila circular estática. Quando a fila está cheia, o
evento mais antigo é descartado. Não são usados `String`, `malloc` ou listas
dinâmicas.

<!-- section: fault-isolation -->
## Isolamento de falhas

OLED ausente não deve impedir LEDs, botões, escalonador, TFT ou serial. O serial
permanece o canal diagnóstico principal.

<!-- section: evolution-policy -->
## Política de evolução

A versão-base prioriza clareza, observabilidade e baixo uso de SRAM. Otimizações
agressivas permanecem separadas para permitir comparações futuras.
