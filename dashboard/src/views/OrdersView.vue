<template>
  <div>
    <div class="page-header">
      <h1>Siparişler</h1>
      <p>Tüm müşteri siparişleri</p>
    </div>

    <div class="filter-bar">
      <button v-for="f in filters" :key="f.value" class="filter-chip"
        :class="{ active: activeFilter === f.value }" @click="activeFilter = f.value">
        {{ f.label }}
        <span class="chip-count" v-if="getCount(f.value) > 0">{{ getCount(f.value) }}</span>
      </button>
    </div>

    <div class="loading" v-if="loading">Yükleniyor...</div>

    <div class="card" v-else>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Müşteri</th>
            <th>Ürünler</th>
            <th>Tutar</th>
            <th>Not</th>
            <th>Tarih</th>
            <th>Durum</th>
            <th>İşlem</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in filteredOrders" :key="o.id">
            <td>#{{ o.id }}</td>
            <td>
              <strong>{{ o.user_name }}</strong>
              <br><small style="color:#94a3b8;">{{ o.user_email }}</small>
            </td>
            <td>
              <div v-for="item in o.items" :key="item.product_name" style="font-size:13px;">
                {{ item.product_name }} x{{ item.quantity }}
              </div>
            </td>
            <td><strong>{{ o.total_price.toFixed(2) }} ₺</strong></td>
            <td style="max-width:150px; font-size:13px; color:#64748b;">{{ o.note || '-' }}</td>
            <td>{{ formatDate(o.created_at) }}</td>
            <td>
              <span class="badge" :class="getStatusBadge(o.status)">{{ getStatusLabel(o.status) }}</span>
            </td>
            <td>
              <div style="display:flex; gap:4px; flex-wrap:wrap;">
                <button v-if="o.status === 'hazırlanıyor'" class="btn btn-sm btn-success" @click="updateStatus(o.id, 'hazır')">Hazır</button>
                <button v-if="o.status === 'hazır'" class="btn btn-sm btn-info" @click="updateStatus(o.id, 'teslim_edildi')">Teslim Et</button>
                <button v-if="o.status !== 'iptal' && o.status !== 'teslim_edildi'" class="btn btn-sm btn-danger" @click="updateStatus(o.id, 'iptal')">İptal</button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredOrders.length === 0">
            <td colspan="8" style="text-align:center; color:#94a3b8; padding:40px;">Bu filtreye uygun sipariş yok</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const orders = ref([])
const loading = ref(true)
const activeFilter = ref('all')

const filters = [
  { label: 'Tümü', value: 'all' },
  { label: 'Hazırlanıyor', value: 'hazırlanıyor' },
  { label: 'Hazır', value: 'hazır' },
  { label: 'Teslim Edildi', value: 'teslim_edildi' },
  { label: 'İptal', value: 'iptal' }
]

const filteredOrders = computed(() => {
  if (activeFilter.value === 'all') return orders.value
  return orders.value.filter(o => o.status === activeFilter.value)
})

function getCount(f) {
  if (f === 'all') return orders.value.length
  return orders.value.filter(o => o.status === f).length
}

onMounted(async () => {
  await fetchOrders()
})

async function fetchOrders() {
  loading.value = true
  try {
    const res = await api.get('/admin/orders')
    orders.value = res.data
  } finally {
    loading.value = false
  }
}

async function updateStatus(orderId, newStatus) {
  try {
    await api.patch(`/admin/orders/${orderId}/status`, { status: newStatus })
    await fetchOrders()
  } catch (err) {
    alert('Durum güncellenemedi')
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getStatusBadge(s) {
  return { 'hazırlanıyor': 'badge-warning', 'hazır': 'badge-success', 'teslim_edildi': 'badge-info', 'iptal': 'badge-danger' }[s] || 'badge-gray'
}

function getStatusLabel(s) {
  return { 'hazırlanıyor': 'Hazırlanıyor', 'hazır': 'Hazır', 'teslim_edildi': 'Teslim Edildi', 'iptal': 'İptal' }[s] || s
}
</script>
