<template>
  <div class="row">
    <div class="flex md8">
      <div class="row justify-start align-content-start">
        <div class="flex" style="padding-right: 0">
          <va-icon name="fa-arrow-left" @click="goBack"></va-icon>
        </div>
        <div class="flex md11" style="padding-left: 5px">
          <h1 style="display: inline">{{ projectName }}</h1>
          <div style="display: inline; padding-left: 5px">
            <ProjectConfigPopup v-if="isAdmin" />
          </div>
        </div>
      </div>
    </div>
    <div class="flex md4">
      <div class="row justify-end">
        <div class="flex"><FiltersPopup /></div>
        <div class="flex md8"><TimeRangeSlider /></div>
      </div>
    </div>
  </div>
  <br />
  <div v-if="config">
    <va-tabs v-model="activeTab">
      <template #tabs>
        <va-tab v-for="tab in config.project.tabs" :key="tab.name">
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

      //Widgets
      Placeholder: defineAsyncComponent(() => import('./widgets/Placeholder.vue')),
      HTMLText: defineAsyncComponent(() => import('./widgets/HTMLText.vue')),
      ProjectTestsOverTime: defineAsyncComponent(() => import('./widgets/ProjectTestsOverTime.vue')),
      ProjectTestRunsList: defineAsyncComponent(() => import('./widgets/ProjectTestRunsList.vue')),
      ProjectTopFailedTests: defineAsyncComponent(() => import('./widgets/ProjectTopFailedTests.vue')),
      ProjectMetrics: defineAsyncComponent(() => import('./widgets/ProjectMetrics.vue')),

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
  import { onMounted, ref, watch, Ref, computed } from 'vue'
  import axios from 'axios'
  import { useRoute, useRouter } from 'vue-router'
  import { HashUtil, GenericJSONResponse } from '../../utils'
  import { defaultProjectConfig } from './DefaultProjectConfig'
  import { useProjectState } from '../../store'

  interface Config {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [prop: string]: any
  }

  const route = useRoute()
  const router = useRouter()
  const hash = new HashUtil()
  const state = useProjectState()

  const savedTab = state.getProperty(route.params.project as string, 'ProjectTab')

  const projectName = ref('')
  const activeTab = ref(savedTab ? savedTab : 0)
  const activeTabLayout = ref('FullPage')
  const activeTabWidgets = ref([]) as Ref<GenericJSONResponse>
  const config = ref(undefined) as Ref<Config | undefined>

  const readProjectDetails = () => {
    return axios.get(`/projects/${route.params.project}`).then((response) => {
      projectName.value = response.data.name
      config.value = response.data.config && Object.keys(response.data.config).length > 0 ? response.data.config : defaultProjectConfig
    })
  }

  const refreshElements = () => {
    if (config.value) {
      activeTabLayout.value = config.value.project.tabs[activeTab.value].layout
      activeTabWidgets.value = config.value.project.tabs[activeTab.value].widgets
    }
  }

  const goBack = () => {
    router.push(`/projects`)
  }

  const isAdmin = computed(() => {
    return hash.get('admin') == 'true'
  })

  onMounted(async () => {
    const savedQuery = state.getProperty(route.params.project as string, 'ProjectQuery')
    const savedHash = state.getProperty(route.params.project as string, 'ProjectHash')
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
    })
  })

  watch(
    () => activeTab.value,
    async () => {
      await hash.set('tab', activeTab.value.toString()).then(() => {
        refreshElements()
      })
      state.setProperty(route.params.project as string, 'ProjectTab', activeTab.value)
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
      if (to !== from && route.params.project && !route.params.testrun) {
        state.setProperty(route.params.project as string, 'ProjectQuery', to)
      }
    },
  )

  watch(
    () => route.hash,
    (to, from) => {
      if (to !== from && route.params.project && !route.params.testrun) {
        state.setProperty(route.params.project as string, 'ProjectHash', to)
      }
    },
  )
</script>

<style lang="scss" scoped></style>
