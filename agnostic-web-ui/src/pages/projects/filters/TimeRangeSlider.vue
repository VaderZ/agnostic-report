<template>
  <va-slider v-model="value" :max="max" :track-label="trackLabel" track-label-visible pins @change="setFilterQuery" />
</template>

<script lang="ts" setup>
  import { onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  const route = useRoute()
  const router = useRouter()

  const intervals = ['Week', 'Month', 'Quarter', 'Year', 'All']

  const max = ref(4)
  const value = ref(1)
  const trackLabel = ref((val: number) => intervals[val])

  const setFilterQuery = () => {
    const interval = intervals[value.value]
    if (route.query.interval !== interval) {
      router.replace({ ...route, query: { ...route.query, interval: interval } })
    }
  }

  onMounted(() => {
    if (route.query.interval) {
      value.value = intervals.indexOf(route.query.interval as string)
    } else {
      setFilterQuery()
    }
  })

  watch(
    () => route.query.interval,
    (to, from) => {
      if (to && to !== from && route.params.project) {
        const interval = intervals.indexOf(route.query.interval as string)
        if (interval !== value.value) {
          value.value = interval
        }
      }
    },
  )
</script>

<style scoped></style>
