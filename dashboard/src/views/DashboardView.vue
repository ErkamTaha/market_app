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
          <div class="stat-label">Toplam Satış</div>
          <div class="stat-value blue">{{ stats.purchases?.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Satılan Ürün</div>
          <div class="stat-value blue">{{ stats.purchases?.total_items_sold || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Kayıtlı Müşteri</div>
          <div class="stat-value green">{{ stats.users?.total || 0 }}</div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Toplam Ürün</div>
          <div class="stat-value blue">{{ stats.products?.total || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Kategori</div>
          <div class="stat-value green">{{ stats.products?.categories || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Düşük Stok</div>
          <div class="stat-value yellow">{{ stats.products?.low_stock || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">İptal Edilen</div>
          <div class="stat-value red">{{ stats.purchases?.cancelled || 0 }}</div>
        </div>
      </div>

      <!-- Recent purchases -->
      <div class="card">
        <h2>Son Satışlar</h2>
        <table v-if="recentPurchases.length > 0">
          <thead>
            <tr>
              <th>Fiş No</th>
              <th>Müşteri</th>
              <th>Ürün</th>
              <th>Tutar</th>
              <th>Ödeme</th>
              <th>Tarih</th>
              <th>Durum</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in recentPurchases" :key="p.id">
              <td><code>{{ p.receipt_code }}</code></td>
              <td><strong>{{ p.user_name }}</strong></td>
              <td>{{ p.item_count }} ürün</td>
              <td><strong>{{ p.total_price.toFixed(2) }} ₺</strong></td>
              <td>{{ getPaymentLabel(p.payment_method) }}</td>
              <td>{{ formatDate(p.created_at) }}</td>
              <td>
                <span class="badge" :class="p.status === 'ödendi' ? 'badge-success' : 'badge-danger'">
                  {{ p.status === 'ödendi' ? 'Ödendi' : 'İptal' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else style="color:#94a3b8; text-align:center; padding:20px;">Henüz satış yok</p>
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
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function getPaymentLabel(m) {
  return { 'kart': 'Kart', 'nakit': 'Nakit', 'cüzdan': 'Cüzdan' }[m] || m
}
</script>

<style scoped>
code { font-size: 12px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
</style>
