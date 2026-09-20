<!-- doc-id: displays -->
<!-- language: PT -->
<!-- content-revision: 1 -->

# Subsistema de Displays

<!-- section: strategy -->
## Estratégia

A arquitetura fixa a alternativa A:

- **ILI9341**: interface visual principal;
- **SSD1306**: painel diagnóstico compacto.

<!-- section: ili9341 -->
## ILI9341

A TFT usa D9 (D/C), D10 (CS), D11 (MOSI) e D13 (SCK). A versão-base utiliza o
caminho de SPI por software da biblioteca Adafruit, preservando D12 para o LED
laranja.

Para compensar o custo de CPU, o firmware:

- não mantém framebuffer da TFT;
- não usa `fillScreen()` em operação normal;
- avança cada gráfico apenas uma coluna por amostra;
- divide a atualização em etapas;
- mantém cache dos campos textuais e não redesenha valores inalterados;
- limita o console a uma fila circular fixa.

<!-- section: ssd1306 -->
## SSD1306

O OLED usa A4/SDA e A5/SCL, endereço `0x3C`, por I2C de hardware. A biblioteca
`SSD1306Ascii` evita reservar 1024 bytes de framebuffer. O painel mostra apenas
estado diagnóstico resumido e é atualizado aproximadamente uma vez por segundo.

<!-- section: visual-snapshot -->
## Snapshot visual

Uma amostra de métricas é copiada para `displaySnapshot`. Todas as etapas de um
mesmo ciclo utilizam essa cópia; amostras mais novas esperam o ciclo terminar.

<!-- section: display-activity-led -->
## LED laranja

D12 fica HIGH quando o subsistema visual está logicamente ocioso e LOW dentro de
operações delimitadas por `busyBegin()`/`busyEnd()`. É um indicador de software,
não um analisador de barramento.

<!-- section: builtin-led -->
## LED L

D13 também aciona o LED `L` da placa; assim, atividade de clock da TFT pode ser
visível no LED integrado.

<!-- section: functional-priority -->
## Prioridade funcional

Se houver pressão de recursos, a prioridade é manter escalonador, botões, LEDs e
serial. A interface visual deve ser simplificada antes de comprometer essas
funções.
