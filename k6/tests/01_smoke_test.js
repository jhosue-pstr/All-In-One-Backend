import http          from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate, Counter } from "k6/metrics";
import { BASE_URL }  from "../config/thresholds.js";

http.setResponseCallback(http.expectedStatuses(
  { min: 200, max: 599 }
));

const docsDuration     = new Trend("docs_duration",     true);
const healthDuration   = new Trend("health_duration", true);
const apiDuration      = new Trend("api_duration",  true);
const errorRate         = new Rate("error_rate");
const totalRequests     = new Counter("total_requests");

export const options = {
  scenarios: {
    smoke: {
      executor: "constant-vus",
      vus:      1,
      duration: "1m",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<3000", "p(99)<5000"],
    http_req_failed:   ["rate<0.01"],
    checks:            ["rate>0.90"],
    error_rate:        ["rate<0.10"],
    docs_duration:     ["p(95)<3000"],
    health_duration:   ["p(95)<3000"],
    api_duration:      ["p(95)<3000"],
  },
};

function visitPage(url, name, trend) {
  const res = http.get(url, {
    redirects: 5,
    timeout:   "10s",
    tags:      { name }
  });

  if (trend) trend.add(res.timings.duration);
  totalRequests.add(1);

  const ok = check(res, {
    [`${name} — responde`]:    (r) => r.status > 0,
    [`${name} — tiempo < 3s`]: (r) => r.timings.duration < 3000,
  });
  errorRate.add(!ok);

  return res;
}

export default function () {
  visitPage(`${BASE_URL}/docs`,                 "GET_docs",          docsDuration);
  sleep(1);
  visitPage(`${BASE_URL}/api/publico/check-system`, "GET_health",   healthDuration);
  sleep(1);
  visitPage(`${BASE_URL}/api/openapi.json`,     "GET_openapi",       null);
  sleep(1);
  visitPage(`${BASE_URL}/api/auth/me`,          "GET_auth_me",       apiDuration);
  sleep(1);
  visitPage(`${BASE_URL}/api/modulos/blog`,     "GET_blog_list",     null);
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
  const p95D    = data.metrics.docs_duration?.values?.["p(95)"]?.toFixed(0)     || "N/A";
  const p95H    = data.metrics.health_duration?.values?.["p(95)"]?.toFixed(0) || "N/A";
  const p95A    = data.metrics.api_duration?.values?.["p(95)"]?.toFixed(0)  || "N/A";

  console.log("================================================");
  console.log("  SMOKE TEST — RESUMEN");
  console.log("================================================");
  console.log(`  Checks pasados    : ${passed}/${total} (${pct}%)`);
  console.log(`  Tasa error checks : ${errPct}%`);
  console.log(`  http_req_failed   : ${failPct}%`);
  console.log(`  Requests total    : ${reqs}`);
  console.log(`  Docs       p95    : ${p95D} ms`);
  console.log(`  Health     p95    : ${p95H} ms`);
  console.log(`  Auth API   p95    : ${p95A} ms`);
  console.log("================================================");
  return {};
}
