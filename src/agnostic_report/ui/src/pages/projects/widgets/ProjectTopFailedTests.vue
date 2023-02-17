<template>
  <va-card style="width: 100%; height: 100%">
    <va-card-title>Top {{ count }} Failed Tests</va-card-title>
    <va-card-content>
      <va-data-table :items="items" :columns="columns" :loading="loading" hide-default-header>
        <template #cell(percent_failed)="{ rowData }"> {{ rowData.percent_failed }}% </template>
      </va-data-table>
    </va-card-content>
  </va-card>
</template>

<script lang="ts" setup>
  import { defineProps, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { useRoute } from 'vue-router'
  import { getShortUpdateInterval } from '../../../utils'

  interface WidgetConfigOptions {
    count?: number
  }

  interface WidgetConfig {
    config: WidgetConfigOptions
  }

  const route = useRoute()

  const props = defineProps<WidgetConfig>()

  const count = ref(props.config && props.config.count ? props.config.count : 5)
  const columns = ref([
    {
      key: 'name',
      label: 'Name',
      align: 'left',
      alignHead: 'left',
      width: '90%',
      style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '200px' },
    },
    { key: 'percent_failed', label: '% Failed', align: 'right', alignHead: 'right', width: '10%' },
  ])
  const loading = ref(false)
  const items = ref([])

  const readItems = () => {
    const params = {
      ...route.query,
      ...{
        limit: count.value,
      },
    }

    return axios
      .get(`/reporting/projects/${route.params.project}/top-failed-tests`, { params })
      .then((response) => {
        items.value = response.data.data
      })
      .catch()
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
