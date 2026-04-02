<script setup>
import { computed, toRef } from "vue";
import { useCountUp } from "../composables/useCountUp";

const props = defineProps({
  points: { type: Number, default: 0 },
  distanceKm: { type: Number, default: 0 },
});

const animatedPoints = useCountUp(toRef(props, "points"), 800);
const distanceText = computed(() => Number(props.distanceKm || 0).toFixed(2));
</script>

<template>
  <div class="score-box">
    <div class="score-box__points">+{{ animatedPoints }} pts</div>
    <div class="score-box__distance">{{ distanceText }} km away</div>
  </div>
</template>
