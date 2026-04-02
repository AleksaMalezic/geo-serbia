const USER_KEY = "adaptive_user_skill_v1";
const LOCATION_KEY = "adaptive_location_profiles_v1";
const MODE_KEY = "adaptive_mode_v1";

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function loadUserProfile() {
  return readJson(USER_KEY, {
    skill_rating: 52,
    recent_points: [],
    recent_distances: [],
    consistency_index: 0,
    last_updated_at: null,
  });
}

function saveUserProfile(profile) {
  writeJson(USER_KEY, profile);
}

function loadLocationProfiles() {
  return readJson(LOCATION_KEY, {});
}

function saveLocationProfiles(profiles) {
  writeJson(LOCATION_KEY, profiles);
}

function normalizeLocationId(location) {
  return String(location?.id ?? "");
}

function estimateLocationDifficulty(location, profiles) {
  const key = normalizeLocationId(location);
  const existing = profiles[key];
  if (existing?.difficulty_rating != null) return Number(existing.difficulty_rating);
  return 50;
}

export function getAdaptiveMode() {
  const raw = localStorage.getItem(MODE_KEY);
  return raw === "fixed" ? "fixed" : "adaptive";
}

export function setAdaptiveMode(mode) {
  localStorage.setItem(MODE_KEY, mode === "fixed" ? "fixed" : "adaptive");
}

export function getDifficultyTier(skillRating) {
  if (skillRating < 40) return "Easy";
  if (skillRating > 66) return "Hard";
  return "Normal";
}

export function getAdaptiveStatsSnapshot() {
  const profile = loadUserProfile();
  const recentPoints = profile.recent_points || [];
  const firstHalf = recentPoints.slice(0, Math.floor(recentPoints.length / 2));
  const secondHalf = recentPoints.slice(Math.floor(recentPoints.length / 2));
  const baseAvg = average(firstHalf);
  const newAvg = average(secondHalf);
  const improvement = baseAvg > 0 ? ((newAvg - baseAvg) / baseAvg) * 100 : 0;

  return {
    current_skill_rating: Number(profile.skill_rating || 52),
    difficulty_tier: getDifficultyTier(Number(profile.skill_rating || 52)),
    recent_improvement_percent: Number(improvement.toFixed(1)),
    consistency_index: Number(profile.consistency_index || 0),
  };
}

export function selectAdaptiveRounds(locations, totalRounds, mode = "adaptive") {
  if (!Array.isArray(locations) || locations.length === 0) return [];
  const shuffled = [...locations];
  for (let i = shuffled.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  if (mode === "fixed") {
    return shuffled.slice(0, totalRounds).map((loc) => ({
      ...loc,
      adaptive_difficulty: "Normal",
      adaptive_rating: 50,
      adaptive_source: "fixed",
    }));
  }

  const user = loadUserProfile();
  const profiles = loadLocationProfiles();
  const target = Number(user.skill_rating || 52);

  const scored = shuffled.map((loc) => {
    const rating = estimateLocationDifficulty(loc, profiles);
    const distance = Math.abs(rating - target);
    return { loc, rating, distance };
  });

  scored.sort((a, b) => a.distance - b.distance);
  return scored.slice(0, totalRounds).map(({ loc, rating }) => ({
    ...loc,
    adaptive_difficulty: getDifficultyTier(rating),
    adaptive_rating: rating,
    adaptive_source: "client-fallback",
  }));
}

export function applyRoundOutcome({ locationId, points, distanceKm }) {
  const profile = loadUserProfile();
  const locations = loadLocationProfiles();
  const pointsNumber = Number(points || 0);
  const distanceNumber = Number(distanceKm || 0);

  const beforePointsAvg = average(profile.recent_points || []);

  const recentPoints = [...(profile.recent_points || []), pointsNumber].slice(-10);
  const recentDistances = [...(profile.recent_distances || []), distanceNumber].slice(-10);
  const avgPoints = average(recentPoints);
  const avgDistance = average(recentDistances);

  // Lightweight skill update: points up, distance down.
  const rawSkill = (avgPoints / 10) * 70 + clamp(1 - avgDistance / 250, 0, 1) * 30;
  const updatedSkill = clamp(rawSkill, 0, 100);

  const variance = recentPoints.length > 1 ? average(recentPoints.map((p) => Math.pow(p - avgPoints, 2))) : 0;
  const consistency = clamp(1 - Math.sqrt(variance) / 250, 0, 1);

  const nextProfile = {
    ...profile,
    skill_rating: Number(updatedSkill.toFixed(1)),
    recent_points: recentPoints,
    recent_distances: recentDistances,
    consistency_index: Number(consistency.toFixed(2)),
    recent_avg_points: Number(avgPoints.toFixed(1)),
    recent_avg_distance_km: Number(avgDistance.toFixed(2)),
    last_updated_at: new Date().toISOString(),
  };
  saveUserProfile(nextProfile);

  const locationKey = String(locationId ?? "");
  if (locationKey) {
    const existing = locations[locationKey] || {
      difficulty_rating: 50,
      global_avg_distance_km: 0,
      global_avg_points: 0,
      attempt_count: 0,
    };

    const attempts = Number(existing.attempt_count || 0) + 1;
    const globalAvgDistance = (Number(existing.global_avg_distance_km || 0) * (attempts - 1) + distanceNumber) / attempts;
    const globalAvgPoints = (Number(existing.global_avg_points || 0) * (attempts - 1) + pointsNumber) / attempts;
    const difficultyRating = clamp((globalAvgDistance / 250) * 70 + clamp(1 - globalAvgPoints / 500, 0, 1) * 30, 0, 100);

    locations[locationKey] = {
      difficulty_rating: Number(difficultyRating.toFixed(1)),
      global_avg_distance_km: Number(globalAvgDistance.toFixed(2)),
      global_avg_points: Number(globalAvgPoints.toFixed(1)),
      attempt_count: attempts,
      updated_at: new Date().toISOString(),
    };
    saveLocationProfiles(locations);
  }

  const afterPointsAvg = average(nextProfile.recent_points || []);
  const improvementPercent = beforePointsAvg > 0 ? ((afterPointsAvg - beforePointsAvg) / beforePointsAvg) * 100 : 0;

  return {
    skill_rating_before: Number(profile.skill_rating || 52),
    skill_rating_after: Number(nextProfile.skill_rating || 52),
    recent_improvement_percent: Number(improvementPercent.toFixed(1)),
    difficulty_tier: getDifficultyTier(Number(nextProfile.skill_rating || 52)),
  };
}
