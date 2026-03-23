<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Mağaza Haritası</ion-title>
      </ion-toolbar>
      <!-- Search bar -->
      <ion-toolbar>
        <ion-searchbar
          v-model="searchQuery"
          placeholder="Ürün ara ve haritada bul..."
          @ionInput="handleSearch"
          debounce="300"
        />
      </ion-toolbar>
    </ion-header>

    <ion-content>
      <!-- Search results overlay -->
      <div class="search-results" v-if="searchResults.length > 0 && searchQuery">
        <div
          v-for="r in searchResults"
          :key="r.id"
          class="search-item"
          @click="navigateToProduct(r)"
        >
          <div class="search-item-info">
            <strong>{{ r.name }}</strong>
            <span>{{ r.brand }} · {{ r.discount_price || r.price }} ₺</span>
          </div>
          <ion-icon :icon="navigateOutline" color="primary" v-if="r.location" />
          <span v-else class="no-loc">Konum yok</span>
        </div>
      </div>

      <!-- Map canvas -->
      <canvas
        ref="canvasRef"
        @click="handleCanvasClick"
        @touchstart="handleTouchStart"
        @touchmove.prevent="handleTouchMove"
        class="map-canvas"
      ></canvas>

      <!-- Navigation info bar -->
      <div class="nav-info" v-if="targetProduct">
        <div class="nav-product">
          <strong>{{ targetProduct.product_name }}</strong>
          <span v-if="navPath">{{ navPath.distance.toFixed(0) }}m · ~{{ navPath.estimated_seconds }} saniye</span>
        </div>
        <div class="nav-actions">
          <ion-button size="small" fill="outline" @click="addTargetToCart">
            <ion-icon :icon="cartOutline" slot="start" />
            Sepete Ekle
          </ion-button>
          <ion-button size="small" color="medium" fill="clear" @click="clearNavigation">
            <ion-icon :icon="closeOutline" slot="icon-only" />
          </ion-button>
        </div>
      </div>

      <!-- Draggable position hint -->
      <div class="position-hint" v-if="!targetProduct">
        <ion-icon :icon="fingerPrintOutline" />
        <span>Mavi noktayı sürükleyerek konumunuzu ayarlayın</span>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePositionStore } from '../stores/position'
import { useCartStore } from '../stores/cart'
import { getMapLayout, getAllProductLocations, getNavigationPath, searchWithLocation } from '../services/navigation'
import { drawMap, screenToMap, hitTestProduct } from './mapUtils'
import {
  navigateOutline, cartOutline, closeOutline, fingerPrintOutline
} from 'ionicons/icons'
import {
  IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
  IonSearchbar, IonButton, IonIcon, toastController
} from '@ionic/vue'

const route = useRoute()
const positionStore = usePositionStore()
const cartStore = useCartStore()

const canvasRef = ref(null)
const zones = ref([])
const productLocations = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const targetProduct = ref(null)
const navPath = ref(null)

const scale = ref(8)
const offsetX = ref(10)
const offsetY = ref(10)
let animFrame = 0
let animId = null
let isDraggingUser = false

onMounted(async () => {
  try {
    const [zonesData, locsData] = await Promise.all([
      getMapLayout(),
      getAllProductLocations()
    ])
    zones.value = zonesData
    productLocations.value = locsData
  } catch (err) {
    console.error('Harita yüklenemedi:', err)
  }

  await nextTick()
  resizeCanvas()
  startAnimation()
  window.addEventListener('resize', resizeCanvas)

  // Check if navigated here with a product_id query param
  if (route.query.product_id) {
    const pid = parseInt(route.query.product_id)
    const loc = productLocations.value.find(l => l.product_id === pid)
    if (loc) {
      targetProduct.value = loc
      await calculatePath(loc.x, loc.y)
    }
  }
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  window.removeEventListener('resize', resizeCanvas)
})

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width = canvas.parentElement.clientWidth
  canvas.height = canvas.parentElement.clientHeight - 60
}

function startAnimation() {
  function tick() {
    animFrame++
    render()
    animId = requestAnimationFrame(tick)
  }
  animId = requestAnimationFrame(tick)
}

function render() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')

  drawMap(ctx, {
    zones: zones.value,
    productLocations: productLocations.value,
    scale: scale.value,
    offsetX: offsetX.value,
    offsetY: offsetY.value,
    highlightProductId: targetProduct.value?.product_id || null,
    navigationPath: navPath.value?.waypoints || null,
    userPosition: { x: positionStore.x, y: positionStore.y },
    animFrame
  })
}

