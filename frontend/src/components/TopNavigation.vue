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
          <span>실시간 모니터링</span>
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
   Premium Glass Navigation
   ============================================= */

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 24px;
  /* Use glass-header mixin equivalent */
  background: var(--glass-header);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  z-index: 50;
}

/* Left Section */
.nav-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.logo-img {
  height: 36px;
  width: auto;
  object-fit: contain;
  filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
}

.logo-text {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.logo-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: var(--text-secondary);
  letter-spacing: 0.1em;
  backdrop-filter: blur(4px);
}

.mock-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 4px 8px;
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.5);
  border-radius: 4px;
  color: #f59e0b;
  letter-spacing: 0.1em;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
}

/* Navigation Menu */
.nav-menu {
  display: flex;
  gap: 8px;
  background: var(--overlay-dark);
  padding: 4px;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  min-height: 38px;
  border-radius: 6px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--overlay-lighter);
}

.nav-item.active {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 0 15px var(--color-primary-glow);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: translateX(-100%);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}

.nav-item svg {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
}

/* Right Section */
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-group {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 20px;
  background: var(--overlay-dark);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.status-label {
  font-size: 9px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  color: var(--text-secondary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  box-shadow: 0 0 5px currentColor;
}

.status-dot.online {
  background-color: var(--color-success);
  color: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
}

.status-dot.error {
  background-color: var(--color-error);
  color: var(--color-error);
  box-shadow: 0 0 8px var(--color-error);
}

.status-online .status-text {
  color: var(--color-success);
  text-shadow: 0 0 5px rgba(16, 185, 129, 0.4);
}

.status-offline .status-text {
  color: var(--color-error);
  text-shadow: 0 0 5px rgba(239, 68, 68, 0.4);
}

.battery-text {
  font-weight: 700;
}

.text-success { color: var(--color-success); text-shadow: 0 0 5px var(--color-success-glow); }
.text-error { color: var(--color-error); text-shadow: 0 0 5px var(--color-error-glow); }

.status-divider {
  width: 1px;
  height: 24px;
  background: var(--glass-border);
}

/* Alert Button */
.alert-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--overlay-lighter);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.alert-btn svg {
  width: 20px;
  height: 20px;
}

.alert-btn:hover {
  background: var(--overlay-light);
  color: var(--text-primary);
  border-color: var(--glass-border-hover);
}

.alert-btn.has-alerts {
  color: var(--color-error);
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.1);
}

.alert-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: var(--color-error);
  border-radius: 9px;
  font-size: 10px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 8px var(--color-error);
}

/* Theme Toggle */
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--overlay-lighter);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--overlay-light);
  color: var(--color-warning);
  border-color: var(--glass-border-hover);
  box-shadow: 0 0 10px var(--color-warning-glow);
}

/* Responsive */
@media (max-width: 1024px) {
  .status-item { display: none; }
  .status-item.system-status { display: flex; }
}

@media (max-width: 768px) {
  .top-nav { padding: 0 16px; }
  .logo-text { display: none; }
  .status-group { display: none; }
  .nav-menu {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--glass-header);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    padding: 8px;
    z-index: 100;
  }
}
</style>
