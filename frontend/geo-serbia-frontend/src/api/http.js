import axios from "axios";
import { getStoredToken } from "./token";

function buildBaseUrl() {
  const loopback = new Set(["127.0.0.1", "localhost"]);
  const browserHost = typeof window !== "undefined" ? window.location.hostname : "";
  const envRaw = import.meta.env.VITE_API_URL;
  if (envRaw && String(envRaw).startsWith("/")) {
    return String(envRaw).replace(/\/+$/, "");
  }

  const raw = envRaw || `http://${browserHost || "localhost"}:8000`;
  const normalized = String(raw).replace(/\/+$/, "");
  const parsed = new URL(normalized);

  if (browserHost && loopback.has(parsed.hostname) && loopback.has(browserHost) && parsed.hostname !== browserHost) {
    parsed.hostname = browserHost;
  }

  const origin = parsed.origin;
  return /\/api\/v1$/i.test(parsed.pathname) ? `${origin}${parsed.pathname}` : `${origin}/api/v1`;
}

const http = axios.create({
  baseURL: buildBaseUrl(),
  withCredentials: true,
});

http.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default http;
