<template>
  <va-button preset="secondary" size="small" icon="fa-plus-circle" @click="showModal = !showModal">
    New Project
  </va-button>
  <va-modal v-model="showModal" ok-text="Create" @ok="createProject">
    <div v-if="showModal">
      <div class="row">
        <div class="flex md12">
          <va-input v-model="value" class="mb-4" placeholder="Project Name" />
        </div>
      </div>
    </div>
  </va-modal>
</template>

<script lang="ts" setup>
  import { ref } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router'

  const router = useRouter()

  const showModal = ref(false)
  const value = ref('')

  const createProject = () => {
    axios.post('/projects', { name: value.value }).then(() => {
      router.go(0)
    })
  }
</script>

<style scoped></style>
