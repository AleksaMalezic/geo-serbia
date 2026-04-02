<template>
  <section class="card">
    <h2>Create Location (multipart POST /api/v1/locations/)</h2>
    <form class="grid-form" @submit.prevent="emitSubmit">
      <input v-model.trim="name" placeholder="Name" required />
      <input v-model.trim="description" placeholder="Description" />
      <input v-model.number="latitude" type="number" step="any" placeholder="Latitude" required />
      <input v-model.number="longitude" type="number" step="any" placeholder="Longitude" required />
      <input type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" @change="handleFileChange" />
      <button type="submit">Create Location</button>
    </form>
  </section>
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(["submit"]);

const name = ref("");
const description = ref("");
const latitude = ref(null);
const longitude = ref(null);
const image = ref(null);

function handleFileChange(event) {
  const [file] = event.target.files || [];
  image.value = file || null;
}

function resetForm() {
  name.value = "";
  description.value = "";
  latitude.value = null;
  longitude.value = null;
  image.value = null;
}

function emitSubmit() {
  emit("submit", {
    name: name.value,
    description: description.value,
    latitude: latitude.value,
    longitude: longitude.value,
    image: image.value,
    resetForm,
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
</style>
