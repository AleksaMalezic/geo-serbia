import http from "./http";

export const authApi = {
  login(payload) {
    return http.post("/auth/login", payload);
  },
  register(payload) {
    return http.post("/auth/register", payload);
  },
  me() {
    return http.get("/auth/me");
  },
  logout() {
    return http.post("/auth/logout");
  },
};
