<template>
  <va-modal v-model="showModal" fullscreen large :max-width="getModalSize()" fixed-layout hide-default-actions>
    <template #header>
      <div class="row">
        <div class="md1">
          <va-badge :text="testResult" :color="getTestColorByResult(testResult)" text-color="#ffffff"></va-badge>
        </div>
        <div class="flex md11">
          <div class="va-modal__title" style="color: rgb(21, 78, 193); padding-left: 5px; padding-top: 5px">
            {{ testTitle }}
          </div>
        </div>
      </div>
    </template>
    <div v-if="showModal">
      <div class="row">
        <div class="flex md6">
          <h3 style="padding-left: 10px">Info</h3>
          <br />
          <va-data-table :items="testInfo" :columns="testInfoColumns" hide-default-header> </va-data-table>
        </div>
        <div class="flex md6" style="padding-left: 20px">
          <h3 v-if="testDescription">Description</h3>
          <br />
          <div>{{ testDescription }}</div>
          <div v-if="testSkipReason">
            <br />
            <h3>Skip Reason</h3>
            <br />
            <div>{{ testSkipReason }}</div>
          </div>
        </div>
      </div>
      <br />
      <br />
      <div v-if="testAttachments.length > 0">
        <h3 style="padding-left: 10px">Attachments</h3>
        <br />
        <div class="row" style="padding-left: 10px">
          <div v-for="attachment of testAttachments" :key="attachment.id" class="flex md6" style="padding: 5px 0 5px 0">
            <va-icon :name="getIconByMime(attachment.mime_type)" style="padding-right: 5px"></va-icon>
            <a
              :href="`${axios.defaults.baseURL}/projects/${route.params.project}/test-runs/${route.params.testrun}/tests/${testId}/attachments/${attachment.id}`"
            >
              {{ attachment.name }} ({{ formatByteSize(attachment.size) }})
            </a>
          </div>
        </div>
      </div>
      <br />
      <br />
      <div v-if="testErrorMessage" class="row">
        <div class="flex md12">
          <va-collapse v-model="testErrorMessageCollapse" header="Error Message" class="mb-3">
            <template #default>
              <div>
                <pre style="overflow-x: scroll; overflow-y: clip">{{ testErrorMessage }}</pre>
              </div>
            </template>
          </va-collapse>
        </div>
      </div>
      <div v-if="testMetrics.length > 0" class="row">
        <div class="flex md12">
          <va-collapse v-model="testMetricsCollapse" header="Metrics" class="mb-3">
            <va-data-table :items="testMetrics" :columns="testMetricsColumns" animated hoverable></va-data-table>
          </va-collapse>
        </div>
      </div>
      <div v-if="testLogs.length > 0" class="row">
        <div class="flex md12">
          <va-collapse
            v-for="log of testLogs"
            :key="log.id"
            v-model="testLogsCollapse[log.id]"
            :model-value="false"
            class="mb-3"
          >
            <template #default>
              <div>
                <pre style="overflow-x: scroll; overflow-y: clip">{{ log.body }}</pre>
              </div>
            </template>
            <template #header>
              <div class="va-collapse__header" style="color: rgb(38, 40, 36); background-color: rgb(235, 241, 244)">
                <div class="va-collapse__header__text">
                  Log: <i>{{ log.name }}</i>
                </div>
                <i
                  class="va-icon material-icons va-collapse__header__icon"
                  style="color: rgb(38, 40, 36); font-size: 19px; height: 19px; line-height: 19px"
                  >expand_more</i
                >
              </div>
            </template>
          </va-collapse>
        </div>
      </div>
      <div v-if="testRequestsTimeline.length > 0" class="row">
        <div class="flex mb12" style="width: 100%">
          <va-collapse v-model="testRequestsTimelineCollapse" header="Requests Timeline" class="mb-3">
            <va-timeline vertical centered>
              <va-timeline-item v-for="request of testRequestsTimeline" :key="request.id" active>
                <template #before>
                  <div class="va-timeline-item__date">
                    <span class="title va-timeline-item__text">
                      {{ formatTimelineDate(request.timestamp) }}
                    </span>
                  </div>
                </template>
                <template #after>
                  <va-card
                    stripe
                    :stripe-color="
                      'code' in request.contents && (!request.contents.code || request.contents.code >= 400)
                        ? 'danger'
                        : 'success'
                    "
                    class="mb-0"
                  >
                    <va-card-title>{{ request.request_type }}</va-card-title>
                    <va-card-content>{{ formatTimelineRequest(request) }}</va-card-content>
                  </va-card>
                </template>
              </va-timeline-item>
            </va-timeline>
          </va-collapse>
        </div>
      </div>
      <div v-if="testRequestsHTTP.length > 0" class="row">
        <div class="flex md12">
          <va-collapse v-model="testRequestsHTTPCollapse" header="HTTP Requests" class="mb-3">
            <va-data-table :items="testRequestsHTTP" :columns="testRequestsHTTPColumns" animated hoverable>
              <template #cell(url)="{ rowData }">
                <div style="white-space: pre-wrap; overflow: hidden">{{ rowData.url }}</div>
              </template>
              <template #cell(payload)="{ rowData }">
                <DownloadableCell
                  :content="rowData.payload || ''"
                  :file-name="`HTTP-Payload-${rowData.url.slice(0, 50)}`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
              <template #cell(response)="{ rowData }">
                <DownloadableCell
                  :content="rowData.response"
                  :file-name="`HTTP-Response-${rowData.url.slice(0, 50)}`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
            </va-data-table>
            <template #header>
              <div class="va-collapse__header" style="color: rgb(38, 40, 36); background-color: rgb(235, 241, 244)">
                <div class="va-collapse__header__text">Requests: <i>HTTP</i></div>
                <i
                  class="va-icon material-icons va-collapse__header__icon"
                  style="color: rgb(38, 40, 36); font-size: 19px; height: 19px; line-height: 19px"
                  >expand_more</i
                >
              </div>
            </template>
          </va-collapse>
        </div>
      </div>
      <div v-if="testRequestsGRPC.length > 0" class="row">
        <div class="flex md12">
          <va-collapse v-model="testRequestsGRPCCollapse" header="HTTP Requests" class="mb-3">
            <va-data-table :items="testRequestsGRPC" :columns="testRequestsGRPCColumns" animated hoverable>
              <template #cell(request)="{ rowData }">
                <DownloadableCell
                  :content="rowData.request"
                  :file-name="`GRPC-Request-${rowData.method}`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
              <template #cell(response)="{ rowData }">
                <DownloadableCell
                  :content="rowData.response"
                  :file-name="`GRPC-Response-${rowData.method}`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
            </va-data-table>
            <template #header>
              <div class="va-collapse__header" style="color: rgb(38, 40, 36); background-color: rgb(235, 241, 244)">
                <div class="va-collapse__header__text">Requests: <i>GRPC</i></div>
                <i
                  class="va-icon material-icons va-collapse__header__icon"
                  style="color: rgb(38, 40, 36); font-size: 19px; height: 19px; line-height: 19px"
                  >expand_more</i
                >
              </div>
            </template>
          </va-collapse>
        </div>
      </div>
      <div v-if="testRequestsNATS.length > 0" class="row">
        <div class="flex md12">
          <va-collapse v-model="testRequestsNATSCollapse" header="HTTP Requests" class="mb-3">
            <va-data-table :items="testRequestsNATS" :columns="testRequestsNATSColumns" animated hoverable>
              <template #cell(pqyload)="{ rowData }">
                <DownloadableCell
                  :content="rowData.payload"
                  :file-name="`NATS-Message`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
            </va-data-table>
            <template #header>
              <div class="va-collapse__header" style="color: rgb(38, 40, 36); background-color: rgb(235, 241, 244)">
                <div class="va-collapse__header__text">Requests: <i>NATS</i></div>
                <i
                  class="va-icon material-icons va-collapse__header__icon"
                  style="color: rgb(38, 40, 36); font-size: 19px; height: 19px; line-height: 19px"
                  >expand_more</i
                >
              </div>
            </template>
          </va-collapse>
        </div>
      </div>
      <div v-if="testRequestsSQL.length > 0" class="row">
        <div class="flex md12">
          <va-collapse v-model="testRequestsSQLCollapse" header="HTTP Requests" class="mb-3">
            <va-data-table :items="testRequestsSQL" :columns="testRequestsSQLColumns" animated hoverable>
              <template #cell(request)="{ rowData }">
                <DownloadableCell
                  :content="rowData.response"
                  :file-name="`SQL-Request`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
              <template #cell(response)="{ rowData }">
                <DownloadableCell
                  :content="rowData.response"
                  :file-name="`SQL-Response`"
                  :limit="1000"
                ></DownloadableCell>
              </template>
            </va-data-table>
            <template #header>
              <div class="va-collapse__header" style="color: rgb(38, 40, 36); background-color: rgb(235, 241, 244)">
                <div class="va-collapse__header__text">Requests: <i>SQL</i></div>
                <i
                  class="va-icon material-icons va-collapse__header__icon"
                  style="color: rgb(38, 40, 36); font-size: 19px; height: 19px; line-height: 19px"
                  >expand_more</i
                >
              </div>
            </template>
          </va-collapse>
        </div>
      </div>
    </div>
  </va-modal>
