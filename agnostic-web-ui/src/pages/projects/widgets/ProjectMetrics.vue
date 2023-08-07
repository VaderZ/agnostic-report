<template>
  <va-card style="width: 100%; height: 100%">
    <va-card-title>{{ title }}</va-card-title>
    <va-card-content>
      <va-data-table :items="items" :columns="columns" :loading="loading" hide-default-header> </va-data-table>
    </va-card-content>
  </va-card>
</template>

<script lang="ts" setup>
  import { defineProps, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { useRoute } from 'vue-router'
  import { formatMetric, getShortUpdateInterval } from '../../../utils'

  interface MetricConfig {
    table: string
    name: string
    field: string | undefined
    func: string
    filter: string | undefined
    title: string
    format: string
  }

  interface WidgetConfigOptions {
    title: string
    metrics: MetricConfig[]
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
      alignHead: 'left',
      width: '90%',
      style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '200px' },
    },
    { key: 'value', label: 'Value', align: 'right', alignHead: 'right', width: '10%' },
  ])
  const title = ref(props.config && props.config.title ? props.config.title : 'Project Metrics')
  const loading = ref(false)
  const items = ref([])

  const readItems = () => {
    if (props.config) {
      return axios
        .post(`/reporting/projects/${route.params.project}/project-metrics`, props.config.metrics, {
          params: route.query,
        })
        .then((response) => {
          const data = response.data.data
          if (props.config) {
            for (const i in props.config.metrics) {
              if ('format' in props.config.metrics[i]) {
                data[i].value = formatMetric(data[i].value, props.config.metrics[i].format)
              }
            }
          }
          items.value = data
        })
    } else {
      return new Promise((resolve) => resolve(true))
    }
  }

  let timer: number

  onMounted(() => {
    loading.value = true
    readItems().then(() => {
      loading.value = false
    })
    timer = window.setInterval(readItems, getShortUpdateInterval())
  })

  onBeforeUnmount(() => {
    clearInterval(timer)
  })

  watch(
    () => route.query,
    (to, from) => {
      if (to !== from && route.params.project) {
        readItems()
      }
    },
  )
</script>

<style scoped></style>
