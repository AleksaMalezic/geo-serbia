<script setup>
import { reactive, ref } from "vue";
import { locationsApi } from "../api/locations";
import GameMap from "../components/GameMap.vue";

const form = reactive({
  name: "",
  description: "",
  hint1: "",
  hint2: "",
  hint3: "",
  latitude: "",
  longitude: "",
  image: null,
});

const loading = ref(false);
const success = ref("");
const error = ref("");

function onMapGuess(value) {
  form.latitude = value.lat.toFixed(6);
  form.longitude = value.lng.toFixed(6);
}

function onImageChange(event) {
  const file = event?.target?.files?.[0] || null;
  form.image = file;
}

async function onSubmit() {
  loading.value = true;
  success.value = "";
  error.value = "";
  try {
    await locationsApi.create({
      name: form.name,
      description: form.description,
      hints: [form.hint1, form.hint2, form.hint3].map((h) => h.trim()).filter(Boolean),
      latitude: Number(form.latitude),
      longitude: Number(form.longitude),
      image: form.image,
    });
    success.value = "Location added.";
    form.name = "";
    form.description = "";
    form.hint1 = "";
    form.hint2 = "";
    form.hint3 = "";
    form.latitude = "";
    form.longitude = "";
    form.image = null;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to add location.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="container add-location-page">
    <div class="panel add-location-layout">
      <div>
        <h1>Add Location</h1>
        <p>Click map to auto-fill coordinates.</p>
        <form class="stack-form" @submit.prevent="onSubmit">
          <label>
            Name
            <input v-model="form.name" required type="text" />
          </label>
          <label>
            Description
            <input v-model="form.description" type="text" />
          </label>
          <label>
            Hint 1 (optional)
            <input v-model="form.hint1" type="text" />
          </label>
          <label>
            Hint 2 (optional)
            <input v-model="form.hint2" type="text" />
          </label>
          <label>
            Hint 3 (optional)
            <input v-model="form.hint3" type="text" />
          </label>
          <label>
            Latitude
            <input v-model="form.latitude" required type="number" step="any" />
          </label>
          <label>
            Longitude
            <input v-model="form.longitude" required type="number" step="any" />
          </label>
          <label>
            Image (jpg/png, optional)
            <input type="file" accept=".jpg,.jpeg,.png,image/png,image/jpeg" @change="onImageChange" />
          </label>
          <button class="btn btn-primary" :disabled="loading">
            {{ loading ? "Saving..." : "Save Location" }}
          </button>
          <p v-if="success" class="success-text">{{ success }}</p>
          <p v-if="error" class="error-text">{{ error }}</p>
        </form>
      </div>
      <GameMap
        :interactive="true"
        :guess-marker="form.latitude && form.longitude ? { lat: Number(form.latitude), lng: Number(form.longitude) } : null"
        :show-result="false"
        @guess="onMapGuess"
      />
    </div>
  </section>
</template>
