<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Market</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="welcome" v-if="authStore.user">
        <h2>Hello, {{ authStore.user.full_name.split(' ')[0] }}!</h2>
        <div class="points-badge">
          <ion-icon :icon="starOutline" />
          {{ authStore.user.loyalty_points }} points
        </div>
      </div>

      <!-- In-store location banner -->
      <div class="store-banner">
        <ion-icon :icon="locationOutline" class="store-icon" />
        <div>
          <strong>Market Çerkezköy</strong>
          <p>You are in the store — Scan products to start shopping</p>
        </div>
      </div>

      <!-- Scan & Go button -->
      <ion-button expand="block" class="scan-go-btn" router-link="/tabs/barcode">
        <ion-icon :icon="barcodeOutline" slot="start" />
        Scan Product & Start Shopping
      </ion-button>

      <!-- On sale banner -->
      <div class="sale-banner" @click="router.push('/tabs/search?on_sale=true')">
        <ion-icon :icon="pricetagOutline" class="sale-icon" />
        <div>
          <strong>On Sale</strong>
          <p>Don't miss the deals!</p>
        </div>
        <ion-icon :icon="chevronForwardOutline" />
      </div>

      <!-- Categories grid -->
      <h3 class="section-title">Categories</h3>
      <div class="ion-text-center" v-if="loading">
        <ion-spinner name="crescent" />
      </div>

      <ion-grid class="ion-no-padding" v-else>
        <ion-row>
          <ion-col size="3" v-for="cat in categories" :key="cat.id">
            <div class="cat-card" @click="router.push(`/tabs/categories/${cat.id}`)">
              <ion-icon :icon="getCatIcon(cat.icon)" class="cat-icon" />
              <span class="cat-name">{{ cat.name }}</span>
            </div>
          </ion-col>
        </ion-row>
      </ion-grid>

      <!-- Featured products (on sale) -->
      <h3 class="section-title">Deals</h3>
      <div class="product-scroll">
        <div
          v-for="p in saleProducts"
          :key="p.id"
          class="product-card"
          @click="router.push(`/product/${p.id}`)"
        >
          <img :src="p.image_url" :alt="p.name" class="product-img" />
          <div class="product-info">
            <span class="product-brand">{{ p.brand }}</span>
            <span class="product-name">{{ p.name }}</span>
            <div class="price-row">
              <span class="old-price" v-if="p.discount_price">{{ p.price }} ₺</span>
              <span class="current-price">{{ p.discount_price || p.price }} ₺</span>
              <span class="unit">/{{ p.unit }}</span>
            </div>
          </div>
          <ion-button size="small" fill="solid" class="add-btn" @click.stop="addToCart(p)">
            <ion-icon :icon="addOutline" />
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import api from '../services/api'
import {
  starOutline, pricetagOutline, chevronForwardOutline, addOutline,
  leafOutline, waterOutline, restaurantOutline, pizzaOutline,
  beerOutline, fastFoodOutline, sparklesOutline, bodyOutline,
  locationOutline, barcodeOutline
} from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
  IonGrid, IonRow, IonCol, IonIcon, IonSpinner, IonButton,
  toastController
} from '@ionic/vue'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const categories = ref([])
const saleProducts = ref([])
const loading = ref(true)

const iconMap = {
  'leaf-outline': leafOutline,
  'water-outline': waterOutline,
  'restaurant-outline': restaurantOutline,
  'pizza-outline': pizzaOutline,
  'beer-outline': beerOutline,
  'fast-food-outline': fastFoodOutline,
  'sparkles-outline': sparklesOutline,
  'body-outline': bodyOutline,
}

function getCatIcon(iconName) {
  return iconMap[iconName] || leafOutline
}

onMounted(async () => {
  try {
    if (authStore.token && !authStore.user) {
      await authStore.fetchProfile()
    }
    const [catRes, saleRes] = await Promise.all([
      api.get('/products/categories'),
      api.get('/products/', { params: { on_sale: true } })
    ])
    categories.value = catRes.data
    saleProducts.value = saleRes.data
  } catch (err) {
    if (err.response?.status === 401) {
      authStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
})

async function addToCart(product) {
  try {
    await cartStore.addToCart(product.id, 1)
    const toast = await toastController.create({
      message: `${product.name} added to cart`,
      duration: 1500, color: 'success', position: 'bottom'
    })
    await toast.present()
  } catch (err) {
    const toast = await toastController.create({
      message: err.response?.data?.detail || 'Could not add',
      duration: 2000, color: 'danger', position: 'bottom'
    })
    await toast.present()
  }
}
</script>

<style scoped>
.welcome { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.welcome h2 { margin: 0; font-size: 20px; }
.points-badge { display: flex; align-items: center; gap: 4px; background: var(--ion-color-warning-tint); padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }

.store-banner { display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: linear-gradient(135deg, #059669, #10b981); color: white; border-radius: 12px; margin-bottom: 12px; }
.store-icon { font-size: 28px; }
.store-banner p { font-size: 12px; opacity: 0.85; margin: 2px 0 0; }

.scan-go-btn { margin-bottom: 12px; --padding-top: 14px; --padding-bottom: 14px; font-size: 16px; font-weight: 700; }

.sale-banner { display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; border-radius: 12px; margin-bottom: 16px; cursor: pointer; }
.sale-icon { font-size: 28px; }
.sale-banner p { font-size: 12px; opacity: 0.85; margin: 2px 0 0; }
.sale-banner > ion-icon:last-child { margin-left: auto; }

.section-title { font-size: 18px; font-weight: 600; margin: 20px 0 12px; }

.cat-card { display: flex; flex-direction: column; align-items: center; padding: 12px 4px; cursor: pointer; border-radius: 12px; transition: background 0.2s; }
.cat-card:active { background: var(--ion-color-light); }
.cat-icon { font-size: 28px; color: var(--ion-color-primary); margin-bottom: 6px; }
.cat-name { font-size: 11px; text-align: center; font-weight: 500; line-height: 1.2; }

.product-scroll { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; -webkit-overflow-scrolling: touch; }
.product-card { min-width: 160px; max-width: 160px; background: var(--ion-background-color); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); position: relative; cursor: pointer; }
.product-img { width: 100%; height: 120px; object-fit: cover; }
.product-info { padding: 8px 10px; }
.product-brand { font-size: 11px; color: var(--ion-color-medium); }
.product-name { display: block; font-size: 13px; font-weight: 600; margin-top: 2px; line-height: 1.2; }
.price-row { margin-top: 6px; display: flex; align-items: baseline; gap: 4px; }
.old-price { text-decoration: line-through; color: var(--ion-color-medium); font-size: 12px; }
.current-price { font-size: 16px; font-weight: 700; color: var(--ion-color-primary); }
.unit { font-size: 11px; color: var(--ion-color-medium); }
.add-btn { position: absolute; bottom: 8px; right: 8px; --padding-start: 6px; --padding-end: 6px; }
</style>
