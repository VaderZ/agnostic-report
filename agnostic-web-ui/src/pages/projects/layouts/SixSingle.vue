<template>
  <div class="row">
    <div class="flex md4">
      <slot name="0" />
    </div>
    <div class="flex md4">
      <slot name="1" />
    </div>
    <div class="flex md4">
      <slot name="2" />
    </div>
  </div>
  <div class="row">
    <div class="flex md4">
      <slot name="3" />
    </div>
    <div class="flex md4">
      <slot name="4" />
    </div>
    <div class="flex md4">
      <slot name="5" />
    </div>
  </div>
</template>

<script lang="ts">
  export default {}
</script>

<style scoped></style>
