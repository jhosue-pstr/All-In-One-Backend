import { sleep, group } from "k6";
import { Trend, Rate }  from "k6/metrics";
import { BASE_URL }     from "../config/thresholds.js";
import { setupResponseCallback, visitPage } from "../config/utils.js";

setupResponseCallback();

const pageLoad   = new Trend("stress_page_load_ms", true);
const errorRate  = new Rate("stress_errors");

export const options = {
  stages: [
    { duration: "1m",  target: 20  },
    { duration: "2m",  target: 50  },
    { duration: "2m",  target: 80  },
    { duration: "3m",  target: 100 },
    { duration: "2m",  target: 80  },
    { duration: "1m",  target: 20  },
    { duration: "1m",  target: 0   },
  ],
  thresholds: {
    http_req_duration:   ["p(95)<5000", "p(99)<8000"],
    http_req_failed:     ["rate<0.05"],
    stress_errors:       ["rate<0.10"],
    checks:              ["rate>0.85"],
  },
};

export default function () {
  group("Stress — API endpoints", () => {
    visitPage(`${BASE_URL}/docs`,                 "stress_docs",   errorRate, pageLoad, 5000);
    sleep(0.3);
    visitPage(`${BASE_URL}/api/publico/check-system`, "stress_health", errorRate, pageLoad, 5000);
    sleep(0.3);
    visitPage(`${BASE_URL}/api/openapi.json`,     "stress_openapi", errorRate, pageLoad, 5000);
    sleep(0.2);
    visitPage(`${BASE_URL}/api/auth/me`,          "stress_auth",   errorRate, pageLoad, 5000);
  });
  sleep(0.2);
}

export function handleSummary(data) {
  const p95  = data.metrics.stress_page_load_ms?.values?.["p(95)"]?.toFixed(0);
  const p99  = data.metrics.stress_page_load_ms?.values?.["p(99)"]?.toFixed(0);
  const max  = data.metrics.stress_page_load_ms?.values?.max?.toFixed(0);
  const err  = data.metrics.stress_errors?.values?.rate;
  const fail = data.metrics.http_req_failed?.values?.rate;
  const reqs = data.metrics.http_reqs?.values?.count;
  const rps  = data.metrics.http_reqs?.values?.rate?.toFixed(1);

  console.log("════════════════════════════════════════════");
  console.log("  STRESS TEST — RESUMEN");
  console.log("════════════════════════════════════════════");
  console.log(`  Total requests : ${reqs || "N/A"}`);
  console.log(`  Req/segundo    : ${rps  || "N/A"} req/s`);
  console.log(`  p95 respuesta  : ${p95  || "N/A"} ms`);
  console.log(`  p99 respuesta  : ${p99  || "N/A"} ms`);
  console.log(`  Max respuesta  : ${max  || "N/A"} ms`);
  console.log(`  Tasa errores   : ${err  ? (err  * 100).toFixed(2) : "N/A"}%`);
  console.log(`  Net failures   : ${fail ? (fail * 100).toFixed(2) : "N/A"}%`);
  console.log("════════════════════════════════════════════");
  return {};
}
