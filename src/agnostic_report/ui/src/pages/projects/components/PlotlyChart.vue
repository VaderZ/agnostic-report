<template>
  <va-card :style="`width: 100%; height: ${props.height}px;`">
    <va-card-title> {{ props.title }} </va-card-title>
    <va-card-content>
      <div style="height: 200px"><VuePlotly :data="data" :layout="layout" :options="options"></VuePlotly></div>
    </va-card-content>
  </va-card>
</template>

<script lang="ts" setup>
  import { VuePlotly } from 'vue3-plotly'
  import { defineProps, ref, toRef, watch } from 'vue'

  interface Options {
    [props: string]: unknown
  }

  interface Layout {
    [props: string]: unknown
  }

  interface Trace {
    [props: string]: unknown
  }

  type Data = Trace[]

  interface ChartProperties {
    data: Data
    layout?: Layout
    options?: Options
    loading?: boolean
    title?: string
    height?: number
  }

  const props = defineProps<ChartProperties>()

  const defaultLayout = {
    autosize: true,
    height: props.height ? props.height - 50 : props.height,
    font: {
      family: '"Source Sans Pro", Avenir, Helvetica, Arial, sans-serif',
    },
    margin: {
      b: 30,
      l: 40,
      r: 40,
      t: 20,
    },
  }

  const data = toRef(props, 'data')
  const layout = ref(props.layout ? { ...defaultLayout, ...props.layout } : defaultLayout)
  const options = toRef(props, 'options')

  watch(
    () => props.layout,
    () => {
      layout.value = props.layout ? { ...defaultLayout, ...props.layout } : defaultLayout
    },
  )
</script>

<style scoped>
  .va-card__title {
    padding-bottom: 0;
  }
</style>
