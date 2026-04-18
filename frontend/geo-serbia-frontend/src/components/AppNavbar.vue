<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { logout, useAuthStore } from "../stores/authStore";

const auth = useAuthStore();
const router = useRouter();
const displayName = computed(() => auth.user?.username || auth.user?.email || "Player");
const isAdmin = computed(() => Boolean(auth.user?.is_admin));

async function onLogout() {
  await logout();
  router.push({ name: "auth" });
}
</script>

<template>
  <header class="nav-wrap">
    <nav class="nav container">
      <RouterLink class="brand" to="/">Geo Serbia</RouterLink>
      <div class="nav-links">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/profile">Profile</RouterLink>
        <RouterLink to="/leaderboard">Leaderboard</RouterLink>
        <RouterLink to="/add-location">Add Location</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin/pending-locations">Pending Locations</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin/locations">Manage Locations</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin/adaptive-stats">Adaptive Analytics</RouterLink>
      </div>
      <div class="nav-user">
        <span>{{ displayName }}</span>
        <button class="btn btn-ghost" @click="onLogout">Logout</button>
      </div>
    </nav>
  </header>
</template>
