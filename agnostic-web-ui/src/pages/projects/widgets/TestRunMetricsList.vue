<template>
  <va-card title="Test Run Metrics">
    <div class="row tests-table--container">
      <div class="flex md12">
        <va-data-table
          v-model:sort-by="sortBy"
          v-model:sorting-order="sortingOrder"
          :items="items"
          :columns="columns"
          animated
          hoverable
        >
        </va-data-table>
      </div>
    </div>
    <div class="row justify-end">
      <div class="flex" style="padding-right: 1.5em">
        <va-pagination v-model="currentPage" :pages="totalPages" gapped input />
      </div>
    </div>
  </va-card>
</template>

<script lang="ts" setup>
  import { defineProps, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { getShortUpdateInterval } from '../../../utils'
  import { useRoute } from 'vue-router'
  import { useGlobalState } from '../../../store'

  interface ColumnConfig {
    [prop: string]: string
  }

  interface WidgetConfigOptions {
    columns: ColumnConfig[]
  }

  interface WidgetConfig {
    config?: WidgetConfigOptions
  }

  const route = useRoute()
  const globalState = useGlobalState()
  let timer: number

  const props = defineProps<WidgetConfig>()

  const columns = ref(
    props.config && props.config.columns
      ? props.config.columns
      : [
          { key: 'description', label: 'Description', sortable: true, align: 'left', alignHead: 'left', width: '80%' },
          { key: 'name', label: 'Reference', sortable: true, align: 'right', alignHead: 'right', width: '10%' },
          { key: 'value', label: 'Raw', sortable: true, align: 'right', alignHead: 'right', width: '10%' },
        ],
  )
  const perPage = ref(10)
  const currentPage = ref(1)
  const sortBy = ref('name')
  const sortingOrder = ref('asc')
  const totalPages = ref(0)
  const items = ref([])

  const readItems = () => {
    if (!globalState.getProperty('isTestRunActive')) {
      clearInterval(timer)
    }

    const params = { ...route.query }
    params['page'] = currentPage.value.toString()
    params['page_size'] = perPage.value.toString()
    if (sortBy.value && sortingOrder.value) {
      params['order_by'] = sortBy.value
      params['order'] = sortingOrder.value
    }

    axios
      .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/metrics-list`, { params })
      .then((response) => {
        items.value = response.data.data
        totalPages.value = response.data.pages
      })
  }

  onMounted(() => {
    readItems()
    timer = window.setInterval(readItems, getShortUpdateInterval())
  })

  onBeforeUnmount(() => {
    clearInterval(timer)
  })

  watch(
    () => currentPage.value,
    () => readItems(),
  )
  watch(
    () => sortBy.value,
    () => readItems(),
  )
  watch(
    () => sortingOrder.value,
    () => readItems(),
  )

  watch(
    () => route.query,
    (to, from) => {
      if (to !== from && route.params.testrun) {
        readItems()
      }
    },
  )
</script>

<style lang="scss" scoped>
  .tests-table--container {
    min-height: 460px;
  }
</style>
