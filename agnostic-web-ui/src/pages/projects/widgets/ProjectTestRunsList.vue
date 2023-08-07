<template>
  <va-card title="Test Runs">
    <div class="row test-runs-table--container">
      <div class="flex md12">
        <va-data-table
          v-model:sort-by="sortBy"
          v-model:sorting-order="sortingOrder"
          :items="items"
          :columns="columns"
          animated
          clickable
          hoverable
          @row:click="openProject"
        >
          <template #cell(start)="{ rowData }">
            {{ formatDate(rowData.start) }}
          </template>
          <template #cell(finish)="{ rowData }">
            {{ formatDate(rowData.finish) }}
          </template>
          <template #cell(tests)="{ rowData }">
            {{ `${rowData.tests_executed} / ${rowData.tests_failed}` }}
          </template>
          <template #cell(status)="{ rowData }">
            <va-icon
              :name="rowData.status.running ? 'loop' : 'fa-circle'"
              :color="rowData.status.terminated ? '#aaa' : rowData.status.failed ? '#fd5a3e' : '#97cc64'"
              :spin="rowData.status.running"
            ></va-icon>
          </template>
          <template #cell(variant)="{ rowData }">
            {{ formatVariant(rowData.variant) }}
          </template>
          <template #cell(properties)="{ rowData }">
            {{ JSON.stringify(rowData.properties) }}
          </template>
          <template #cell(execution_time)="{ rowData }">
            {{ formatInterval(rowData.execution_time) }}
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
  import { formatDate, formatInterval, getShortUpdateInterval } from '../../../utils'
  import { useRoute, useRouter } from 'vue-router'

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

  interface Variant {
    [prop: string]: string
  }

  interface EventItem {
    [prop: string]: string
  }

  interface Event {
    item: EventItem
  }

  const route = useRoute()
  const router = useRouter()

  const props = defineProps<WidgetConfig>()

  const columns = ref(
    props.config && props.config.columns
      ? props.config.columns
      : [
          { key: 'status', label: 'Status', sortable: true, align: 'center', alignHead: 'center', width: '5%' },
          {
            key: 'sut_branch',
            label: 'Branch',
            sortable: true,
            align: 'left',
            alignHead: 'left',
            width: '10%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
          {
            key: 'sut_version',
            label: 'Version',
            sortable: true,
            align: 'center',
            alignHead: 'center',
            width: '5%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '50px' },
          },
          {
            key: 'variant',
            label: 'Variant',
            sortable: true,
            width: '10%',
            align: 'right',
            alignHead: 'right',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
          {
            key: 'test_branch',
            label: 'Test Branch',
            sortable: true,
            align: 'left',
            alignHead: 'left',
            width: '10%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
          {
            key: 'test_version',
            label: 'Test Version',
            sortable: true,
            align: 'center',
            alignHead: 'center',
            width: '5%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '50px' },
          },
          { key: 'tests', label: 'Total / Failed', sortable: true, align: 'right', alignHead: 'right', width: '5%' },
          {
            key: 'execution_time',
            label: 'Execution Time',
            sortable: true,
            align: 'center',
            alignHead: 'center',
            width: '5%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '50px' },
          },
          {
            key: 'start',
            label: 'Start',
            sortable: true,
            align: 'right',
            alignHead: 'right',
            width: '10%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
          {
            key: 'finish',
            label: 'Finish',
            sortable: true,
            align: 'right',
            alignHead: 'right',
            width: '10%',
            style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100px' },
          },
        ],
  )
  const variantFormat = ref(props.config && props.config.variantFormat ? props.config.variantFormat : [])
  const perPage = ref(10)
  const currentPage = ref(1)
  const sortBy = ref('start')
  const sortingOrder = ref('desc')
  const totalPages = ref(0)
  const items = ref([])

  const readItems = () => {
    const params = { ...route.query }
    params['page'] = currentPage.value.toString()
    params['page_size'] = perPage.value.toString()
    if (sortBy.value && sortingOrder.value) {
      params['order_by'] = sortBy.value
      params['order'] = sortingOrder.value
    }

    axios
      .get(`/reporting/projects/${route.params.project}/test-runs`, { params })
      .then((response) => {
        items.value = response.data.data
        totalPages.value = response.data.pages
      })
      .catch()
  }

  const openProject = (event: Event) => {
    router.push(`/projects/${route.params.project}/test-runs/${event.item.id}`)
  }

  const formatVariant = (variant: Variant): string => {
    if (variant) {
      const formatted = []
      for (const key of variantFormat.value) {
        if (variant[key]) {
          formatted.push(variant[key])
        }
      }
      return formatted.join('/')
    }

    return ''
  }

  let timer: number

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
      if (to !== from && route.params.project) {
        readItems()
      }
    },
  )
</script>

<style lang="scss" scoped>
  .test-runs-table--container {
    min-height: 460px;
  }
</style>
