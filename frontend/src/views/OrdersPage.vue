<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>My Receipts</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="ion-text-center ion-padding" v-if="loading">
        <ion-spinner name="crescent" />
      </div>

      <div class="empty" v-else-if="purchases.length === 0">
        <ion-icon :icon="receiptOutline" class="empty-icon" />
        <h3>No purchases yet</h3>
        <p>Your receipts will appear here after you scan products and pay</p>
        <ion-button router-link="/tabs/barcode">Scan Product</ion-button>
      </div>

      <template v-else>
        <!-- Summary -->
        <ion-card class="summary-card">
          <ion-card-content>
            <div class="summary-grid">
              <div class="summary-item">
                <div class="summary-number">{{ purchases.length }}</div>
                <div class="summary-label">Purchases</div>
              </div>
              <div class="summary-item">
                <div class="summary-number">{{ totalSpent.toFixed(0) }} ₺</div>
                <div class="summary-label">Total Spent</div>
              </div>
              <div class="summary-item">
                <div class="summary-number">{{ totalPoints }}</div>
                <div class="summary-label">Points Earned</div>
              </div>
            </div>
          </ion-card-content>
        </ion-card>

        <!-- Purchase list -->
        <ion-card v-for="p in purchases" :key="p.id" @click="selectedPurchase = p; showDetail = true">
          <ion-card-header>
            <div class="purchase-header">
              <div>
                <ion-card-title style="font-size: 16px;">{{ p.store_name }}</ion-card-title>
                <ion-card-subtitle>{{ formatDate(p.created_at) }}</ion-card-subtitle>
              </div>
              <div class="purchase-amount">{{ p.total_price.toFixed(2) }} ₺</div>
            </div>
          </ion-card-header>
          <ion-card-content>
            <p class="item-summary">{{ p.item_count }} items · {{ getPaymentLabel(p.payment_method) }}</p>
            <div class="receipt-code">
              <ion-icon :icon="receiptOutline" />
              <span>{{ p.receipt_code }}</span>
            </div>
          </ion-card-content>
        </ion-card>
      </template>

      <!-- Receipt detail modal -->
      <ion-modal :is-open="showDetail" @didDismiss="showDetail = false">
        <ion-header>
          <ion-toolbar>
            <ion-title>Receipt Details</ion-title>
            <ion-buttons slot="end">
              <ion-button @click="showDetail = false">Close</ion-button>
            </ion-buttons>
          </ion-toolbar>
        </ion-header>
        <ion-content class="ion-padding" v-if="selectedPurchase">
          <div class="detail-top">
            <h2>{{ selectedPurchase.store_name }}</h2>
            <p>{{ formatDate(selectedPurchase.created_at) }}</p>
          </div>

          <!-- QR for verification -->
          <div class="detail-qr">
            <img :src="'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + selectedPurchase.receipt_code" alt="QR" />
            <p class="qr-code-text">{{ selectedPurchase.receipt_code }}</p>
          </div>

          <!-- Items -->
          <div class="detail-items">
            <div v-for="item in selectedPurchase.items" :key="item.id" class="detail-item">
              <div>
                <strong>{{ item.product_name }}</strong>
                <span class="item-qty">x{{ item.quantity }} · {{ item.product_price }} ₺</span>
              </div>
              <span class="item-sub">{{ item.subtotal.toFixed(2) }} ₺</span>
            </div>
          </div>

          <div class="detail-total">
            <span>Total</span>
            <strong>{{ selectedPurchase.total_price.toFixed(2) }} ₺</strong>
          </div>

          <div class="detail-meta">
            <div><span>Payment</span><span>{{ getPaymentLabel(selectedPurchase.payment_method) }}</span></div>
            <div><span>Points</span><span>+{{ selectedPurchase.points_earned }}</span></div>
            <div><span>Status</span><span>{{ selectedPurchase.status === 'paid' ? 'Paid' : 'Cancelled' }}</span></div>
          </div>
        </ion-content>
      </ion-modal>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import { receiptOutline } from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonButtons,
  IonCard, IonCardHeader, IonCardTitle, IonCardSubtitle, IonCardContent,
  IonSpinner, IonButton, IonIcon, IonModal, IonBadge
} from '@ionic/vue'

const purchases = ref([])
const loading = ref(true)
const showDetail = ref(false)
const selectedPurchase = ref(null)

const totalSpent = computed(() => purchases.value.filter(p => p.status === 'paid').reduce((s, p) => s + p.total_price, 0))
const totalPoints = computed(() => purchases.value.reduce((s, p) => s + p.points_earned, 0))

onMounted(async () => {
  try {
    const res = await api.get('/purchases/')
    purchases.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getPaymentLabel(m) {
  return { 'card': 'Card', 'cash': 'Cash', 'wallet': 'Wallet' }[m] || m
}
</script>

<style scoped>
.empty { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 64px; color: var(--ion-color-medium); margin-bottom: 12px; }

.summary-card { margin-bottom: 16px; }
.summary-grid { display: flex; justify-content: space-around; text-align: center; }
.summary-number { font-size: 22px; font-weight: 700; color: var(--ion-color-primary); }
.summary-label { font-size: 12px; color: var(--ion-color-medium); margin-top: 2px; }

.purchase-header { display: flex; justify-content: space-between; align-items: center; }
.purchase-amount { font-size: 20px; font-weight: 700; color: var(--ion-color-primary); }
.item-summary { font-size: 13px; color: var(--ion-color-medium); margin-bottom: 8px; }
.receipt-code { display: flex; align-items: center; gap: 6px; font-size: 13px; font-family: monospace; color: var(--ion-color-dark); }

/* Detail modal */
.detail-top { text-align: center; margin-bottom: 16px; }
.detail-top h2 { margin: 0; font-size: 20px; }
.detail-top p { color: var(--ion-color-medium); font-size: 14px; }

.detail-qr { text-align: center; padding: 16px; background: var(--ion-color-light); border-radius: 12px; margin-bottom: 20px; }
.detail-qr img { width: 150px; height: 150px; }
.qr-code-text { font-family: monospace; font-size: 16px; font-weight: 700; margin-top: 8px; }

.detail-items { margin-bottom: 12px; }
.detail-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--ion-color-light); }
.item-qty { font-size: 13px; color: var(--ion-color-medium); display: block; }
.item-sub { font-weight: 600; }

.detail-total { display: flex; justify-content: space-between; border-top: 2px solid var(--ion-color-primary); padding-top: 12px; margin-top: 8px; font-size: 18px; color: var(--ion-color-primary); }

.detail-meta { margin-top: 16px; padding-top: 12px; border-top: 1px dashed var(--ion-color-light-shade); }
.detail-meta div { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: var(--ion-color-medium); }
</style>
