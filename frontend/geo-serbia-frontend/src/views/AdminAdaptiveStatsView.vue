<script setup>
import { computed, onMounted, ref } from "vue";
import { getAdaptiveAdminStats } from "../api/admin";

const loading = ref(true);
const error = ref("");
const stats = ref(null);
const rankOrder = ["bronze", "silver", "gold", "platinum", "diamond", "champion"];
const rankCards = computed(() => {
  const distribution = stats.value?.rank_distribution || {};
  return rankOrder.map((rank) => ({
    key: rank,
    label: `${rank.charAt(0).toUpperCase()}${rank.slice(1)} Users`,
    value: Number(distribution?.[rank] ?? 0),
  }));
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const payload = await getAdaptiveAdminStats();
    stats.value = payload || {};
  } catch (e) {
    error.value = e?.response?.data?.detail || "Adaptive stats endpoint is not available yet.";
    stats.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="container admin-adaptive-page">
    <div class="panel">
      <div class="admin-page-head">
        <h1>Adaptive Analytics</h1>
        <button class="btn btn-ghost" :disabled="loading" @click="load">Reload</button>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <div v-if="loading">Loading...</div>

      <div v-else-if="stats" class="adaptive-admin-grid">
        <article class="metric-card">
          <span>Fallback Rate</span>
          <strong>{{ Number(stats.fallback_rate || 0).toFixed(2) }}%</strong>
        </article>
        <article v-for="item in rankCards" :key="item.key" class="metric-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </article>
      </div>

      <div v-if="stats?.top_unstable_locations?.length" class="panel admin-unstable">
        <h3>Top Unstable Locations</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Location</th>
              <th>Variance</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in stats.top_unstable_locations" :key="item.location_id || item.id || item.name">
              <td>{{ item.name || `#${item.location_id}` }}</td>
              <td>{{ Number(item.variance || item.score_variance || 0).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
