<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import TopNavigation from './components/TopNavigation.vue'
import { useTheme } from './composables'

// 테마 초기화
const { initTheme } = useTheme()

onMounted(() => {
  initTheme()
})
</script>

<template>
  <div class="app-layout">
    <TopNavigation />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Global App Styles */
#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-base);
}

.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
