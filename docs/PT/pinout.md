<!-- doc-id: pinout -->
<!-- language: PT -->
<!-- content-revision: 2 -->

# Pinagem Oficial

<!-- BEGIN GENERATED: pin-map -->
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
| D11 | TFT MOSI — SPI por software |
| D12 | LED laranja de atividade dos displays |
| D13 | TFT SCK — SPI por software + LED L integrado |
| A0 | botão principal |
| A1 | diminuir intervalo |
| A2 | aumentar intervalo |
| A3 | LED amarelo de heartbeat do escalonador |
| A4 / SDA | OLED SDA |
| A5 / SCL | OLED SCL |
<!-- END GENERATED: pin-map -->

<!-- section: tft -->
## TFT

Os pinos de sinal canônicos são gerados no mapa acima. A TFT é somente de
escrita e usa SPI por software, preservando o pino de MISO de hardware para o
indicador de atividade dos displays.

<!-- section: display-activity-led -->
## LED laranja de atividade dos displays

Semântica lógica:

```text
HIGH -> subsistema de displays ocioso
LOW  -> operação instrumentada de display em andamento
```

Seu pino atual é gerado no mapa acima. O indicador não pretende reproduzir cada
transição elétrica dos barramentos.

<!-- section: builtin-led -->
## LED L integrado

O pino usado como SCK da TFT também aciona o LED `L` da placa; por isso,
atividade do clock do display pode aparecer nele. Esse efeito é esperado e o
pino atual é gerado acima.

<!-- section: oled -->
## OLED

Os pinos SDA/SCL canônicos são gerados acima. Endereço, frequência do bus e
alimentação pertencem a `config/hardware.json` e são resumidos em
[`displays.md`](displays.md).

<!-- section: buttons -->
## Botões

Os três botões da aplicação usam `INPUT_PULLUP` e conectam-se ao GND quando
pressionados. Seus pinos e funções atuais são gerados acima.

<!-- section: uart -->
## UART

Os pinos mostrados acima permanecem reservados exclusivamente para comunicação
serial.
