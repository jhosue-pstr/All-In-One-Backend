import http          from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate, Counter } from "k6/metrics";
import { BASE_URL, ENDPOINTS } from "../config/thresholds.js";

http.setResponseCallback(http.expectedStatuses(
  { min: 200, max: 599 }
));

const homeDuration       = new Trend("home_duration",       true);
const healthDuration     = new Trend("health_duration",     true);
const modulosDuration    = new Trend("modulos_duration",    true);
const sitiosDuration     = new Trend("sitios_duration",     true);
const plantillasDuration = new Trend("plantillas_duration", true);
const errorRate          = new Rate("error_rate");
const totalRequests      = new Counter("total_requests");

export const options = {
  scenarios: {
    smoke: {
      executor: "constant-vus",
      vus:      1,
      duration: "1m",
    },
  },
  thresholds: {
    http_req_duration:  ["p(95)<3000", "p(99)<5000"],
    http_req_failed:    ["rate<0.01"],
    checks:             ["rate>0.90"],
    error_rate:         ["rate<0.10"],
    home_duration:       ["p(95)<3000"],
    health_duration:     ["p(95)<2000"],
    modulos_duration:    ["p(95)<3000"],
    sitios_duration:     ["p(95)<3000"],
    plantillas_duration: ["p(95)<3000"],
  },
};

function visitPage(url, name, trend, maxMs = 3000) {
  const res = http.get(url, {
    redirects: 5,
    timeout:   "10s",
    tags:      { name }
  });

  if (trend) trend.add(res.timings.duration);
  totalRequests.add(1);

  const ok = check(res, {
    [`${name} — responde`]:    (r) => r.status > 0,
    [`${name} — tiempo < ${maxMs}ms`]: (r) => r.timings.duration < maxMs,
  });
  errorRate.add(!ok);

  return res;
}

export default function () {
  visitPage(`${BASE_URL}${ENDPOINTS.home.path}`,    "GET_home",     homeDuration);
  sleep(1);
  visitPage(`${BASE_URL}${ENDPOINTS.health.path}`,  "GET_health",   healthDuration);
  sleep(1);
  visitPage(`${BASE_URL}${ENDPOINTS.modulos.path}`, "GET_modulos",  modulosDuration);
  sleep(1);
  visitPage(`${BASE_URL}${ENDPOINTS.sitios.path}`,  "GET_sitios",   sitiosDuration);
  sleep(1);
  visitPage(`${BASE_URL}${ENDPOINTS.plantillas.path}`, "GET_plantillas", plantillasDuration);
  sleep(1);
}

export function handleSummary(data) {
  const passed  = data.metrics.checks?.values?.passes          || 0;
  const failed  = data.metrics.checks?.values?.fails           || 0;
  const total   = passed + failed;
  const pct     = total > 0 ? ((passed / total) * 100).toFixed(1) : 0;
  const failPct = ((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(1);
  const errPct  = ((data.metrics.error_rate?.values?.rate      || 0) * 100).toFixed(1);
  const reqs    = data.metrics.total_requests?.values?.count   || 0;
  const pHome   = data.metrics.home_duration?.values?.["p(95)"]?.toFixed(0)       || "N/A";
  const pHealth = data.metrics.health_duration?.values?.["p(95)"]?.toFixed(0)     || "N/A";
  const pModules= data.metrics.modulos_duration?.values?.["p(95)"]?.toFixed(0)    || "N/A";

  console.log("================================================");
  console.log("  SMOKE TEST — RESUMEN");
  console.log("================================================");
  console.log(`  Checks pasados    : ${passed}/${total} (${pct}%)`);
  console.log(`  Tasa error checks : ${errPct}%`);
  console.log(`  http_req_failed   : ${failPct}%`);
  console.log(`  Requests total    : ${reqs}`);
  console.log(`  Home       p95    : ${pHome} ms`);
  console.log(`  Health     p95    : ${pHealth} ms`);
  console.log(`  Modulos    p95    : ${pModules} ms`);
  console.log("================================================");
  return {};
}
