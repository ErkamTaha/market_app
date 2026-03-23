<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/tabs/home" text="Geri" />
        </ion-buttons>
        <ion-title>{{ categoryName }}</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="ion-text-center ion-padding" v-if="loading">
        <ion-spinner name="crescent" />
      </div>

      <div class="empty" v-else-if="products.length === 0">
        <p>Bu kategoride ürün bulunamadı</p>
      </div>

      <div class="product-list" v-else>
        <div v-for="p in products" :key="p.id" class="product-row" @click="router.push(`/product/${p.id}`)">
          <img :src="p.image_url" :alt="p.name" class="row-img" />
          <div class="row-info">
            <span class="row-brand">{{ p.brand }}</span>
            <span class="row-name">{{ p.name }}</span>
            <div class="row-price">
              <span class="old" v-if="p.discount_price">{{ p.price }} ₺</span>
              <span class="current">{{ p.discount_price || p.price }} ₺</span>
              <span class="unit">/{{ p.unit }}</span>
            </div>
          </div>
          <ion-button fill="outline" size="small" @click.stop="addToCart(p)">
            <ion-icon :icon="addOutline" slot="icon-only" />
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import api from '../services/api'
import { addOutline } from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons,
  IonBackButton, IonSpinner, IonButton, IonIcon, toastController
} from '@ionic/vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const products = ref([])
const categoryName = ref('')
const loading = ref(true)

async function loadCategory(id) {
  loading.value = true
  try {
    const [catRes, prodRes] = await Promise.all([
      api.get('/products/categories'),
      api.get('/products/', { params: { category_id: id } })
    ])
    const cat = catRes.data.find(c => c.id === parseInt(id))
    categoryName.value = cat?.name || 'Kategori'
    products.value = prodRes.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadCategory(route.params.id))
watch(() => route.params.id, (newId) => { if (newId) loadCategory(newId) })

async function addToCart(product) {
  try {
    await cartStore.addToCart(product.id, 1)
    const toast = await toastController.create({ message: `${product.name} sepete eklendi`, duration: 1500, color: 'success', position: 'bottom' })
    await toast.present()
  } catch (err) {
    const toast = await toastController.create({ message: err.response?.data?.detail || 'Eklenemedi', duration: 2000, color: 'danger', position: 'bottom' })
    await toast.present()
  }
}
</script>

<style scoped>
.empty { text-align: center; padding: 60px 20px; color: var(--ion-color-medium); }
.product-list { display: flex; flex-direction: column; gap: 12px; }
.product-row { display: flex; align-items: center; gap: 12px; padding: 8px; background: var(--ion-background-color); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); cursor: pointer; }
.row-img { width: 64px; height: 64px; border-radius: 8px; object-fit: cover; }
.row-info { flex: 1; }
.row-brand { font-size: 11px; color: var(--ion-color-medium); }
.row-name { display: block; font-size: 14px; font-weight: 600; }
.row-price { margin-top: 4px; display: flex; align-items: baseline; gap: 4px; }
.old { text-decoration: line-through; color: var(--ion-color-medium); font-size: 12px; }
.current { font-size: 16px; font-weight: 700; color: var(--ion-color-primary); }
.unit { font-size: 11px; color: var(--ion-color-medium); }
</style>
