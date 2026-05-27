@echo off
chcp 65001 >nul
echo ============================================
echo  All-In-One Backend - Setup Rapido
echo ============================================
echo.
echo [1/5] Creando red Docker (si no existe)...
docker network create app-network 2>nul && echo  Red creada! || echo  Red ya existe.
echo.
echo [2/5] Construyendo all-in-one-backend...
docker build -t all-in-one-backend:latest .
echo.
echo [3/5] Construyendo k6-tests...
docker build -t k6-tests:latest -f Dockerfile.k6-tests .
echo.
echo [4/5] Construyendo zap-tester...
docker build -t zap-tester:latest -f zap/Dockerfile ./zap
echo.
echo [5/5] Construyendo grafana-custom...
docker build -t grafana-custom:latest -f Dockerfile.grafana .
echo.
echo ============================================
echo  LISTOOO! Ya puedes correr:
echo ============================================
echo.
echo  1. Levantar infraestructura:
echo     docker-compose -p k6 -f docker-compose.k6.yml up -d influxdb grafana
echo.
echo  2. Correr test k6 (1 solo test):
echo     docker run --rm --add-host host.docker.internal:host-gateway ^
echo       -e K6_OUT=influxdb=http://host.docker.internal:8086/k6 ^
echo       -e BASE_URL=http://host.docker.internal:8000 ^
echo       k6-tests:latest run /scripts/tests/01_smoke_test.js
echo.
echo  3. Correr ZAP scans:
echo     docker-compose -p zap -f docker-compose.zap.yml run --rm baseline ^
echo       || true
echo.
echo  4. Ver reportes:
echo     .\zap\reportes\payload-report.html
echo.
echo  5. Grafana: http://localhost:3000
echo.
echo  NOTA: Asegurate que tu backend este corriendo
echo  y expuesto en localhost:8000 antes de correr
echo  los tests.
echo ============================================
pause
