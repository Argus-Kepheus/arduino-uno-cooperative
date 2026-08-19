# Checklist de Validação

## Compilação e inicialização

- [ ] Compila para Arduino Uno R3 no Wokwi web.
- [ ] Todas as dependências de `libraries.txt` são resolvidas.
- [ ] Uso de flash e SRAM estática é registrado.
- [ ] Serial abre em 115200 baud.
- [ ] São registradas 11 tarefas.
- [ ] TFT e OLED inicializam.
- [ ] LED amarelo apresenta heartbeat.
- [ ] LED laranja retorna a HIGH após inicialização.

## LEDs azuis

- [ ] LEDs 1 a 6 piscam.
- [ ] Cada um permanece associado a callback próprio.
- [ ] Intervalo inicial é 500 ms.
- [ ] Funcionam em 125, 250, 500, 1000, 2000 e 4000 ms.
- [ ] Limites inferior e superior são respeitados.

## Botões

- [ ] Botão principal controla o LED verde após debounce.
- [ ] Pressão e liberação geram eventos únicos.
- [ ] Botões de intervalo geram uma mudança por pressão.
- [ ] Manter botão de intervalo pressionado não repete ação.
- [ ] Não existe `delay()` no debounce.

## Escalonador

- [ ] Heartbeat em A3 permanece visível.
- [ ] `PASS/s` é atualizado.
- [ ] `MAX CALLBACK` é atualizado.
- [ ] `MAX LATE` é atualizado.
- [ ] `OVR` é observável.
- [ ] O sistema atravessa `65535 ms -> 0 ms` sem parar ou disparar tarefas em rajada.

## TFT

- [ ] Usa D9/D10/D11/D13 em SPI por software.
- [ ] Exibe os dois gráficos.
- [ ] Exibe intervalo, botão, BUSY, RAM, PASS, CBMAX, LATE, OVR e RAM LOW.
- [ ] Console circular funciona.
- [ ] Valores inalterados não são continuamente redesenhados.
- [ ] Não há `fillScreen()` durante operação normal.

## OLED

- [ ] Usa A4/SDA e A5/SCL.
- [ ] Endereço é `0x3C`.
- [ ] Exibe resumo diagnóstico.
- [ ] Atualiza aproximadamente a 1 Hz.
- [ ] Ausência do OLED não paralisa a aplicação.

## Indicadores

- [ ] D12 aciona o LED laranja.
- [ ] Laranja HIGH = display idle, LOW = operação instrumentada.
- [ ] A3 aciona o heartbeat amarelo.
- [ ] LED `L` em D13 pode refletir clock da TFT sem ser interpretado como erro.

## SRAM

Registrar:

```text
SRAM estática compilada:
SRAM FREE inicial:
RAM LOW:
```

- [ ] RAM LOW permanece >= 400 bytes.
- [ ] Preferencialmente RAM LOW permanece >= 512 bytes.
- [ ] Não há queda progressiva inexplicada.

## Estresse integrado

- [ ] Intervalo de 125 ms com TFT, OLED e serial ativos.
- [ ] Pressionamentos rápidos dos três botões.
- [ ] Mudanças repetidas 125 <-> 4000 ms.
- [ ] Console recebe eventos suficientes para circular.
- [ ] Execução por pelo menos 15 minutos sem reset ou travamento.
- [ ] Serial permanece funcional durante carga gráfica.
- [ ] Heartbeat permanece contínuo.

## Registro de resultado

Data:

Versão/commit:

Wokwi URL:

Flash usada:

SRAM estática:

RAM LOW:

MAX CALLBACK:

MAX LATE:

OVR:

Observações:
