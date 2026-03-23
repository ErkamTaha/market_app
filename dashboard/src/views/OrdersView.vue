<template>
  <div>
    <div class="page-header">
      <h1>Satışlar</h1>
      <p>Tüm müşteri alışverişleri ve fişler</p>
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
            <th>Fiş No</th>
            <th>Müşteri</th>
            <th>Ürünler</th>
            <th>Tutar</th>
            <th>Ödeme</th>
            <th>Puan</th>
            <th>Tarih</th>
            <th>Durum</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filteredPurchases" :key="p.id">
            <td><code>{{ p.receipt_code }}</code></td>
            <td>
              <strong>{{ p.user_name }}</strong>
              <br><small style="color:#94a3b8;">{{ p.user_email }}</small>
            </td>
            <td>
              <div v-for="item in p.items" :key="item.product_name" style="font-size:13px;">
                {{ item.product_name }} x{{ item.quantity }}
              </div>
            </td>
            <td><strong>{{ p.total_price.toFixed(2) }} ₺</strong></td>
            <td>{{ getPaymentLabel(p.payment_method) }}</td>
            <td>+{{ p.points_earned }}</td>
            <td>{{ formatDate(p.created_at) }}</td>
            <td>
              <span class="badge" :class="p.status === 'ödendi' ? 'badge-success' : 'badge-danger'">
                {{ p.status === 'ödendi' ? 'Ödendi' : 'İptal' }}
              </span>
            </td>
          </tr>
          <tr v-if="filteredPurchases.length === 0">
            <td colspan="8" style="text-align:center; color:#94a3b8; padding:40px;">Bu filtreye uygun satış yok</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const purchases = ref([])
const loading = ref(true)
const activeFilter = ref('all')

const filters = [
  { label: 'Tümü', value: 'all' },
  { label: 'Ödendi', value: 'ödendi' },
  { label: 'İptal', value: 'iptal' }
]

const filteredPurchases = computed(() => {
  if (activeFilter.value === 'all') return purchases.value
  return purchases.value.filter(p => p.status === activeFilter.value)
})

function getCount(f) {
  if (f === 'all') return purchases.value.length
  return purchases.value.filter(p => p.status === f).length
}

onMounted(async () => {
  try {
    const res = await api.get('/admin/purchases')
    purchases.value = res.data
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getPaymentLabel(m) {
  return { 'kart': 'Kart', 'nakit': 'Nakit', 'cüzdan': 'Cüzdan' }[m] || m
}
</script>

<style scoped>
code { font-size: 12px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
</style>
