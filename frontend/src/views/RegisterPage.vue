<template>
  <ion-page>
    <ion-content class="ion-padding">
      <div class="auth-container">
        <div class="auth-header">
          <h1>Market</h1>
          <p>Create an account</p>
        </div>
        <form @submit.prevent="handleRegister">
          <ion-item>
            <ion-input v-model="form.full_name" label="Full Name" label-placement="floating" required />
          </ion-item>
          <ion-item>
            <ion-input v-model="form.email" type="email" label="Email" label-placement="floating" required />
          </ion-item>
          <ion-item>
            <ion-input v-model="form.phone" type="tel" label="Phone" label-placement="floating" placeholder="+905XX" required />
          </ion-item>
          <ion-item>
            <ion-input v-model="form.password" type="password" label="Password" label-placement="floating" required />
          </ion-item>
          <ion-button expand="block" type="submit" :disabled="loading" class="ion-margin-top">
            {{ loading ? 'Creating...' : 'Sign Up' }}
          </ion-button>
        </form>
        <ion-text color="danger" v-if="error"><p class="ion-text-center">{{ error }}</p></ion-text>
        <p class="ion-text-center">Already have an account? <router-link to="/login">Sign In</router-link></p>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { IonPage, IonContent, IonItem, IonInput, IonButton, IonText, toastController } from '@ionic/vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')
const form = ref({ full_name: '', email: '', phone: '', password: '' })

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await authStore.register(form.value)
    await authStore.login(form.value.email, form.value.password)
    const toast = await toastController.create({ message: 'Welcome!', duration: 2000, color: 'success', position: 'bottom' })
    await toast.present()
    router.push({ path: '/tabs/home', replace: true })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container { max-width: 400px; margin: 0 auto; padding-top: 60px; }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-header h1 { font-size: 32px; font-weight: 700; color: var(--ion-color-primary); }
.auth-header p { color: var(--ion-color-medium); }
ion-item { margin-bottom: 8px; --background: transparent; }
</style>
