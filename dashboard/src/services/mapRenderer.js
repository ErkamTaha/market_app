/**
 * Map Renderer — draws the market floor plan on an HTML5 Canvas.
 *
 * Used by both the admin dashboard (with editing) and the mobile app (read-only).
 * Handles coordinate transformations, zone rendering, product pins,
 * navigation paths, and user position markers.
 */

// Category colors for product pins
const CATEGORY_COLORS = {
  1: '#16a34a',  // Meyve & Sebze — green
  2: '#2563eb',  // Süt Ürünleri — blue
  3: '#dc2626',  // Et & Tavuk — red
  4: '#ca8a04',  // Ekmek & Fırın — amber
  5: '#0891b2',  // İçecekler — cyan
  6: '#ea580c',  // Atıştırmalık — orange
  7: '#0d9488',  // Temizlik — teal
  8: '#7c3aed',  // Kişisel Bakım — violet
}

/**
 * Draw the complete market map on a canvas.
 *
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} options
 * @param {Array} options.zones - MapZone objects from API
 * @param {Array} options.productLocations - Product locations from API
 * @param {number} options.scale - Zoom level (pixels per map unit)
 * @param {number} options.offsetX - Pan offset X
 * @param {number} options.offsetY - Pan offset Y
 * @param {number|null} options.highlightProductId - Product to highlight
 * @param {Array|null} options.navigationPath - Waypoints to draw as path
 * @param {Object|null} options.userPosition - {x, y} of user position
 * @param {number|null} options.selectedZoneId - Zone to highlight as selected
 * @param {number} options.animFrame - Animation frame counter for animations
 */
export function drawMap(ctx, options) {
  const {
    zones = [],
    productLocations = [],
    scale = 10,
    offsetX = 0,
    offsetY = 0,
    highlightProductId = null,
    navigationPath = null,
    userPosition = null,
    selectedZoneId = null,
    animFrame = 0
  } = options

  const w = ctx.canvas.width
  const h = ctx.canvas.height

  // Clear canvas
  ctx.fillStyle = '#f1f5f9'
  ctx.fillRect(0, 0, w, h)

  ctx.save()
  ctx.translate(offsetX, offsetY)
  ctx.scale(scale, scale)

  // Draw zones
  for (const zone of zones) {
    ctx.fillStyle = zone.color || '#e2e8f0'

    // Highlight selected zone
    if (zone.id === selectedZoneId) {
      ctx.fillStyle = adjustBrightness(zone.color || '#e2e8f0', -20)
      ctx.strokeStyle = '#059669'
      ctx.lineWidth = 0.3
      ctx.strokeRect(zone.x, zone.y, zone.width, zone.height)
    }

    ctx.fillRect(zone.x, zone.y, zone.width, zone.height)

    // Draw zone label
    if (zone.label) {
      ctx.fillStyle = '#374151'
      ctx.font = '1.8px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      const lines = zone.label.split('\n')
      const cx = zone.x + zone.width / 2
      const cy = zone.y + zone.height / 2
      lines.forEach((line, i) => {
        ctx.fillText(line, cx, cy + (i - (lines.length - 1) / 2) * 2.2)
      })
    }

    // Draw zone type indicator for walls
    if (zone.zone_type === 'wall') {
      ctx.fillStyle = '#374151'
      ctx.fillRect(zone.x, zone.y, zone.width, zone.height)
    }
  }

  // Draw product pins
  for (const loc of productLocations) {
    const color = CATEGORY_COLORS[loc.category_id] || '#6b7280'
    const isHighlighted = loc.product_id === highlightProductId

    if (isHighlighted) {
      // Pulsing red circle for target product
      const pulseRadius = 1.5 + Math.sin(animFrame * 0.1) * 0.5
      ctx.beginPath()
      ctx.arc(loc.x, loc.y, pulseRadius + 0.5, 0, Math.PI * 2)
      ctx.fillStyle = 'rgba(239, 68, 68, 0.2)'
      ctx.fill()

      ctx.beginPath()
      ctx.arc(loc.x, loc.y, 1.2, 0, Math.PI * 2)
      ctx.fillStyle = '#ef4444'
      ctx.fill()
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 0.3
      ctx.stroke()
    } else {
      // Normal product dot
      ctx.beginPath()
      ctx.arc(loc.x, loc.y, 0.8, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.fill()
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 0.2
      ctx.stroke()
    }
  }

  // Draw navigation path
  if (navigationPath && navigationPath.length > 1) {
    ctx.beginPath()
    ctx.moveTo(navigationPath[0].x, navigationPath[0].y)
    for (let i = 1; i < navigationPath.length; i++) {
      ctx.lineTo(navigationPath[i].x, navigationPath[i].y)
    }
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 0.5
    ctx.setLineDash([1, 0.5])
    ctx.lineDashOffset = -animFrame * 0.3  // Animated flowing dashes
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Draw user position
  if (userPosition) {
    // Outer ring
    ctx.beginPath()
    ctx.arc(userPosition.x, userPosition.y, 2, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(59, 130, 246, 0.15)'
    ctx.fill()

    // Inner dot
    ctx.beginPath()
    ctx.arc(userPosition.x, userPosition.y, 1, 0, Math.PI * 2)
    ctx.fillStyle = '#3b82f6'
    ctx.fill()
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 0.3
    ctx.stroke()

    // Label
    ctx.fillStyle = '#1e40af'
    ctx.font = 'bold 1.5px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('📍', userPosition.x, userPosition.y - 2.5)
  }

  ctx.restore()
}

/**
 * Convert screen (pixel) coordinates to map coordinates.
 */
export function screenToMap(screenX, screenY, scale, offsetX, offsetY) {
  return {
    x: (screenX - offsetX) / scale,
    y: (screenY - offsetY) / scale
  }
}

/**
 * Convert map coordinates to screen (pixel) coordinates.
 */
export function mapToScreen(mapX, mapY, scale, offsetX, offsetY) {
  return {
    x: mapX * scale + offsetX,
    y: mapY * scale + offsetY
  }
}

/**
 * Find which zone contains a map coordinate.
 */
export function hitTestZone(zones, mapX, mapY) {
  for (const zone of zones) {
    if (
      mapX >= zone.x && mapX <= zone.x + zone.width &&
      mapY >= zone.y && mapY <= zone.y + zone.height
    ) {
      return zone
    }
  }
  return null
}

/**
 * Find which product location is near a map coordinate.
 */
export function hitTestProduct(locations, mapX, mapY, radius = 2) {
  let nearest = null
  let nearestDist = radius

  for (const loc of locations) {
    const dx = loc.x - mapX
    const dy = loc.y - mapY
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < nearestDist) {
      nearest = loc
      nearestDist = dist
    }
  }

  return nearest
}

function adjustBrightness(hex, amount) {
  const num = parseInt(hex.replace('#', ''), 16)
  const r = Math.min(255, Math.max(0, ((num >> 16) & 0xff) + amount))
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0xff) + amount))
  const b = Math.min(255, Math.max(0, (num & 0xff) + amount))
  return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`
}
