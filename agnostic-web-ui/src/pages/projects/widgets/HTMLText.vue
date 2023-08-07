<template>
  <va-card style="width: 100%; height: 100%">
    <div style="padding: 10px" v-html="html"></div>
  </va-card>
</template>

<script lang="ts" setup>
  import { ref, defineProps } from 'vue'

  interface WidgetConfigOptions {
    html: string
  }

  interface WidgetConfig {
    config?: WidgetConfigOptions
  }

  const props = defineProps<WidgetConfig>()
  const html = ref(props.config && props.config.html ? props.config.html : 'Edit <b>html</b> property to add text')
</script>

<style scoped></style>
