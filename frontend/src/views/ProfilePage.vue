<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Profil</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="profile-header" v-if="authStore.user">
        <div class="avatar">{{ getInitials(authStore.user.full_name) }}</div>
        <h2>{{ authStore.user.full_name }}</h2>
      </div>

      <ion-card class="points-card" v-if="authStore.user">
        <ion-card-content>
          <div class="points-display">
            <ion-icon :icon="starOutline" class="points-icon" />
            <div>
              <div class="points-number">{{ authStore.user.loyalty_points }}</div>
              <div class="points-label">Sadakat Puanı</div>
            </div>
          </div>
          <p class="points-info">Her 10 ₺ harcamada 1 puan kazanırsınız.</p>
        </ion-card-content>
      </ion-card>

      <ion-list v-if="authStore.user">
        <ion-item>
          <ion-icon :icon="mailOutline" slot="start" color="primary" />
          <ion-label><p>E-posta</p><h3>{{ authStore.user.email }}</h3></ion-label>
        </ion-item>
        <ion-item>
          <ion-icon :icon="callOutline" slot="start" color="primary" />
          <ion-label><p>Telefon</p><h3>{{ authStore.user.phone }}</h3></ion-label>
        </ion-item>
      </ion-list>

      <ion-button expand="block" color="danger" fill="outline" class="ion-margin-top" @click="handleLogout">
        <ion-icon :icon="logOutOutline" slot="start" />
        Çıkış Yap
      </ion-button>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { starOutline, mailOutline, callOutline, logOutOutline } from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
  IonCard, IonCardContent, IonList, IonItem, IonLabel, IonIcon, IonButton
} from '@ionic/vue'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    try { await authStore.fetchProfile() } catch { authStore.logout(); router.push('/login') }
  }
})

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function handleLogout() {
  authStore.logout()
  router.push({ path: '/login', replace: true })
}
</script>

<style scoped>
.profile-header { text-align: center; padding: 20px 0; }
.avatar { width: 80px; height: 80px; border-radius: 50%; background: var(--ion-color-primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; margin: 0 auto 12px; }
.profile-header h2 { margin: 0; font-size: 22px; font-weight: 700; }
.points-card { margin-bottom: 16px; }
.points-display { display: flex; align-items: center; gap: 16px; }
.points-icon { font-size: 40px; color: var(--ion-color-warning); }
.points-number { font-size: 28px; font-weight: 700; color: var(--ion-color-primary); }
.points-label { font-size: 14px; color: var(--ion-color-medium); }
.points-info { margin-top: 12px; font-size: 13px; color: var(--ion-color-medium); }
</style>
