<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Sepetim</ion-title>
        <ion-buttons slot="end" v-if="cartStore.items.length > 0">
          <ion-button color="danger" @click="clearCart">Temizle</ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="empty" v-if="cartStore.items.length === 0">
        <ion-icon :icon="cartOutline" class="empty-icon" />
        <h3>Sepetiniz boş</h3>
        <p>Ürün eklemek için ana sayfaya dönün</p>
        <ion-button router-link="/tabs/home">Alışverişe Başla</ion-button>
      </div>

      <template v-else>
        <!-- Cart items -->
        <div class="cart-list">
          <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
            <img :src="item.product.image_url" :alt="item.product.name" class="item-img" />
            <div class="item-info">
              <span class="item-brand">{{ item.product.brand }}</span>
              <span class="item-name">{{ item.product.name }}</span>
              <span class="item-price">{{ getPrice(item.product) }} ₺/{{ item.product.unit }}</span>
            </div>
            <div class="qty-controls">
              <ion-button fill="outline" size="small" @click="decreaseQty(item)">
                <ion-icon :icon="removeOutline" slot="icon-only" />
              </ion-button>
              <span class="qty">{{ item.quantity }}</span>
              <ion-button fill="outline" size="small" @click="increaseQty(item)">
                <ion-icon :icon="addOutline" slot="icon-only" />
              </ion-button>
            </div>
            <span class="item-subtotal">{{ (getPrice(item.product) * item.quantity).toFixed(2) }} ₺</span>
          </div>
        </div>

        <!-- Cart summary -->
        <div class="cart-summary">
          <div class="summary-row">
            <span>Ürün Sayısı</span>
            <strong>{{ cartStore.itemCount }} adet</strong>
          </div>
          <div class="summary-row total">
            <span>Toplam</span>
            <strong>{{ cartStore.totalPrice.toFixed(2) }} ₺</strong>
          </div>
        </div>

        <!-- Checkout -->
        <ion-item>
          <ion-textarea v-model="note" label="Sipariş Notu (isteğe bağlı)" label-placement="floating" placeholder="Örn: Kapıda bırakın" :rows="2" />
        </ion-item>

        <ion-button expand="block" class="ion-margin-top checkout-btn" :disabled="checkoutLoading" @click="handleCheckout">
          <ion-icon :icon="checkmarkOutline" slot="start" />
          {{ checkoutLoading ? 'Sipariş veriliyor...' : 'Siparişi Onayla' }}
        </ion-button>
      </template>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { cartOutline, addOutline, removeOutline, checkmarkOutline } from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons,
  IonButton, IonIcon, IonItem, IonTextarea,
  toastController, alertController
} from '@ionic/vue'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const note = ref('')
const checkoutLoading = ref(false)

function getPrice(product) {
  return product.discount_price || product.price
}

async function increaseQty(item) {
  await cartStore.updateQuantity(item.id, item.quantity + 1)
}

async function decreaseQty(item) {
  if (item.quantity <= 1) {
    await cartStore.removeItem(item.id)
  } else {
    await cartStore.updateQuantity(item.id, item.quantity - 1)
  }
}

async function clearCart() {
  const alert = await alertController.create({
    header: 'Sepeti Temizle',
    message: 'Tüm ürünler sepetten kaldırılacak. Emin misiniz?',
    buttons: [
      { text: 'İptal', role: 'cancel' },
      { text: 'Temizle', role: 'destructive', handler: () => cartStore.clearCart() }
    ]
  })
  await alert.present()
}

async function handleCheckout() {
  checkoutLoading.value = true
  try {
    await api.post('/orders/checkout', { note: note.value || null })
    await cartStore.fetchCart()
    await authStore.fetchProfile()

    const toast = await toastController.create({
      message: 'Siparişiniz alındı! Hazırlanıyor...',
      duration: 2500, color: 'success', position: 'bottom'
    })
    await toast.present()
    router.push('/tabs/orders')
  } catch (err) {
    const toast = await toastController.create({
      message: err.response?.data?.detail || 'Sipariş oluşturulamadı',
      duration: 3000, color: 'danger', position: 'bottom'
    })
    await toast.present()
  } finally {
    checkoutLoading.value = false
  }
}
</script>

<style scoped>
.empty { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 64px; color: var(--ion-color-medium); margin-bottom: 12px; }
.empty h3 { margin-bottom: 8px; }
.empty p { color: var(--ion-color-medium); margin-bottom: 20px; }

.cart-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.cart-item { display: flex; align-items: center; gap: 10px; padding: 10px; background: var(--ion-background-color); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.item-img { width: 56px; height: 56px; border-radius: 8px; object-fit: cover; }
.item-info { flex: 1; min-width: 0; }
.item-brand { font-size: 10px; color: var(--ion-color-medium); }
.item-name { display: block; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-price { font-size: 12px; color: var(--ion-color-medium); }
.qty-controls { display: flex; align-items: center; gap: 6px; }
.qty { font-size: 16px; font-weight: 700; min-width: 20px; text-align: center; }
.item-subtotal { font-size: 14px; font-weight: 700; color: var(--ion-color-primary); min-width: 60px; text-align: right; }

.cart-summary { background: var(--ion-color-light); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.summary-row { display: flex; justify-content: space-between; padding: 6px 0; }
.summary-row.total { border-top: 2px solid var(--ion-color-primary); margin-top: 8px; padding-top: 12px; font-size: 18px; color: var(--ion-color-primary); }

.checkout-btn { --padding-top: 14px; --padding-bottom: 14px; font-size: 16px; font-weight: 700; }
</style>
