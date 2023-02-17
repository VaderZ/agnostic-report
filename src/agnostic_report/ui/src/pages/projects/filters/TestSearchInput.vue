<template>
  <va-input
    v-model="value"
    placeholder="Search test name"
    label="Search"
    clearable
    @keyup="setFilterQuery"
    @clear="setFilterQuery"
  >
  </va-input>
</template>

<script lang="ts" setup>
  import { onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  const route = useRoute()
  const router = useRouter()

  const value = ref('')

  let timer: number | undefined = undefined

  const setFilterQuery = () => {
    if (timer) {
      clearInterval(timer)
    }
    timer = window.setInterval(() => {
      const update = { ...route.query }
      if (!value.value) {
        delete update.search
        router.replace({ ...route, query: update })
      } else {
        update.search = value.value
          .trim()
          .split(' || ')
          .filter((val) => val !== '')
        router.replace({ ...route, query: update })
      }
      clearInterval(timer)
    }, 500)
  }

  onMounted(() => {
    if (route.query.search) {
      value.value = Array.isArray(route.query.search) ? route.query.search.join(' || ') : (route.query.search as string)
    }
  })

  watch(
    () => route.query.search,
    (to, from) => {
      if (to && to !== from && route.params.testrun) {
        if (route.query.search !== value.value) {
          value.value = Array.isArray(route.query.search)
            ? route.query.search.join(' || ')
            : (route.query.search as string)
        }
      }
    },
  )
</script>

<style scoped></style>
