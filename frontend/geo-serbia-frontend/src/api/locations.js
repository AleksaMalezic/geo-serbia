import http from "./http";

export const locationsApi = {
  list(params = {}) {
    return http.get("/locations/", { params });
  },
  adminAll(params = {}) {
    return http.get("/locations/admin/all", { params });
  },
  pending() {
    return http.get("/locations/pending");
  },
  approve(locationId) {
    return http.post(`/locations/${locationId}/approve`);
  },
  reject(locationId) {
    return http.post(`/locations/${locationId}/reject`);
  },
  update(locationId, payload) {
    return http.patch(`/locations/${locationId}`, payload);
  },
  delete(locationId) {
    return http.delete(`/locations/${locationId}`);
  },
  create(payload) {
    const form = new FormData();
    form.append("name", payload.name);
    form.append("description", payload.description || "");
    form.append("hints", JSON.stringify(payload.hints || []));
    form.append("latitude", String(payload.latitude));
    form.append("longitude", String(payload.longitude));
    if (payload.image) {
      form.append("image", payload.image);
    }
    return http.post("/locations/", form);
  },
};