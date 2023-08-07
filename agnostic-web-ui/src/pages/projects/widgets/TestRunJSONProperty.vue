<template>
  <va-card style="width: 100%; height: 100%">
    <va-card-title>{{ title }}</va-card-title>
    <va-card-content>
      <va-data-table :items="items" :columns="columns" :loading="loading" no-data-html="" hide-default-header>
      </va-data-table>
    </va-card-content>
  </va-card>
</template>

<script lang="ts" setup>
  import { defineProps, onMounted, ref, Ref } from 'vue'
  import axios from 'axios'
  import { useRoute } from 'vue-router'

  interface Item {
    name: string
    value: string
  }

  interface WidgetConfigOptions {
    title: string
    path: string[]
  }

  interface WidgetConfig {
    config?: WidgetConfigOptions
  }

  const route = useRoute()

  const props = defineProps<WidgetConfig>()
  const columns = ref([
    {
      key: 'name',
      label: 'Name',
      align: 'left',
      width: '50%',
      style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '180px' },
    },
    { key: 'value', label: 'Value', align: 'left', width: '50%' },
  ])
  const title = ref(props.config && props.config.title ? props.config.title : 'JSON Property')
  const loading = ref(false)
  const items = ref([]) as Ref<Item[]>

  const readItems = () => {
    return axios.get(`/projects/${route.params.project}/test-runs/${route.params.testrun}`).then((response) => {
      let property = response.data.properties
      const _items = []
      if (props.config !== undefined) {
        for (const node of props.config.path) {
          property = property[node]
        }
      }
      for (const key in property) {
        _items.push({ name: key, value: property[key] })
      }
      items.value = _items
    })
  }

  onMounted(() => {
    loading.value = true
    readItems().then(() => {
      loading.value = false
    })
  })
</script>

<style scoped></style>
