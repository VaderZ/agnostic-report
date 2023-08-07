<template>
  <div class="row">
    <div class="flex md6">
      <div class="row justify-start align-content-start">
        <div class="flex" style="padding-right: 0">
          <va-icon name="fa-arrow-left" @click="goBack"></va-icon>
        </div>
        <div class="flex md11" style="padding-left: 5px">
          <div class="row justify-start">
            <div class="flex" style="padding-right: 0">
              <h1>{{ projectName }}</h1>
            </div>
            <div class="flex md6" style="padding-left: 5px">
              <va-badge
                v-if="testRunDetails && testRunDetails.sut_branch"
                right
                top
                :text="testRunDetails.sut_branch"
                :color="
                  testRunDetails.status.terminated ? '#aaa' : testRunDetails.status.failed ? '#fd5a3e' : '#97cc64'
                "
                text-color="#ffffff"
                style="padding-left: 5px"
              />
              <va-badge
                v-if="testRunDetails && testRunDetails.sut_version"
                right
                top
                :text="testRunDetails.sut_version"
                :color="
                  testRunDetails.status.terminated ? '#aaa' : testRunDetails.status.failed ? '#fd5a3e' : '#97cc64'
                "
                text-color="#ffffff"
                style="padding: 0 5px 0 5px"
              />
              <va-icon v-if="testRunDetails && testRunDetails.status.running" name="loop" spin></va-icon>
              <ProjectConfigPopup v-if="isAdmin" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="flex md6">
      <div class="row justify-end">
        <div class="flex"><TestResultDropdown /></div>
        <div class="flex md5 sm5 xs5"><TestSearchInput /></div>
      </div>
    </div>
  </div>
  <br />
  <div v-if="config && config.testrun">
    <va-tabs v-model="activeTab">
      <template #tabs>
        <va-tab v-for="tab in config.testrun.tabs" :key="tab.name">
          {{ tab.name }}
        </va-tab>
      </template>
    </va-tabs>
    <va-separator />
    <component :is="activeTabLayout" :key="activeTab">
      <template v-for="[idx, widget] in activeTabWidgets.entries()" #[idx] :key="idx">
        <component :is="widget.type" v-if="widget" :config="widget.config" />
      </template>
    </component>
  </div>
  <div v-else>
    <va-inner-loading loading></va-inner-loading>
  </div>
</template>

<script lang="ts">
  import { defineAsyncComponent } from 'vue'

  export default {
    components: {
      //Filters
      TimeRangeSlider: defineAsyncComponent(() => import('./filters/TimeRangeSlider.vue')),
      FiltersPopup: defineAsyncComponent(() => import('./filters/FiltersPopup.vue')),
      TestResultDropdown: defineAsyncComponent(() => import('./filters/TestResultDropdown.vue')),
      TestSearchInput: defineAsyncComponent(() => import('./filters/TestSearchInput.vue')),

      //Widgets
      Placeholder: defineAsyncComponent(() => import('./widgets/Placeholder.vue')),
      HTMLText: defineAsyncComponent(() => import('./widgets/HTMLText.vue')),
      TestRunTestsByResult: defineAsyncComponent(() => import('./widgets/TestRunTestsByResult.vue')),
      TestsRunTestsList: defineAsyncComponent(() => import('./widgets/TestRunTestsList/index.vue')),
      TestRunMetricsList: defineAsyncComponent(() => import('./widgets/TestRunMetricsList.vue')),
      TestRunProgress: defineAsyncComponent(() => import('./widgets/TestRunProgress.vue')),
      TestRunLogsList: defineAsyncComponent(() => import('./widgets/TestRunLogsList.vue')),
      TestRunOverTimeCharts: defineAsyncComponent(() => import('./widgets/TestRunOverTimeCharts.vue')),
      TestRunVariant: defineAsyncComponent(() => import('./widgets/TestRunVariant.vue')),
      TestRunJSONProperty: defineAsyncComponent(() => import('./widgets/TestRunJSONProperty.vue')),
      TestRunMetricsAndProperties: defineAsyncComponent(() => import('./widgets/TestRunMetricsAndProperties.vue')),

      // Layouts
      FullPage: defineAsyncComponent(() => import('./layouts/FullPage.vue')),
      SixSingle: defineAsyncComponent(() => import('./layouts/SixSingle.vue')),
      FourTopDoubleLeftDoubleRight: defineAsyncComponent(() => import('./layouts/FourTopDoubleLeftDoubleRight.vue')),

      //Components
      ProjectConfigPopup: defineAsyncComponent(() => import('./components/ProjectConfigPopup.vue')),
    },
  }
