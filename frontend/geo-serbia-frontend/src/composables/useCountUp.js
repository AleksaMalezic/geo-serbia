import { ref, watch } from "vue";

export function useCountUp(targetRef, duration = 900) {
  const current = ref(0);
  let rafId = null;

  watch(
    targetRef,
    (target) => {
      cancelAnimationFrame(rafId);
      const start = performance.now();
      const from = current.value;
      const delta = Number(target || 0) - from;

      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        current.value = Math.round(from + delta * (1 - Math.pow(1 - progress, 3)));
        if (progress < 1) rafId = requestAnimationFrame(tick);
      };

      rafId = requestAnimationFrame(tick);
    },
    { immediate: true }
  );

  return current;
}
