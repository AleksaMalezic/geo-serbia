<script setup>
import { computed } from "vue";

const summary = computed(() => {
  const raw = sessionStorage.getItem("lastGameSummary");
  if (!raw) return { totalScore: 0, avgDistance: 0, rounds: [] };
  try {
    return JSON.parse(raw);
  } catch {
    return { totalScore: 0, avgDistance: 0, rounds: [] };
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
