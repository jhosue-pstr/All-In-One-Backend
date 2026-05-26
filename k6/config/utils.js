import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

export function setupResponseCallback() {
  http.setResponseCallback(
    http.expectedStatuses({ min: 200, max: 599 })
  );
}

export const REQ_PARAMS = {
  redirects: 5,
  timeout:   "15s",
  headers: {
    "User-Agent": "k6-loader/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
  },
};

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
