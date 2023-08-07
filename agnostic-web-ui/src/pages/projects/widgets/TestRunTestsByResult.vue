<template>
  <plotly-chart :data="data" :layout="layout" title="Test Results" :height="350"></plotly-chart>
</template>

<script lang="ts" setup>
  import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { getShortUpdateInterval, getTestColorByResult } from '../../../utils'
  import { useRoute } from 'vue-router'
  import { useGlobalState } from '../../../store'

  const route = useRoute()
  const globalState = useGlobalState()
  let timer: number

  const layout = ref({
    height: 300,
    margin: {
      b: 20,
      l: 30,
      r: 30,
      t: 20,
    },
  })
  const data = ref([{}])

  const readData = () => {
    if (!globalState.getProperty('isTestRunActive')) {
      clearInterval(timer)
    }

    axios
      .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/tests-by-result`, {
        params: route.query,
      })
      .then((response) => {
        data.value = [
          {
            values: response.data.data.series,
            labels: response.data.data.labels,
            type: 'pie',
            marker: {
              colors: response.data.data.labels.map((label: string) => getTestColorByResult(label)),
            },
          },
        ]
      })
  }

  onMounted(() => {
    readData()
    timer = window.setInterval(readData, getShortUpdateInterval())
  })

  onBeforeUnmount(() => {
    clearInterval(timer)
  })

  watch(
    () => route.query,
    (to, from) => {
      if (to !== from && route.params.testrun) {
        readData()
      }
    },
  )
</script>

<style scoped></style>
