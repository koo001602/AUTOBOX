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
  <!-- 상단 상태바 (간소화) -->
  <header class="status-bar">
    <div class="status-bar-left">
      <img src="/assets/logo_original.png" alt="Autobox" class="status-logo" />
      <span class="status-title">Autobox</span>
      <span v-if="isMockMode" class="mock-badge">MOCK</span>
    </div>
    
    <div class="status-bar-right">
      <!-- 시스템 상태 그룹 -->
      <div class="status-group">
        <!-- 연결 상태 -->
        <div class="status-chip" :class="isConnected ? 'online' : 'offline'">
          <span class="chip-dot"></span>
          <span class="chip-text">{{ isConnected ? 'Online' : 'Error' }}</span>
        </div>
        
        <!-- 배터리 -->
        <div class="status-chip battery" :class="batteryLevel > 20 ? 'ok' : 'low'">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="16" height="10" rx="2" ry="2" />
            <line x1="22" x2="22" y1="11" y2="13" />
          </svg>
          <span class="chip-text">{{ batteryLevel }}%</span>
        </div>
      </div>

      <!-- 알림 -->
      <button class="status-btn" :class="{ 'has-alerts': alertCount > 0 }">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
        </svg>
        <span v-if="alertCount > 0" class="alert-badge">{{ alertCount > 99 ? '99+' : alertCount }}</span>
      </button>

      <!-- 테마 토글 -->
      <button class="status-btn" @click="toggleTheme">
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
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
        </svg>
      </button>
    </div>
  </header>

  <!-- 하단 탭바 -->
  <nav class="bottom-tab-bar">
    <RouterLink to="/" class="tab-item" active-class="active">
      <div class="tab-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="7" height="9" x="3" y="3" rx="1" />
          <rect width="7" height="5" x="14" y="3" rx="1" />
          <rect width="7" height="9" x="14" y="12" rx="1" />
          <rect width="7" height="5" x="3" y="16" rx="1" />
        </svg>
      </div>
      <span class="tab-label">대시보드</span>
    </RouterLink>

    <RouterLink to="/live" class="tab-item" active-class="active">
      <div class="tab-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m22 8-6 4 6 4V8Z" />
          <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
        </svg>
      </div>
      <span class="tab-label">모니터링</span>
    </RouterLink>

    <RouterLink to="/settings" class="tab-item" active-class="active">
      <div class="tab-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      </div>
      <span class="tab-label">설정</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
/* =============================================
   Mobile App Style Navigation
   ============================================= */

/* 상단 상태바 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
  padding: 0 16px;
  background: var(--glass-header);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--glass-border);
  flex-shrink: 0;
  z-index: 50;
  gap: 16px;
  overflow: hidden;
}

.status-bar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.status-logo {
  height: 28px;
  width: auto;
  object-fit: contain;
}

:global([data-theme="dark"]) .status-logo {
  filter: brightness(1.2);
}

.status-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--color-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.mock-badge {
  font-size: 9px;
  font-weight: 700;
  padding: 3px 6px;
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.5);
  border-radius: 4px;
  color: #f59e0b;
  letter-spacing: 0.05em;
}

.status-bar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* 상태 그룹 */
.status-group {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px;
  background: var(--overlay-dark);
  border-radius: 20px;
  border: 1px solid var(--glass-border);
}

/* 상태 칩 */
.status-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-family-mono);
  white-space: nowrap;
}

.status-chip.online {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
}

.status-chip.offline {
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-error);
}

.status-chip.battery.ok {
  color: var(--color-success);
}

.status-chip.battery.low {
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-error);
}

.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 6px currentColor;
  flex-shrink: 0;
}

.chip-text {
  flex-shrink: 0;
}

/* 상태 버튼 */
.status-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  border-radius: 50%;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.status-btn:hover {
  background: var(--overlay-lighter);
  color: var(--text-primary);
}

.status-btn.has-alerts {
  color: var(--color-error);
}

.alert-badge {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: var(--color-error);
  border-radius: 8px;
  font-size: 9px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* =============================================
   하단 탭바
   ============================================= */

.bottom-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 70px;
  padding-bottom: env(safe-area-inset-bottom, 8px);
  background: var(--glass-header);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--glass-border);
  z-index: 100;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1;
  height: 100%;
  padding: 8px 0;
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 32px;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.tab-item svg {
  width: 22px;
  height: 22px;
  transition: all 0.2s ease;
}

.tab-label {
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s ease;
}

/* Active State */
.tab-item.active {
  color: var(--color-primary);
}

.tab-item.active .tab-icon {
  background: rgba(99, 102, 241, 0.15);
}

.tab-item.active svg {
  transform: scale(1.1);
}

.tab-item.active .tab-label {
  font-weight: 700;
}

/* Hover State */
.tab-item:hover:not(.active) {
  color: var(--text-secondary);
}

.tab-item:hover:not(.active) .tab-icon {
  background: var(--overlay-lighter);
}

/* Active Indicator */
.tab-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 3px;
  background: var(--color-primary);
  border-radius: 0 0 3px 3px;
}

/* Responsive */
@media (max-width: 600px) {
  .status-bar {
    padding: 0 12px;
  }
  
  .status-title {
    display: none;
  }
  
  .status-chip .chip-text {
    display: none;
  }
  
  .status-chip {
    padding: 6px;
  }
  
  .status-group {
    gap: 4px;
    padding: 3px;
  }
}

@media (max-width: 400px) {
  .mock-badge {
    display: none;
  }
  
  .status-group {
    display: none;
  }
}
</style>
