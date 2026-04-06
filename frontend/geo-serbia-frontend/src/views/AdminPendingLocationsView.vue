<script setup>
import { onMounted, ref } from "vue";
import { locationsApi } from "../api/locations";

const loading = ref(true);
const actionLoadingId = ref(null);
const error = ref("");
const items = ref([]);

function imageUrl(raw) {
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
  return raw.startsWith("/") ? raw : `/${raw}`;
}

function unwrapList(data) {
  const payload = data?.data ?? data ?? [];
  return Array.isArray(payload) ? payload : [];
}

async function loadPending() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await locationsApi.pending();
    items.value = unwrapList(data);
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to load pending locations.";
  } finally {
    loading.value = false;
  }
}

async function approve(locationId) {
  actionLoadingId.value = locationId;
  try {
    await locationsApi.approve(locationId);
    await loadPending();
  } catch (e) {
    error.value = e?.response?.data?.detail || "Approve failed.";
  } finally {
    actionLoadingId.value = null;
  }
}

async function reject(locationId) {
  actionLoadingId.value = locationId;
  try {
    await locationsApi.reject(locationId);
    await loadPending();
  } catch (e) {
    error.value = e?.response?.data?.detail || "Reject failed.";
  } finally {
    actionLoadingId.value = null;
  }
}

onMounted(loadPending);
</script>

<template>
  <section class="container admin-pending-page">
    <div class="panel">
      <div class="admin-page-head">
        <h1>Pending Locations</h1>
        <button class="btn btn-ghost" :disabled="loading" @click="loadPending">Reload</button>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
      <div v-if="loading">Loading...</div>

      <div v-else-if="items.length === 0" class="admin-empty">No pending locations.</div>

      <div v-else class="admin-pending-list">
        <article v-for="item in items" :key="item.id" class="admin-pending-card">
          <img v-if="item.image_url" :src="imageUrl(item.image_url)" alt="Pending location image" />
          <div class="admin-pending-meta">
            <h3>{{ item.name }}</h3>
            <p v-if="item.description">{{ item.description }}</p>
            <p>Lat: {{ item.latitude }} | Lng: {{ item.longitude }}</p>
            <p>Submitted by user #{{ item.created_by_id }}</p>
          </div>
          <div class="admin-actions">
            <button class="btn btn-primary" :disabled="actionLoadingId === item.id" @click="approve(item.id)">
              Approve
            </button>
            <button class="btn btn-danger" :disabled="actionLoadingId === item.id" @click="reject(item.id)">
              Delete
            </button>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
