<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import L from "leaflet";

const props = defineProps({
  interactive: { type: Boolean, default: true },
  guessMarker: { type: Object, default: null },
  realMarker: { type: Object, default: null },
  showResult: { type: Boolean, default: false },
  center: { type: Array, default: () => [44.0165, 21.0059] },
  zoom: { type: Number, default: 7 },
});

const emit = defineEmits(["guess"]);
const mapEl = ref(null);
let map = null;
let guessLayer = null;
let realLayer = null;
let lineLayer = null;
let drawRaf = null;

function normalizePoint(point) {
  if (!point) return null;
  if (Array.isArray(point)) return point;
  return [point.lat, point.lng];
}

function setGuessLayer() {
  if (!map) return;
  if (guessLayer) map.removeLayer(guessLayer);
  const g = normalizePoint(props.guessMarker);
  if (!g) return;
  guessLayer = L.circleMarker(g, {
    radius: 8,
    color: "#1f6feb",
    fillColor: "#59a8ff",
    fillOpacity: 1,
    weight: 2,
  }).addTo(map);
}

function setRealLayer() {
  if (!map) return;
  if (realLayer) map.removeLayer(realLayer);
  const r = normalizePoint(props.realMarker);
  if (!r) return;
  realLayer = L.circleMarker(r, {
    radius: 8,
    color: "#0a7f3f",
    fillColor: "#31d985",
    fillOpacity: 1,
    weight: 2,
  }).addTo(map);
}

function animateLineAndFit() {
  cancelAnimationFrame(drawRaf);
  if (!map || !props.showResult) return;
  const g = normalizePoint(props.guessMarker);
  const r = normalizePoint(props.realMarker);
  if (!g || !r) return;

  if (lineLayer) map.removeLayer(lineLayer);
  lineLayer = L.polyline([g, g], {
    color: "#f7b500",
    dashArray: "8 10",
    weight: 3,
    opacity: 0.9,
  }).addTo(map);

  const start = performance.now();
  const duration = 750;

  const tick = (now) => {
    const t = Math.min((now - start) / duration, 1);
    const p = [g[0] + (r[0] - g[0]) * t, g[1] + (r[1] - g[1]) * t];
    lineLayer.setLatLngs([g, p]);
    if (t < 1) {
      drawRaf = requestAnimationFrame(tick);
    } else {
      lineLayer.setLatLngs([g, r]);
    }
  };

  drawRaf = requestAnimationFrame(tick);
}

function clearResultLayers() {
  if (!map) return;
  if (lineLayer) {
    map.removeLayer(lineLayer);
    lineLayer = null;
  }
  if (realLayer) {
    map.removeLayer(realLayer);
    realLayer = null;
  }
}

onMounted(() => {
  map = L.map(mapEl.value, { zoomControl: true }).setView(props.center, props.zoom);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  map.on("click", (e) => {
    if (!props.interactive || props.showResult) return;
    emit("guess", { lat: e.latlng.lat, lng: e.latlng.lng });
  });

  setGuessLayer();
});

watch(
  () => [props.guessMarker, props.realMarker, props.showResult],
  () => {
    setGuessLayer();
    setRealLayer();
    if (props.showResult) animateLineAndFit();
    else clearResultLayers();
  },
  { deep: true }
);

onBeforeUnmount(() => {
  cancelAnimationFrame(drawRaf);
  if (map) map.remove();
});
</script>

<template>
  <div ref="mapEl" class="game-map"></div>
</template>
