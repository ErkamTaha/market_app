<template>
  <div>
    <div class="page-header">
      <h1>Map Editor</h1>
      <p>Place products on the map — click to position</p>
    </div>

    <div class="loading" v-if="loading">Loading...</div>

    <div class="editor-layout" v-else>
      <!-- Left: Canvas Map -->
      <div class="map-panel">
        <div class="map-toolbar">
          <span class="toolbar-info">
            Placed: {{ placedCount }}/{{ products.length }} products
          </span>
          <span class="toolbar-info" v-if="selectedProduct">
            Selected: <strong>{{ selectedProduct.name }}</strong> — click on map to place
          </span>
        </div>
        <canvas
          ref="canvasRef"
          @click="handleCanvasClick"
          @mousemove="handleMouseMove"
          @wheel.prevent="handleWheel"
          class="map-canvas"
        ></canvas>
        <div class="map-legend">
          <span v-for="(color, cat) in legendItems" :key="cat" class="legend-item">
            <span class="legend-dot" :style="{ background: color }"></span>
            {{ cat }}
          </span>
        </div>
      </div>

      <!-- Right: Product List -->
      <div class="product-panel">
        <h3>Products</h3>
        <input
          v-model="searchQuery"
          placeholder="Search products..."
          class="search-input"
        />

        <!-- Unplaced products first -->
        <div class="product-section" v-if="unplacedProducts.length > 0">
          <h4 class="section-label warning">Unplaced ({{ unplacedProducts.length }})</h4>
          <div
            v-for="p in unplacedProducts"
            :key="p.id"
            class="product-item"
            :class="{ selected: selectedProduct?.id === p.id }"
            @click="selectProduct(p)"
          >
            <span class="p-name">{{ p.name }}</span>
            <span class="p-brand">{{ p.brand }}</span>
          </div>
        </div>

        <!-- Placed products -->
        <div class="product-section">
          <h4 class="section-label success">Placed ({{ placedProducts.length }})</h4>
          <div
            v-for="p in placedProducts"
            :key="p.id"
            class="product-item placed"
            :class="{ selected: selectedProduct?.id === p.id }"
            @click="selectProduct(p)"
          >
            <span class="p-name">{{ p.name }}</span>
            <span class="p-location">{{ getLocationLabel(p.id) }}</span>
          </div>
        </div>

        <!-- Selected product info -->
        <div class="selected-info" v-if="selectedProduct">
          <h4>{{ selectedProduct.name }}</h4>
          <p>{{ selectedProduct.brand }} · {{ selectedProduct.category }}</p>
          <p v-if="getLocation(selectedProduct.id)">
            Location: ({{ getLocation(selectedProduct.id).x.toFixed(0) }}, {{ getLocation(selectedProduct.id).y.toFixed(0) }})
          </p>
          <button
            v-if="getLocation(selectedProduct.id)"
            class="btn btn-sm btn-danger"
            @click="removeLocation(selectedProduct.id)"
          >Remove Location</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../services/api'
import { drawMap, screenToMap, hitTestZone, hitTestProduct } from '../services/mapRenderer'

const canvasRef = ref(null)
const loading = ref(true)

const zones = ref([])
const productLocations = ref([])
const products = ref([])
const searchQuery = ref('')
const selectedProduct = ref(null)

// Canvas state
const scale = ref(10)
const offsetX = ref(20)
const offsetY = ref(20)
let animFrame = 0
let animId = null

const legendItems = {
  'Meyve': '#16a34a',
  'Süt': '#2563eb',
  'Et': '#dc2626',
  'Ekmek': '#ca8a04',
  'İçecek': '#0891b2',
  'Atıştırmalık': '#ea580c',
  'Temizlik': '#0d9488',
  'Bakım': '#7c3aed',
}

const placedCount = computed(() => productLocations.value.length)

const unplacedProducts = computed(() => {
  const placedIds = new Set(productLocations.value.map(l => l.product_id))
  let list = products.value.filter(p => !placedIds.has(p.id))
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || (p.brand && p.brand.toLowerCase().includes(q)))
  }
  return list
})

const placedProducts = computed(() => {
  const placedIds = new Set(productLocations.value.map(l => l.product_id))
  let list = products.value.filter(p => placedIds.has(p.id))
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || (p.brand && p.brand.toLowerCase().includes(q)))
  }
  return list
})

function getLocation(productId) {
  return productLocations.value.find(l => l.product_id === productId)
}

