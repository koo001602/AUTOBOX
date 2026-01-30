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
  background: var(--bg-gradient);
  color: var(--text-primary);
}
</style>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  /* Glass effect on top of gradient */
  background: transparent;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
  /* 하단 탭바 공간 확보 */
  padding-bottom: 70px;
}
</style>