</template>

<script lang="ts" setup>
  import { defineAsyncComponent, onMounted, ref, Ref, watch } from 'vue'
  import axios from 'axios'
  import {
    formatByteSize,
    formatTime,
    getFormattedInterval,
    getIconByMime,
    getModalSize,
    getTestColorByResult,
    HashUtil,
    GenericJSONResponse,
  } from '../../../../utils'
  import { useRoute } from 'vue-router'
  import moment from 'moment'

  interface TestInfo {
    name: string
    value: string | undefined
  }

  interface Request {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [props: string]: any
  }

  const DownloadableCell = defineAsyncComponent(() => import('../../components/DownloadableCell.vue'))

  const route = useRoute()
  const hash = new HashUtil()

  const showModal = ref(false)
  const testId = ref(null)
  const testTitle = ref('')
  const testResult = ref('')
  const testDescription = ref('')
  const testSkipReason = ref('')

  const testInfoColumns = ref([
    { key: 'name', label: 'Name', align: 'left', alignHead: 'left', width: '20%' },
    {
      key: 'value',
      label: 'Value',
      align: 'right',
      alignHead: 'left',
      width: '80%',
      style: { overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '250px' },
    },
  ])
  const testInfo = ref([]) as Ref<TestInfo[]>

  const testErrorMessageCollapse = ref(false)
  const testErrorMessage = ref('')

  const testAttachments = ref([]) as Ref<GenericJSONResponse>

  const testMetricsCollapse = ref(false)
  const testMetricsColumns = ref([
    { key: 'description', label: 'Description', sortable: true, align: 'left', alignHead: 'left', width: '80%' },
    { key: 'name', label: 'Reference', sortable: true, align: 'right', alignHead: 'right', width: '10%' },
    { key: 'value', label: 'Raw', sortable: true, align: 'right', alignHead: 'right', width: '10%' },
  ])
  const testMetrics = ref([])

  const testLogsCollapse = ref({})
  const testLogs = ref([]) as Ref<GenericJSONResponse[]>

  const testRequestsTimelineCollapse = ref(false)
  const testRequestsTimeline = ref([]) as Ref<GenericJSONResponse[]>

  const testRequestsHTTPCollapse = ref(false)
  const testRequestsHTTPColumns = ref([
    {
      key: 'code',
      label: 'Code',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '5%',
    },
    {
      key: 'elapsed',
      label: 'Elapsed (s)',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '5%',
    },
    {
      key: 'method',
      label: 'Method',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '5%',
    },
    { key: 'url', label: 'URL', sortable: false, align: 'left', alignHead: 'left', verticalAlign: 'top', width: '10%' },
    {
      key: 'payload',
      label: 'Payload',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '30%',
    },
    {
      key: 'response',
      label: 'Response',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '45%',
    },
  ])
  const testRequestsHTTP = ref([]) as Ref<Request[]>

  const testRequestsGRPCCollapse = ref(false)
  const testRequestsGRPCColumns = ref([
    {
      key: 'method',
      label: 'Method',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '20%',
    },
    {
      key: 'elapsed',
      label: 'Elapsed (s)',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '10%',
    },
    {
      key: 'request',
      label: 'Request',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '35%',
    },
    {
      key: 'response',
      label: 'Response',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '35%',
    },
  ])
  const testRequestsGRPC = ref([]) as Ref<Request[]>

  const testRequestsNATSCollapse = ref(false)
  const testRequestsNATSColumns = ref([
    {
      key: 'method',
      label: 'Method',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '10%',
    },
    {
      key: 'subject',
      label: 'Subject',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '30%',
    },
    {
      key: 'payload',
      label: 'Payload',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '60%',
    },
  ])
  const testRequestsNATS = ref([]) as Ref<Request[]>

  const testRequestsSQLCollapse = ref(false)
  const testRequestsSQLColumns = ref([
    {
      key: 'elapsed',
      label: 'Elapsed (s)',
      sortable: false,
      align: 'center',
      alignHead: 'center',
      verticalAlign: 'top',
      width: '10%',
    },
    {
      key: 'request',
      label: 'Request',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '45%',
    },
    {
      key: 'response',
      label: 'Response',
      sortable: false,
      align: 'left',
      alignHead: 'left',
      verticalAlign: 'top',
      width: '45%',
    },
  ])
  const testRequestsSQL = ref([]) as Ref<Request[]>

  const readData = () => {
    axios
      .get(`/reporting/projects/${route.params.project}/test-runs/${route.params.testrun}/tests/${hash.get('test-id')}`)
      .then((response) => {
        testId.value = response.data.details.id
        testTitle.value = response.data.details.name
        testResult.value = response.data.details.result
        testDescription.value = response.data.details.description
        testSkipReason.value = response.data.details.reason
        testErrorMessage.value = response.data.details.error_message

        const info = []
        info.push({
          name: 'Elapsed',
          value: getFormattedInterval(response.data.details.start, response.data.details.finish),
        })
        info.push({ name: 'Start', value: formatTime(response.data.details.start) })
        info.push({ name: 'Finish', value: formatTime(response.data.details.finish) })
        info.push({ name: 'Reference', value: `${response.data.details.path}::${response.data.details.name}` })
        testInfo.value = info

        testMetrics.value = response.data.metrics
        testAttachments.value = response.data.attachments

        testLogs.value = response.data.logs

        testRequestsTimeline.value = response.data.requests

        const http = []
        const grpc = []
        const nats = []
        const sql = []
        for (const request of response.data.requests) {
          switch (request.request_type) {
            case 'http':
              http.push(request.contents)
              break
            case 'grpc':
              grpc.push(request.contents)
              break
            case 'nats':
              nats.push(request.contents)
              break
            case 'sql':
              sql.push(request.contents)
              break
          }
        }
        testRequestsHTTP.value = http
        testRequestsGRPC.value = grpc
        testRequestsNATS.value = nats
        testRequestsSQL.value = sql
      })
  }

  const formatTimelineDate = (date: string) => {
    if (date) {
      return moment(date).format('HH:mm:ss.SSS')
    }
    return date
  }

  const formatTimelineRequest = (request: Request) => {
    let result = ''
    switch (request.request_type) {
      case 'http':
        result = `${request.contents.method} ${request.contents.url}`
        break
      case 'grpc':
        result = `${request.contents.method}`
        break
      case 'nats':
        result = `${request.contents.method} ${request.contents.subject}`
        break
      case 'sql':
        result = request.contents.request
        break
    }
    return result
  }

  onMounted(() => {
    if (hash.get('test-id')) {
      showModal.value = true
    }
  })

  watch(
    () => route.hash,
    () => {
      if (hash.get('test-id')) {
        showModal.value = true
      }
    },
  )
  watch(
    () => showModal.value,
    (isOpen: boolean) => {
      if (isOpen) {
        readData()
      } else {
        if (hash.get('test-id')) {
          hash.remove('test-id')
        }
      }
    },
  )
</script>

<style lang="scss">
  :root {
    --va-collapse-header-content-text-font-weight: 300;
  }
  // TODO: Replace dirty fixes either with another timeline
  //  or with Vuestic timeline one it is fixed
  //  https://github.com/epicmaxco/vuestic-ui/issues/2245#issuecomment-1219257286
  .va-timeline-separator {
    &__line {
      background-color: rgb(61, 146, 9) !important;
    }
    &__center--active {
      background-color: rgb(61, 146, 9) !important;
    }
  }
  .va-timeline-item {
    &__date {
      text-align: end;
    }
  }
</style>
