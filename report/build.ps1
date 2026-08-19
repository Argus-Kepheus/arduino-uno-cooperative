param(
    [switch]$Clean,
    [switch]$KeepTemp,
    [switch]$Open
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

$Base = "relatorio"
$Tex  = "$Base.tex"
$Pdf  = "$Base.pdf"

$TempExtensions = @(
    "aux", "log", "out", "toc", "fls", "fdb_latexmk", "synctex.gz"
)

function Remove-Temps {
    foreach ($ext in $TempExtensions) {
        Get-ChildItem -Path $Here -Filter "$Base.$ext" -ErrorAction SilentlyContinue |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

if ($Clean) {
    Remove-Temps
    exit 0
}

if (-not (Test-Path $Tex)) {
    throw "Arquivo $Tex nao encontrado."
}

$Succeeded = $false

try {
    $latexmk = Get-Command latexmk -ErrorAction SilentlyContinue
    if ($latexmk) {
        & latexmk -lualatex -interaction=nonstopmode -halt-on-error $Tex
        if ($LASTEXITCODE -eq 0) { $Succeeded = $true }
    }

    if (-not $Succeeded) {
        $lualatex = Get-Command lualatex -ErrorAction SilentlyContinue
        if (-not $lualatex) { throw "lualatex nao encontrado." }
        & lualatex -interaction=nonstopmode -halt-on-error $Tex
        if ($LASTEXITCODE -ne 0) { throw "Primeira passagem lualatex falhou." }
        & lualatex -interaction=nonstopmode -halt-on-error $Tex
        if ($LASTEXITCODE -ne 0) { throw "Segunda passagem lualatex falhou." }
        $Succeeded = $true
    }
}
finally {
    if ($Succeeded -and -not $KeepTemp) { Remove-Temps }
}

if (-not $Succeeded -or -not (Test-Path $Pdf)) {
    throw "Compilacao nao produziu $Pdf."
}

if ($Open) { Start-Process $Pdf }
