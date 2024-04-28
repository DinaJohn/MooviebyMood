<template>
  <div class="bg">
    <div class="content">
        <router-view />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'App',
});
</script>

<style scoped>
.bg {
  background-color: black;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  height: 100vh;
  width: 100vw;
  position: fixed;
  overflow-y: scroll;
}

.content {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 100vh;
  width: 100vw;
}
</style>