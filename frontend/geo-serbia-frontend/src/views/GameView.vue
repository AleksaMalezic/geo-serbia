<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { gameApi } from "../api/game";
import { locationsApi } from "../api/locations";
import GameMap from "../components/GameMap.vue";
import RoundProgress from "../components/RoundProgress.vue";
import ScoreCounter from "../components/ScoreCounter.vue";
import {
  applyRoundOutcome,
  getAdaptiveMode,
  getAdaptiveStatsSnapshot,
  selectAdaptiveRounds,
  setAdaptiveMode,
} from "../composables/useAdaptiveDifficulty";

const router = useRouter();
const totalRounds = 5;
const loading = ref(true);
const submitting = ref(false);
const error = ref("");

const sessionId = ref(null);
const roundIndex = ref(1);
const currentRound = ref(null);
const rounds = ref([]);
const guess = ref(null);
const showResult = ref(false);
const roundResult = ref(null);
const allResults = ref([]);
const revealedHints = ref([]);
const hintLoading = ref(false);
const hintsUsedCount = ref(0);
const adaptiveMode = ref(getAdaptiveMode());
const difficultyTier = ref("Normal");
const usedServerAdaptive = ref(false);
const recentImprovementPercent = ref(0);
const skillRating = ref(getAdaptiveStatsSnapshot().current_skill_rating || 52);

const imageUrl = computed(() => {
  const raw = currentRound.value?.image_url || currentRound.value?.image || currentRound.value?.photo_url || "";
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
  return raw.startsWith("/") ? raw : `/${raw}`;
});

const canSubmit = computed(() => !!guess.value && !submitting.value && !showResult.value && !!currentRound.value);
const maxHints = computed(() => {
  const value = Number(currentRound.value?.max_hints ?? 0);
  return Number.isFinite(value) && value > 0 ? value : 0;
});
const canAskHint = computed(() => {
  if (!currentRound.value || showResult.value || hintLoading.value) return false;
  return hintsUsedCount.value < maxHints.value;
});
const adaptiveStatusText = computed(() => {
  const source = usedServerAdaptive.value ? "server" : "local fallback";
  const modeText = adaptiveMode.value === "adaptive" ? "Adaptive" : "Fixed";
  return `${modeText} (${source})`;
});

function setMode(mode) {
  const nextMode = mode === "fixed" ? "fixed" : "adaptive";
  if (adaptiveMode.value === nextMode) return;
  adaptiveMode.value = nextMode;
  setAdaptiveMode(adaptiveMode.value);
  startGame();
}

function parseStartPayload(raw) {
  const payload = raw?.data ?? raw ?? {};
  const items = payload?.rounds || payload?.items || payload?.locations || [];
  const normalized = Array.isArray(items) ? items : [];
  const tier = payload?.difficulty_tier || payload?.difficulty || null;
  const skill = Number(payload?.skill_rating || payload?.skill_rating_before || skillRating.value || 52);
  const session = payload?.session_id || payload?.game_id || `local-${Date.now()}`;
  return { rounds: normalized, tier, skill, session };
}

async function buildClientRounds() {
  const { data } = await locationsApi.list({ approved: true, page: 1, limit: 200 });
  const items = data?.data?.items || data?.items || [];
  if (!Array.isArray(items) || items.length < totalRounds) {
    throw new Error("Not enough approved locations for a 5-round game.");
  }
  return selectAdaptiveRounds(items, totalRounds, adaptiveMode.value);
}

