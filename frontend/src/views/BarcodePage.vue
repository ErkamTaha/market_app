<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/tabs/home" text="Geri" />
        </ion-buttons>
        <ion-title>Barkod Tara</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <!-- Scanner simulation -->
      <div class="scanner-area">
        <div class="scanner-frame">
          <ion-icon :icon="barcodeOutline" class="scan-icon" />
          <p>Barkodu Tarayın</p>
        </div>
      </div>

      <!-- Demo: manual barcode entry -->
      <ion-card class="demo-card">
        <ion-card-header>
          <ion-card-subtitle>Prototip Demo</ion-card-subtitle>
          <ion-card-title>Barkod Girin</ion-card-title>
        </ion-card-header>
        <ion-card-content>
          <p class="demo-note">Gerçek uygulamada kamera ile barkod taranacak. Demo için aşağıdan bir ürün seçin:</p>

          <!-- Quick select barcodes -->
          <div class="barcode-chips">
            <ion-chip
              v-for="item in demoItems"
              :key="item.barcode"
              @click="scanBarcode(item.barcode)"
              :color="selectedBarcode === item.barcode ? 'primary' : 'medium'"
            >
              <ion-label>{{ item.name }}</ion-label>
            </ion-chip>
          </div>

          <!-- Manual input -->
          <ion-item>
            <ion-input v-model="manualBarcode" placeholder="Barkod numarası girin" inputmode="numeric" @keyup.enter="scanBarcode(manualBarcode)" />
            <ion-button slot="end" fill="clear" @click="scanBarcode(manualBarcode)">
              <ion-icon :icon="searchOutline" />
            </ion-button>
          </ion-item>
        </ion-card-content>
      </ion-card>

      <!-- Scanned product result -->
      <ion-card v-if="product" class="result-card">
        <img :src="product.image_url" :alt="product.name" class="result-img" />
        <ion-card-header>
          <ion-card-subtitle>{{ product.brand }} · {{ product.category?.name }}</ion-card-subtitle>
          <ion-card-title>{{ product.name }}</ion-card-title>
        </ion-card-header>
        <ion-card-content>
          <div class="result-price">
            <span class="old" v-if="product.discount_price">{{ product.price }} ₺</span>
            <span class="current">{{ product.discount_price || product.price }} ₺</span>
            <span class="unit">/{{ product.unit }}</span>
          </div>

          <div class="result-stock">
            <ion-badge :color="product.is_in_stock ? 'success' : 'danger'">
              {{ product.is_in_stock ? `Stokta (${product.stock})` : 'Tükendi' }}
            </ion-badge>
          </div>

          <div class="result-barcode">
            <ion-icon :icon="barcodeOutline" />
            <span>{{ product.barcode }}</span>
          </div>

          <!-- Quantity + add to cart -->
          <div class="qty-row" v-if="product.is_in_stock">
            <div class="qty-controls">
              <ion-button fill="outline" size="small" @click="qty > 1 && qty--">
                <ion-icon :icon="removeOutline" slot="icon-only" />
              </ion-button>
              <span class="qty-val">{{ qty }}</span>
              <ion-button fill="outline" size="small" @click="qty++">
                <ion-icon :icon="addOutline" slot="icon-only" />
              </ion-button>
            </div>
            <ion-button @click="addToCart" color="success">
              <ion-icon :icon="cartOutline" slot="start" />
              Sepete Ekle
            </ion-button>
          </div>
        </ion-card-content>
      </ion-card>

      <!-- Error -->
      <ion-card v-if="error" color="danger">
        <ion-card-content>
          <ion-icon :icon="alertCircleOutline" /> {{ error }}
        </ion-card-content>
      </ion-card>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '../stores/cart'
import api from '../services/api'
import {
  barcodeOutline, searchOutline, cartOutline,
  addOutline, removeOutline, alertCircleOutline
} from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons,
  IonBackButton, IonCard, IonCardHeader, IonCardTitle, IonCardSubtitle,
  IonCardContent, IonChip, IonItem, IonInput, IonButton, IonIcon,
  IonLabel, IonBadge, toastController
} from '@ionic/vue'

const cartStore = useCartStore()

const demoItems = [
  { name: 'Domates', barcode: '8690000000101' },
  { name: 'Süt', barcode: '8690000000201' },
  { name: 'Tavuk', barcode: '8690000000302' },
  { name: 'Ekmek', barcode: '8690000000401' },
  { name: 'Cola', barcode: '8690000000504' },
  { name: 'Çikolata', barcode: '8690000000602' },
]

const manualBarcode = ref('')
const selectedBarcode = ref('')
const product = ref(null)
const error = ref('')
const qty = ref(1)

async function scanBarcode(barcode) {
  if (!barcode) return
  error.value = ''
  product.value = null
  selectedBarcode.value = barcode
  qty.value = 1

  try {
    const res = await api.get(`/products/barcode/${barcode}`)
    product.value = res.data
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = `"${barcode}" barkoduna ait ürün bulunamadı`
    } else {
      error.value = 'Ürün bilgisi alınamadı'
    }
  }
}

async function addToCart() {
  try {
    await cartStore.addToCart(product.value.id, qty.value)
    const toast = await toastController.create({
      message: `${qty.value}x ${product.value.name} sepete eklendi`,
      duration: 2000, color: 'success', position: 'bottom'
    })
    await toast.present()
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
.scanner-area { display: flex; justify-content: center; padding: 20px 0; }
.scanner-frame { width: 220px; height: 160px; border: 3px dashed var(--ion-color-primary); border-radius: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--ion-color-primary-tint); opacity: 0.8; }
.scan-icon { font-size: 56px; color: var(--ion-color-primary); margin-bottom: 8px; }
.scanner-frame p { color: var(--ion-color-primary); font-weight: 600; margin: 0; }

.demo-card { margin-top: 12px; }
.demo-note { font-size: 13px; color: var(--ion-color-medium); margin-bottom: 12px; }
.barcode-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }

.result-card { margin-top: 16px; }
.result-img { width: 100%; height: 180px; object-fit: cover; }
.result-price { display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px; }
.old { text-decoration: line-through; color: var(--ion-color-medium); font-size: 14px; }
.current { font-size: 24px; font-weight: 700; color: var(--ion-color-primary); }
.unit { font-size: 13px; color: var(--ion-color-medium); }
.result-stock { margin-bottom: 8px; }
.result-barcode { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--ion-color-medium); font-family: monospace; margin-bottom: 16px; }

.qty-row { display: flex; justify-content: space-between; align-items: center; }
.qty-controls { display: flex; align-items: center; gap: 8px; }
.qty-val { font-size: 20px; font-weight: 700; min-width: 30px; text-align: center; }
</style>