function getLocationLabel(productId) {
  const loc = getLocation(productId)
  return loc ? loc.shelf_label || `(${loc.x.toFixed(0)}, ${loc.y.toFixed(0)})` : ''
}

onMounted(async () => {
  try {
    const [zonesRes, locsRes, prodsRes] = await Promise.all([
      api.get('/navigation/map'),
      api.get('/navigation/all-locations'),
      api.get('/admin/products')
    ])
    zones.value = zonesRes.data
    productLocations.value = locsRes.data
    products.value = prodsRes.data
  } catch (err) {
    console.error('Failed to load map data:', err)
  } finally {
    loading.value = false
  }

  await nextTick()
  resizeCanvas()
  startAnimation()
  window.addEventListener('resize', resizeCanvas)
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  window.removeEventListener('resize', resizeCanvas)
})

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.parentElement.getBoundingClientRect()
  canvas.width = rect.width
  canvas.height = rect.height - 80  // minus toolbar + legend
  render()
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
    highlightProductId: selectedProduct.value?.id || null,
    animFrame
  })
}

function selectProduct(product) {
  selectedProduct.value = selectedProduct.value?.id === product.id ? null : product
}

async function handleCanvasClick(event) {
  const rect = canvasRef.value.getBoundingClientRect()
  const sx = event.clientX - rect.left
  const sy = event.clientY - rect.top
  const mapCoord = screenToMap(sx, sy, scale.value, offsetX.value, offsetY.value)

  // If a product is selected, place it at the click position
  if (selectedProduct.value) {
    const zone = hitTestZone(zones.value, mapCoord.x, mapCoord.y)

    try {
      await api.put(`/admin/products/${selectedProduct.value.id}/location`, {
        zone_id: zone?.id || null,
        x: Math.round(mapCoord.x * 10) / 10,
        y: Math.round(mapCoord.y * 10) / 10,
        z: 1.0,
        shelf_label: zone?.label || zone?.name || null,
        updated_by: "Admin"
      })

      // Refresh locations
      const locsRes = await api.get('/navigation/all-locations')
      productLocations.value = locsRes.data
      selectedProduct.value = null
    } catch (err) {
      alert('Failed to save location: ' + (err.response?.data?.detail || err.message))
    }
    return
  }

  // Otherwise, check if clicked on a product pin
  const hitProduct = hitTestProduct(productLocations.value, mapCoord.x, mapCoord.y)
  if (hitProduct) {
    const p = products.value.find(pr => pr.id === hitProduct.product_id)
    if (p) selectedProduct.value = p
  }
}

function handleMouseMove(event) {
  // Could add hover effects here in the future
}

function handleWheel(event) {
  const delta = event.deltaY > 0 ? -1 : 1
  scale.value = Math.max(4, Math.min(20, scale.value + delta))
}

async function removeLocation(productId) {
  try {
    await api.delete(`/admin/products/${productId}/location`)
    const locsRes = await api.get('/navigation/all-locations')
    productLocations.value = locsRes.data
    selectedProduct.value = null
  } catch (err) {
    alert('Failed to remove location')
  }
}
</script>

<style scoped>
.editor-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
}

.map-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.map-toolbar {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
}

.toolbar-info {
  color: #64748b;
}

.map-canvas {
  flex: 1;
  cursor: crosshair;
}

.map-legend {
  display: flex;
  gap: 12px;
  padding: 8px 16px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

/* Product panel */
.product-panel {
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  padding: 16px;
  overflow-y: auto;
}

.product-panel h3 {
  margin: 0 0 12px;
  font-size: 18px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  margin-bottom: 12px;
}

.search-input:focus {
  border-color: #059669;
}

.section-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 8px 0 4px;
  padding: 4px 8px;
  border-radius: 4px;
}

.section-label.warning {
  background: #fef3c7;
  color: #92400e;
}

.section-label.success {
  background: #d1fae5;
  color: #065f46;
}

.product-item {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  margin-bottom: 2px;
  transition: background 0.15s;
}

.product-item:hover {
  background: #f1f5f9;
}

.product-item.selected {
  background: #d1fae5;
  border-left: 3px solid #059669;
}

.p-name {
  display: block;
  font-weight: 600;
}

.p-brand, .p-location {
  font-size: 11px;
  color: #94a3b8;
}

.selected-info {
  margin-top: 16px;
  padding: 12px;
  background: #f0fdf4;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
}

.selected-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
}

.selected-info p {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}
</style>
