<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/tabs/home" text="Geri" />
        </ion-buttons>
        <ion-title>{{ product?.name || 'Ürün' }}</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content>
      <div class="ion-text-center ion-padding" v-if="loading">
        <ion-spinner name="crescent" />
      </div>

      <template v-else-if="product">
        <img :src="product.image_url" :alt="product.name" class="product-hero" />

        <div class="product-detail ion-padding">
          <div class="detail-top">
            <div>
              <span class="brand">{{ product.brand }}</span>
              <h1>{{ product.name }}</h1>
              <span class="category-tag">{{ product.category?.name }}</span>
            </div>
            <div class="price-block">
              <span class="old-price" v-if="product.discount_price">{{ product.price }} ₺</span>
              <span class="main-price">{{ product.discount_price || product.price }} ₺</span>
              <span class="unit">/{{ product.unit }}</span>
            </div>
          </div>

          <p class="description" v-if="product.description">{{ product.description }}</p>

          <div class="stock-info">
            <ion-badge :color="product.is_in_stock ? 'success' : 'danger'">
              {{ product.is_in_stock ? 'Stokta' : 'Tükendi' }}
            </ion-badge>
            <span class="stock-count" v-if="product.is_in_stock">{{ product.stock }} adet mevcut</span>
          </div>

          <div class="barcode" v-if="product.barcode">
            <ion-icon :icon="barcodeOutline" />
            <span>{{ product.barcode }}</span>
          </div>

          <!-- Quantity selector -->
          <div class="qty-section" v-if="product.is_in_stock">
            <span class="qty-label">Adet:</span>
            <div class="qty-controls">
              <ion-button fill="outline" size="small" @click="qty > 1 && qty--">
                <ion-icon :icon="removeOutline" slot="icon-only" />
              </ion-button>
              <span class="qty-val">{{ qty }}</span>
              <ion-button fill="outline" size="small" @click="qty < product.stock && qty++">
                <ion-icon :icon="addOutline" slot="icon-only" />
              </ion-button>
            </div>
          </div>

          <ion-button
            expand="block"
            class="add-cart-btn"
            :disabled="!product.is_in_stock"
            @click="addToCart"
          >
            <ion-icon :icon="cartOutline" slot="start" />
            {{ product.is_in_stock ? `Sepete Ekle — ${((product.discount_price || product.price) * qty).toFixed(2)} ₺` : 'Stokta Yok' }}
          </ion-button>
        </div>
      </template>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import api from '../services/api'
import { cartOutline, addOutline, removeOutline, barcodeOutline } from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons,
  IonBackButton, IonSpinner, IonButton, IonIcon, IonBadge, toastController
} from '@ionic/vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref(null)
const loading = ref(true)
const qty = ref(1)

onMounted(async () => {
  try {
    const res = await api.get(`/products/${route.params.id}`)
    product.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

async function addToCart() {
  try {
    await cartStore.addToCart(product.value.id, qty.value)
    const toast = await toastController.create({
      message: `${qty.value}x ${product.value.name} sepete eklendi`,
      duration: 2000, color: 'success', position: 'bottom'
    })
    await toast.present()
    router.back()
  } catch (err) {
    const toast = await toastController.create({
      message: err.response?.data?.detail || 'Eklenemedi',
      duration: 2000, color: 'danger', position: 'bottom'
    })
    await toast.present()
  }
}
</script>

<style scoped>
.product-hero { width: 100%; height: 250px; object-fit: cover; }
.product-detail { padding-top: 16px; }
.detail-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.brand { font-size: 13px; color: var(--ion-color-medium); }
h1 { font-size: 22px; font-weight: 700; margin: 4px 0 8px; }
.category-tag { font-size: 12px; background: var(--ion-color-light); padding: 4px 10px; border-radius: 12px; }
.price-block { text-align: right; }
.old-price { display: block; text-decoration: line-through; color: var(--ion-color-medium); font-size: 14px; }
.main-price { font-size: 28px; font-weight: 700; color: var(--ion-color-primary); }
.unit { font-size: 14px; color: var(--ion-color-medium); }

.description { color: var(--ion-color-dark); margin-bottom: 16px; line-height: 1.5; }
.stock-info { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.stock-count { font-size: 13px; color: var(--ion-color-medium); }
.barcode { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--ion-color-medium); font-family: monospace; margin-bottom: 20px; }

.qty-section { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.qty-label { font-size: 16px; font-weight: 600; }
.qty-controls { display: flex; align-items: center; gap: 8px; }
.qty-val { font-size: 20px; font-weight: 700; min-width: 30px; text-align: center; }

.add-cart-btn { --padding-top: 14px; --padding-bottom: 14px; font-size: 16px; font-weight: 700; margin-top: 8px; }
</style>
