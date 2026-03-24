<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Market</h1>
      <p class="subtitle">Admin Panel</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" placeholder="admin@market.com" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" placeholder="••••••••" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        <p class="error-msg" v-if="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.post('/auth/login', { email: email.value, password: password.value })
    localStorage.setItem('market_admin_token', response.data.access_token)
    router.push('/')
  } catch (err) {
    error.value = 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>
