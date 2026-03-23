import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Simulated user position store.
 *
 * For the prototype, the user drags a blue dot on the map.
 * In production, this would be updated by BLE beacon triangulation.
 *
 * Default position: near the entrance (37, 55)
 */
export const usePositionStore = defineStore('position', () => {
  const x = ref(37)
  const y = ref(55)

  function setPosition(newX, newY) {
    x.value = newX
    y.value = newY
  }

  return { x, y, setPosition }
})
