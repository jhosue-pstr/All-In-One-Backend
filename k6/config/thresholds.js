export const BASE_URL = __ENV.BASE_URL || "http://host.docker.internal:8000";

export const THRESHOLDS = {
  http_req_duration: [
    "p(50)<800",
    "p(90)<2000",
    "p(95)<3000",
    "p(99)<5000",
  ],
  http_req_failed: ["rate<0.01"],
  checks:          ["rate>0.95"],
};
