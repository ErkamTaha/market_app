import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('market_access_token') || null)
  const isLoggedIn = ref(!!token.value)

  async function register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  }

  async function login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    token.value = response.data.access_token
    localStorage.setItem('market_access_token', response.data.access_token)
    isLoggedIn.value = true
    await fetchProfile()
    return response.data
  }

  async function fetchProfile() {
    const response = await api.get('/users/me')
    user.value = response.data
    return response.data
  }

  function logout() {
    token.value = null
    user.value = null
    isLoggedIn.value = false
    localStorage.removeItem('market_access_token')
  }

  return { user, token, isLoggedIn, register, login, fetchProfile, logout }
})
