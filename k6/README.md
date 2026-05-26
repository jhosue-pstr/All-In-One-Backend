# 🔥 SauceDemo — K6 + InfluxDB + Grafana

Stack completo de pruebas de rendimiento con visualización en tiempo real.

```
┌─────────┐   métricas    ┌───────────┐   consultas   ┌─────────┐
│   k6    │ ────────────► │ InfluxDB  │ ◄───────────  │ Grafana │
│(runner) │               │  (TSDB)   │               │(charts) │
└─────────┘               └───────────┘               └─────────┘
```

## 🚀 Inicio rápido

### Windows (PowerShell)
```powershell
.\run.ps1 up      # Levantar InfluxDB + Grafana
.\run.ps1 smoke   # Ejecutar prueba de humo
.\run.ps1 grafana # Abrir dashboard en el navegador
```

### Linux / Mac
```bash
chmod +x run.sh
./run.sh up
./run.sh smoke
./run.sh grafana
```

## 🧪 Pruebas disponibles
```powershell
.\run.ps1 smoke    # 1 VU,   1 min  — sistema vivo?
.\run.ps1 load     # 30 VUs, 8 min  — carga normal
.\run.ps1 stress   # 100 VUs,12 min — punto de quiebre
.\run.ps1 spike    # 200 VUs, 7 min — pico sudito
.\run.ps1 soak     # 20 VUs, 30 min — resistencia
.\run.ps1 all      # smoke + load + stress en secuencia
```

## 📊 Grafana Dashboard
Acceder en http://localhost:3000
- Dashboard auto-cargado: Dashboards → K6 Performance → SauceDemo
- Incluye: RPS, VUs, error rate, p50/p90/p95/p99, por endpoint

## 🧹 Limpieza
```powershell
.\run.ps1 down   # Apagar (conserva datos)
.\run.ps1 clean  # Apagar y borrar todo
```
