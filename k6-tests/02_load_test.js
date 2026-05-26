import { sleep, group } from "k6";
import { Trend, Rate }  from "k6/metrics";
import { BASE_URL, ENDPOINTS } from "../config/thresholds.js";
import { setupResponseCallback, visitPage } from "../config/utils.js";

setupResponseCallback();

const homeTime     = new Trend("load_home_ms",       true);
const healthTime   = new Trend("load_health_ms",     true);
const modulosTime  = new Trend("load_modulos_ms",    true);
const sitiosTime   = new Trend("load_sitios_ms",     true);
const plantTime    = new Trend("load_plantillas_ms", true);
const loadErrors    = new Rate("load_errors");

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
    load_home_ms:       ["p(95)<3000"],
    load_health_ms:     ["p(95)<2000"],
    load_modulos_ms:    ["p(95)<3000"],
    load_sitios_ms:     ["p(95)<3000"],
    load_plantillas_ms: ["p(95)<3000"],
    load_errors:        ["rate<0.05"],
    checks:             ["rate>0.90"],
  },
};

function rand(min, max) { return Math.random() * (max - min) + min; }

export default function () {
  group("Home", () => {
    visitPage(`${BASE_URL}${ENDPOINTS.home.path}`, "load_home", loadErrors, homeTime, 3000);
  });
  sleep(rand(0.5, 1.5));

  group("Health", () => {
    visitPage(`${BASE_URL}${ENDPOINTS.health.path}`, "load_health", loadErrors, healthTime, 2000);
  });
  sleep(rand(0.5, 1.5));

  group("Modulos", () => {
    visitPage(`${BASE_URL}${ENDPOINTS.modulos.path}`, "load_modulos", loadErrors, modulosTime, 3000);
  });
  sleep(rand(0.5, 1.5));

  group("Sitios", () => {
    visitPage(`${BASE_URL}${ENDPOINTS.sitios.path}`, "load_sitios", loadErrors, sitiosTime, 3000);
  });
  sleep(rand(0.5, 1.5));

  group("Plantillas", () => {
    visitPage(`${BASE_URL}${ENDPOINTS.plantillas.path}`, "load_plantillas", loadErrors, plantTime, 3000);
  });
  sleep(rand(1, 2));
}

export function handleSummary(data) {
  const pHome   = data.metrics.load_home_ms?.values?.["p(95)"]?.toFixed(0)       || "N/A";
  const pHealth = data.metrics.load_health_ms?.values?.["p(95)"]?.toFixed(0)     || "N/A";
  const pMod    = data.metrics.load_modulos_ms?.values?.["p(95)"]?.toFixed(0)    || "N/A";
  const pSit    = data.metrics.load_sitios_ms?.values?.["p(95)"]?.toFixed(0)     || "N/A";
  const pPlant  = data.metrics.load_plantillas_ms?.values?.["p(95)"]?.toFixed(0)  || "N/A";
  const err     = data.metrics.load_errors?.values?.rate;
  const fail    = data.metrics.http_req_failed?.values?.rate;

  console.log("════════════════════════════════════════════");
  console.log("  LOAD TEST — RESUMEN");
  console.log("════════════════════════════════════════════");
  console.log(`  Home       p95 : ${pHome} ms`);
  console.log(`  Health     p95 : ${pHealth} ms`);
  console.log(`  Modulos    p95 : ${pMod} ms`);
  console.log(`  Sitios     p95 : ${pSit} ms`);
  console.log(`  Plantillas p95 : ${pPlant} ms`);
  console.log(`  Errors         : ${err  ? (err  * 100).toFixed(2) : "N/A"}%`);
  console.log(`  Net failures   : ${fail ? (fail * 100).toFixed(2) : "N/A"}%`);
  console.log("════════════════════════════════════════════");
  return {};
}
