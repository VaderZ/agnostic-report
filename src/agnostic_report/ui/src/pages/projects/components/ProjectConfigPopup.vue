<template>
  <va-icon name="far-edit" @click="showModal = !showModal" />
  <va-modal v-model="showModal" ok-text="Save" no-esc-dismiss fullscreen fixed-layout @ok="saveData">
    <div v-if="showModal">
      <div class="row">
        <div class="flex md12">
          <h3>Name</h3>
        </div>
      </div>
      <div class="row">
        <div class="flex md12">
          <va-input v-model="projectName"> </va-input>
        </div>
      </div>
      <br />
      <div class="row">
        <div class="flex md12">
          <h3>Config</h3>
        </div>
      </div>
      <div class="row">
        <div class="flex md12">
          <JsonEditorVue v-model="projectConfig" />
        </div>
      </div>
    </div>
    <template #header>
      <div class="row">
        <div class="flex md12">
          <div class="va-modal__title" style="color: rgb(21, 78, 193)">Configure Project</div>
        </div>
      </div>
    </template>
  </va-modal>
</template>

<script lang="js">
  // TODO: Rewrite in TS, JsonEditorVue might be an issue
  import JsonEditorVue from "json-editor-vue"
  import {defaultProjectConfig} from "../DefaultProjectConfig";

  export default {
    name: "ProjectConfigPopup",
    components: {JsonEditorVue},
    data () {
      return {
        showModal: false,
        projectConfig: '',
        projectName: ''
      }
    },
    watch: {
      showModal: function(isOpen) {
        if (isOpen) {
          this.readData()
        }
      }
    },
    methods: {
      readData() {
        this.$axios.get(
          `/projects/${this.$route.params.project}`
        ).then((response) => {
          this.projectConfig  = response.data.config ? response.data.config : defaultProjectConfig
          this.projectName = response.data.name
        })
      },
      saveData() {
        const configContent = typeof(this.projectConfig) == 'string' ? JSON.parse(this.projectConfig) : this.projectConfig
        this.$axios.patch(
          `/projects/${this.$route.params.project}`, {name: this.projectName, config: configContent}
        ).then(() => {
          this.$router.go()
        })
      }
    }
  }
</script>

<style scoped></style>