async function startGame() {
  loading.value = true;
  error.value = "";
  usedServerAdaptive.value = false;
  try {
    try {
      const response = await gameApi.startChallenge(adaptiveMode.value);
      const parsed = parseStartPayload(response.data);
      if (!parsed.rounds.length) throw new Error("No rounds from /game/start");
      rounds.value = parsed.rounds.slice(0, totalRounds);
      sessionId.value = parsed.session;
      difficultyTier.value = parsed.tier || "Normal";
      skillRating.value = parsed.skill;
      usedServerAdaptive.value = true;
    } catch {
      rounds.value = await buildClientRounds();
      sessionId.value = `local-${Date.now()}`;
      difficultyTier.value = rounds.value[0]?.adaptive_difficulty || getAdaptiveStatsSnapshot().difficulty_tier || "Normal";
      skillRating.value = getAdaptiveStatsSnapshot().current_skill_rating || 52;
      usedServerAdaptive.value = false;
    }

    currentRound.value = rounds.value[0] || null;
    roundIndex.value = 1;
    guess.value = null;
    showResult.value = false;
    roundResult.value = null;
    allResults.value = [];
    revealedHints.value = [];
    hintsUsedCount.value = 0;
    hintLoading.value = false;
    recentImprovementPercent.value = 0;
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || "Failed to start game.";
  } finally {
    loading.value = false;
  }
}

function onGuess(value) {
  guess.value = value;
}

function toSummary() {
  const totalScore = allResults.value.reduce((sum, r) => sum + r.points, 0);
  const avgDistance =
    allResults.value.length > 0
      ? allResults.value.reduce((sum, r) => sum + r.distanceKm, 0) / allResults.value.length
      : 0;

  const summary = {
    totalScore,
    avgDistance,
    rounds: allResults.value,
    adaptive: {
      mode: adaptiveMode.value,
      tier: difficultyTier.value,
      skillRating: skillRating.value,
    },
  };

  sessionStorage.setItem("lastGameSummary", JSON.stringify(summary));
  router.push({ name: "summary" });
}

