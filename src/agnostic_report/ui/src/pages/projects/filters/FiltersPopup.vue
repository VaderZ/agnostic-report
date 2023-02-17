<template>
  <va-button size="small" icon="fa-filter" preset="secondary" @click="showModal = !showModal"></va-button>
  <va-modal v-model="showModal" ok-text="Apply" @ok="setFilterQuery">
    <div v-if="showModal && filters && values">
      <div v-for="(filter, name) of filters" :key="name">
        <div v-if="Array.isArray(filter)">
          <h3>{{ getFilterName(name) }}</h3>
          <va-select v-model="values[name]" placeholder="<any>" :options="filter" multiple></va-select>
          <br />
        </div>
        <div v-else>
          <h3>{{ getFilterName(name) }}</h3>
          <div v-for="(subfilter, subname) of filter" :key="subname">
            <h4>{{ subname }}</h4>
            <va-select v-model="values[name][subname]" placeholder="<any>" :options="subfilter" multiple></va-select>
          </div>
        </div>
      </div>
    </div>
    <template #header>
      <div class="row">
        <div class="flex md7">
          <div class="va-modal__title" style="color: rgb(21, 78, 193)">Filters</div>
        </div>
        <div class="flex md5">
          <va-button size="small" icon="clear" @click="clearAllFilters">Clear All</va-button>
        </div>
      </div>
    </template>
  </va-modal>
</template>

<script lang="ts" setup>
  import { defineProps, Ref, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import axios from 'axios'

  interface Filters {
    filters: { [key: string]: string }
  }

  interface WidgetConfig {
    config?: Filters
  }

  const props = defineProps<WidgetConfig>()

  interface Filter {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [prop: string]: any
  }

  const route = useRoute()
  const router = useRouter()

  const enabledFilters = ref(
    props.config && props.config.filters
      ? props.config.filters
      : {
          sut_branch: 'SUT Branch',
          test_branch: 'Test Branch',
          variant: 'Variant',
        },
  )

  const showModal = ref(false)
  const values = ref({}) as Ref<Filter>
  const filters = ref(null)

  const readData = () => {
    axios
      .get(`/reporting/projects/${route.params.project}/test-run-filters`, { params: route.query })
      .then((response) => {
        const data = response.data.data
        for (const name in data) {
          if (Array.isArray(data[name])) {
            values.value[name] = []
            if (route.query[name]) {
              const query = Array.isArray(route.query[name]) ? route.query[name] : [route.query[name]]
              if (query) {
                for (const val of query) {
                  if (data[name].includes(val)) {
                    values.value[name].push(val)
                  }
                }
              }
            }
          } else {
            values.value[name] = {}
            for (const subname in data[name]) {
              values.value[name][subname] = []
            }
            if (route.query[name]) {
              const query = Array.isArray(route.query[name]) ? route.query[name] : ([route.query[name]] as string[])
              if (query) {
                for (const val of query) {
                  if (val) {
                    const parts = val.split(' -eq ')
                    if (data[name][parts[0]].includes(parts[1])) {
                      values.value[name][parts[0]].push(parts[1])
                    }
                  }
                }
              }
            }
          }
        }
        filters.value = data
      })
  }

  const setFilterQuery = () => {
    let update = {} as Filter
    if (route.query) {
      update = { ...route.query }
    }
    for (const name in values.value) {
      if (Array.isArray(values.value[name])) {
        update[name] = values.value[name]
      } else {
        update[name] = []
        for (const subname in values.value[name]) {
          for (const val of values.value[name][subname]) {
            update[name].push(`${subname} -eq ${val}`)
          }
        }
      }
    }
    router.replace({ ...route, query: update })
  }

  const getFilterName = (name: string | number): string => {
    return enabledFilters.value[name]
  }

  const clearAllFilters = () => {
    const vals = { ...values.value }
    for (const name in vals) {
      if (Array.isArray(vals[name])) {
        vals[name] = []
      } else {
        for (const subname in vals[name]) {
          vals[name][subname] = []
        }
      }
    }
    values.value = vals
  }

  watch(
    () => showModal.value,
    (isOpen: boolean) => {
      if (isOpen) {
        readData()
      }
    },
  )
</script>

<style scoped></style>
