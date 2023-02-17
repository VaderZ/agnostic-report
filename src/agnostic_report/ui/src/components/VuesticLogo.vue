<template>
  <svg class="va-icon-vuestic" :height="height" viewBox="0 0 478 57" fill="none" xmlns="http://www.w3.org/2000/svg">
    <text x="0" y="55" font-size="70px" fill="url(#paint0_linear)">AGNOSTIC</text>
    <defs>
      <linearGradient id="paint0_linear" x1="0" y1="56.1386" x2="357.64" y2="56.1386" gradientUnits="userSpaceOnUse">
        <stop :stop-color="colorsComputed.end" />
        <stop offset="1" :stop-color="colorsComputed.start" />
      </linearGradient>
    </defs>
  </svg>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import { useColors } from 'vuestic-ui'
  const { getColor, shiftHSLAColor } = useColors()

  const props = withDefaults(
    defineProps<{
      height?: number | string
      color?: string
    }>(),
    {
      height: 16,
      color: 'primary',
    },
  )

  const colorsComputed = computed(() => {
    const color = getColor(props.color, 'primary')
    return { start: color, end: shiftHSLAColor(color, { l: -20 }) }
  })
</script>
