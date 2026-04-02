import API from "./axios";
import http from "./http";

export async function getAdminStats() {
  const { data } = await API.get("/api/v1/admin/stats");
  return data?.data ?? null;
}

export async function getAdaptiveAdminStats() {
  const { data } = await http.get("/admin/adaptive/stats");
  return data?.data ?? data ?? null;
}
