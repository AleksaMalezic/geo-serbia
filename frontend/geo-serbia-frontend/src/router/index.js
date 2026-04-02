import { createRouter, createWebHistory } from "vue-router";
import { ensureSession, useAuthStore } from "../stores/authStore";

const routes = [
  { path: "/auth", name: "auth", component: () => import("../views/AuthView.vue"), meta: { guestOnly: true } },
  { path: "/", name: "home", component: () => import("../views/HomeView.vue"), meta: { requiresAuth: true } },
  { path: "/game", name: "game", component: () => import("../views/GameView.vue"), meta: { requiresAuth: true } },
  { path: "/summary", name: "summary", component: () => import("../views/SummaryView.vue"), meta: { requiresAuth: true } },
  { path: "/leaderboard", name: "leaderboard", component: () => import("../views/LeaderboardView.vue"), meta: { requiresAuth: true } },
  { path: "/profile", name: "profile", component: () => import("../views/ProfileView.vue"), meta: { requiresAuth: true } },
  { path: "/add-location", name: "add-location", component: () => import("../views/AddLocationView.vue"), meta: { requiresAuth: true } },
  {
    path: "/admin/pending-locations",
    name: "admin-pending-locations",
    component: () => import("../views/AdminPendingLocationsView.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/admin/adaptive-stats",
    name: "admin-adaptive-stats",
    component: () => import("../views/AdminAdaptiveStatsView.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.sessionHydrated) {
    await ensureSession();
  }

  if (to.meta.requiresAuth && !auth.user) {
    return { name: "auth" };
  }

  if (to.meta.guestOnly && auth.user) {
    return { name: "home" };
  }

  if (to.meta.requiresAdmin && !auth.user?.is_admin) {
    return { name: "home" };
  }

  return true;
});

export default router;