</script>

<script lang="ts" setup>
  import { onMounted, ref, watch, Ref, onBeforeUnmount, computed } from 'vue'
  import axios from 'axios'
  import { useRoute, useRouter } from 'vue-router'
  import { getShortUpdateInterval, HashUtil, GenericJSONResponse } from '../../utils'
  import { defaultProjectConfig } from './DefaultProjectConfig'
  import { useProjectState, useGlobalState } from '../../store'

  interface Config {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [prop: string]: any
  }

  const route = useRoute()
  const router = useRouter()
  const hash = new HashUtil()
  const projectState = useProjectState()
  const globalState = useGlobalState()

  const savedTab = projectState.getProperty(route.params.project as string, 'TestRunTab')

  const projectName = ref('')
  const testRunDetails = ref(undefined) as Ref<GenericJSONResponse | undefined>
  const activeTab = ref(savedTab ? savedTab : 0)
  const activeTabLayout = ref('FullPage')
  const activeTabWidgets = ref([]) as Ref<GenericJSONResponse[]>
  const config = ref(undefined) as Ref<Config | undefined>

  const readProjectDetails = () => {
    return axios.get(`/projects/${route.params.project}`).then((response) => {
      projectName.value = response.data.name
      config.value = response.data.config ? response.data.config : defaultProjectConfig
    })
  }

  const readTestRunDetails = () => {
    const params = {
      test_run_id: route.params.testrun,
    }
    return axios.get(`/reporting/projects/${route.params.project}/test-runs`, { params }).then((response) => {
      testRunDetails.value = response.data.data[0]
      globalState.setProperty('isTestRunActive', response.data.data[0].status.running)
    })
  }

  const refreshElements = () => {
    if (config.value) {
      activeTabLayout.value = config.value.testrun.tabs[activeTab.value].layout
      activeTabWidgets.value = config.value.testrun.tabs[activeTab.value].widgets
    }
  }

  const goBack = () => {
    router.push(`/projects/${route.params.project}`)
  }

  const isAdmin = computed(() => {
    return hash.get('admin') == 'true'
  })

  let timer: number

  onMounted(async () => {
    const savedQuery = projectState.getProperty(route.params.project as string, 'TestRunQuery')
    const savedHash = projectState.getProperty(route.params.project as string, 'TestRunHash')
    if (route.hash.length <= 1) {
      await router.replace({ ...route, hash: savedHash })
    }
    if (Object.keys(route.query).length == 0) {
      await router.replace({ ...route, query: savedQuery })
    }
    if (hash.get('tab')) {
      activeTab.value = parseInt(hash.get('tab'))
    }

    readProjectDetails().then(() => {
      refreshElements()
      readTestRunDetails()
    })
    timer = window.setInterval(readTestRunDetails, getShortUpdateInterval())
  })

  onBeforeUnmount(() => {
    clearInterval(timer)
  })

  watch(
    () => activeTab.value,
    () => {
      hash.set('tab', activeTab.value.toString()).then(() => {
        refreshElements()
      })
      projectState.setProperty(route.params.project as string, 'TestRunTab', activeTab.value)
    },
  )

  watch(
    () => config.value,
    () => {
      refreshElements()
    },
  )

  watch(
    () => route.query,
    (to, from) => {
      if (to !== from && route.params.project && route.params.testrun) {
        projectState.setProperty(route.params.project as string, 'TestRunQuery', to)
      }
    },
  )

  watch(
    () => route.hash,
    (to, from) => {
      if (to !== from && route.params.project && route.params.testrun) {
        projectState.setProperty(route.params.project as string, 'TestRunHash', to)
      }
    },
  )
</script>

<style lang="scss">
  .va-badge {
    --va-badge-text-wrapper-border-radius: 0.6em;
  }
</style>
