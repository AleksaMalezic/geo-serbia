<script setup>
import { computed, ref } from "vue";
import { leaderboardApi } from "../api/leaderboard";
import { useAuthStore } from "../stores/authStore";

const auth = useAuthStore();
const activeTab = ref("daily");
const loading = ref(true);
const rows = ref([]);

const userId = computed(() => auth.user?.id);
const currentUsername = computed(() => auth.user?.username || auth.user?.email || "");

function medal(rank) {
  if (rank === 1) return "\u{1F947}";
  if (rank === 2) return "\u{1F948}";
  if (rank === 3) return "\u{1F949}";
  return `${rank}.`;
}

function pickScore(entry) {
  return Number(entry?.score ?? entry?.points ?? entry?.total_score ?? entry?.total_points ?? 0);
}

function pickUserId(entry) {
  return entry?.user_id ?? entry?.id ?? null;
}

function pickUsername(entry) {
  return entry?.username ?? entry?.user ?? entry?.email ?? "Unknown";
}

function normalizeRows(payload) {
  return payload.map((entry) => ({
    userId: pickUserId(entry),
    username: pickUsername(entry),
    score: pickScore(entry),
    raw: entry,
  }));
}

function dedupeMonthlyByBest(rowsInput) {
  const byUser = new Map();
  for (const row of rowsInput) {
    const key = row.userId != null ? `id:${row.userId}` : `name:${row.username.toLowerCase()}`;
    const existing = byUser.get(key);
    if (!existing || row.score > existing.score) {
      byUser.set(key, row);
    }
  }
  return [...byUser.values()].sort((a, b) => b.score - a.score);
}

async function loadData() {
  loading.value = true;
  try {
    const { data } = activeTab.value === "daily" ? await leaderboardApi.daily() : await leaderboardApi.monthly();
    const payload = data?.data || data || [];
    const normalized = normalizeRows(Array.isArray(payload) ? payload : []);
    rows.value = activeTab.value === "monthly" ? dedupeMonthlyByBest(normalized) : normalized;
  } finally {
    loading.value = false;
  }
}

function setTab(tab) {
  if (activeTab.value === tab) return;
  activeTab.value = tab;
  loadData();
}

loadData();
</script>

<template>
  <section class="container leaderboard-page">
    <div class="panel">
      <h1>Leaderboard</h1>
      <div class="tabs">
        <button :class="['tab', { active: activeTab === 'daily' }]" @click="setTab('daily')">Daily</button>
        <button :class="['tab', { active: activeTab === 'monthly' }]" @click="setTab('monthly')">Monthly</button>
      </div>

      <div v-if="loading">Loading...</div>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, i) in rows"
            :key="row.userId ?? `${row.username}-${i}`"
            :class="{ 'is-current-user': row.userId === userId || row.username === currentUsername }"
          >
            <td>{{ medal(i + 1) }}</td>
            <td>{{ row.username }}</td>
            <td>{{ row.score }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
