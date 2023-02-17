<template>
  <div style="white-space: pre-wrap; overflow: hidden">
    {{ content.slice(0, limit) }} {{ content.length > limit ? '...' : '' }}
  </div>
  <div v-if="content.length > limit">
    <br />
    <va-button outline @click="saveContent">Full Message</va-button>
  </div>
</template>

<script lang="ts" setup>
  import { saveAs } from 'file-saver'
  import { defineProps, ref } from 'vue'

  interface ComponentConfig {
    content: string
    limit: number
    fileName: string
  }

  const props = defineProps<ComponentConfig>()

  const content = ref(props.content ? props.content : '')
  const limit = ref(props.limit ? props.limit : 1000)
  const fileName = ref(props.fileName)

  const saveContent = () => {
    saveAs(
      new Blob([content.value], { type: 'text/plain;charset=utf-8' }),
      fileName.value ? `${fileName.value.replace(/[/\\?%*:|"<>]/g, '-')}.txt` : `full-message.txt`,
    )
  }
</script>

<style scoped></style>
