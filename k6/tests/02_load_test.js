import { sleep, group } from "k6";
import { Trend, Rate }  from "k6/metrics";
import { BASE_URL }     from "../config/thresholds.js";
import { setupResponseCallback, visitPage } from "../config/utils.js";

setupResponseCallback();

const docsTime     = new Trend("docs_ms",     true);
const healthTime   = new Trend("health_ms", true);
const authTime     = new Trend("auth_ms",  true);
const blogTime     = new Trend("blog_ms",  true);
const flowErrors   = new Rate("flow_errors");

export const options = {
  stages: [
    { duration: "1m30s", target: 10 },
    { duration: "1m30s", target: 20 },
    { duration: "2m",    target: 30 },
    { duration: "1m30s", target: 10 },
    { duration: "30s",   target: 0  },
  ],
  thresholds: {
    http_req_duration:  ["p(95)<3000", "p(99)<5000"],
    http_req_failed:    ["rate<0.01"],
    docs_ms:            ["p(95)<3000"],
    health_ms:          ["p(95)<3000"],
    auth_ms:            ["p(95)<3000"],
    blog_ms:            ["p(95)<3000"],
    flow_errors:        ["rate<0.05"],
    checks:             ["rate>0.90"],
  },
};

function rand(min, max) { return Math.random() * (max - min) + min; }

export default function () {
  group("Docs", () => {
    visitPage(`${BASE_URL}/docs`, "docs", flowErrors, docsTime, 3000);
  });
  sleep(rand(0.5, 1.5));

  group("Health", () => {
    visitPage(`${BASE_URL}/api/publico/check-system`, "health", flowErrors, healthTime, 3000);
  });
  sleep(rand(1, 3));

  group("Auth", () => {
    visitPage(`${BASE_URL}/api/auth/me`, "auth_me", flowErrors, authTime, 3000);
  });
  sleep(rand(0.5, 1));

  group("Blog", () => {
    visitPage(`${BASE_URL}/api/modulos/blog`, "blog_list", flowErrors, blogTime, 3000);
  });
  sleep(rand(1, 2));
}

export function handleSummary(data) {
  const p95D  = data.metrics.docs_ms?.values?.["p(95)"]?.toFixed(0)   || "N/A";
  const p95H  = data.metrics.health_ms?.values?.["p(95)"]?.toFixed(0) || "N/A";
  const p95A  = data.metrics.auth_ms?.values?.["p(95)"]?.toFixed(0)   || "N/A";
  const p95B  = data.metrics.blog_ms?.values?.["p(95)"]?.toFixed(0)   || "N/A";
  const err   = data.metrics.flow_errors?.values?.rate;
  const fail  = data.metrics.http_req_failed?.values?.rate;

  console.log("════════════════════════════════════════════");
  console.log("  LOAD TEST — RESUMEN");
  console.log("════════════════════════════════════════════");
  console.log(`  Docs       p95 : ${p95D} ms`);
  console.log(`  Health     p95 : ${p95H} ms`);
  console.log(`  Auth       p95 : ${p95A} ms`);
  console.log(`  Blog       p95 : ${p95B} ms`);
  console.log(`  Flow errors    : ${err  ? (err  * 100).toFixed(2) : "N/A"}%`);
  console.log(`  Net failures   : ${fail ? (fail * 100).toFixed(2) : "N/A"}%`);
  console.log("════════════════════════════════════════════");
  return {};
}
