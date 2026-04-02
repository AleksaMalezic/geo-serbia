<template>
  <header class="topbar">
    <div>
      <h1>GeoSerbia</h1>
      <p v-if="profile">
        Signed in as <strong>{{ profile.username }}</strong>
        <span v-if="profile.is_admin">(admin)</span>
      </p>
    </div>
    <button type="button" @click="$emit('logout')">Logout</button>
  </header>
</template>

<script setup>
defineProps({
  profile: {
    type: Object,
    default: null,
  },
});

defineEmits(["logout"]);
</script>

<style scoped>
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
</style>
