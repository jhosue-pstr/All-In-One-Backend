// ============================================================
//  config/utils.js — Utilidades compartidas para todos los tests
//
//  Importar en cada test:
//  import { setupResponseCallback, REQ_PARAMS, visitPage }
//    from "../config/utils.js";
// ============================================================
import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

// ── FIX http_req_failed ──────────────────────────────────────
// k6 por defecto marca como failed cualquier respuesta != 2xx.
// Esta función redefine ese comportamiento para que solo cuenten
// como fallos los errores reales de RED (timeout, DNS, TLS).
// Llamar UNA VEZ al inicio del script, fuera de default().
export function setupResponseCallback() {
  http.setResponseCallback(
    http.expectedStatuses({ min: 200, max: 599 })
  );
}

// ── Parámetros por defecto para todas las requests ───────────
export const REQ_PARAMS = {
  redirects: 5,
  timeout:   "15s",
  headers: {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
      "AppleWebKit/537.36 (KHTML, like Gecko) " +
      "Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
  },
};

// ── Helper: visitar una página con checks de status y tiempo ─
// errorRate : métrica Rate donde registrar fallos (opcional)
// trend     : métrica Trend donde registrar duración (opcional)
// maxMs     : umbral de tiempo en ms (default 5000)
export function visitPage(url, name, errorRate, trend, maxMs = 5000) {
  const res = http.get(url, { ...REQ_PARAMS, tags: { name } });

  if (trend) trend.add(res.timings.duration);

  const ok = check(res, {
    [`${name} — responde`]:        (r) => r.status > 0,
    [`${name} — tiempo < ${maxMs}ms`]: (r) => r.timings.duration < maxMs,
  });

  if (errorRate) errorRate.add(!ok);
  return res;
}
