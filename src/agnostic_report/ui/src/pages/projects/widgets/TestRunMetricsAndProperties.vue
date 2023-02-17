<template>
  <va-card style="width: 100%; height: 100%">
    <va-card-title>{{ title }}</va-card-title>
    <va-card-content>
      <va-data-table :items="items" :columns="columns" :loading="loading" hide-default-header> </va-data-table>
    </va-card-content>
  </va-card>
</template>

<script lang="ts" setup>
  import { useRoute } from 'vue-router'
  import { defineProps, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { getShortUpdateInterval, formatMetric } from '../../../utils'
  import { useGlobalState } from '../../../store'

  interface MetricConfig {
    table: string
    name: string
    field?: string
    func?: string
    filter?: string
    path?: string[]
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
  const globalState = useGlobalState()
  let timer: number

  const props = defineProps<WidgetConfig>()

  const columns = ref([
    { key: 'name', label: 'Name', align: 'left', alignHead: 'left', width: '90%' },
    { key: 'value', label: 'Value', align: 'right', alignHead: 'right', width: '10%' },
  ])
  const title = ref(props.config && props.config.title ? props.config.title : 'Test Run Metrics')
  const loading = ref(false)
  const items = ref([])

  const readItems = () => {
    if (!globalState.getProperty('isTestRunActive')) {
      clearInterval(timer)
    }

    if (props.config) {
      return axios
        .post(
          `/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/test-run-metrics`,
          props.config.metrics,
          { params: route.query },
        )
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
      if (to !== from && route.params.testrun) {
        readItems()
      }
    },
  )
</script>

<style scoped></style>
