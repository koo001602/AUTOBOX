<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchSystemStatus } from '../api'

// 상태 변수
const batteryLevel = ref(0)
const isConnected = ref(false)
const connectionText = ref('Connecting...')
let timer = null

// 데이터 가져오기 함수
const getStatus = async () => {
  try {
    // 시스템 상태 조회
    const res = await fetchSystemStatus()
    const data = res.data.data

    batteryLevel.value = data.battery_level || 0
    isConnected.value = data.is_connected || false
    
    // 연결 상태 텍스트 설정
    if (data.is_connected) {
      connectionText.value = 'Stable'
    } else {
      connectionText.value = 'Offline'
    }
  } catch (error) {
    console.error('헤더 상태 조회 실패:', error)
    isConnected.value = false
    connectionText.value = 'Error'
  }
}

onMounted(() => {
  getStatus() // 초기 실행
  // 5초마다 상태 갱신 (Polling)
  timer = setInterval(getStatus, 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <header class="top-header">
    <div class="header-title">
      <span class="bar">|</span>
      <h2>스마트 물류 관리 시스템</h2>
      <span class="badge">DASHBOARD VIEW</span>
    </div>

    <div class="header-status">
      <div class="status-item">
        <span class="label">CONNECTION</span>
        <div class="value-box" :class="isConnected ? 'green-text' : 'red-text'">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path v-if="isConnected" d="M22 12h-4l-3 9L9 3l-3 9H2" />
            <path v-else d="M18.36 6.64a9 9 0 1 1-12.73 0" />
          </svg>
          <span>{{ connectionText }}</span>
        </div>
      </div>

      <div class="divider"></div>

      <div class="status-item">
        <span class="label">BATTERY</span>
        <div class="value-box">
          <span class="battery-text">{{ batteryLevel }}%</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="batteryLevel > 20 ? '#34d399' : '#ef4444'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="16" height="10" rx="2" ry="2" />
            <line x1="22" x2="22" y1="11" y2="13" />
            <rect x="4" y="9" :width="Math.max(0, (batteryLevel / 100) * 12)" height="6" fill="currentColor" stroke="none"/>
          </svg>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top-header { height: 60px; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; background-color: rgba(15, 23, 42, 0.95); border-bottom: 1px solid var(--border-color); }
.header-title { display: flex; align-items: center; gap: 12px; }
.bar { color: var(--primary-blue); font-weight: 900; font-size: 1.2rem; width: 4px; height: 24px; background-color: var(--primary-blue); border-radius: 2px; display: block; text-indent: -9999px; }
h2 { font-size: 1.2rem; margin: 0; font-weight: 700; color: #f1f5f9; }
.badge { background-color: #1e293b; color: #94a3b8; font-size: 0.65rem; padding: 4px 8px; border-radius: 4px; border: 1px solid #334155; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-left: 8px; }
.header-status { display: flex; align-items: center; gap: 20px; }
.status-item { display: flex; flex-direction: column; align-items: flex-end; }
.status-item .label { font-size: 0.6rem; color: #64748b; letter-spacing: 1px; font-weight: 700; margin-bottom: 2px; text-transform: uppercase; }
.value-box { display: flex; align-items: center; gap: 6px; font-family: monospace; }
.green-text { color: #34d399; font-weight: bold; font-size: 0.9rem; }
.red-text { color: #ef4444; font-weight: bold; font-size: 0.9rem; }
.divider { width: 1px; height: 30px; background-color: #334155; }
.battery-text { font-weight: bold; font-size: 0.95rem; color: #e2e8f0; }
</style>