# Relatório LaTeX

Esta pasta contém o relatório técnico da arquitetura-base do projeto
`arduino-uno-cooperative`.

## Estrutura

```text
report/
├── relatorio.tex
├── relatorio.pdf
├── build.ps1
├── README.md
└── figures/
    └── README.md
```

O relatório atual não depende de nenhuma figura externa; a pasta `figures/`
fica preparada para uma futura captura do circuito Wokwi.

## Compilação no PowerShell

A partir da pasta `report/`:

```powershell
.\build.ps1
```

O script tenta `latexmk -lualatex` e, se necessário, usa duas passagens de
`lualatex`.

Opções:

```powershell
.\build.ps1 -Clean
.\build.ps1 -KeepTemp
.\build.ps1 -Open
```

## TeXstudio

Abra `relatorio.tex`, selecione **LuaLaTeX** como compilador e compile duas
vezes. O arquivo já contém `% !TeX program = lualatex`.
