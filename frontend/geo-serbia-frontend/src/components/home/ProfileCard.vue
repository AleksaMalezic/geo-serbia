<template>
  <section class="card" v-if="profile">
    <h2>Profile (/api/v1/auth/me)</h2>
    <p>Email: {{ profile.email }}</p>
    <p>Joined: {{ formatDate(profile.joined) }}</p>
    <p>Total sessions: {{ profile.stats?.total_sessions ?? 0 }}</p>
    <p>Total rounds: {{ profile.stats?.total_rounds ?? 0 }}</p>
    <p>Total score: {{ profile.stats?.total_score ?? 0 }}</p>
    <p>Average score: {{ profile.stats?.average_score ?? 0 }}</p>
    <p>Last played: {{ formatDate(profile.stats?.last_played) }}</p>
  </section>
</template>

<script setup>
defineProps({
  profile: {
    type: Object,
    default: null,
  },
  formatDate: {
    type: Function,
    required: true,
  },
});
</script>

<style scoped>
.card {
  border: 1px solid #d7d7d7;
  border-radius: 8px;
  padding: 1rem;
}
</style>
