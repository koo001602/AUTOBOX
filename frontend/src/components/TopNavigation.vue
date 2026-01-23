<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useSystemStatus, useTheme, useAlerts } from '../composables'
import { getMockMode } from '../api'

// Composables
const { batteryLevel, isConnected, connectionText } = useSystemStatus()
const { theme, toggleTheme } = useTheme()
const { alerts } = useAlerts()

// 미해결 알림 수
const alertCount = computed(() => alerts.value.length)

// 목업 모드 여부
const isMockMode = getMockMode()
</script>

<template>
  <header class="top-nav">
    <!-- Left: Logo & Navigation -->
    <div class="nav-left">
      <div class="logo">
        <img src="/assets/logo_original.png" alt="Autobox" class="logo-img" />
        <span class="logo-text">Autobox</span>
        <span class="logo-badge">CONTROL</span>
        <span v-if="isMockMode" class="mock-badge">MOCK</span>
      </div>

      <nav class="nav-menu">
        <RouterLink to="/" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="7" height="9" x="3" y="3" rx="1" />
            <rect width="7" height="5" x="14" y="3" rx="1" />
            <rect width="7" height="9" x="14" y="12" rx="1" />
            <rect width="7" height="5" x="3" y="16" rx="1" />
          </svg>
          <span>대시보드</span>
        </RouterLink>

        <RouterLink to="/live" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m22 8-6 4 6 4V8Z" />
            <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
          </svg>
          <span>실시간 영상</span>
        </RouterLink>
      </nav>
    </div>

    <!-- Right: Status & Controls -->
    <div class="nav-right">
      <!-- System Status -->
      <div class="status-group">
        <div class="status-item">
          <span class="status-label">CONNECTION</span>
          <div class="status-value" :class="isConnected ? 'status-online' : 'status-offline'">
            <span class="status-dot" :class="isConnected ? 'online' : 'error'"></span>
            <span class="status-text">{{ connectionText }}</span>
          </div>
        </div>

        <div class="status-divider"></div>

        <div class="status-item">
          <span class="status-label">BATTERY</span>
          <div class="status-value">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" :stroke="batteryLevel > 20 ? 'var(--color-success)' : 'var(--color-error)'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="7" width="16" height="10" rx="2" ry="2" />
              <line x1="22" x2="22" y1="11" y2="13" />
            </svg>
            <span class="battery-text" :class="batteryLevel > 20 ? 'text-success' : 'text-error'">{{ batteryLevel }}%</span>
          </div>
        </div>

        <div class="status-divider"></div>

        <div class="status-item system-status">
          <span class="status-label">SYSTEM</span>
          <div class="status-value status-online">
            <span class="status-dot online"></span>
            <span class="status-text">ONLINE</span>
          </div>
        </div>
      </div>

      <!-- Alert Badge -->
      <button class="alert-btn" :class="{ 'has-alerts': alertCount > 0 }" title="알림">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
        </svg>
        <span v-if="alertCount > 0" class="alert-badge">{{ alertCount > 99 ? '99+' : alertCount }}</span>
      </button>

      <!-- Theme Toggle -->
      <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? '라이트 모드' : '다크 모드'">
        <!-- Sun Icon (Light Mode) -->
        <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2"/>
          <path d="M12 20v2"/>
          <path d="m4.93 4.93 1.41 1.41"/>
          <path d="m17.66 17.66 1.41 1.41"/>
          <path d="M2 12h2"/>
          <path d="M20 12h2"/>
          <path d="m6.34 17.66-1.41 1.41"/>
          <path d="m19.07 4.93-1.41 1.41"/>
        </svg>
        <!-- Moon Icon (Dark Mode) -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
/* =============================================
   미니멀 상단 네비게이션
   ============================================= */

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
  padding: 0 20px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

/* Left Section */
.nav-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-img {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.logo-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 6px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.mock-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 6px;
  background-color: #f59e0b;
  border: 1px solid #d97706;
  border-radius: 4px;
  color: white;
  letter-spacing: 0.05em;
}

/* Navigation Menu */
.nav-menu {
  display: flex;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  min-height: 36px;
  border-radius: 6px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.nav-item:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background-color: var(--color-primary);
  color: white;
}

.nav-item svg {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

/* Right Section */
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-group {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 6px 14px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.status-label {
  font-size: 9px;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-family-mono);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.online {
  background-color: var(--color-success);
}

.status-dot.error {
  background-color: var(--color-error);
}

.status-online .status-text {
  color: var(--color-success);
}

.status-offline .status-text {
  color: var(--color-error);
}

.battery-text {
  font-weight: 600;
}

.text-success {
  color: var(--color-success);
}

.text-error {
  color: var(--color-error);
}

.status-divider {
  width: 1px;
  height: 24px;
  background-color: var(--border-color);
}

/* Alert Button */
.alert-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.alert-btn svg {
  width: 16px;
  height: 16px;
}

.alert-btn:hover {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
}

.alert-btn.has-alerts {
  color: var(--color-error);
  border-color: var(--color-error);
}

.alert-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background-color: var(--color-error);
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Theme Toggle */
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.theme-toggle svg {
  width: 16px;
  height: 16px;
}

.theme-toggle:hover {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
}

/* 태블릿 세로 모드 */
@media (max-width: 1024px) {
  .status-item {
    display: none;
  }
  
  .status-item.system-status {
    display: flex;
  }
}

@media (max-width: 768px) {
  .status-group {
    display: none;
  }
  
  .logo-badge,
  .mock-badge {
    display: none;
  }
}
</style>
