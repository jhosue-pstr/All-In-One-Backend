# 🔐 ZAP Security Testing Suite — Windows + Docker Desktop
**Target:** `https://www.saucedemo.com/v1/`

---

## ✅ Requisitos

- **Docker Desktop** instalado y corriendo (ícono en la barra de tareas)
- Windows 10/11 con WSL2 habilitado (lo activa Docker Desktop automáticamente)

---

## 🚀 Inicio rápido

### Opción A — PowerShell (recomendado)

Abre PowerShell en la carpeta del proyecto:

```powershell
# Si es la primera vez, permitir scripts:
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Ejecutar el menu interactivo
.\run.ps1

# O directo al escaneo:
.\run.ps1 baseline
```

### Opción B — Símbolo del sistema (CMD)

```cmd
run.bat
```

### Opción C — Comandos Docker directos

```powershell
# Baseline scan
docker compose run --rm baseline

# Full scan
docker compose run --rm fullscan

# Ver reportes en el navegador
docker compose up viewer -d
# → Abre http://localhost:8090
```

---

## 📊 Tipos de escaneo

| Opción | Duración | Qué hace |
|--------|----------|----------|
| **Baseline** | ~2-3 min | Spider pasivo. No ataca. Seguro. **Empieza aquí.** |
| **Full Scan** | ~15-30 min | Spider + XSS, SQLi, CSRF, headers, etc. |
| **API Scan** | ~5-10 min | Escanea APIs REST por spec OpenAPI/Swagger |

---

## 📂 Reportes

Los reportes se guardan en la carpeta `reports\`:

```
reports\
├── baseline-report.html   ← abrir en Chrome/Edge
├── baseline-report.json
├── baseline-report.xml
├── fullscan-report.html
└── ...
```

Para abrirlos directamente:
```powershell
Start-Process reports\baseline-report.html
```

O con el visor integrado:
```powershell
.\run.ps1 viewer
# → http://localhost:8090
```

---

## 🎯 Cambiar la URL objetivo

Edita el archivo `.env`:
```
TARGET_URL=https://tu-app.com
```

Si tu app corre **localmente en Windows**, usa esta URL especial en lugar de `localhost`:
```
TARGET_URL=http://host.docker.internal:3000
```

> Docker Desktop en Windows no puede acceder a `localhost` del host directamente.
> `host.docker.internal` es el hostname especial que resuelve al host.

---

## 🗂️ Estructura del proyecto

```
zap-saucedemo\
├── docker-compose.yml     ← servicios ZAP
├── .env                   ← URL objetivo
├── run.ps1                ← script PowerShell (recomendado)
├── run.bat                ← script CMD alternativo
├── config\
│   ├── nginx.conf         ← visor de reportes
└── reports\               ← reportes generados aqui
```

---

## ❓ Solución de problemas

**"docker: command not found"**
→ Asegúrate de que Docker Desktop esté abierto (ícono en bandeja del sistema)

**"permission denied" al escribir reportes**
→ El `docker-compose.yml` ya incluye `user: root` para evitar esto en Windows

**No se genera el reporte HTML**
→ Verifica que la carpeta `reports\` exista. El script la crea automáticamente.

**La app local no es accesible desde ZAP**
→ Usa `host.docker.internal` en lugar de `localhost` en el `.env`
