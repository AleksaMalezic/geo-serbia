<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { login, logout, register } from "../stores/authStore";

const router = useRouter();
const isLogin = ref(true);
const loading = ref(false);
const error = ref("");

const form = reactive({
  username: "",
  email: "",
  password: "",
});

function toggleMode() {
  error.value = "";
  isLogin.value = !isLogin.value;
}

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    if (isLogin.value) {
      await login({
        username: form.email,
        email: form.email,
        password: form.password,
      });
      router.push({ name: "home" });
    } else {
      await register({ username: form.username, email: form.email, password: form.password });
      await logout();
      isLogin.value = true;
      form.password = "";
    }
  } catch (e) {
    const detail = e?.response?.data?.detail;
    error.value = Array.isArray(detail) ? JSON.stringify(detail) : detail || "Authentication failed.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-card">
      <h1>{{ isLogin ? "Welcome back" : "Create account" }}</h1>
      <p>Play the Serbia daily geography challenge.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label v-if="!isLogin">
          Username
          <input v-model="form.username" required type="text" />
        </label>
        <label>
          {{ isLogin ? "Username or Email" : "Email" }}
          <input v-model="form.email" required :type="isLogin ? 'text' : 'email'" />
        </label>
        <label>
          Password
          <input v-model="form.password" required type="password" />
        </label>
        <button class="btn btn-primary" :disabled="loading">
          {{ loading ? "Please wait..." : isLogin ? "Login" : "Register" }}
        </button>
      </form>

      <button class="btn btn-link" @click="toggleMode">
        {{ isLogin ? "Need an account? Register" : "Already have an account? Login" }}
      </button>
      <p v-if="error" class="error-text">{{ error }}</p>
    </div>
  </section>
</template>
