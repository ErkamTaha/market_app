import { createRouter, createWebHistory } from 'vue-router'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import OrdersView from './views/OrdersView.vue'
import ProductsView from './views/ProductsView.vue'
import MapEditorView from './views/MapEditorView.vue'

const routes = [
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/', name: 'Dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/orders', name: 'Orders', component: OrdersView, meta: { requiresAuth: true } },
  { path: '/products', name: 'Products', component: ProductsView, meta: { requiresAuth: true } },
  { path: '/map', name: 'MapEditor', component: MapEditorView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('market_admin_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
