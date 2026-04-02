<template>
  <section class="card">
    <h2>Play Round (POST /api/v1/game/play)</h2>
    <form class="grid-form" @submit.prevent="emitSubmit">
      <input v-model.number="locationId" type="number" min="1" placeholder="location_id" required />
      <input v-model.number="guessedLatitude" type="number" step="any" placeholder="guessed_latitude" required />
      <input v-model.number="guessedLongitude" type="number" step="any" placeholder="guessed_longitude" required />
      <button type="submit">Play</button>
    </form>
    <div v-if="lastRound" class="result">
      <p>Round ID: {{ lastRound.round_id }}</p>
      <p>Distance km: {{ lastRound.distance_km }}</p>
      <p>Score: {{ lastRound.score }}</p>
      <p>Total score: {{ lastRound.total_score }}</p>
      <p>Rounds played: {{ lastRound.rounds_played }}</p>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";

defineProps({
  lastRound: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["submit"]);

const locationId = ref(null);
const guessedLatitude = ref(null);
const guessedLongitude = ref(null);

function emitSubmit() {
  emit("submit", {
    location_id: locationId.value,
    guessed_latitude: guessedLatitude.value,
    guessed_longitude: guessedLongitude.value,
  });
}
</script>

<style scoped>
.card {
  border: 1px solid #d7d7d7;
  border-radius: 8px;
  padding: 1rem;
}

.grid-form {
  display: grid;
  gap: 0.5rem;
}

input,
button {
  padding: 0.5rem;
}

.result {
  margin-top: 0.75rem;
}
</style>
