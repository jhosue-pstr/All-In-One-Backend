import { sleep } from "k6";
import { Trend, Rate } from "k6/metrics";
import { BASE_URL, ENDPOINTS } from "../config/thresholds.js";
import { setupResponseCallback, visitPage } from "../config/utils.js";

setupResponseCallback();

const spikeResponse = new Trend("spike_response_ms", true);
const spikeErrors   = new Rate("spike_error_rate");

export const options = {
  stages: [
    { duration: "1m",  target: 10  },
    { duration: "30s", target: 200 },
    { duration: "1m",  target: 200 },
    { duration: "30s", target: 10  },
    { duration: "3m",  target: 10  },
    { duration: "1m",  target: 0   },
  ],
  thresholds: {
    http_req_duration: ["p(95)<6000"],
    http_req_failed:   ["rate<0.10"],
    spike_error_rate:  ["rate<0.15"],
    checks:            ["rate>0.80"],
  },
};

export default function () {
  visitPage(`${BASE_URL}${ENDPOINTS.home.path}`, "spike_home", spikeErrors, spikeResponse, 6000);
  sleep(0.1);
}

export function handleSummary(data) {
  const p95  = data.metrics.spike_response_ms?.values?.["p(95)"]?.toFixed(0);
  const max  = data.metrics.spike_response_ms?.values?.max?.toFixed(0);
  const err  = data.metrics.spike_error_rate?.values?.rate;
  const fail = data.metrics.http_req_failed?.values?.rate;

  console.log("════════════════════════════════════════════");
  console.log("  SPIKE TEST — RESUMEN");
  console.log("════════════════════════════════════════════");
  console.log(`  p95 durante pico  : ${p95  || "N/A"} ms`);
  console.log(`  Max durante pico  : ${max  || "N/A"} ms`);
  console.log(`  Tasa de errores   : ${err  ? (err  * 100).toFixed(2) : "N/A"}%`);
  console.log(`  Net failures      : ${fail ? (fail * 100).toFixed(2) : "N/A"}%`);
  console.log("════════════════════════════════════════════");
  return {};
}
