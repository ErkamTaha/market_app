import api from './api'

export async function getMapLayout() {
  const res = await api.get('/navigation/map')
  return res.data
}

export async function getAllProductLocations() {
  const res = await api.get('/navigation/all-locations')
  return res.data
}

export async function getProductLocation(productId) {
  const res = await api.get(`/navigation/product/${productId}/location`)
  return res.data
}

export async function getNavigationPath(fromX, fromY, toX, toY) {
  const res = await api.get('/navigation/path', {
    params: { from_x: fromX, from_y: fromY, to_x: toX, to_y: toY }
  })
  return res.data
}

export async function searchWithLocation(query) {
  const res = await api.get('/navigation/search', { params: { q: query } })
  return res.data
}

export async function getMultiProductRoute(productIds, fromX, fromY) {
  const res = await api.get('/navigation/route', {
    params: { product_ids: productIds.join(','), from_x: fromX, from_y: fromY }
  })
  return res.data
}
