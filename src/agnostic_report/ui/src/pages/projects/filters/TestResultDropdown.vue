<template>
  <va-select
    v-model="value"
    :options="options"
    label="Result"
    multiple
    clearable
    style="width: 155px"
    @clear="clearFilter"
  >
    <template #content="{ value }">
      <va-badge
        v-for="[idx, chip] of value.entries()"
        :key="chip"
        :color="getTestColorByResult(chip)"
        :text="chip[0]"
        text-color="#ffffff"
        size="small"
        class="mr-1 my-1"
        :style="idx > 0 ? 'padding-left: 8px' : ''"
      >
        <div style="height: 5px" />
      </va-badge>
    </template>
  </va-select>
</template>

<script lang="ts" setup>
  import { onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { getTestColorByResult } from '../../../utils'

  const route = useRoute()
  const router = useRouter()

  const results = ['passed', 'failed', 'xpassed', 'xfailed', 'skipped', 'unknown']
  const value = ref(results)
  const options = ref(results)

  const setFilterQuery = () => {
    router.replace({ ...route, query: { ...route.query, result: value.value } })
  }

  const clearFilter = () => {
    value.value = results
  }

  onMounted(() => {
    if (route.query.result) {
      value.value = route.query.result as string[]
    } else {
      setFilterQuery()
    }
  })

  watch(
    () => value.value,
    () => {
      setFilterQuery()
    },
  )

  watch(
    () => route.query.result,
    (to, from) => {
      if (to && to !== from && route.params.testrun) {
        if (route.query.result !== value.value) {
          value.value = route.query.result as string[]
        }
      }
    },
  )
</script>

<style scoped></style>
