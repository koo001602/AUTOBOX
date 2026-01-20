<script setup>
import { RouterView } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import TopHeader from './components/TopHeader.vue'
</script>

<template>
  <div class="app-layout">
    <Sidebar />

    <div class="main-content">
      <TopHeader />
      <div class="view-container">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style>
:root {
  --bg-dark: #0b1120;
  --bg-panel: #151b2d;
  --primary-blue: #4f8aff;
  --text-main: #ffffff;
  --text-sub: #94a3b8;
  --accent-green: #10b981;
  --accent-red: #ef4444;
  --border-color: #2d3748;
}

body {
  background-color: var(--bg-dark);
  color: var(--text-main);
  font-family: 'Noto Sans KR', sans-serif;
  margin: 0;
  overflow: hidden; 
  height: 100vh;
}

#app {
  height: 100vh;
}
</style>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-dark);
  height: 100%;
  overflow: hidden;
}

.view-container {
  flex: 1;
  padding: 12px; 
  overflow: hidden; 
  display: flex;
  flex-direction: column;
}
</style>