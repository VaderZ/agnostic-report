import { defineStore } from 'pinia'
import { ref, Ref } from 'vue'
import { useStorage } from '@vueuse/core'

class GlobalProperties {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [prop: string]: any
}

export const useGlobalState = defineStore('globalState', () => {
  const states = ref(useStorage('globalState', {})) as Ref<GlobalProperties>

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const setProperty = (name: string, value: any) => {
    states.value[name] = value
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const getProperty = (name: string, defaultValue: any = undefined): any => {
    if (name in states.value) {
      return states.value[name]
    }
    return defaultValue
  }

  return { states, setProperty, getProperty }
})

class ProjectProperty {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [prop: string]: any
}

class ProjectProperties {
  [prop: string]: ProjectProperty
}

export const useProjectState = defineStore('projectState', () => {
  const states = ref(useStorage('projectState', {})) as Ref<ProjectProperties>

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const setProperty = (projectId: string, name: string, value: any) => {
    if (!(projectId in states.value)) {
      states.value[projectId] = {}
    }
    states.value[projectId][name] = value
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const getProperty = (projectId: string, name: string): any => {
    if (projectId in states.value) {
      if (name in states.value[projectId]) {
        return states.value[projectId][name]
      }
    }
    return undefined
  }

  return { states, setProperty, getProperty }
})
