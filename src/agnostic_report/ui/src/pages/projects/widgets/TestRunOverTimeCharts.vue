<template>
  <div class="row">
    <div class="flex md4">
      <va-card>
        <va-select
          v-model="selectedCharts"
          :options="availableCharts"
          label="Charts"
          multiple
          clearable
          class="mb-1"
        ></va-select>
      </va-card>
    </div>
  </div>
  <div v-for="chart in selectedCharts" :key="chart.value" class="row">
    <div class="flex md12">
      <plotly-chart
        :data="data[chart.value] || []"
        :title="charts[chart.value].title"
        :layout="getChartLayout(chart.value)"
        :height="300"
      ></plotly-chart>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { defineProps, onBeforeUnmount, onMounted, ref, Ref, watch } from 'vue'
  import axios from 'axios'
  import { GenericJSONResponse, getShortUpdateInterval, HashUtil } from '../../../utils'
  import { useRoute } from 'vue-router'
  import { useGlobalState } from '../../../store'

  interface SeriesConfig {
    key: string
    label: string
    color: string
  }

  interface ChartConfig {
    name: string
    title: string
    type: string
    stacked: boolean
    series: SeriesConfig[]
    units: string
  }

  interface WidgetConfigOptions {
    defaultCharts: number[]
    charts: ChartConfig
  }

  interface WidgetConfig {
    config?: WidgetConfigOptions
  }

  interface ChartItem {
    value: number
    text: string
  }

  interface Series {
    name: string
    data: string[]
  }

  interface SeriesCollection {
    [prop: number]: Series[]
  }

  interface APISeries {
    name: string
    data: string[]
  }

  interface ChartLayouts {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [prop: string]: any
  }

  interface ChartLayoutsCollection {
    [prop: number]: ChartLayouts
  }

  const route = useRoute()
  const hash = new HashUtil()
  const globalState = useGlobalState()
  let timer: number

  const props = defineProps<WidgetConfig>()

  const data = ref({}) as Ref<GenericJSONResponse>
  const charts = ref(props.config && props.config.charts ? props.config.charts : []) as Ref<ChartConfig[]>
  const defaultCharts = ref(props.config && props.config.defaultCharts ? props.config.defaultCharts : []) as Ref<
    number[]
  >
  const availableCharts = ref([]) as Ref<ChartItem[]>
  const selectedCharts = ref([]) as Ref<ChartItem[]>
  const series = ref({}) as Ref<SeriesCollection>
  const chartLayouts = ref({}) as Ref<ChartLayoutsCollection>

  const readData = () => {
    if (!globalState.getProperty('isTestRunActive')) {
      clearInterval(timer)
    }

    selectedCharts.value.forEach((selector) => {
      const chart = charts.value[selector.value]
      const keys: string[] = []
      chart.series.forEach((series) => keys.push(series.key))
      const params = {
        ...route.query,
        ...{
          name: charts.value[selector.value].name,
          key: keys,
        },
      }

      axios
        .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/metrics-ot`, { params })
        .then((response) => {
          data.value[selector.value] = []
          response.data.data.series.forEach((s: APISeries) =>
            data.value[selector.value].push({
              name: s.name,
              y: s.data,
              x: response.data.data.categories,
              stackgroup: chart.stacked ? `stack-${selector.value}` : undefined,
              type: chart.type,
              hovertemplate: `%{x} <br>${s.name}: %{y}${chart.units}<extra></extra>`,
            }),
          )
        })
    })
  }

  const getChartLayout = (selector: number) => {
    const chart = charts.value[selector]
    const layout = {
      legend: {
        orientation: 'h',
        xanchor: 'left',
        x: 0,
        yanchor: 'top',
        y: 1.2,
      },
      yaxis: {
        title: {
          text: chart.units,
        },
      },
    } as ChartLayouts
    const colors: string[] = []
    chart.series.forEach((s) => {
      if (s.color) {
        colors.push(s.color)
      }
    })
    if (colors.length > 0) {
      layout.colors = colors
    }
    return layout
  }

  onMounted(() => {
    charts.value.forEach((chart, i) => {
      availableCharts.value.push({ value: i, text: chart.title })
      series.value[i] = []
      chartLayouts.value[i] = getChartLayout(i)
    })
    if (hash.get('chart-id')) {
      hash
        .get('chart-id')
        .split(',')
        .forEach((i) => selectedCharts.value.push(availableCharts.value[parseInt(i)]))
    } else {
      defaultCharts.value.forEach((i) => selectedCharts.value.push(availableCharts.value[i]))
    }
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

  watch(
    () => selectedCharts.value,
    () => {
      const chartId: number[] = []
      selectedCharts.value.forEach((chart) => {
        chartLayouts.value[chart.value] = getChartLayout(chart.value)
        chartId.push(chart.value)
      })

      if (chartId.length > 0) {
        hash.set('chart-id', chartId.join(','))
      } else {
        hash.remove('chart-id')
      }
    },
  )
</script>

<style scoped></style>
