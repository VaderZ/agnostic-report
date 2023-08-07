<template>
  <plotly-chart :data="data" :layout="layout" height="350" title="Tests Over Time"></plotly-chart>
</template>

<script lang="ts" setup>
  import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { getShortUpdateInterval, getTestColorByResult } from '../../../utils'
  import { useRoute } from 'vue-router'

  const route = useRoute()

  const layout = ref({
    legend: {
      orientation: 'h',
      xanchor: 'center',
      x: 0.5,
      yanchor: 'center',
      y: -0.15,
    },
  })

  const data = ref([{}])

  const readData = () => {
    axios
      .get(`/reporting/projects/${route.params.project}/tests-over-time`, { params: route.query })
      .then((response) => {
        data.value = response.data.data.series.map((s: any) => {
          return {
            y: s.data,
            x: response.data.data.categories,
            name: s.name,
            type: 'scatter',
            stackgroup: 'tests',
            marker: {
              color: getTestColorByResult(s.name),
            },
            line: {
              shape: 'spline',
              smoothing: 0.7,
            },
            hovertemplate: `%{x} <br>${s.name} tests: %{y}<extra></extra>`,
          }
        })
      })
  }

  let timer: number

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
      if (to !== from && route.params.project) {
        readData()
      }
    },
  )
</script>

<style scoped></style>
