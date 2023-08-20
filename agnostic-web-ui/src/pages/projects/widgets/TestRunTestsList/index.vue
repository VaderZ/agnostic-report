<template>
  <va-card title="Tests">
    <div class="row tests-table--container">
      <div class="flex md12">
        <va-data-table
          v-model:sort-by="sortBy"
          v-model:sorting-order="sortingOrder"
          :items="items"
          :columns="columns"
          animated
          clickable
          hoverable
          @row:click="openTest"
        >
          <template #cell(result)="{ rowData }">
            <va-badge
              :text="rowData.result"
              :color="getTestColorByResult(rowData.result)"
              text-color="#ffffff"
            ></va-badge>
          </template>
          <template #cell(execution_time)="{ rowData }">
            {{ moment.utc(moment.duration(rowData.execution_time).asMilliseconds()).format('mm:ss') }}
          </template>
        </va-data-table>
      </div>
    </div>
    <div class="row justify-end">
      <div class="flex" style="padding-right: 1.5em">
        <va-pagination v-model="currentPage" :pages="totalPages" gapped input />
      </div>
    </div>
    <TestPopup></TestPopup>
  </va-card>
</template>

<script lang="ts" setup>
  import { defineAsyncComponent, defineProps, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { getShortUpdateInterval, getTestColorByResult, HashUtil } from '../../../../utils'
  import { useRoute } from 'vue-router'
  import { useGlobalState } from '../../../../store'
  import moment from 'moment'

  interface ColumnConfig {
    [prop: string]: string
  }

  interface WidgetConfigOptions {
    columns: ColumnConfig[]
    variantFormat: string[]
  }

  interface WidgetConfig {
    config?: WidgetConfigOptions
  }

  interface EventItem {
    [prop: string]: string
  }

  interface Event {
    item: EventItem
  }

  const TestPopup = defineAsyncComponent(() => import('./TestPopup.vue'))

  const route = useRoute()
  const hash = new HashUtil()
  const globalState = useGlobalState()
  let timer: number

  const props = defineProps<WidgetConfig>()

  const columns = ref(
    props.config && props.config.columns
      ? props.config.columns
      : [
          { key: 'result', label: 'Result', sortable: true, align: 'center', alignHead: 'center', width: '5%' },
          {
            key: 'name',
            label: 'Name',
            sortable: true,
            align: 'left',
            alignHead: 'left',
            width: '45%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
          {
            key: 'path',
            label: 'Path',
            sortable: true,
            align: 'left',
            alignHead: 'left',
            width: '45%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
          {
            key: 'execution_time',
            label: 'Execution Time',
            sortable: true,
            align: 'center',
            alignHead: 'center',
            width: '5%',
          },
        ],
  )
  const perPage = ref(10)
  const currentPage = ref(1)
  const sortBy = ref('path')
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
      .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/tests`, { params })
      .then((response) => {
        items.value = response.data.data
        totalPages.value = response.data.pages
      })
  }

  const openTest = (event: Event) => {
    hash.set('test-id', event.item.id)
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
