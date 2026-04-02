<script setup>
import { onMounted, ref } from "vue";
import { profileApi } from "../api/profile";
import { getAdaptiveMode, getAdaptiveStatsSnapshot, setAdaptiveMode } from "../composables/useAdaptiveDifficulty";

const stats = ref({
  average_score: 0,
  total_sessions: 0,
  total_rounds: 0,
});
const adaptiveStats = ref({
  current_skill_rating: 52,
  difficulty_tier: "Normal",
  recent_improvement_percent: 0,
});
const adaptiveMode = ref(getAdaptiveMode());
const loading = ref(true);

function getTrendArrow(value) {
  if (value > 0) return "UP";
  if (value < 0) return "DOWN";
  return "FLAT";
}

function setMode(mode) {
  adaptiveMode.value = mode === "fixed" ? "fixed" : "adaptive";
  setAdaptiveMode(adaptiveMode.value);
}

onMounted(async () => {
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
      };
    } catch {
      adaptiveStats.value = getAdaptiveStatsSnapshot();
    }
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="container profile-page">
    <div class="panel">
      <h1>Profile Stats</h1>
      <div v-if="loading">Loading...</div>
      <div v-else class="profile-cards">
        <article class="metric-card">
          <span>Average Score</span>
          <strong>{{ stats.average_score.toFixed(0) }}</strong>
        </article>
        <article class="metric-card">
          <span>Total Sessions</span>
          <strong>{{ stats.total_sessions }}</strong>
        </article>
        <article class="metric-card">
          <span>Total Rounds</span>
          <strong>{{ stats.total_rounds }}</strong>
        </article>
      </div>

      <h2 class="profile-subtitle">Adaptive Challenge</h2>
      <div class="adaptive-settings">
        <div class="mode-toggle">
          <button :class="['tab', { active: adaptiveMode === 'adaptive' }]" @click="setMode('adaptive')">Adaptive</button>
          <button :class="['tab', { active: adaptiveMode === 'fixed' }]" @click="setMode('fixed')">Fixed</button>
        </div>
        <div class="adaptive-metrics">
          <article class="metric-card">
            <span>Current Skill</span>
            <strong>{{ Number(adaptiveStats.current_skill_rating || 52).toFixed(1) }}</strong>
          </article>
          <article class="metric-card">
            <span>Difficulty Tier</span>
            <strong>{{ adaptiveStats.difficulty_tier || "Normal" }}</strong>
          </article>
          <article class="metric-card">
            <span>Recent Trend</span>
            <strong>
              {{ getTrendArrow(Number(adaptiveStats.recent_improvement_percent || 0)) }}
              {{ Number(adaptiveStats.recent_improvement_percent || 0).toFixed(1) }}%
            </strong>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>
