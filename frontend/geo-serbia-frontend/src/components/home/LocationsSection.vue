<template>
  <section class="card">
    <h2>Locations (/api/v1/locations/)</h2>
    <form class="inline-form" @submit.prevent="$emit('apply')">
      <input
        :value="locationSearch"
        placeholder="Search by name/description"
        @input="$emit('update:locationSearch', $event.target.value)"
      />
      <label>
        Approved:
        <select :value="approvedFilter" @change="$emit('update:approvedFilter', $event.target.value)">
          <option value="true">true</option>
          <option value="false">false</option>
          <option value="all">all</option>
        </select>
      </label>
      <button type="submit">Apply</button>
    </form>
    <ul>
      <li v-for="item in locations" :key="item.id">
        <strong>#{{ item.id }} {{ item.name }}</strong>
        <span> ({{ item.latitude }}, {{ item.longitude }})</span>
        <div>{{ item.description || "No description" }}</div>
        <div v-if="item.image_url">Image: {{ item.image_url }}</div>
      </li>
    </ul>
    <div class="pagination">
      <button type="button" :disabled="locationPage <= 1" @click="$emit('prev')">Prev</button>
      <span>Page {{ locationPage }}</span>
      <button type="button" @click="$emit('next')">Next</button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  locations: {
    type: Array,
    required: true,
  },
  locationPage: {
    type: Number,
    required: true,
  },
  locationSearch: {
    type: String,
    required: true,
  },
  approvedFilter: {
    type: String,
    required: true,
  },
});

defineEmits(["apply", "prev", "next", "update:locationSearch", "update:approvedFilter"]);
</script>

<style scoped>
.card {
  border: 1px solid #d7d7d7;
  border-radius: 8px;
  padding: 1rem;
}

.inline-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

input,
select,
button {
  padding: 0.5rem;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
</style>
