<template>
  <va-card title="Test Run Logs">
    <div class="row logs-table--container">
      <div class="flex md12">
        <va-data-table
          v-model:sort-by="sortBy"
          v-model:sorting-order="sortingOrder"
          :items="items"
          :columns="columns"
          animated
          hoverable
        >
          <template #cell(download)="{ rowData }">
            <va-button icon="fa-download" preset="secondary" size="small" @click="downloadLog(rowData.id)"> </va-button>
          </template>
          <template #cell(view)="{ rowData }">
            <va-button
              icon="fa-eye"
              preset="secondary"
              size="small"
              @click="showLog(rowData.id, rowData.name, rowData.start)"
            >
            </va-button>
          </template>
          <template #cell(start)="{ rowData }">
            {{ formatDate(rowData.start) }}
          </template>
          <template #cell(finish)="{ rowData }">
            {{ formatDate(rowData.finish) }}
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
  <va-modal v-model="viewLog" fullscreen large :max-width="getModalSize()" fixed-layout hide-default-actions>
    <template #default>
      <pre>{{ logContent }}</pre>
    </template>
    <template #header>
      <div class="row">
        <div class="md10">
          <div class="va-modal__title" style="color: rgb(21, 78, 193)">
            {{ `${logName} - ${formatDate(logStart)}` }}
          </div>
        </div>
        <div class="flex md2">
          <va-icon v-if="logLoading" name="loop" :spin="logLoading"></va-icon>
        </div>
      </div>
    </template>
  </va-modal>
</template>

<script lang="ts" setup>
  import { defineProps, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { formatDate, getModalSize, getShortUpdateInterval, HashUtil } from '../../../utils'
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
  const hash = new HashUtil()
  const globalState = useGlobalState()
  let timer: number

  const props = defineProps<WidgetConfig>()

  const columns = ref(
    props.config && props.config.columns
      ? props.config.columns
      : [
          { key: 'download', label: 'Download', sortable: false, align: 'center', alignHead: 'center', width: '5%' },
          { key: 'view', label: 'View', sortable: false, align: 'center', alignHead: 'center', width: '5%' },
          { key: 'name', label: 'Name', sortable: true, align: 'left', alignHead: 'left', width: '70%' },
          { key: 'start', label: 'Start', sortable: true, align: 'right', alignHead: 'right', width: '10%' },
          { key: 'finish', label: 'Finish', sortable: true, align: 'right', alignHead: 'right', width: '10%' },
        ],
  )
  const perPage = ref(10)
  const currentPage = ref(1)
  const sortBy = ref('start')
  const sortingOrder = ref('asc')
  const totalPages = ref(0)
  const items = ref([])

  const viewLog = ref(false)
  const logContent = ref('')
  const logName = ref('Loading...')
  const logStart = ref('')
  const logLoading = ref(false)

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

    return axios
      .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/logs`, { params })
      .then((response) => {
        items.value = response.data.data
        totalPages.value = response.data.pages
      })
  }

  const readLog = (logId: string) => {
    logLoading.value = true
    return axios
      .get(`/projects/${route.params.project}/test-runs/${route.params.testrun}/logs/${logId}`)
      .then((response) => {
        logContent.value = response.data.body
        logName.value = response.data.name
        logStart.value = response.data.start
        logLoading.value = false
      })
      .catch()
  }

  const showLog = (logId: string, name: string, start: string) => {
    hash.set('log-id', logId)
    logName.value = name
    logStart.value = start
    viewLog.value = true
  }

  const downloadLog = (logId: string) => {
    window.open(
      `${axios.defaults.baseURL}/projects/${route.params.project}/test-runs/${route.params.testrun}/logs/${logId}/download`,
    )
  }

  onMounted(() => {
    readItems()
    timer = window.setInterval(readItems, getShortUpdateInterval())

    if (hash.get('log-id')) {
      viewLog.value = true
      readLog(hash.get('log-id'))
    }
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

  watch(
    () => route.hash,
    () => {
      if (hash.get('log-id')) {
        readLog(hash.get('log-id'))
      }
    },
  )

  watch(
    () => viewLog.value,
    () => {
      // Clear content to avoid lags on modal reopen
      if (!viewLog.value) {
        logContent.value = ''
        hash.remove('log-id')
      }
    },
  )
</script>

<style lang="scss" scoped>
  .logs-table--container {
    min-height: 460px;
  }
</style>
