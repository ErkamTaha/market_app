<template>
  <div>
    <div class="page-header">
      <h1>Genel Bakış</h1>
      <p>Market işletme durumu</p>
    </div>

    <div class="loading" v-if="loading">Yükleniyor...</div>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Toplam Gelir</div>
          <div class="stat-value green">{{ stats.revenue?.total?.toLocaleString('tr-TR') || 0 }} ₺</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Toplam Sipariş</div>
          <div class="stat-value blue">{{ stats.orders?.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Kayıtlı Kullanıcı</div>
          <div class="stat-value blue">{{ stats.users?.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Toplam Ürün</div>
          <div class="stat-value green">{{ stats.products?.total || 0 }}</div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Hazırlanıyor</div>
          <div class="stat-value yellow">{{ stats.orders?.preparing || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Hazır</div>
          <div class="stat-value green">{{ stats.orders?.ready || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Teslim Edildi</div>
          <div class="stat-value blue">{{ stats.orders?.delivered || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Düşük Stok Ürün</div>
          <div class="stat-value red">{{ stats.products?.low_stock || 0 }}</div>
        </div>
      </div>

      <!-- Recent orders -->
      <div class="card">
        <h2>Son Siparişler</h2>
        <table v-if="recentOrders.length > 0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Müşteri</th>
              <th>Ürün</th>
              <th>Tutar</th>
              <th>Tarih</th>
              <th>Durum</th>
              <th>İşlem</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in recentOrders" :key="o.id">
              <td>#{{ o.id }}</td>
              <td><strong>{{ o.user_name }}</strong></td>
              <td>{{ o.item_count }} ürün</td>
              <td><strong>{{ o.total_price.toFixed(2) }} ₺</strong></td>
              <td>{{ formatDate(o.created_at) }}</td>
              <td>
                <span class="badge" :class="getStatusBadge(o.status)">{{ getStatusLabel(o.status) }}</span>
              </td>
              <td>
                <button v-if="o.status === 'hazırlanıyor'" class="btn btn-sm btn-success" @click="updateStatus(o.id, 'hazır')">Hazır</button>
                <button v-if="o.status === 'hazır'" class="btn btn-sm btn-info" @click="updateStatus(o.id, 'teslim_edildi')">Teslim Et</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else style="color: #94a3b8; text-align: center; padding: 20px;">Henüz sipariş yok</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const stats = ref({})
const orders = ref([])
const loading = ref(true)

const recentOrders = computed(() => orders.value.slice(0, 10))

onMounted(async () => {
  try {
    const [statsRes, ordersRes] = await Promise.all([
      api.get('/admin/stats'),
      api.get('/admin/orders')
    ])
    stats.value = statsRes.data
    orders.value = ordersRes.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

async function updateStatus(orderId, newStatus) {
  try {
    await api.patch(`/admin/orders/${orderId}/status`, { status: newStatus })
    const res = await api.get('/admin/orders')
    orders.value = res.data
    const statsRes = await api.get('/admin/stats')
    stats.value = statsRes.data
  } catch (err) {
    alert('Durum güncellenemedi')
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function getStatusBadge(s) {
  return { 'hazırlanıyor': 'badge-warning', 'hazır': 'badge-success', 'teslim_edildi': 'badge-info', 'iptal': 'badge-danger' }[s] || 'badge-gray'
}

function getStatusLabel(s) {
  return { 'hazırlanıyor': 'Hazırlanıyor', 'hazır': 'Hazır', 'teslim_edildi': 'Teslim Edildi', 'iptal': 'İptal' }[s] || s
}
</script>
