<!-- doc-id: displays -->
<!-- language: PT -->
<!-- content-revision: 2 -->

# Subsistema de Displays

<!-- section: strategy -->
## Estratégia

A arquitetura fixa a alternativa A:

- **ILI9341**: interface visual principal;
- **SSD1306**: painel diagnóstico compacto.

<!-- BEGIN GENERATED: display-summary -->
| Display | Interface | Ligações canônicas | Geometria / temporização |
|---|---|---|---|
| ILI9341 | software SPI | D/C D9, CS D10, MOSI D11, SCK D13 | 240×320 nativo; rotação 1 -> 320×240 lógico |
| SSD1306 | I2C (hardware) | SDA A4, SCL A5 | 128×64; endereço 0x3C; atualização 1000 ms |
<!-- END GENERATED: display-summary -->

<!-- section: ili9341 -->
## ILI9341

A TFT segue o caminho de SPI por software resumido acima, preservando o pino de
MISO de hardware para o LED laranja de atividade.

Para compensar o custo de CPU, o firmware:

- não mantém framebuffer da TFT;
- não usa `fillScreen()` em operação normal;
- avança cada gráfico apenas uma coluna por amostra;
- divide a atualização em etapas;
- mantém cache dos campos textuais e não redesenha valores inalterados;
- limita o console a uma fila circular fixa.

<!-- section: ssd1306 -->
## SSD1306

O OLED usa a configuração de I2C de hardware resumida acima. A biblioteca
`SSD1306Ascii` evita reservar um framebuffer de 1024 bytes e mantém um painel
diagnóstico compacto.

<!-- section: visual-snapshot -->
## Snapshot visual

Uma amostra de métricas é copiada para `displaySnapshot`. Todas as etapas de um
mesmo ciclo utilizam essa cópia; amostras mais novas esperam o ciclo terminar.

<!-- section: display-activity-led -->
## LED laranja

O indicador de atividade fica HIGH quando o subsistema visual está
logicamente ocioso e LOW dentro de operações delimitadas por
`busyBegin()`/`busyEnd()`. Seu pino atual pertence a
`config/hardware.json`; é um indicador de software, não um analisador de
barramento.

<!-- section: builtin-led -->
## LED L

O pino de clock da TFT também aciona o LED `L` da placa; por isso, atividade
de clock pode ser visível no LED integrado. A relação de pinos atual é gerada a
partir da configuração canônica de hardware.

<!-- section: functional-priority -->
## Prioridade funcional

Se houver pressão de recursos, a prioridade é manter escalonador, botões, LEDs e
serial. A interface visual deve ser simplificada antes de comprometer essas
funções.
