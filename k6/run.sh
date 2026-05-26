#!/bin/bash
# ============================================================
#  run.sh — Script de ejecución conveniente
#  Uso: ./run.sh [smoke|load|stress|spike|soak] [opciones]
# ============================================================

set -e

# ── Colores ─────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

header() { echo -e "\n${CYAN}════════════════════════════════════════${NC}"; echo -e "${CYAN}  $1${NC}"; echo -e "${CYAN}════════════════════════════════════════${NC}"; }
ok()     { echo -e "${GREEN}  ✓ $1${NC}"; }
warn()   { echo -e "${YELLOW}  ⚠ $1${NC}"; }
err()    { echo -e "${RED}  ✗ $1${NC}"; }
info()   { echo -e "${BLUE}  ➤ $1${NC}"; }

# ── Comandos disponibles ─────────────────────────────────────
usage() {
  header "SauceDemo K6 — Comandos disponibles"
  echo ""
  echo "  Infraestructura:"
  echo "    ./run.sh up         Levantar InfluxDB + Grafana"
  echo "    ./run.sh down       Apagar todos los servicios"
  echo "    ./run.sh status     Ver estado de los servicios"
  echo "    ./run.sh logs       Ver logs en tiempo real"
  echo ""
  echo "  Pruebas:"
  echo "    ./run.sh smoke      🔥 Prueba de humo   (1 VU, 1 min)"
  echo "    ./run.sh load       📊 Prueba de carga  (30 VUs, 8 min)"
  echo "    ./run.sh stress     💥 Prueba de estrés (100 VUs, 12 min)"
  echo "    ./run.sh spike      ⚡ Prueba de pico   (200 VUs, 7 min)"
  echo "    ./run.sh soak       🏊 Prueba resistencia (20 VUs, 30 min)"
  echo "    ./run.sh all        Ejecutar smoke + load + stress en secuencia"
  echo ""
  echo "  Reportes:"
  echo "    ./run.sh grafana    Abrir Grafana en el navegador"
  echo "    ./run.sh clean      Limpiar datos y volúmenes"
  echo ""
}

# ── Levantar stack ───────────────────────────────────────────
cmd_up() {
  header "Levantando stack InfluxDB + Grafana"
  docker compose up -d influxdb grafana
  echo ""
  info "Esperando que los servicios estén listos..."
  sleep 8
  ok "InfluxDB  → http://localhost:8086"
  ok "Grafana   → http://localhost:3000"
  echo ""
  warn "Abre Grafana y ve a: Dashboards → K6 Performance → SauceDemo"
}

# ── Ejecutar test ────────────────────────────────────────────
run_test() {
  local test_file=$1
  local test_name=$2
  local test_emoji=$3

  header "$test_emoji Ejecutando: $test_name"

  # Verificar que InfluxDB está corriendo
  if ! docker compose ps influxdb | grep -q "running\|Up"; then
    warn "InfluxDB no está corriendo. Levantando stack primero..."
    cmd_up
  fi

  info "Test: $test_file"
  info "Métricas → http://localhost:3000"
  echo ""

  # Guardar resultado JSON
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local result_file="results/${test_name}_${timestamp}.json"

  docker compose run --rm \
    -e K6_OUT="influxdb=http://influxdb:8086/k6" \
    k6 run \
    --out "json=/results/${test_name}_${timestamp}.json" \
    "/scripts/$test_file"

  echo ""
  ok "Test completado. Resultado: $result_file"
  ok "Ver métricas en: http://localhost:3000"
}

# ── Comandos principales ─────────────────────────────────────
case "${1:-help}" in

  up)     cmd_up ;;

  down)
    header "Apagando servicios"
    docker compose down
    ok "Servicios detenidos. Los datos se conservan en los volúmenes."
    ;;

  status)
    header "Estado de los servicios"
    docker compose ps
    ;;

  logs)
    docker compose logs -f --tail=50
    ;;

  smoke)  run_test "tests/01_smoke_test.js"  "smoke"  "🔥" ;;
  load)   run_test "tests/02_load_test.js"   "load"   "📊" ;;
  stress) run_test "tests/03_stress_test.js" "stress" "💥" ;;
  spike)  run_test "tests/04_spike_test.js"  "spike"  "⚡" ;;
  soak)   run_test "tests/05_soak_test.js"   "soak"   "🏊" ;;

  all)
    header "Ejecutando suite completa: smoke + load + stress"
    run_test "tests/01_smoke_test.js"  "smoke"  "🔥"
    echo ""
    warn "Smoke OK → ejecutando load test..."
    run_test "tests/02_load_test.js"   "load"   "📊"
    echo ""
    warn "Load OK → ejecutando stress test..."
    run_test "tests/03_stress_test.js" "stress" "💥"
    echo ""
    ok "Suite completa finalizada."
    ok "Ver todos los resultados en: http://localhost:3000"
    ;;

  grafana)
    info "Abriendo Grafana en el navegador..."
    if command -v xdg-open &>/dev/null; then xdg-open "http://localhost:3000"
    elif command -v open &>/dev/null; then open "http://localhost:3000"
    else echo "Abre manualmente: http://localhost:3000"; fi
    ;;

  clean)
    header "Limpiando datos y volúmenes"
    docker compose down -v
    rm -rf results/*.json
    ok "Stack y datos eliminados."
    ;;

  help|*) usage ;;
esac
