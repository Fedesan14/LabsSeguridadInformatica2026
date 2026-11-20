# Arranque del swarm PTaaS en un solo comando: construye el sandbox, levanta el
# blanco (phantomcorp) y abre el panel web. Se puede correr desde cualquier lado:
# el script se ubica solo en la raíz del repo.
#   Arrancar:  .\entregas\labfinal\grupo03\ptaas\levantar.ps1
#   Bajar:     .\entregas\labfinal\grupo03\ptaas\levantar.ps1 -Down
param([switch]$Down)
$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$compose = @("compose", "-p", "cyberlab", "--project-directory", ".",
             "-f", "entorno/docker-compose.yml",
             "-f", "labs/labfinal-practico-integrador/entorno/target.compose.yml")

if ($Down) {
    docker @compose down
    exit $LASTEXITCODE
}

Write-Host "[1/3] Chequeando Docker..."
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker no responde. Abrí Docker Desktop y esperá a que diga 'Engine running'." -ForegroundColor Red
    exit 1
}

Write-Host "[2/3] Construyendo la imagen del sandbox (ptaas-runner)..."
docker build -t ptaas-runner -f entregas/labfinal/grupo03/ptaas/Dockerfile.runner entregas/labfinal/grupo03/ptaas
if ($LASTEXITCODE -ne 0) { Write-Host "Falló el build del sandbox." -ForegroundColor Red; exit 1 }

Write-Host "[3/3] Levantando el blanco (phantomcorp)..."
docker @compose up -d --build phantomcorp
if ($LASTEXITCODE -ne 0) { Write-Host "Falló el levantado del blanco." -ForegroundColor Red; exit 1 }

Write-Host "`nListo. Abriendo el panel en http://127.0.0.1:8765/  (Ctrl+C para cerrarlo)." -ForegroundColor Green
Write-Host "Para bajar el lab al terminar:  .\entregas\labfinal\grupo03\ptaas\levantar.ps1 -Down`n" -ForegroundColor DarkGray

python entregas/labfinal/grupo03/ptaas/panel.py
