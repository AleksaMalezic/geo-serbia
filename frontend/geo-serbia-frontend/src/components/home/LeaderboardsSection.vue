<template>
  <section class="card">
    <h2>Leaderboards</h2>
    <div class="inline">
      <button type="button" @click="$emit('reload')">Reload</button>
    </div>
    <h3>Daily (/api/v1/game/leaderboard/daily)</h3>
    <ul>
      <li v-for="entry in dailyLeaderboard" :key="`d-${entry.username}-${entry.date}`">
        {{ entry.username }} - score {{ entry.total_score }} (rounds {{ entry.rounds_played }})
      </li>
    </ul>
    <h3>Monthly (/api/v1/game/leaderboard/monthly)</h3>
    <ul>
      <li v-for="entry in monthlyLeaderboard" :key="`m-${entry.username}`">
        {{ entry.username }} - points {{ entry.total_points }}
      </li>
    </ul>
  </section>
</template>

<script setup>
defineProps({
  dailyLeaderboard: {
    type: Array,
    required: true,
  },
  monthlyLeaderboard: {
    type: Array,
    required: true,
  },
});

defineEmits(["reload"]);
</script>

<style scoped>
.card {
  border: 1px solid #d7d7d7;
  border-radius: 8px;
  padding: 1rem;
}

.inline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

button {
  padding: 0.5rem;
}
</style>
