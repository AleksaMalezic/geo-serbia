<script setup>
import { computed } from "vue";

const summary = computed(() => {
  const raw = sessionStorage.getItem("lastGameSummary");
  if (!raw) return { totalScore: 0, avgDistance: 0, rounds: [], adaptive: {} };
  try {
    return JSON.parse(raw);
  } catch {
    return { totalScore: 0, avgDistance: 0, rounds: [], adaptive: {} };
  }
});
</script>

<template>
  <section class="container summary-page">
    <div class="panel summary-card">
      <h1>Challenge Summary</h1>
      <div class="summary-stats">
        <div>
          <span>Total Score</span>
          <strong>{{ summary.totalScore }}</strong>
        </div>
        <div>
          <span>Average Distance</span>
          <strong>{{ Number(summary.avgDistance || 0).toFixed(2) }} km</strong>
        </div>
      </div>

      <div class="profile-adaptive-line">
        <span>Rank: {{ summary?.adaptive?.rank_tier || "-" }}</span>
      </div>
      <div class="profile-skill-wrap">
        <div class="profile-skill-label">
          <span>Skill Progress</span>
          <strong>{{ Number(summary?.adaptive?.skillRating || 0).toFixed(1) }}/100</strong>
        </div>
        <div class="profile-skill-bar">
          <div
            class="profile-skill-fill"
            :style="{ width: `${Math.max(0, Math.min(100, Number(summary?.adaptive?.skillRating || 0)))}%` }"
          ></div>
        </div>
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>Round</th>
            <th>Points</th>
            <th>Distance (km)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="round in summary.rounds" :key="round.round">
            <td>{{ round.round }}</td>
            <td>{{ round.points }}</td>
            <td>{{ Number(round.distanceKm || 0).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>

      <RouterLink to="/" class="btn btn-primary">Back to Home</RouterLink>
    </div>
  </section>
</template>
