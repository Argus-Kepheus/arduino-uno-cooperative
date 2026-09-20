<!-- doc-id: scheduler -->
<!-- language: PT -->
<!-- content-revision: 2 -->

# Escalonador Cooperativo

<!-- section: model -->
## Modelo

Cada tarefa é um callback `void callback()`. O escalonador verifica o instante
de liberação, chama a função, mede sua duração e calcula a próxima liberação.
Não existem pilhas por tarefa nem preempção entre callbacks.

<!-- section: compact-descriptor -->
## Estrutura compacta

```cpp
struct Task {
    TaskCallback callback;
    TickMs nextRunMs;
    uint16_t periodMs;
};
```

<!-- BEGIN GENERATED: scheduler-summary -->
| Contrato | Valor canônico |
|---|---|
| Capacidade | 11 |
| Tick | uint16_t / 16 bit |
| Faixa modular | 65536 ms |
| Meia-faixa assinada | 32768 ms |
| Maior período configurado | 4000 ms |
| Política de escalonamento | fixed-rate |
| Política de liberações perdidas | skip missed releases; do not execute catch-up bursts |
<!-- END GENERATED: scheduler-summary -->

<!-- section: modular-clock -->
## Relógio modular de 16 bits

O escalonador usa os bits inferiores de `millis()` representados pelo
contrato de tick gerado. As comparações usam diferença modular assinada, o que
permite atravessar o rollover sem interromper o sistema enquanto a regra de
meia-faixa resumida acima for respeitada.

<!-- section: fixed-rate -->
## Taxa fixa

A próxima liberação é calculada a partir do instante planejado, e não do fim do
callback:

```text
next = scheduled + period
```

Isso evita deriva acumulativa.

<!-- section: overrun-policy -->
## Overrun

Quando o callback termina tarde demais e uma ou mais liberações ficaram no
passado, o escalonador as descarta, contabiliza `OVR` e avança para uma liberação
futura. Não executa rajadas de catch-up.

<!-- section: period-changes -->
## Mudança de período

Ao alterar o período dos LEDs, a posição relativa no ciclo atual é escalada
para o novo período. O objetivo é evitar que uma alteração intencional seja
interpretada como atraso artificial.

<!-- section: instrumentation -->
## Instrumentação

O escalonador registra:

- tempo total de callbacks por janela;
- número de passagens;
- maior callback;
- maior atraso;
- quantidade de liberações perdidas.

<!-- section: registration-order -->
## Ordem de registro

<!-- BEGIN GENERATED: registration-order -->
| ID da tarefa | Callback |
|---:|---|
| 0 | blinkLed1 |
| 1 | blinkLed2 |
| 2 | blinkLed3 |
| 3 | blinkLed4 |
| 4 | blinkLed5 |
| 5 | blinkLed6 |
| 6 | scanButtons |
| 7 | sampleMetrics |
| 8 | serviceDisplays |
| 9 | printStatus |
| 10 | schedulerHeartbeat |
<!-- END GENERATED: registration-order -->

A faixa inicial de tarefas dos LEDs é deliberadamente aritmética, eliminando a
necessidade de uma tabela separada de IDs.

<!-- section: callback-rules -->
## Regras dos callbacks

Callbacks devem retornar rapidamente, não chamar `delay()`, não esperar
ativamente e dividir operações longas em etapas cooperativas.
