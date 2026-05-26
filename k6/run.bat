@echo off
:: ============================================================
::  run.bat — Script de ejecucion para CMD de Windows
::  Uso: run.bat [comando]
:: ============================================================
setlocal EnableDelayedExpansion

:: Activar colores ANSI en CMD (Windows 10+)
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

set "CYAN=[36m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "RED=[31m"
set "NC=[0m"

set "CMD_ARG=%~1"
if "%CMD_ARG%"==""        goto :show_help
if /i "%CMD_ARG%"=="help"    goto :show_help
if /i "%CMD_ARG%"=="up"      goto :cmd_up
if /i "%CMD_ARG%"=="rebuild" goto :cmd_rebuild
if /i "%CMD_ARG%"=="down"    goto :cmd_down
if /i "%CMD_ARG%"=="status"  goto :cmd_status
if /i "%CMD_ARG%"=="logs"    goto :cmd_logs
if /i "%CMD_ARG%"=="smoke"   goto :cmd_smoke
if /i "%CMD_ARG%"=="load"    goto :cmd_load
if /i "%CMD_ARG%"=="stress"  goto :cmd_stress
if /i "%CMD_ARG%"=="spike"   goto :cmd_spike
if /i "%CMD_ARG%"=="soak"    goto :cmd_soak
if /i "%CMD_ARG%"=="all"     goto :cmd_all
if /i "%CMD_ARG%"=="grafana" goto :cmd_grafana
if /i "%CMD_ARG%"=="clean"   goto :cmd_clean

echo %RED%  Error: Comando desconocido: %CMD_ARG%%NC%
goto :show_help

:: ============================================================
:show_help
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   SauceDemo K6 -- Comandos disponibles%NC%
echo %CYAN%================================================%NC%
echo.
echo   run.bat up          Levantar InfluxDB 2.x + Grafana (compila k6)
echo   run.bat rebuild     Recompilar imagen k6 desde cero (sin cache)
echo   run.bat down        Apagar todos los servicios
echo   run.bat status      Ver estado de los servicios
echo   run.bat logs        Ver logs en tiempo real
echo.
echo   run.bat smoke       Prueba de humo   (1 VU,   1 min)
echo   run.bat load        Prueba de carga  (30 VUs, 8 min)
echo   run.bat stress      Prueba de estres (100 VUs,12 min)
echo   run.bat spike       Prueba de pico   (200 VUs, 7 min)
echo   run.bat soak        Prueba resistencia (20 VUs,30 min)
echo   run.bat all         smoke + load + stress en secuencia
echo.
echo   run.bat grafana     Abrir Grafana en el navegador
echo   run.bat clean       Limpiar datos y volumenes
echo.
goto :eof

:: ============================================================
:cmd_up
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Levantando stack InfluxDB 2.x + Grafana%NC%
echo %CYAN%================================================%NC%

docker info >nul 2>&1
if errorlevel 1 (
    echo %RED%  ERR Docker no esta corriendo. Inicia Docker Desktop primero.%NC%
    goto :eof
)

:: Paso 1: Compilar imagen k6 con xk6-output-influxdb
:: La primera vez tarda ~3-5 min (descarga Go + compila el plugin)
:: Las siguientes veces usa cache de Docker → rapido
echo %BLUE%  --> Paso 1/2: Compilando imagen k6 con xk6-output-influxdb...%NC%
echo %YELLOW%  !   Primera vez puede tardar 3-5 minutos (compilando Go)%NC%
docker compose build k6
if errorlevel 1 (
    echo %RED%  ERR Error al compilar la imagen k6. Verifica Dockerfile.k6%NC%
    goto :eof
)
echo %GREEN%  OK  Imagen k6 compilada correctamente.%NC%

:: Paso 2: Levantar InfluxDB + Grafana
echo %BLUE%  --> Paso 2/2: Levantando InfluxDB 2.x + Grafana...%NC%
docker compose up -d influxdb grafana
if errorlevel 1 (
    echo %RED%  ERR Error al levantar los servicios.%NC%
    goto :eof
)

echo %BLUE%  --> Esperando 15 segundos para que InfluxDB 2.x inicialice...%NC%
ping -n 16 127.0.0.1 >nul 2>&1

echo.
echo %GREEN%  OK  InfluxDB 2.x  -^> http://localhost:8086%NC%
echo %GREEN%  OK              usuario: admin  /  clave: admin12345%NC%
echo %GREEN%  OK  Grafana       -^> http://localhost:3000%NC%
echo.
echo %YELLOW%  !   Abre Grafana: Dashboards -^> K6 Performance -^> SauceDemo%NC%
goto :eof

:: ============================================================
:cmd_rebuild
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Forzando recompilacion de imagen k6%NC%
echo %CYAN%================================================%NC%
echo %YELLOW%  !   Esto tarda 3-5 minutos (compila Go desde cero)%NC%
docker compose build --no-cache k6
if errorlevel 1 (
    echo %RED%  ERR Error al compilar. Revisa Dockerfile.k6%NC%
    goto :eof
)
echo %GREEN%  OK  Imagen k6 recompilada con xk6-output-influxdb%NC%
goto :eof

:: ============================================================
:cmd_down
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Apagando servicios%NC%
echo %CYAN%================================================%NC%
docker compose down
echo %GREEN%  OK  Servicios detenidos. Datos conservados en volumenes.%NC%
goto :eof

:: ============================================================
:cmd_status
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Estado de los servicios%NC%
echo %CYAN%================================================%NC%
docker compose ps
goto :eof

:: ============================================================
:cmd_logs
docker compose logs -f --tail=50
goto :eof

:: ============================================================
:cmd_smoke
call :run_test "tests/01_smoke_test.js" "smoke"
goto :eof

:cmd_load
call :run_test "tests/02_load_test.js" "load"
goto :eof

:cmd_stress
call :run_test "tests/03_stress_test.js" "stress"
goto :eof

:cmd_spike
call :run_test "tests/04_spike_test.js" "spike"
goto :eof

:cmd_soak
call :run_test "tests/05_soak_test.js" "soak"
goto :eof

:: ============================================================
:cmd_all
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Suite completa: smoke + load + stress%NC%
echo %CYAN%================================================%NC%

echo %BLUE%  --> Paso 1/3 Smoke test...%NC%
call :run_test "tests/01_smoke_test.js" "smoke"
if errorlevel 1 (
    echo %RED%  ERR Smoke test fallo. Abortando suite.%NC%
    goto :eof
)

echo.
echo %YELLOW%  !   Smoke OK -- ejecutando load test...%NC%
call :run_test "tests/02_load_test.js" "load"
if errorlevel 1 (
    echo %RED%  ERR Load test fallo.%NC%
    goto :eof
)

echo.
echo %YELLOW%  !   Load OK -- ejecutando stress test...%NC%
call :run_test "tests/03_stress_test.js" "stress"

echo.
echo %GREEN%  OK  Suite completa finalizada.%NC%
echo %GREEN%  OK  Ver resultados en: http://localhost:3000%NC%
goto :eof

:: ============================================================
:cmd_grafana
echo %BLUE%  --> Abriendo Grafana en el navegador...%NC%
start http://localhost:3000
goto :eof

:: ============================================================
:cmd_clean
echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Limpiando datos y volumenes%NC%
echo %CYAN%================================================%NC%
echo.
set /p "CONFIRM=Esto borrara TODOS los datos. Continuar? (s/N): "
if /i not "%CONFIRM%"=="s" (
    echo %YELLOW%  !   Operacion cancelada.%NC%
    goto :eof
)
docker compose down -v
if exist "results\*.json" del /q "results\*.json"
echo %GREEN%  OK  Stack y datos eliminados.%NC%
goto :eof

:: ============================================================
::  SUBRUTINA: run_test
::  %1 = archivo (ej: tests/01_smoke_test.js)
::  %2 = nombre  (ej: smoke)
:: ============================================================
:run_test
set "T_FILE=%~1"
set "T_NAME=%~2"

echo.
echo %CYAN%================================================%NC%
echo %CYAN%   Ejecutando: %T_NAME%%NC%
echo %CYAN%================================================%NC%

:: Crear carpeta results si no existe
:: FIX: usar 2>nul para evitar "Acceso denegado" si ya existe o hay permisos
if not exist "results\" (
    mkdir "results" 2>nul
    if errorlevel 1 (
        echo %YELLOW%  !   No se pudo crear carpeta results — usando directorio actual%NC%
    )
)

