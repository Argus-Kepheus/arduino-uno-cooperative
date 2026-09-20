<!-- doc-id: pinout -->
<!-- language: PT -->
<!-- content-revision: 1 -->

# Pinagem Oficial

| Pino | Função |
|---|---|
| D0 / RX | recepção serial |
| D1 / TX | transmissão serial |
| D2 | LED azul 1 |
| D3 | LED azul 2 |
| D4 | LED azul 3 |
| D5 | LED azul 4 |
| D6 | LED azul 5 |
| D7 | LED azul 6 |
| D8 | LED verde |
| D9 | TFT D/C |
| D10 | TFT CS |
| D11 | TFT MOSI - SPI por software |
| D12 | LED laranja - display idle/activity |
| D13 | TFT SCK - SPI por software + LED `L` integrado |
| A0 | botão principal |
| A1 | diminuir intervalo |
| A2 | aumentar intervalo |
| A3 | LED amarelo - scheduler heartbeat |
| A4 / SDA | OLED SDA |
| A5 / SCL | OLED SCL |

<!-- section: tft -->
## TFT

```text
D9  -> D/C
D10 -> CS
D11 -> MOSI
D13 -> SCK
5V  -> VCC
GND -> GND
```

A TFT é somente de escrita. O projeto-base usa SPI por software para que D12
permaneça GPIO normal.

<!-- section: display-activity-led -->
## LED laranja em D12

Semântica lógica:

```text
HIGH -> subsistema de displays ocioso
LOW  -> operação instrumentada de display em andamento
```

O indicador não pretende mostrar cada transição elétrica dos barramentos.

<!-- section: builtin-led -->
## LED L em D13

Como D13 também é o clock da TFT, o LED `L` integrado pode apresentar atividade
durante atualizações da ILI9341. Esse efeito é esperado.

<!-- section: oled -->
## OLED

```text
A4 -> SDA
A5 -> SCL
5V -> VCC
GND -> GND
endereço -> 0x3C
```

A4/A5 utilizam o periférico I2C/TWI de hardware.

<!-- section: buttons -->
## Botões

A0, A1 e A2 utilizam `INPUT_PULLUP` e são conectados ao GND quando pressionados.

<!-- section: uart -->
## UART

D0 e D1 permanecem exclusivamente reservados para comunicação serial.
