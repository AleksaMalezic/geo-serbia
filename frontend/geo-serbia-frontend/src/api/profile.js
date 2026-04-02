import http from "./http";

export const profileApi = {
  stats() {
    return http.get("/auth/me");
  },
  adaptiveStats() {
    return http.get("/profile/adaptive-stats");
  },
};
