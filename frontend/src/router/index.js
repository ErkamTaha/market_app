import { createRouter, createWebHistory } from '@ionic/vue-router'
import TabsPage from '../views/TabsPage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'

const routes = [
  { path: '/', redirect: '/tabs/home' },
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/register', name: 'Register', component: RegisterPage },
  {
    path: '/tabs/',
    component: TabsPage,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/tabs/home' },
      { path: 'home', name: 'Home', component: () => import('../views/HomePage.vue') },
      { path: 'categories/:id', name: 'Category', component: () => import('../views/CategoryPage.vue') },
      { path: 'search', name: 'Search', component: () => import('../views/SearchPage.vue') },
      { path: 'barcode', name: 'Barcode', component: () => import('../views/BarcodePage.vue') },
      { path: 'map', name: 'Map', component: () => import('../views/MapPage.vue') },
      { path: 'cart', name: 'Cart', component: () => import('../views/CartPage.vue') },
      { path: 'orders', name: 'Orders', component: () => import('../views/OrdersPage.vue') },
      { path: 'profile', name: 'Profile', component: () => import('../views/ProfilePage.vue') },
    ]
  },
  {
    path: '/product/:id',
    name: 'Product',
    component: () => import('../views/ProductPage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('market_access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/tabs/home')
  } else {
    next()
  }
})

export default router
