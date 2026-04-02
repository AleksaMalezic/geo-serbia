<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppNavbar from "./components/AppNavbar.vue";

const route = useRoute();
const hideNavbar = computed(() => route.name === "auth");
</script>

<template>
  <div class="app-shell">
    <AppNavbar v-if="!hideNavbar" />
    <main :class="['app-main', { 'with-nav': !hideNavbar }]">
      <RouterView />
    </main>
  </div>
</template>
