<template>
  <section class="card">
    <h2>Admin</h2>
    <div class="inline">
      <button type="button" @click="$emit('loadPending')">Load Pending</button>
      <button type="button" @click="$emit('loadStats')">Load Stats (/api/v1/admin/stats)</button>
    </div>

    <div v-if="adminStats">
      <p>Users: {{ adminStats.users?.total }} (admins: {{ adminStats.users?.admins }})</p>
      <p>
        Locations: {{ adminStats.locations?.total }} approved {{ adminStats.locations?.approved }} pending
        {{ adminStats.locations?.pending }}
      </p>
      <p>Game: sessions {{ adminStats.game?.sessions }} rounds {{ adminStats.game?.rounds }}</p>
    </div>

    <h3>Pending Locations (/api/v1/locations/pending)</h3>
    <ul>
      <li v-for="item in pendingLocations" :key="`p-${item.id}`">
        <strong>#{{ item.id }} {{ item.name }}</strong>
        <button type="button" @click="$emit('approve', item.id)">Approve</button>
        <button type="button" @click="$emit('reject', item.id)">Reject</button>
      </li>
    </ul>
  </section>
</template>

<script setup>
defineProps({
  adminStats: {
    type: Object,
    default: null,
  },
  pendingLocations: {
    type: Array,
    required: true,
  },
});

defineEmits(["loadPending", "loadStats", "approve", "reject"]);
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
