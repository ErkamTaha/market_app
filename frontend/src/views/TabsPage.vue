<template>
  <ion-page>
    <ion-tabs>
      <ion-router-outlet />
      <ion-tab-bar slot="bottom">
        <ion-tab-button tab="home" href="/tabs/home">
          <ion-icon :icon="homeOutline" />
          <ion-label>Ana Sayfa</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="barcode" href="/tabs/barcode">
          <ion-icon :icon="barcodeOutline" />
          <ion-label>Tara</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="map" href="/tabs/map">
          <ion-icon :icon="mapOutline" />
          <ion-label>Harita</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="cart" href="/tabs/cart">
          <ion-icon :icon="cartOutline" />
          <ion-label>Sepet</ion-label>
          <ion-badge v-if="cartStore.itemCount > 0" color="danger">{{ cartStore.itemCount }}</ion-badge>
        </ion-tab-button>
        <ion-tab-button tab="orders" href="/tabs/orders">
          <ion-icon :icon="receiptOutline" />
          <ion-label>Fişlerim</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="profile" href="/tabs/profile">
          <ion-icon :icon="personOutline" />
          <ion-label>Profil</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  </ion-page>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '../stores/cart'
import { homeOutline, barcodeOutline, mapOutline, cartOutline, receiptOutline, personOutline } from 'ionicons/icons'
import { IonPage, IonTabs, IonTabBar, IonTabButton, IonIcon, IonLabel, IonRouterOutlet, IonBadge } from '@ionic/vue'

const cartStore = useCartStore()
onMounted(() => { cartStore.fetchCart() })
</script>
