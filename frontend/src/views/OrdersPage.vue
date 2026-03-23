<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Siparişlerim</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="ion-text-center ion-padding" v-if="loading">
        <ion-spinner name="crescent" />
      </div>

      <div class="empty" v-else-if="orders.length === 0">
        <ion-icon :icon="receiptOutline" class="empty-icon" />
        <h3>Henüz siparişiniz yok</h3>
        <p>Alışverişe başlayın!</p>
        <ion-button router-link="/tabs/home">Ana Sayfaya Dön</ion-button>
      </div>

      <div v-else>
        <ion-card v-for="order in orders" :key="order.id">
          <ion-card-header>
            <div class="order-header">
              <ion-card-title>Sipariş #{{ order.id }}</ion-card-title>
              <ion-badge :color="getStatusColor(order.status)">{{ getStatusLabel(order.status) }}</ion-badge>
            </div>
            <ion-card-subtitle>{{ formatDate(order.created_at) }}</ion-card-subtitle>
          </ion-card-header>
          <ion-card-content>
            <div class="order-items">
              <div v-for="item in order.items" :key="item.id" class="order-item-row">
                <span>{{ item.product_name }} x{{ item.quantity }}</span>
                <span class="item-total">{{ item.subtotal.toFixed(2) }} ₺</span>
              </div>
            </div>
            <div class="order-total">
              <span>Toplam ({{ order.item_count }} ürün)</span>
              <strong>{{ order.total_price.toFixed(2) }} ₺</strong>
            </div>
            <p class="order-note" v-if="order.note">Not: {{ order.note }}</p>
          </ion-card-content>
        </ion-card>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { receiptOutline } from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
  IonCard, IonCardHeader, IonCardTitle, IonCardSubtitle, IonCardContent,
  IonSpinner, IonButton, IonIcon, IonBadge
} from '@ionic/vue'

const orders = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/orders/')
    orders.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

function getStatusColor(status) {
  return { 'hazırlanıyor': 'warning', 'hazır': 'success', 'teslim_edildi': 'medium', 'iptal': 'danger' }[status] || 'medium'
}

function getStatusLabel(status) {
  return { 'hazırlanıyor': 'Hazırlanıyor', 'hazır': 'Hazır', 'teslim_edildi': 'Teslim Edildi', 'iptal': 'İptal' }[status] || status
}
</script>

<style scoped>
.empty { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 64px; color: var(--ion-color-medium); margin-bottom: 12px; }

.order-header { display: flex; justify-content: space-between; align-items: center; }
.order-items { margin-bottom: 12px; }
.order-item-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; }
.item-total { font-weight: 600; }
.order-total { display: flex; justify-content: space-between; border-top: 2px solid var(--ion-color-primary); padding-top: 8px; margin-top: 8px; font-size: 16px; color: var(--ion-color-primary); }
.order-note { font-size: 13px; color: var(--ion-color-medium); margin-top: 8px; font-style: italic; }
</style>
