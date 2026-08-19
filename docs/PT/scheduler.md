# Escalonador Cooperativo

## Modelo

Cada tarefa é um callback `void callback()`. O escalonador verifica o instante
de liberação, chama a função, mede sua duração e calcula a próxima liberação.
Não existem pilhas por tarefa nem preempção entre callbacks.

## Estrutura compacta

```cpp
struct Task {
    TaskCallback callback;
    TickMs nextRunMs;
    uint16_t periodMs;
};
```

A capacidade-base é exatamente 11 tarefas.

## Relógio modular de 16 bits

O escalonador utiliza os 16 bits inferiores de `millis()`. As comparações usam
diferença modular assinada. Essa técnica permite atravessar `65535 -> 0` sem
parar o sistema, desde que os intervalos permaneçam menores que 32768 ms e o
escalonador não fique impedido de executar por uma janela tão longa.

O maior período atual é 4000 ms.

## Taxa fixa

A próxima liberação é calculada a partir do instante planejado, e não do fim do
callback:

```text
next = scheduled + period
```

Isso evita deriva acumulativa.

## Overrun

Quando o callback termina tarde demais e uma ou mais liberações ficaram no
passado, o escalonador as descarta, contabiliza `OVR` e avança para uma liberação
futura. Não executa rajadas de catch-up.

## Mudança de período

Ao alterar o período dos LEDs, a posição relativa no ciclo atual é escalada
para o novo período. O objetivo é evitar que uma alteração intencional seja
interpretada como atraso artificial.

## Instrumentação

O escalonador registra:

- tempo total de callbacks por janela;
- número de passagens;
- maior callback;
- maior atraso;
- quantidade de liberações perdidas.

## Ordem de registro

Os IDs 0 a 5 pertencem obrigatoriamente a `blinkLed1` ... `blinkLed6`. Essa
propriedade elimina a necessidade de uma tabela extra com IDs das seis tarefas.

## Regras dos callbacks

Callbacks devem retornar rapidamente, não chamar `delay()`, não esperar
ativamente e dividir operações longas em etapas cooperativas.
