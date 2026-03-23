<template>
  <ion-page>
    <ion-content class="ion-padding">
      <div class="auth-container">
        <div class="auth-header">
          <h1>Market</h1>
          <p>Tekrar hoş geldiniz</p>
        </div>
        <form @submit.prevent="handleLogin">
          <ion-item>
            <ion-input v-model="form.email" type="email" label="E-posta" label-placement="floating" required />
          </ion-item>
          <ion-item>
            <ion-input v-model="form.password" type="password" label="Şifre" label-placement="floating" required />
          </ion-item>
          <ion-button expand="block" type="submit" :disabled="loading" class="ion-margin-top">
            {{ loading ? 'Giriş yapılıyor...' : 'Giriş Yap' }}
          </ion-button>
        </form>
        <ion-text color="danger" v-if="error"><p class="ion-text-center">{{ error }}</p></ion-text>
        <p class="ion-text-center">Hesabınız yok mu? <router-link to="/register">Kayıt Ol</router-link></p>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { IonPage, IonContent, IonItem, IonInput, IonButton, IonText } from '@ionic/vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')
const form = ref({ email: '', password: '' })

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push({ path: '/tabs/home', replace: true })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Giriş başarısız'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container { max-width: 400px; margin: 0 auto; padding-top: 80px; }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-header h1 { font-size: 32px; font-weight: 700; color: var(--ion-color-primary); }
.auth-header p { color: var(--ion-color-medium); }
ion-item { margin-bottom: 8px; --background: transparent; }
</style>
