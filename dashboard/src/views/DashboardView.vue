<template>
  <div>
    <div class="page-header">
      <h1>Overview</h1>
      <p>Market business status</p>
    </div>

    <div class="loading" v-if="loading">Loading...</div>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Revenue</div>
          <div class="stat-value green">{{ stats.revenue?.total?.toLocaleString('en-US') || 0 }} ₺</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Sales</div>
          <div class="stat-value blue">{{ stats.purchases?.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Items Sold</div>
          <div class="stat-value blue">{{ stats.purchases?.total_items_sold || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Registered Customers</div>
          <div class="stat-value green">{{ stats.users?.total || 0 }}</div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Products</div>
          <div class="stat-value blue">{{ stats.products?.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Categories</div>
          <div class="stat-value green">{{ stats.products?.categories || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Low Stock</div>
          <div class="stat-value yellow">{{ stats.products?.low_stock || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Cancelled</div>
          <div class="stat-value red">{{ stats.purchases?.cancelled || 0 }}</div>
        </div>
      </div>

      <!-- Recent purchases -->
      <div class="card">
        <h2>Recent Sales</h2>
        <table v-if="recentPurchases.length > 0">
          <thead>
            <tr>
              <th>Receipt No</th>
              <th>Customer</th>
              <th>Products</th>
              <th>Amount</th>
              <th>Payment</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in recentPurchases" :key="p.id">
              <td><code>{{ p.receipt_code }}</code></td>
              <td><strong>{{ p.user_name }}</strong></td>
              <td>{{ p.item_count }} items</td>
              <td><strong>{{ p.total_price.toFixed(2) }} ₺</strong></td>
              <td>{{ getPaymentLabel(p.payment_method) }}</td>
              <td>{{ formatDate(p.created_at) }}</td>
              <td>
                <span class="badge" :class="p.status === 'paid' ? 'badge-success' : 'badge-danger'">
                  {{ p.status === 'paid' ? 'Paid' : 'Cancelled' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else style="color:#94a3b8; text-align:center; padding:20px;">No sales yet</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const stats = ref({})
const purchases = ref([])
const loading = ref(true)

const recentPurchases = computed(() => purchases.value.slice(0, 10))

onMounted(async () => {
  try {
    const [statsRes, purchasesRes] = await Promise.all([
      api.get('/admin/stats'),
      api.get('/admin/purchases')
    ])
    stats.value = statsRes.data
    purchases.value = purchasesRes.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('en-US', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function getPaymentLabel(m) {
  return { 'card': 'Card', 'cash': 'Cash', 'wallet': 'Wallet' }[m] || m
}
</script>

<style scoped>
code { font-size: 12px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
</style>
