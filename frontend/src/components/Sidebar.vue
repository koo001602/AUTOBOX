<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <aside class="sidebar">
    <div class="logo-area">
      <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 18H3c-.6 0-1-.4-1-1V9c0-.6.4-1 1-1h6c.6 0 1 .4 1 1v8c0 .6-.4 1-1 1H7"/>
        <path d="M15 18H9"/>
        <path d="M19 18h2c.6 0 1-.4 1-1v-5c0-.6-.4-1-1-1h-2"/>
        <circle cx="7" cy="18" r="2"/>
        <circle cx="17" cy="18" r="2"/>
        <path d="M15 9h2v3h-2z"/>
      </svg>
      <span class="logo-text">LogiTwin System</span>
    </div>

    <nav class="menu">
      <RouterLink to="/" class="menu-item" active-class="active">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-icon">
          <rect width="7" height="9" x="3" y="3" rx="1" />
          <rect width="7" height="5" x="14" y="3" rx="1" />
          <rect width="7" height="9" x="14" y="12" rx="1" />
          <rect width="7" height="5" x="3" y="16" rx="1" />
        </svg>
        메인 대시보드
      </RouterLink>

      <RouterLink to="/live" class="menu-item" active-class="active">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-icon">
          <path d="m22 8-6 4 6 4V8Z" />
          <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
        </svg>
        실시간 영상
      </RouterLink>
      </nav>

    <div class="sidebar-footer">
      <div class="status-dot"></div>
      <span>SYSTEM ONLINE</span>
    </div>
  </aside>
</template>

<style scoped>
.sidebar { width: 240px; background-color: var(--bg-dark); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; flex-shrink: 0; }
.logo-area { display: flex; align-items: center; gap: 12px; margin-bottom: 40px; font-weight: bold; font-size: 1.1rem; color: white; }
.menu { display: flex; flex-direction: column; gap: 10px; flex: 1; }
.menu-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 8px; color: var(--text-sub); text-decoration: none; cursor: pointer; transition: all 0.2s ease; font-size: 0.95rem; font-weight: 500; }
.menu-icon { transition: stroke 0.2s; }
.menu-item:hover { background-color: rgba(255, 255, 255, 0.05); color: white; }
.menu-item.active { background-color: var(--primary-blue); color: white; font-weight: 600; box-shadow: 0 4px 12px rgba(79, 138, 255, 0.3); }
.sidebar-footer { margin-top: auto; display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: var(--text-sub); padding-left: 10px; }
.status-dot { width: 8px; height: 8px; background-color: var(--accent-green); border-radius: 50%; box-shadow: 0 0 8px var(--accent-green); animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>