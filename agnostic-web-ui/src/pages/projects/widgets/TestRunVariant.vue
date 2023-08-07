<template>
  <va-card :title="title" style="width: 100%; height: 100%">
    <va-card-title>{{ title }}</va-card-title>
    <va-card-content>
      <va-data-table :items="items" :columns="columns" :loading="loading" hide-default-header> </va-data-table>
    </va-card-content>
  </va-card>
</template>

<script lang="ts" setup>
  import { useRoute } from 'vue-router'
  import { defineProps, onMounted, ref, Ref } from 'vue'
  import axios from 'axios'

  interface Variant {
    name: string
    key: string
  }

  interface WidgetConfigOptions {
    title: string
    variants: Variant[]
  }

  interface WidgetConfig {
    config?: WidgetConfigOptions
  }

  interface Item {
    name: string
    value: string
  }

  const route = useRoute()

  const props = defineProps<WidgetConfig>()

  const columns = ref([
    { key: 'name', label: 'Name', align: 'left', alignHead: 'left', width: '50%' },
    { key: 'value', label: 'Value', align: 'right', alignHead: 'right', width: '50%' },
  ])
  const variants = ref(props.config && props.config.variants ? props.config.variants : [])
  const title = ref(props.config && props.config.title ? props.config.title : 'Test Run Metrics')
  const loading = ref(false)
  const items = ref([]) as Ref<Item[]>

  const readItems = () => {
    return axios
      .get(`/projects/${route.params.project}/test-runs/${route.params.testrun}`)
      .then((response) => {
        const _items = []
        for (const variant of variants.value) {
          _items.push({ name: variant.name, value: response.data.variant[variant.key] })
        }
        items.value = _items
      })
      .catch()
  }

  onMounted(() => {
    loading.value = true
    readItems().then(() => {
      loading.value = false
    })
  })
</script>

<style scoped></style>
