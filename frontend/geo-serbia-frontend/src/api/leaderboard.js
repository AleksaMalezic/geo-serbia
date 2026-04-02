import http from "./http";

export const leaderboardApi = {
  daily() {
    return http.get("/game/leaderboard/daily");
  },
  monthly() {
    return http.get("/game/leaderboard/monthly");
  },
};
