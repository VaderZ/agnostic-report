import { createApp } from 'vue'
import i18n from './i18n'
import { createVuestic } from 'vuestic-ui'
import { createGtm } from '@gtm-support/vue-gtm'

import axios from 'axios'
import Qs from 'qs'
import { createPinia } from 'pinia'
import PlotlyChart from './pages/projects/components/PlotlyChart.vue'

import router from './router'
import vuesticGlobalConfig from './services/vuestic-ui/global-config'
import App from './App.vue'

const app = createApp(App)

const pinia = createPinia()
axios.defaults.baseURL = '/api/v1'
axios.defaults.paramsSerializer = (params) => Qs.stringify(params, { arrayFormat: 'repeat' })
app.config.globalProperties.$axios = axios
app.provide('axios', app.config.globalProperties.$axios)

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(createVuestic({ config: vuesticGlobalConfig }))

if (import.meta.env.VITE_APP_GTM_ENABLED) {
  app.use(
    createGtm({
      id: import.meta.env.VITE_APP_GTM_KEY,
      debug: false,
      vueRouter: router,
    }),
  )
}

app.component('PlotlyChart', PlotlyChart)

app.mount('#app')
