import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

/**
 * Cart store — manages the shopping cart.
 *
 * This is THE key difference from the car wash app.
 * The car wash app has bookings (one item at a time).
 * The market app has a cart (multiple items, quantities, totals).
 */
export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const loading = ref(false)

  // Total number of items in cart (sum of quantities)
  const itemCount = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  // Total price of cart
  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => {
      const price = item.product.discount_price || item.product.price
      return sum + (price * item.quantity)
    }, 0)
  })

  async function fetchCart() {
    loading.value = true
    try {
      const response = await api.get('/cart/')
      items.value = response.data
    } catch (err) {
      console.error('Sepet yüklenemedi:', err)
    } finally {
      loading.value = false
    }
  }

  async function addToCart(productId, quantity = 1) {
    const response = await api.post('/cart/', { product_id: productId, quantity })
    await fetchCart()
    return response.data
  }

  async function updateQuantity(itemId, quantity) {
    if (quantity <= 0) {
      await removeItem(itemId)
      return
    }
    await api.patch(`/cart/${itemId}`, { quantity })
    await fetchCart()
  }

  async function removeItem(itemId) {
    await api.delete(`/cart/${itemId}`)
    await fetchCart()
  }

  async function clearCart() {
    await api.delete('/cart/')
    items.value = []
  }

  return {
    items, loading, itemCount, totalPrice,
    fetchCart, addToCart, updateQuantity, removeItem, clearCart
  }
})
