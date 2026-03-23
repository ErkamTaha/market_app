<template>
  <div class="app-layout" v-if="isLoggedIn">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <h2>Market</h2>
        <span class="brand-sub">Yönetim Paneli</span>
      </div>
      <nav class="sidebar-nav">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path"
          class="nav-item" :class="{ active: isActive(item.path) }">
          {{ item.label }}
        </router-link>
      </nav>
      <button class="logout-btn" @click="logout">Çıkış Yap</button>
    </aside>
    <main class="main-content">
      <router-view :key="$route.fullPath" />
    </main>
  </div>
  <div v-else>
    <router-view />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isLoggedIn = ref(!!localStorage.getItem('market_admin_token'))

const navItems = [
  { path: '/', label: 'Genel Bakış' },
  { path: '/orders', label: 'Satışlar' },
  { path: '/products', label: 'Ürünler' },
]

watch(() => route.path, () => {
  isLoggedIn.value = !!localStorage.getItem('market_admin_token')
})

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function logout() {
  localStorage.removeItem('market_admin_token')
  isLoggedIn.value = false
  router.push('/login')
}
</script>
