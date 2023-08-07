<template>
  <div class="row">
    <div class="flex md8">
      <div class="row">
        <div class="flex md12">
          <h1 style="display: inline">Projects</h1>
        </div>
      </div>
    </div>
    <div v-if="isAdmin" class="flex mb-1 md4">
      <div class="row justify-end">
        <div class="flex align-self--center"><ProjectCreatePopup /></div>
      </div>
    </div>
  </div>
  <br />
  <va-card title="Projects">
    <div class="row projects-table--container">
      <div class="flex md12">
        <va-data-table
          v-model:sort-by="sortBy"
          v-model:sorting-order="sortingOrder"
          :items="items"
          :columns="columns"
          animated
          clickable
          hoverable
          class="projects-table--table"
          @row:click="openProject"
        >
          <template #cell(test_runs_count)="{ rowData }">
            {{ rowData.test_runs_count === 0 ? '' : rowData.test_runs_count }}
          </template>
          <template #cell(latest_test_run)="{ rowData }">
            {{ formatDate(rowData.latest_test_run) }}
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
  import { computed, defineAsyncComponent, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import axios from 'axios'
  import { useRoute, useRouter } from 'vue-router'
  import { formatDate, getLongUpdateInterval, HashUtil } from '../../utils'

  interface EventItem {
    [prop: string]: string
  }

  interface Event {
    item: EventItem
  }

  const route = useRoute()
  const router = useRouter()
  const hash = new HashUtil()

  const ProjectCreatePopup = defineAsyncComponent(() => import('../projects/components/ProjectCreatePopup.vue'))

  const columns = [
    { key: 'name', label: 'Project Name', sortable: true, width: '60%', align: 'left', alignHead: 'left' },
    { key: 'test_runs_count', label: 'Test Runs', sortable: true, width: '10%', align: 'right', alignHead: 'right' },
    { key: 'latest_test_run', label: 'Latest', sortable: true, width: '30%', align: 'right', alignHead: 'right' },
  ]
  const perPage = ref(10)
  const currentPage = ref(1)
  const sortBy = ref('name')
  const sortingOrder = ref('asc')
  const totalPages = ref(0)
  const items = ref([])

  const isAdmin = computed(() => {
    return hash.get('admin') == 'true'
  })

  const readItems = () => {
    const params = { ...route.query }
    params['page'] = currentPage.value.toString()
    params['page_size'] = perPage.value.toString()
    if (sortBy.value && sortingOrder.value) {
      params['order_by'] = sortBy.value
      params['order'] = sortingOrder.value
    }

    axios
      .get('/reporting/projects', { params })
      .then((response) => {
        items.value = response.data.data
        totalPages.value = response.data.pages
      })
      .catch()
  }

  const openProject = (event: Event) => {
    router.push(`/projects/${event.item.id}`)
  }

  let timer: number

  onMounted(() => {
    readItems()
    timer = window.setInterval(readItems, getLongUpdateInterval())
  })

  onBeforeUnmount(() => {
    window.clearInterval(timer)
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
</script>

<style lang="scss" scoped>
  .projects-table--container {
    min-height: 430px;
  }
</style>
