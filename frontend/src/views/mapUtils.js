/**
 * Map rendering utilities for the mobile app.
 * Simplified version of the dashboard's mapRenderer.
 */

const CATEGORY_COLORS = {
  1: '#16a34a', 2: '#2563eb', 3: '#dc2626', 4: '#ca8a04',
  5: '#0891b2', 6: '#ea580c', 7: '#0d9488', 8: '#7c3aed',
}

export function drawMap(ctx, options) {
  const {
    zones = [], productLocations = [],
    scale = 8, offsetX = 0, offsetY = 0,
    highlightProductId = null, navigationPath = null,
    userPosition = null, animFrame = 0
  } = options

  const w = ctx.canvas.width
  const h = ctx.canvas.height

  ctx.fillStyle = '#f1f5f9'
  ctx.fillRect(0, 0, w, h)

  ctx.save()
  ctx.translate(offsetX, offsetY)
  ctx.scale(scale, scale)

  // Draw zones
  for (const zone of zones) {
    if (zone.zone_type === 'wall') {
      ctx.fillStyle = '#374151'
    } else {
      ctx.fillStyle = zone.color || '#e2e8f0'
    }
    ctx.fillRect(zone.x, zone.y, zone.width, zone.height)

    // Labels
    if (zone.label) {
      ctx.fillStyle = zone.zone_type === 'wall' ? '#fff' : '#374151'
      ctx.font = '1.6px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      const lines = zone.label.split('\n')
      const cx = zone.x + zone.width / 2
      const cy = zone.y + zone.height / 2
      lines.forEach((line, i) => {
        ctx.fillText(line, cx, cy + (i - (lines.length - 1) / 2) * 2)
      })
    }
  }

  // Product pins
  for (const loc of productLocations) {
    const color = CATEGORY_COLORS[loc.category_id] || '#6b7280'
    const isTarget = loc.product_id === highlightProductId

    if (isTarget) {
      // Pulsing target
      const r = 1.5 + Math.sin(animFrame * 0.1) * 0.5
      ctx.beginPath()
      ctx.arc(loc.x, loc.y, r + 0.5, 0, Math.PI * 2)
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
      ctx.beginPath()
      ctx.arc(loc.x, loc.y, 0.7, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.fill()
    }
  }

  // Navigation path
  if (navigationPath && navigationPath.length > 1) {
    ctx.beginPath()
    ctx.moveTo(navigationPath[0].x, navigationPath[0].y)
    for (let i = 1; i < navigationPath.length; i++) {
      ctx.lineTo(navigationPath[i].x, navigationPath[i].y)
    }
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 0.5
    ctx.setLineDash([1, 0.5])
    ctx.lineDashOffset = -animFrame * 0.3
    ctx.stroke()
    ctx.setLineDash([])
  }

  // User position
  if (userPosition) {
    ctx.beginPath()
    ctx.arc(userPosition.x, userPosition.y, 2, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(59, 130, 246, 0.15)'
    ctx.fill()
    ctx.beginPath()
    ctx.arc(userPosition.x, userPosition.y, 1, 0, Math.PI * 2)
    ctx.fillStyle = '#3b82f6'
    ctx.fill()
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 0.3
    ctx.stroke()
  }

  ctx.restore()
}

export function screenToMap(sx, sy, scale, offsetX, offsetY) {
  return { x: (sx - offsetX) / scale, y: (sy - offsetY) / scale }
}

export function hitTestProduct(locations, mx, my, radius = 2) {
  let nearest = null, nearestDist = radius
  for (const loc of locations) {
    const d = Math.sqrt((loc.x - mx) ** 2 + (loc.y - my) ** 2)
    if (d < nearestDist) { nearest = loc; nearestDist = d }
  }
  return nearest
}
