import http from "./http";

export const gameApi = {
  startChallenge(mode = "adaptive") {
    return http.post("/game/start", null, {
      params: { mode },
    });
  },
  requestHint({ locationId, hintsUsedCount }) {
    return http.post("/game/hint", null, {
      params: {
        location_id: locationId,
        hints_used_count: hintsUsedCount,
      },
    });
  },
  playRound({ locationId, guessedLatitude, guessedLongitude, hintsUsedCount = 0 }) {
    return http.post("/game/play", null, {
      params: {
        location_id: locationId,
        guessed_latitude: guessedLatitude,
        guessed_longitude: guessedLongitude,
        hints_used_count: hintsUsedCount,
      },
    });
  },
};
