import { setupResponseCallback } from "../config/utils.js";

setupResponseCallback();

export const BASE_URL = "http://backend:8000";

export const THRESHOLDS = {
  http_req_duration: [
    "p(50)<500",
    "p(90)<1500",
    "p(95)<3000",
    "p(99)<5000",
  ],
  http_req_failed: ["rate<0.01"],
  checks:          ["rate>0.95"],
};

export const ENDPOINTS = {
  home:    { path: "/",              name: "Home",        maxMs: 3000 },
  health:  { path: "/health",        name: "Health",      maxMs: 2000 },
  modulos: { path: "/api/modulos",   name: "Modulos",     maxMs: 3000 },
  sitios:  { path: "/api/sitios",    name: "Sitios",      maxMs: 3000 },
  plantillas: { path: "/api/plantillas/publicas", name: "Plantillas", maxMs: 3000 },
};
