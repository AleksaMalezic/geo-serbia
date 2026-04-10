<script setup>
import { computed, onMounted, ref } from "vue";
import { profileApi } from "../api/profile";
import { getAdaptiveMode, getAdaptiveStatsSnapshot, setAdaptiveMode } from "../composables/useAdaptiveDifficulty";

const GAME_HISTORY_KEY = "geoSerbia.game.history.v1";

const stats = ref({
  average_score: 0,
  total_sessions: 0,
  total_rounds: 0,
});
const adaptiveStats = ref({
  current_skill_rating: 52,
  difficulty_tier: "Normal",
  recent_improvement_percent: 0,
  recent_avg_distance_km: 0,
});
const adaptiveMode = ref(getAdaptiveMode());
const loading = ref(true);
const recentGames = ref([]);

const hasNoGames = computed(() => Number(stats.value.total_rounds || 0) === 0);
const bestDailyScore = computed(() => {
  if (!recentGames.value.length) return 0;
  return Math.max(...recentGames.value.map((g) => Number(g.totalScore || 0)));
});
const averageDistance = computed(() => {
  const value = Number(adaptiveStats.value.recent_avg_distance_km || 0);
  return Number.isFinite(value) ? value : 0;
});
const tierText = computed(() => adaptiveStats.value.difficulty_tier || "Normal");
const skillRating = computed(() => Number(adaptiveStats.value.current_skill_rating || 52));
const skillLevel = computed(() => {
  if (skillRating.value < 35) return "Explorer";
  if (skillRating.value < 60) return "Navigator";
  if (skillRating.value < 80) return "Pathfinder";
  return "Expert";
});

function setMode(mode) {
  adaptiveMode.value = mode === "fixed" ? "fixed" : "adaptive";
  setAdaptiveMode(adaptiveMode.value);
}

function formatDate(raw) {
  if (!raw) return "-";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return "-";
  return date.toLocaleString();
}

function loadRecentGames() {
  try {
    const parsed = JSON.parse(localStorage.getItem(GAME_HISTORY_KEY) || "[]");
    recentGames.value = Array.isArray(parsed) ? parsed.slice(0, 5) : [];
  } catch {
    recentGames.value = [];
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await profileApi.stats();
    const payload = data?.data ?? data ?? {};
    const source = payload?.stats ?? payload;
    stats.value = {
      average_score: Number(source?.average_score || source?.avg_score || 0),
      total_sessions: Number(source?.total_sessions || 0),
      total_rounds: Number(source?.total_rounds || 0),
    };

    try {
      const adaptiveResponse = await profileApi.adaptiveStats();
      const adaptivePayload = adaptiveResponse?.data?.data ?? adaptiveResponse?.data ?? {};
      adaptiveStats.value = {
        current_skill_rating: Number(adaptivePayload?.current_skill_rating || 52),
        difficulty_tier: adaptivePayload?.difficulty_tier || "Normal",
        recent_improvement_percent: Number(adaptivePayload?.recent_improvement_percent || 0),
        recent_avg_distance_km: Number(adaptivePayload?.recent_avg_distance_km || 0),
      };
    } catch {
      const fallback = getAdaptiveStatsSnapshot();
      adaptiveStats.value = {
        current_skill_rating: Number(fallback?.current_skill_rating || 52),
        difficulty_tier: fallback?.difficulty_tier || "Normal",
        recent_improvement_percent: Number(fallback?.recent_improvement_percent || 0),
        recent_avg_distance_km: 0,
      };
    }
    loadRecentGames();
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="container profile-page">
    <div class="panel profile-panel">
      <div class="profile-head">
        <h1>Your Profile</h1>
        <div class="mode-toggle">
          <button :class="['tab', { active: adaptiveMode === 'adaptive' }]" @click="setMode('adaptive')">Adaptive</button>
          <button :class="['tab', { active: adaptiveMode === 'fixed' }]" @click="setMode('fixed')">Fixed</button>
        </div>
      </div>

      <div v-if="loading">Loading...</div>

      <template v-else>
        <div v-if="hasNoGames" class="profile-empty">
          <h2>Play your first challenge</h2>
          <p>Your stats will appear after you finish rounds.</p>
          <RouterLink to="/game" class="btn btn-primary">Play Now</RouterLink>
        </div>

        <template v-else>
          <div class="profile-cards">
            <article class="metric-card">
              <span>Best Daily Score</span>
              <strong>{{ bestDailyScore }}</strong>
            </article>
            <article class="metric-card">
              <span>Average Distance</span>
              <strong>{{ averageDistance.toFixed(1) }} km</strong>
            </article>
            <article class="metric-card">
              <span>Games Played</span>
              <strong>{{ stats.total_sessions }}</strong>
            </article>
          </div>

          <div class="profile-adaptive-line">
            <span>Mode: {{ adaptiveMode === "adaptive" ? "Adaptive" : "Fixed" }}</span>
            <span>Tier: {{ tierText }}</span>
            <span>Level: {{ skillLevel }}</span>
          </div>

          <div class="profile-skill-wrap">
            <div class="profile-skill-label">
              <span>Skill Progress</span>
              <strong>{{ skillRating.toFixed(1) }}/100</strong>
            </div>
            <div class="profile-skill-bar">
              <div class="profile-skill-fill" :style="{ width: `${Math.max(0, Math.min(100, skillRating))}%` }"></div>
            </div>
          </div>

          <div class="profile-history">
            <h2>Recent Performance</h2>
            <div v-if="!recentGames.length" class="admin-empty">No recent finished games.</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Total Score</th>
                  <th>Avg Distance</th>
                  <th>Rounds</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in recentGames" :key="`${item.finishedAt}-${index}`">
                  <td>{{ formatDate(item.finishedAt) }}</td>
                  <td>{{ Number(item.totalScore || 0).toFixed(0) }}</td>
                  <td>{{ Number(item.avgDistance || 0).toFixed(1) }} km</td>
                  <td>{{ Number(item.roundsPlayed || 0) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </template>
    </div>
  </section>
</template>