<template>
  <va-card title="Test Run Progress">
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
          <template #cell(level)="{ rowData }">
            <va-badge
              :text="rowData.level"
              :color="getProgressColorByLevel(rowData.level)"
              text-color="#ffffff"
            ></va-badge>
          </template>
          <template #cell(timestamp)="{ rowData }">
            {{ formatTime(rowData.timestamp) }}
          </template>
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
  import { formatTime, getProgressColorByLevel, getShortUpdateInterval } from '../../../utils'
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
          { key: 'level', label: 'Level', sortable: true, align: 'center', alignHead: 'center', width: '5%' },
          { key: 'timestamp', label: 'Time', sortable: true, align: 'left', alignHead: 'left', width: '10%' },
          { key: 'message', label: 'Message', sortable: true, align: 'left', alignHead: 'left', width: '85%' },
        ],
  )
  const perPage = ref(10)
  const currentPage = ref(1)
  const sortBy = ref('timestamp')
  const sortingOrder = ref('desc')
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
      .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/progress`, { params })
      .then((response) => {
        items.value = response.data.data
        totalPages.value = response.data.pages
      })
      .catch()
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