async function requestHint() {
  if (!canAskHint.value) return;
  hintLoading.value = true;
  error.value = "";
  try {
    const { data } = await gameApi.requestHint({
      locationId: currentRound.value?.id,
      hintsUsedCount: hintsUsedCount.value,
    });
    const hintData = data?.data || data || {};
    const hintText = hintData?.hint_text || hintData?.hint;
    if (typeof hintText === "string" && hintText.trim()) {
      revealedHints.value.push(hintText.trim());
      hintsUsedCount.value = Number(hintData?.hints_used_count ?? hintsUsedCount.value + 1);
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || "Could not load hint.";
  } finally {
    hintLoading.value = false;
  }
}

async function submitGuess() {
  if (!canSubmit.value) return;
  submitting.value = true;
  error.value = "";

  try {
    const { data } = await gameApi.playRound({
      locationId: currentRound.value?.id,
      guessedLatitude: guess.value.lat,
      guessedLongitude: guess.value.lng,
      hintsUsedCount: hintsUsedCount.value,
    });
    const resultData = data?.data || data || {};
    const localAdaptive = applyRoundOutcome({
      locationId: currentRound.value?.id,
      points: Number(resultData?.points || resultData?.score || 0),
      distanceKm: Number(resultData?.distance_km || resultData?.distance || 0),
    });

    const skillBefore = Number(resultData?.skill_rating_before ?? localAdaptive.skill_rating_before ?? skillRating.value);
    const skillAfter = Number(resultData?.skill_rating_after ?? localAdaptive.skill_rating_after ?? skillBefore);
    const usedDifficulty = resultData?.difficulty_used || resultData?.difficulty || currentRound.value?.adaptive_difficulty || "Normal";

    const result = {
      round: roundIndex.value,
      points: Number(resultData?.points || resultData?.score || 0),
      distanceKm: Number(resultData?.distance_km || resultData?.distance || 0),
      guess: guess.value,
      real: {
        lat: Number(currentRound.value?.latitude),
        lng: Number(currentRound.value?.longitude),
      },
      difficulty_used: usedDifficulty,
      skill_rating_before: skillBefore,
      skill_rating_after: skillAfter,
      base_score: Number(resultData?.base_score || resultData?.score || 0),
      hint_penalty_percent: Number(resultData?.hint_penalty_percent || 0),
      hints_used_count: Number(resultData?.hints_used_count ?? hintsUsedCount.value),
      recent_improvement_percent: Number(
        resultData?.recent_improvement_percent ?? localAdaptive.recent_improvement_percent ?? 0
      ),
    };

    difficultyTier.value = usedDifficulty;
    skillRating.value = skillAfter;
    recentImprovementPercent.value = result.recent_improvement_percent;
    roundResult.value = result;
    showResult.value = true;
    allResults.value.push(result);

    const finished = roundIndex.value >= totalRounds;
    setTimeout(async () => {
      if (finished) {
        toSummary();
        return;
      }

      roundIndex.value += 1;
      guess.value = null;
      showResult.value = false;
      roundResult.value = null;
      revealedHints.value = [];
      hintsUsedCount.value = 0;
      hintLoading.value = false;
      currentRound.value = rounds.value[roundIndex.value - 1] || null;
    }, 2400);
  } catch (e) {
    error.value = e?.response?.data?.detail || "Could not submit guess.";
  } finally {
    submitting.value = false;
  }
}

onMounted(startGame);
</script>

<template>
  <section class="game-page container">
    <div class="game-header-row">
      <RoundProgress :round="roundIndex" :total="5" />
      <div class="adaptive-chip-wrap">
        <span class="adaptive-chip">
          Difficulty: {{ difficultyTier }} | Skill {{ skillRating.toFixed(1) }}
        </span>
        <span class="adaptive-sub">{{ adaptiveStatusText }}</span>
      </div>
      <div class="mode-toggle">
        <button :class="['tab', { active: adaptiveMode === 'adaptive' }]" @click="setMode('adaptive')">Adaptive</button>
        <button :class="['tab', { active: adaptiveMode === 'fixed' }]" @click="setMode('fixed')">Fixed</button>
        <button class="btn btn-ghost" @click="startGame">Restart</button>
      </div>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>
    <div v-if="loading" class="panel">Loading challenge...</div>

    <div v-else class="game-layout">
      <div class="game-left panel">
        <div class="photo-wrap">
          <img v-if="imageUrl" :src="imageUrl" alt="Guess this location" class="location-photo" />
          <div v-else class="empty-photo">No image available</div>
        </div>
        <div v-if="maxHints > 0" class="hint-panel">
          <div class="hint-panel__head">
            <strong>Hints</strong>
            <span>{{ hintsUsedCount }} / {{ maxHints }} used</span>
          </div>
          <button class="btn btn-ghost" :disabled="!canAskHint" @click="requestHint">
            {{ hintLoading ? "Loading..." : "Get Hint" }}
          </button>
          <ul v-if="revealedHints.length" class="hint-list">
            <li v-for="(hint, idx) in revealedHints" :key="`${idx}-${hint}`">{{ hint }}</li>
          </ul>
        </div>
        <button class="btn btn-primary" :disabled="!canSubmit" @click="submitGuess">
          {{ submitting ? "Submitting..." : "Confirm Guess" }}
        </button>
      </div>

      <div class="game-right panel">
        <GameMap
          :interactive="true"
          :guess-marker="guess"
          :real-marker="showResult ? roundResult?.real : null"
          :show-result="showResult"
          @guess="onGuess"
        />
        <Transition name="fade-rise">
          <ScoreCounter
            v-if="showResult"
            :points="roundResult?.points || 0"
            :distance-km="roundResult?.distanceKm || 0"
          />
        </Transition>
        <p v-if="showResult && recentImprovementPercent > 0" class="improvement-text">
          You improved +{{ recentImprovementPercent.toFixed(1) }}% vs recent rounds.
        </p>
        <p v-if="showResult && roundResult?.hints_used_count > 0" class="hint-penalty-text">
          Hint penalty: -{{ Number(roundResult?.hint_penalty_percent || 0).toFixed(0) }}%
        </p>
      </div>
    </div>
  </section>
</template>
