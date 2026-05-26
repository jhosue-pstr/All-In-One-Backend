import { sleep, group } from "k6";
import { Trend, Rate, Counter } from "k6/metrics";
import { BASE_URL }             from "../config/thresholds.js";
import { setupResponseCallback, visitPage } from "../config/utils.js";

setupResponseCallback();

const responseTime = new Trend("soak_response_ms",   true);
const errorRate    = new Rate("soak_error_rate");
const requestCount = new Counter("soak_total_requests");

export const options = {
  stages: [
    { duration: "2m",  target: 20 },
    { duration: "26m", target: 20 },
    { duration: "2m",  target: 0  },
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000", "p(99)<5000"],
    http_req_failed:   ["rate<0.01"],
    soak_error_rate:   ["rate<0.05"],
    checks:            ["rate>0.90"],
  },
};

export default function () {
  requestCount.add(1);

  group("Soak — API endpoints", () => {
    visitPage(`${BASE_URL}/docs`,                 "soak_docs",   errorRate, responseTime, 3000);
    sleep(1);
    visitPage(`${BASE_URL}/api/publico/check-system`, "soak_health", errorRate, responseTime, 3000);
    sleep(2);
    visitPage(`${BASE_URL}/api/openapi.json`,     "soak_openapi", errorRate, responseTime, 3000);
    sleep(1);
    visitPage(`${BASE_URL}/api/auth/me`,          "soak_auth",   errorRate, responseTime, 3000);
  });
  sleep(3);
}

export function handleSummary(data) {
  const p50  = data.metrics.soak_response_ms?.values?.["p(50)"]?.toFixed(0);
  const p95  = data.metrics.soak_response_ms?.values?.["p(95)"]?.toFixed(0);
  const p99  = data.metrics.soak_response_ms?.values?.["p(99)"]?.toFixed(0);
  const avg  = data.metrics.soak_response_ms?.values?.avg?.toFixed(0);
  const err  = data.metrics.soak_error_rate?.values?.rate;
  const fail = data.metrics.http_req_failed?.values?.rate;
  const tot  = data.metrics.soak_total_requests?.values?.count;

  console.log("════════════════════════════════════════════");
  console.log("  SOAK TEST — RESUMEN DE RESISTENCIA");
  console.log("════════════════════════════════════════════");
  console.log(`  Total iteraciones : ${tot  || "N/A"}`);
  console.log(`  Promedio respuesta: ${avg  || "N/A"} ms`);
  console.log(`  p50 respuesta     : ${p50  || "N/A"} ms`);
  console.log(`  p95 respuesta     : ${p95  || "N/A"} ms`);
  console.log(`  p99 respuesta     : ${p99  || "N/A"} ms`);
  console.log(`  Tasa de errores   : ${err  ? (err  * 100).toFixed(2) : "N/A"}%`);
  console.log(`  Net failures      : ${fail ? (fail * 100).toFixed(2) : "N/A"}%`);
  console.log("════════════════════════════════════════════");
  return {};
}