async function handleSearch() {
  if (!searchQuery.value || searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  try {
    searchResults.value = await searchWithLocation(searchQuery.value)
  } catch (err) {
    console.error(err)
  }
}

async function navigateToProduct(product) {
  searchQuery.value = ''
  searchResults.value = []

  if (!product.location) {
    const toast = await toastController.create({
      message: 'Bu ürünün konumu henüz belirlenmemiş', duration: 2000, color: 'warning', position: 'bottom'
    })
    await toast.present()
    return
  }

  const loc = productLocations.value.find(l => l.product_id === product.id)
  if (loc) {
    targetProduct.value = loc
    await calculatePath(loc.x, loc.y)
  }
}

async function calculatePath(toX, toY) {
  try {
    navPath.value = await getNavigationPath(positionStore.x, positionStore.y, toX, toY)
  } catch (err) {
    console.error('Yol hesaplanamadı:', err)
  }
}

function clearNavigation() {
  targetProduct.value = null
  navPath.value = null
}

function handleCanvasClick(event) {
  const rect = canvasRef.value.getBoundingClientRect()
  const sx = event.clientX - rect.left
  const sy = event.clientY - rect.top
  const mapCoord = screenToMap(sx, sy, scale.value, offsetX.value, offsetY.value)

  // Check if clicked near user position (to start dragging)
  const dx = mapCoord.x - positionStore.x
  const dy = mapCoord.y - positionStore.y
  if (Math.sqrt(dx * dx + dy * dy) < 3) {
    // Move user position
    return
  }

  // Check if clicked on a product
  const hit = hitTestProduct(productLocations.value, mapCoord.x, mapCoord.y, 3)
  if (hit) {
    targetProduct.value = hit
    calculatePath(hit.x, hit.y)
    return
  }

  // Otherwise, move user position
  positionStore.setPosition(
    Math.round(mapCoord.x * 10) / 10,
    Math.round(mapCoord.y * 10) / 10
  )

  // Recalculate path if navigating
  if (targetProduct.value) {
    calculatePath(targetProduct.value.x, targetProduct.value.y)
  }
}

let touchStartPos = null

function handleTouchStart(event) {
  const touch = event.touches[0]
  const rect = canvasRef.value.getBoundingClientRect()
  touchStartPos = { x: touch.clientX - rect.left, y: touch.clientY - rect.top }

  const mapCoord = screenToMap(touchStartPos.x, touchStartPos.y, scale.value, offsetX.value, offsetY.value)
  const dx = mapCoord.x - positionStore.x
  const dy = mapCoord.y - positionStore.y
  isDraggingUser = Math.sqrt(dx * dx + dy * dy) < 4
}

function handleTouchMove(event) {
  const touch = event.touches[0]
  const rect = canvasRef.value.getBoundingClientRect()
  const sx = touch.clientX - rect.left
  const sy = touch.clientY - rect.top

  if (isDraggingUser) {
    const mapCoord = screenToMap(sx, sy, scale.value, offsetX.value, offsetY.value)
    positionStore.setPosition(
      Math.round(mapCoord.x * 10) / 10,
      Math.round(mapCoord.y * 10) / 10
    )
    if (targetProduct.value) {
      calculatePath(targetProduct.value.x, targetProduct.value.y)
    }
  }
}

async function addTargetToCart() {
  if (!targetProduct.value) return
  try {
    await cartStore.addToCart(targetProduct.value.product_id, 1)
    const toast = await toastController.create({
      message: `${targetProduct.value.product_name} sepete eklendi`, duration: 1500, color: 'success', position: 'bottom'
    })
    await toast.present()
  } catch (err) {
    const toast = await toastController.create({
      message: 'Eklenemedi', duration: 2000, color: 'danger', position: 'bottom'
    })
    await toast.present()
  }
}
</script>

<style scoped>
.map-canvas {
  width: 100%;
  height: 100%;
  touch-action: none;
}

.search-results {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: var(--ion-background-color);
  z-index: 10;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--ion-color-light);
  cursor: pointer;
}

.search-item:active {
  background: var(--ion-color-light);
}

.search-item-info {
  display: flex;
  flex-direction: column;
}

.search-item-info strong {
  font-size: 15px;
}

.search-item-info span {
  font-size: 13px;
  color: var(--ion-color-medium);
}

.no-loc {
  font-size: 12px;
  color: var(--ion-color-medium);
}

.nav-info {
  position: fixed;
  bottom: 60px;
  left: 0;
  right: 0;
  background: var(--ion-background-color);
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
  z-index: 5;
}

.nav-product strong {
  display: block;
  font-size: 16px;
}

.nav-product span {
  font-size: 13px;
  color: var(--ion-color-primary);
  font-weight: 600;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.position-hint {
  position: fixed;
  bottom: 68px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 5;
}
</style>