:: Generar timestamp para el archivo de resultado
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "DT=%%a"
set "TS=%DT:~0,8%_%DT:~8,6%"
set "RESULT=results\%T_NAME%_%TS%.json"

echo %BLUE%  --> Test   : %T_FILE%%NC%
echo %BLUE%  --> Grafana: http://localhost:3000%NC%
echo.

:: ── Ejecutar k6 con InfluxDB 1.8 (formato nativo, sin plugins) ──
:: FIX: --out como argumento CLI directo en lugar de K6_OUT env var
:: porque Docker ignora K6_OUT cuando hay conflicto con otros --out
docker compose run --rm ^
    k6 run ^
    --out influxdb=http://influxdb:8086/k6 ^
    --out json=/results/%T_NAME%_%TS%.json ^
    /scripts/%T_FILE%

:: Guardar exit code INMEDIATAMENTE (antes de cualquier otro comando)
set "EXIT_K6=%errorlevel%"

echo.

:: FIX: No usar call :subrutina dentro de if/else — inline directo
if "%EXIT_K6%"=="0" (
    echo %GREEN%  OK  Test PASO todos los umbrales.%NC%
    echo %GREEN%  OK  Resultado : %RESULT%%NC%
    echo %GREEN%  OK  Grafana   : http://localhost:3000%NC%
    exit /b 0
)

:: Si llega aqui el test fallo
echo %RED%  ERR Test FALLO -- umbrales superados ^(exit code: %EXIT_K6%^)%NC%
echo %YELLOW%  !   Revisa config/thresholds.js para ajustar umbrales%NC%
echo %BLUE%  --> Ver detalle en Grafana: http://localhost:3000%NC%
exit /b 1
