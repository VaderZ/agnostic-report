import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

import AppLayout from '../layouts/AppLayout.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/:catchAll(.*)',
    redirect: { name: 'projects' },
  },
  {
    name: 'root',
    path: '/',
    component: AppLayout,
    children: [
      {
        name: 'projects',
        path: 'projects',
        component: () => import('../pages/projects/Projects.vue'),
      },
      {
        name: 'project',
        path: 'projects/:project',
        component: () => import('../pages/projects/Project.vue'),
      },
      {
        name: 'testrun',
        path: 'projects/:project/test-runs/:testrun',
        component: () => import('../pages/projects/TestRun.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  //  mode: process.env.VUE_APP_ROUTER_MODE_HISTORY === 'true' ? 'history' : 'hash',
  routes,
})

export default router
