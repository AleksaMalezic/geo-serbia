<script setup>
import { computed, onMounted, ref } from "vue";
import { locationsApi } from "../api/locations";

const loading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const error = ref("");
const success = ref("");
const items = ref([]);
const selectedId = ref(null);

const filters = ref({
  search: "",
  approved: "all",
  page: 1,
  limit: 100,
});

const form = ref({
  name: "",
  description: "",
  hintsText: "",
  latitude: "",
  longitude: "",
  image_url: "",
  is_approved: false,
});

const selectedItem = computed(() => items.value.find((item) => item.id === selectedId.value) || null);

function imageUrl(raw) {
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
  return raw.startsWith("/") ? raw : `/${raw}`;
}

function toHintsText(hints) {
  if (!Array.isArray(hints)) return "";
  return hints.join("\n");
}

function parseHints(text) {
  const rows = String(text || "")
    .split("\n")
    .map((row) => row.trim())
    .filter(Boolean);
  return rows.slice(0, 3);
}

function fillForm(item) {
  selectedId.value = item.id;
  form.value = {
    name: item.name || "",
    description: item.description || "",
    hintsText: toHintsText(item.hints),
    latitude: String(item.latitude ?? ""),
    longitude: String(item.longitude ?? ""),
    image_url: item.image_url || "",
    is_approved: Boolean(item.is_approved),
  };
  success.value = "";
  error.value = "";
}

function buildParams() {
  const params = {
    page: filters.value.page,
    limit: filters.value.limit,
  };
  if (filters.value.search.trim()) {
    params.search = filters.value.search.trim();
  }
  if (filters.value.approved === "approved") {
    params.approved = true;
  } else if (filters.value.approved === "pending") {
    params.approved = false;
  }
  return params;
}

function unwrapItems(data) {
  const payload = data?.data ?? data ?? {};
  return Array.isArray(payload?.items) ? payload.items : [];
}

async function loadLocations() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await locationsApi.adminAll(buildParams());
    items.value = unwrapItems(data);
    if (!selectedItem.value && items.value.length) {
      fillForm(items.value[0]);
    }
    if (!items.value.length) {
      selectedId.value = null;
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to load locations.";
    items.value = [];
    selectedId.value = null;
  } finally {
    loading.value = false;
  }
}

async function saveSelected() {
  if (!selectedId.value) return;
  saving.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = {
      name: form.value.name.trim(),
      description: form.value.description.trim() || null,
      hints: parseHints(form.value.hintsText),
      latitude: Number(form.value.latitude),
      longitude: Number(form.value.longitude),
      image_url: form.value.image_url.trim() || null,
      is_approved: Boolean(form.value.is_approved),
    };
    await locationsApi.update(selectedId.value, payload);
    success.value = "Location updated.";
    await loadLocations();
  } catch (e) {
    error.value = e?.response?.data?.detail || "Update failed.";
  } finally {
    saving.value = false;
  }
}

async function deleteSelected() {
  if (!selectedId.value || deleting.value) return;
  const ok = window.confirm("Delete selected location?");
  if (!ok) return;
  deleting.value = true;
  error.value = "";
  success.value = "";
  try {
    const id = selectedId.value;
    await locationsApi.delete(id);
    success.value = "Location deleted.";
    selectedId.value = null;
    await loadLocations();
  } catch (e) {
    error.value = e?.response?.data?.detail || "Delete failed.";
  } finally {
    deleting.value = false;
  }
}

onMounted(loadLocations);
</script>

<template>
  <section class="container admin-locations-page">
    <div class="panel">
      <div class="admin-page-head">
        <h1>Manage Locations</h1>
        <button class="btn btn-ghost" :disabled="loading" @click="loadLocations">Reload</button>
      </div>

      <div class="admin-locations-filters">
        <input v-model="filters.search" type="text" placeholder="Search by name/description" />
        <select v-model="filters.approved">
          <option value="all">All</option>
          <option value="approved">Approved</option>
          <option value="pending">Pending</option>
        </select>
        <button class="btn btn-primary" :disabled="loading" @click="loadLocations">Apply</button>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <p v-if="success" class="success-text">{{ success }}</p>
      <div v-if="loading">Loading...</div>

      <div v-else class="admin-locations-layout">
        <div class="admin-locations-list">
          <button
            v-for="item in items"
            :key="item.id"
            class="admin-location-row"
            :class="{ active: item.id === selectedId }"
            @click="fillForm(item)"
          >
            <div>
              <strong>{{ item.name }}</strong>
              <p>#{{ item.id }} | {{ item.is_approved ? "approved" : "pending" }}</p>
            </div>
          </button>
          <p v-if="!items.length" class="admin-empty">No locations found.</p>
        </div>

        <div v-if="selectedId" class="admin-locations-editor">
          <img v-if="form.image_url" :src="imageUrl(form.image_url)" alt="Location image" class="admin-location-image" />
          <label>
            Name
            <input v-model="form.name" type="text" />
          </label>
          <label>
            Description
            <input v-model="form.description" type="text" />
          </label>
          <label>
            Hints (max 3, each in new line)
            <textarea v-model="form.hintsText" rows="4"></textarea>
          </label>
          <label>
            Latitude
            <input v-model="form.latitude" type="number" step="0.000001" />
          </label>
          <label>
            Longitude
            <input v-model="form.longitude" type="number" step="0.000001" />
          </label>
          <label>
            Image URL
            <input v-model="form.image_url" type="text" />
          </label>
          <label class="admin-checkbox">
            <input v-model="form.is_approved" type="checkbox" />
            Approved
          </label>

          <div class="admin-editor-actions">
            <button class="btn btn-primary" :disabled="saving || deleting" @click="saveSelected">
              {{ saving ? "Saving..." : "Save Changes" }}
            </button>
            <button class="btn btn-danger" :disabled="saving || deleting" @click="deleteSelected">
              {{ deleting ? "Deleting..." : "Delete" }}
            </button>
          </div>
        </div>

        <div v-else class="admin-empty">Select a location to edit.</div>
      </div>
    </div>
  </section>
</template>
