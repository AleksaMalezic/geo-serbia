<script setup>
defineProps({
  round: { type: Number, required: true },
  total: { type: Number, default: 5 },
});
</script>

<template>
  <div class="round-progress">
    <div class="round-progress__text">Round {{ round }} / {{ total }}</div>
    <div class="round-progress__bar">
      <div class="round-progress__fill" :style="{ width: `${(round / total) * 100}%` }" />
    </div>
  </div>
</template>
