<template>
  <div>
    <div class="page-header">
      <h1>Products</h1>
      <p>Stock management and product list</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Products</div>
        <div class="stat-value green">{{ products.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">In Stock</div>
        <div class="stat-value blue">{{ products.filter(p => p.is_in_stock).length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Low Stock (≤10)</div>
        <div class="stat-value yellow">{{ products.filter(p => p.stock <= 10 && p.stock > 0).length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Out of Stock</div>
        <div class="stat-value red">{{ products.filter(p => p.stock === 0).length }}</div>
      </div>
    </div>

    <div class="loading" v-if="loading">Loading...</div>

    <div class="card" v-else>
      <!-- Search -->
      <div style="margin-bottom: 16px;">
        <input v-model="search" placeholder="Search product or brand..." style="width:300px; padding:10px 16px; border:2px solid #e2e8f0; border-radius:8px; font-size:14px; outline:none;" />
      </div>

      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Brand</th>
            <th>Category</th>
            <th>Price</th>
            <th>Sale Price</th>
            <th>Unit</th>
            <th>Barcode</th>
            <th>Stock</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filteredProducts" :key="p.id">
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.brand || '-' }}</td>
            <td>{{ p.category }}</td>
            <td>{{ p.price }} ₺</td>
            <td>
              <span v-if="p.discount_price" style="color:#059669; font-weight:600;">{{ p.discount_price }} ₺</span>
              <span v-else style="color:#94a3b8;">-</span>
            </td>
            <td>{{ p.unit }}</td>
            <td><code style="font-size:11px; background:#f1f5f9; padding:2px 6px; border-radius:4px;">{{ p.barcode }}</code></td>
            <td>
              <div class="stock-edit">
                <input
                  type="number"
                  class="stock-input"
                  :value="p.stock"
                  min="0"
                  @change="updateStock(p.id, $event.target.value)"
                />
              </div>
            </td>
            <td>
              <span v-if="p.stock === 0" class="badge badge-danger">Out of Stock</span>
              <span v-else-if="p.stock <= 10" class="badge badge-warning">Low</span>
              <span v-else class="badge badge-success">In Stock</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const products = ref([])
const loading = ref(true)
const search = ref('')

const filteredProducts = computed(() => {
  if (!search.value) return products.value
  const s = search.value.toLowerCase()
  return products.value.filter(p =>
    p.name.toLowerCase().includes(s) || (p.brand && p.brand.toLowerCase().includes(s))
  )
})

onMounted(async () => {
  await fetchProducts()
})

async function fetchProducts() {
  loading.value = true
  try {
    const res = await api.get('/admin/products')
    products.value = res.data
  } finally {
    loading.value = false
  }
}

async function updateStock(productId, newStock) {
  try {
    await api.patch(`/admin/products/${productId}/stock`, { stock: parseInt(newStock) })
    await fetchProducts()
  } catch (err) {
    alert('Failed to update stock')
  }
}
</script>
