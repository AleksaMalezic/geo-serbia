import { reactive } from "vue";
import { authApi } from "../api/auth";
import { clearStoredToken, setStoredToken } from "../api/token";

const state = reactive({
  user: null,
  sessionHydrated: false,
});

function unwrapPayload(raw) {
  return raw?.data ?? raw;
}

function extractToken(payload) {
  return (
    payload?.access_token ||
    payload?.access ||
    payload?.token ||
    payload?.jwt ||
    payload?.accessToken ||
    payload?.auth_token ||
    null
  );
}

function userFromPayload(payload) {
  return payload?.user ?? payload?.profile ?? payload ?? null;
}

export function useAuthStore() {
  return state;
}

export async function ensureSession() {
  try {
    const { data } = await authApi.me();
    const payload = unwrapPayload(data);
    state.user = userFromPayload(payload);
  } catch {
    state.user = null;
    clearStoredToken();
  } finally {
    state.sessionHydrated = true;
  }
}

export async function login(payload) {
  const { data } = await authApi.login(payload);
  const body = unwrapPayload(data);
  const token = extractToken(body);
  if (token) setStoredToken(token);
  const fallbackUser = body?.user ?? body?.profile ?? null;
  if (fallbackUser) {
    state.user = fallbackUser;
    return state.user;
  }

  try {
    const me = await authApi.me();
    const mePayload = unwrapPayload(me.data);
    state.user = userFromPayload(mePayload);
  } catch (err) {
    state.user = null;
    clearStoredToken();
    throw err;
  }
  return state.user;
}

export async function register(payload) {
  const { data } = await authApi.register(payload);
  const body = unwrapPayload(data);
  const token = extractToken(body);
  if (token) setStoredToken(token);
  state.user = userFromPayload(body);
  return state.user;
}

export async function logout() {
  try {
    await authApi.logout();
  } finally {
    clearStoredToken();
  }
  state.user = null;
}
