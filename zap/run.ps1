param([string]$Action = "menu")

$TARGET = "https://www.saucedemo.com/v1/"
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^TARGET_URL=(.+)$") { $TARGET = $Matches[1].Trim() }
    }
}

# Carpeta reports con ruta absoluta — clave para Docker Desktop en Windows
$ReportsPath = Join-Path (Resolve-Path ".").Path "reports"
if (-not (Test-Path $ReportsPath)) { New-Item -ItemType Directory -Path $ReportsPath | Out-Null }

# Exportar para docker-compose (named volume bind)
$env:REPORTS_PATH = $ReportsPath

try { docker --version | Out-Null } catch {
    Write-Host "[ERROR] Docker no esta corriendo." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

function Open-Report($filename) {
    $rpt = Join-Path $ReportsPath $filename
    if (Test-Path $rpt) {
        Start-Process $rpt
    } else {
        Write-Host "  Reporte no encontrado: $rpt" -ForegroundColor Yellow
    }
}

function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "  =====================================================" -ForegroundColor Cyan
    Write-Host "   ZAP Security Testing Suite" -ForegroundColor Cyan
    Write-Host "   Target : $TARGET" -ForegroundColor Yellow
    Write-Host "   Reports: $ReportsPath" -ForegroundColor Gray
    Write-Host "  =====================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Run-Baseline {
    Write-Host ""
    Write-Host "  [*] Iniciando BASELINE SCAN..." -ForegroundColor Cyan
    Write-Host "      Target   : $TARGET"
    Write-Host "      Duracion : ~2-3 minutos"
    Write-Host ""
    docker compose run --rm -e "TARGET_URL=$TARGET" baseline
    Write-Host ""
    Write-Host "  [OK] Completado." -ForegroundColor Green
    $r = Read-Host "  Abrir reporte? (s/N)"
    if ($r -eq "s" -or $r -eq "S") { Open-Report "baseline-report.html" }
}

function Run-Full {
    Write-Host ""
    Write-Host "  [!] ADVERTENCIA: ejecuta ataques activos." -ForegroundColor Yellow
    $r = Read-Host "  Confirmas permiso para escanear $TARGET`? (s/N)"
    if ($r -ne "s" -and $r -ne "S") { Write-Host "  Cancelado."; return }
    Write-Host ""
    Write-Host "  [*] Iniciando FULL SCAN (~15-30 min)..." -ForegroundColor Cyan
    Write-Host ""
    docker compose run --rm -e "TARGET_URL=$TARGET" fullscan
    Write-Host ""
    Write-Host "  [OK] Completado." -ForegroundColor Green
    $r = Read-Host "  Abrir reporte? (s/N)"
    if ($r -eq "s" -or $r -eq "S") { Open-Report "fullscan-report.html" }
}

function Run-Api {
    Write-Host ""
    Write-Host "  [*] Iniciando API SCAN..." -ForegroundColor Cyan
    Write-Host ""
    docker compose run --rm -e "TARGET_URL=$TARGET" apiscan
    Write-Host ""
    Write-Host "  [OK] Completado." -ForegroundColor Green
    $r = Read-Host "  Abrir reporte? (s/N)"
    if ($r -eq "s" -or $r -eq "S") { Open-Report "apiscan-report.html" }
}

function Run-Tester {
    Write-Host ""
    Write-Host "  [*] Iniciando PAYLOAD TESTER..." -ForegroundColor Magenta
    Write-Host "      Probando: SQL Injection, XSS, Command Injection, chars especiales"
    Write-Host "      Reports : $ReportsPath"
    Write-Host ""
    docker compose run --rm tester
    Write-Host ""
    Write-Host "  [OK] Tester completado." -ForegroundColor Green
    $r = Read-Host "  Abrir reporte? (s/N)"
    if ($r -eq "s" -or $r -eq "S") { Open-Report "payload-report.html" }
}

function Start-Viewer {
    Write-Host ""
    Write-Host "  [*] Iniciando visor de reportes..." -ForegroundColor Cyan
    docker compose up viewer -d
    Start-Sleep 2
    Start-Process "http://localhost:8090"
    Write-Host "  [OK] Abierto en http://localhost:8090" -ForegroundColor Green
    Write-Host "       Para detener: docker compose down"
}

function Show-Reports {
    Write-Host ""
    Write-Host "  Reportes en $ReportsPath :" -ForegroundColor Cyan
    Write-Host ""
    $files = Get-ChildItem $ReportsPath -ErrorAction SilentlyContinue
    if ($files) {
        $files | Format-Table Name, @{L="KB";E={"{0:N0}" -f ($_.Length/1KB)}}, LastWriteTime -AutoSize
    } else {
        Write-Host "  No hay reportes aun." -ForegroundColor Yellow
    }
}

function Show-Menu {
    Show-Banner
    Write-Host "  Selecciona una opcion:" -ForegroundColor White
    Write-Host ""
    Write-Host "   1 - Baseline Scan   (pasivo, ~2-3 min)   <- RECOMENDADO" -ForegroundColor Green
    Write-Host "   2 - Full Scan       (activo, ~15-30 min)" -ForegroundColor Yellow
    Write-Host "   3 - API Scan        (REST/OpenAPI)" -ForegroundColor Cyan
    Write-Host "   4 - Payload Tester  (SQLi, XSS, chars especiales)" -ForegroundColor Magenta
    Write-Host "   5 - Ver reportes    (localhost:8090)" -ForegroundColor Cyan
    Write-Host "   6 - Listar reportes"
    Write-Host "   7 - Salir"
    Write-Host ""
    $choice = Read-Host "  Opcion"
    switch ($choice) {
        "1" { Run-Baseline }
        "2" { Run-Full }
        "3" { Run-Api }
        "4" { Run-Tester }
        "5" { Start-Viewer }
        "6" { Show-Reports }
        "7" { exit 0 }
        default { Write-Host "  Opcion invalida." -ForegroundColor Red; Start-Sleep 1; Show-Menu }
    }
}

Show-Banner
switch ($Action.ToLower()) {
    "baseline" { Run-Baseline }
    "full"     { Run-Full }
    "api"      { Run-Api }
    "tester"   { Run-Tester }
    "viewer"   { Start-Viewer }
    "reports"  { Show-Reports }
    default    { Show-Menu }
}

Write-Host ""
Read-Host "Presiona Enter para salir"
