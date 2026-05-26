# ============================================================
#  run.ps1 — Script de ejecución para Windows PowerShell
#  Uso: .\run.ps1 smoke | load | stress | spike | soak
# ============================================================

param([string]$Command = "help")

function Header($msg)  { Write-Host "`n══════════════════════════════════════" -ForegroundColor Cyan; Write-Host "  $msg" -ForegroundColor Cyan; Write-Host "══════════════════════════════════════" -ForegroundColor Cyan }
function Ok($msg)      { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Warn($msg)    { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Info($msg)    { Write-Host "  ➤ $msg" -ForegroundColor Blue }

function Show-Usage {
  Header "SauceDemo K6 — Comandos disponibles"
  Write-Host ""
  Write-Host "  Infraestructura:"
  Write-Host "    .\run.ps1 up         Levantar InfluxDB + Grafana"
  Write-Host "    .\run.ps1 down       Apagar todos los servicios"
  Write-Host "    .\run.ps1 status     Ver estado de los servicios"
  Write-Host ""
  Write-Host "  Pruebas:"
  Write-Host "    .\run.ps1 smoke      Prueba de humo   (1 VU, 1 min)"
  Write-Host "    .\run.ps1 load       Prueba de carga  (30 VUs, 8 min)"
  Write-Host "    .\run.ps1 stress     Prueba de estres (100 VUs, 12 min)"
  Write-Host "    .\run.ps1 spike      Prueba de pico   (200 VUs, 7 min)"
  Write-Host "    .\run.ps1 soak       Prueba resistencia (20 VUs, 30 min)"
  Write-Host "    .\run.ps1 all        Ejecutar smoke + load + stress"
  Write-Host ""
  Write-Host "  Otros:"
  Write-Host "    .\run.ps1 grafana    Abrir Grafana en el navegador"
  Write-Host "    .\run.ps1 clean      Limpiar datos y volumenes"
}

function Start-Stack {
  Header "Levantando stack InfluxDB + Grafana"
  docker compose up -d influxdb grafana
  Start-Sleep 8
  Ok "InfluxDB  -> http://localhost:8086"
  Ok "Grafana   -> http://localhost:3000"
  Warn "Abre Grafana: Dashboards -> K6 Performance -> SauceDemo"
}

function Run-Test($testFile, $testName) {
  Header "Ejecutando: $testName"
  Info "Test: $testFile"
  Info "Metricas en tiempo real -> http://localhost:3000"

  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $resultFile = "results/${testName}_${timestamp}.json"

  docker compose run --rm `
    -e K6_OUT="influxdb=http://influxdb:8086/k6" `
    k6 run `
    --out "json=/results/${testName}_${timestamp}.json" `
    "/scripts/$testFile"

  Ok "Test completado. Resultado: $resultFile"
  Ok "Ver metricas en: http://localhost:3000"
}

switch ($Command) {
  "up"      { Start-Stack }
  "down"    { Header "Apagando servicios"; docker compose down; Ok "Servicios detenidos." }
  "status"  { docker compose ps }
  "logs"    { docker compose logs -f --tail=50 }
  "smoke"   { Run-Test "tests/01_smoke_test.js"  "smoke"  }
  "load"    { Run-Test "tests/02_load_test.js"   "load"   }
  "stress"  { Run-Test "tests/03_stress_test.js" "stress" }
  "spike"   { Run-Test "tests/04_spike_test.js"  "spike"  }
  "soak"    { Run-Test "tests/05_soak_test.js"   "soak"   }
  "all"     {
    Run-Test "tests/01_smoke_test.js"  "smoke"
    Run-Test "tests/02_load_test.js"   "load"
    Run-Test "tests/03_stress_test.js" "stress"
    Ok "Suite completa finalizada. Ver: http://localhost:3000"
  }
  "grafana" { Start-Process "http://localhost:3000" }
  "clean"   { docker compose down -v; Remove-Item results/*.json -ErrorAction SilentlyContinue; Ok "Limpieza completada." }
  default   { Show-Usage }
}
