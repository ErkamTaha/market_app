<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Sepetim</ion-title>
        <ion-buttons slot="end" v-if="cartStore.items.length > 0 && !receipt">
          <ion-button color="danger" @click="clearCart">Temizle</ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <!-- Receipt shown after checkout -->
      <div v-if="receipt" class="receipt-view">
        <div class="receipt-success">
          <ion-icon :icon="checkmarkCircleOutline" class="success-icon" />
          <h2>Ödeme Başarılı!</h2>
          <p class="receipt-store">{{ receipt.store_name }}</p>
        </div>

        <div class="receipt-card">
          <div class="receipt-header">
            <span>Fiş No</span>
            <strong>{{ receipt.receipt_code }}</strong>
          </div>

          <!-- QR code for cashier -->
          <div class="receipt-qr">
            <img :src="'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + receipt.receipt_code" alt="QR" />
            <p>Bu kodu kasada gösterin</p>
          </div>

          <!-- Items -->
          <div class="receipt-items">
            <div v-for="item in receipt.items" :key="item.id" class="receipt-item">
              <span>{{ item.product_name }} x{{ item.quantity }}</span>
              <span>{{ item.subtotal.toFixed(2) }} ₺</span>
            </div>
          </div>

          <div class="receipt-total">
            <span>Toplam</span>
            <strong>{{ receipt.total_price.toFixed(2) }} ₺</strong>
          </div>

          <div class="receipt-meta">
            <div><span>Ödeme</span><span>{{ getPaymentLabel(receipt.payment_method) }}</span></div>
            <div><span>Puan Kazanıldı</span><span>+{{ receipt.points_earned }}</span></div>
            <div><span>Tarih</span><span>{{ formatDate(receipt.created_at) }}</span></div>
          </div>
        </div>

        <ion-button expand="block" @click="receipt = null; router.push('/tabs/home')">
          Alışverişe Devam Et
        </ion-button>
      </div>

      <!-- Empty cart -->
      <div class="empty" v-else-if="cartStore.items.length === 0">
        <ion-icon :icon="cartOutline" class="empty-icon" />
        <h3>Sepetiniz boş</h3>
        <p>Ürün taramak için "Tara" sekmesini kullanın</p>
        <ion-button router-link="/tabs/barcode">Ürün Tara</ion-button>
      </div>

      <!-- Cart items -->
      <template v-else>
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

        <!-- Summary -->
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

        <!-- Payment method -->
        <h4 style="margin: 16px 0 8px;">Ödeme Yöntemi</h4>
        <ion-radio-group v-model="paymentMethod">
          <ion-item>
            <ion-radio value="kart" label-placement="end">Kart ile Öde</ion-radio>
          </ion-item>
          <ion-item>
            <ion-radio value="nakit" label-placement="end">Kasada Nakit Öde</ion-radio>
          </ion-item>
        </ion-radio-group>

        <ion-button expand="block" class="checkout-btn" :disabled="checkoutLoading" @click="handleCheckout">
          <ion-icon :icon="checkmarkOutline" slot="start" />
          {{ checkoutLoading ? 'İşleniyor...' : `${cartStore.totalPrice.toFixed(2)} ₺ Öde` }}
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
import {
  cartOutline, addOutline, removeOutline, checkmarkOutline, checkmarkCircleOutline
} from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons,
  IonButton, IonIcon, IonItem, IonRadioGroup, IonRadio,
  toastController, alertController
} from '@ionic/vue'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const paymentMethod = ref('kart')
const checkoutLoading = ref(false)
const receipt = ref(null)

function getPrice(product) { return product.discount_price || product.price }
async function increaseQty(item) { await cartStore.updateQuantity(item.id, item.quantity + 1) }
async function decreaseQty(item) {
  if (item.quantity <= 1) await cartStore.removeItem(item.id)
  else await cartStore.updateQuantity(item.id, item.quantity - 1)
}

async function clearCart() {
  const alert = await alertController.create({
    header: 'Sepeti Temizle', message: 'Tüm ürünler kaldırılacak. Emin misiniz?',
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
    const res = await api.post('/purchases/checkout', { payment_method: paymentMethod.value })
    receipt.value = res.data
    await cartStore.fetchCart()
    await authStore.fetchProfile()
  } catch (err) {
    const toast = await toastController.create({
      message: err.response?.data?.detail || 'Ödeme başarısız',
      duration: 3000, color: 'danger', position: 'bottom'
    })
    await toast.present()
  } finally {
    checkoutLoading.value = false
  }
}

function getPaymentLabel(method) {
  return { 'kart': 'Kart', 'nakit': 'Nakit', 'cüzdan': 'Cüzdan' }[method] || method
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('tr-TR', {
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
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

.checkout-btn { margin-top: 16px; --padding-top: 14px; --padding-bottom: 14px; font-size: 16px; font-weight: 700; }

/* Receipt */
.receipt-view { max-width: 400px; margin: 0 auto; }
.receipt-success { text-align: center; margin-bottom: 20px; }
.success-icon { font-size: 72px; color: var(--ion-color-success); }
.receipt-success h2 { color: var(--ion-color-success); margin: 8px 0 4px; }
.receipt-store { color: var(--ion-color-medium); }

.receipt-card { background: var(--ion-background-color); border-radius: 16px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }
.receipt-header { display: flex; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px dashed var(--ion-color-light-shade); margin-bottom: 16px; }

.receipt-qr { text-align: center; margin-bottom: 16px; padding: 16px; background: var(--ion-color-light); border-radius: 12px; }
.receipt-qr img { width: 160px; height: 160px; }
.receipt-qr p { font-size: 13px; color: var(--ion-color-medium); margin-top: 8px; }

.receipt-items { margin-bottom: 12px; }
.receipt-item { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; }

.receipt-total { display: flex; justify-content: space-between; border-top: 2px solid var(--ion-color-primary); padding-top: 10px; margin-top: 10px; font-size: 18px; color: var(--ion-color-primary); }

.receipt-meta { margin-top: 16px; padding-top: 12px; border-top: 1px dashed var(--ion-color-light-shade); }
.receipt-meta div { display: flex; justify-content: space-between; padding: 3px 0; font-size: 13px; color: var(--ion-color-medium); }
</style>
