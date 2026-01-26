<template>
  <div class="live-view">
    <!-- Left: Video Panel -->
    <div class="live-left">
      <section class="panel video-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m22 8-6 4 6 4V8Z" />
              <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
            </svg>
            실시간 모니터링
          </div>
          <div class="header-controls">
            <span class="cam-label">
              <span class="cam-dot"></span>
              CAM:01
            </span>
            <span class="live-indicator">LIVE</span>
          </div>
        </div>

        <div class="panel-body video-body">
          <div class="video-container">
            <!-- Video Feed Area -->
            <div class="video-feed">
              <!-- Corner Brackets -->
              <div class="video-corners">
                <div class="corner top-left"></div>
                <div class="corner top-right"></div>
                <div class="corner bottom-left"></div>
                <div class="corner bottom-right"></div>
              </div>

              <!-- Placeholder -->
              <div class="video-placeholder">
                <div class="placeholder-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m22 8-6 4 6 4V8Z" />
                    <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
                  </svg>
                </div>
                <span class="placeholder-text">Camera Feed Unavailable</span>
                <span class="placeholder-sub">연결 대기 중...</span>
              </div>

              <!-- Status Overlay -->
              <div class="video-overlay">
                <div class="overlay-top">
                  <span class="record-indicator">
                    <span class="record-dot"></span>
                    REC
                  </span>
                  <span class="timestamp font-mono">{{ currentTime }}</span>
                </div>
                <div class="overlay-bottom">
                  <span class="resolution">640 x 480</span>
                  <span class="fps">30 FPS</span>
                </div>
              </div>
            </div>

            <!-- Video Controls -->
            <div class="video-controls">
              <div class="control-group">
                <button class="control-btn" title="전체화면">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8 3H5a2 2 0 0 0-2 2v3" />
                    <path d="M21 8V5a2 2 0 0 0-2-2h-3" />
                    <path d="M3 16v3a2 2 0 0 0 2 2h3" />
                    <path d="M16 21h3a2 2 0 0 0 2-2v-3" />
                  </svg>
                </button>
                <button class="control-btn" title="스크린샷">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path
                      d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
                    <circle cx="12" cy="13" r="3" />
                  </svg>
                </button>
                <button class="control-btn scan-btn" @click="handleScan" :disabled="isScanning" title="스캔 시작">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 7V5a2 2 0 0 1 2-2h2" />
                    <path d="M17 3h2a2 2 0 0 1 2 2v2" />
                    <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
                    <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
                    <rect x="7" y="7" width="10" height="10" rx="1" />
                  </svg>
                </button>
              </div>

              <div class="control-group">
                <span class="status-badge badge-success">
                  <span class="status-dot online"></span>
                  연결됨
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Right: Scan Info Panel -->
    <div class="live-right">
      <!-- Current Scan Info -->
      <section class="panel scan-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m7.5 4.27 9 5.15" />
              <path
                d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
              <path d="m3.3 7 8.7 5 8.7-5" />
              <path d="M12 22V12" />
            </svg>
            현재 스캔 정보
          </div>
          <button class="btn-scan" @click="handleScan" :disabled="isScanning">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2" />
              <path d="M17 3h2a2 2 0 0 1 2 2v2" />
              <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
              <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
            </svg>
            {{ isScanning ? '스캔 중...' : '스캔 시작' }}
          </button>
        </div>

        <div class="panel-body">
          <!-- 스캔 대기 상태 -->
          <div class="scan-empty" v-if="!currentScan">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2" />
              <path d="M17 3h2a2 2 0 0 1 2 2v2" />
              <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
              <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
            </svg>
            <span>스캔 대기 중</span>
            <span class="scan-empty-sub">스캔 버튼을 눌러 물류를 등록하세요</span>
          </div>

          <!-- 스캔된 정보 표시 -->
          <div class="scan-info" v-else>
            <div class="scan-main">
              <div class="scan-id">
                <span class="scan-label">WAYBILL ID</span>
                <span class="scan-value">{{ currentScan.waybill_id }}</span>
              </div>
              <div class="scan-status" :class="getStatusClass(currentScan.status)">
                {{ getStatusText(currentScan.status) }}
              </div>
            </div>

            <div class="scan-detail">
              <div class="detail-item">
                <span class="detail-label">운송장 번호</span>
                <span class="detail-value font-mono">{{ currentScan.tracking_number }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">목적지</span>
                <span class="detail-value">{{ currentScan.destination || '인식 대기' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">생성 시각</span>
                <span class="detail-value font-mono">{{ formatTime(currentScan.created_at) }}</span>
              </div>
              <div class="detail-item" v-if="currentScan.confidence_score">
                <span class="detail-label">인식 신뢰도</span>
                <span class="detail-value font-mono">{{ currentScan.confidence_score }}%</span>
              </div>
            </div>

            <!-- 작업 버튼 -->
            <div class="scan-actions" v-if="currentScan.status === 'READY'">
              <button class="btn-action btn-start" @click="handleStartSorting">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                분류 시작
              </button>
            </div>
            <div class="scan-actions" v-else-if="currentScan.status === 'MOVING'">
              <button class="btn-action btn-complete" @click="handleComplete">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                분류 완료
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Scan History -->
      <section class="panel history-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
              <path d="M12 7v5l4 2" />
            </svg>
            최근 스캔 이력
          </div>
          <span class="history-count">{{ scanHistory.length }}건</span>
        </div>

        <div class="panel-body history-body">
          <div class="history-list" v-if="scanHistory.length > 0">
            <div class="history-item" v-for="item in scanHistory" :key="item.waybill_id" @click="selectScan(item)">
              <div class="history-main">
                <span class="history-id font-mono">{{ item.tracking_number }}</span>
                <span class="history-status" :class="getStatusClass(item.status)">
                  {{ getStatusText(item.status) }}
                </span>
              </div>
              <div class="history-sub">
                <span>{{ item.destination || '-' }}</span>
                <span class="font-mono">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </div>
          <div class="history-empty" v-else>
            <span>스캔 이력이 없습니다</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { startWaybillScan, startSorting, completeSorting, fetchWaybills } from '../api'

const currentTime = ref('')
const isScanning = ref(false)
const currentScan = ref(null)
const scanHistory = ref([])

let timeInterval = null

// 시간 업데이트
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('ko-KR', { hour12: false })
}

// 시간 포맷
const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleTimeString('ko-KR', { hour12: false })
}

// 상태 텍스트
const getStatusText = (status) => {
  const map = {
    READY: '대기',
    MOVING: '이동 중',
    COMPLETED: '완료',
    ERROR: '오류'
  }
  return map[status] || status
}

// 상태 클래스
const getStatusClass = (status) => {
  return {
    'status-ready': status === 'READY',
    'status-moving': status === 'MOVING',
    'status-completed': status === 'COMPLETED',
    'status-error': status === 'ERROR'
  }
}

// 스캔 시작
const handleScan = async () => {
  if (isScanning.value) return

  isScanning.value = true
  try {
    const res = await startWaybillScan('CAM:01')
    if (res.data.success) {
      currentScan.value = res.data.data
      // 히스토리에 추가
      scanHistory.value.unshift(res.data.data)
      if (scanHistory.value.length > 10) {
        scanHistory.value.pop()
      }
    }
  } catch (err) {
    console.error('스캔 실패:', err)
  } finally {
    isScanning.value = false
  }
}

// 분류 시작
const handleStartSorting = async () => {
  if (!currentScan.value) return

  try {
    const res = await startSorting(currentScan.value.waybill_id)
    if (res.data.success) {
      currentScan.value = { ...currentScan.value, ...res.data.data }
      updateHistoryItem(res.data.data)
    }
  } catch (err) {
    console.error('분류 시작 실패:', err)
  }
}

// 분류 완료
const handleComplete = async () => {
  if (!currentScan.value) return

  try {
    const res = await completeSorting(currentScan.value.waybill_id)
    if (res.data.success) {
      currentScan.value = { ...currentScan.value, ...res.data.data }
      updateHistoryItem(res.data.data)
    }
  } catch (err) {
    console.error('분류 완료 실패:', err)
  }
}

// 히스토리 아이템 업데이트
const updateHistoryItem = (data) => {
  const idx = scanHistory.value.findIndex(h => h.waybill_id === data.waybill_id)
  if (idx >= 0) {
    scanHistory.value[idx] = { ...scanHistory.value[idx], ...data }
  }
}

// 스캔 선택
const selectScan = (item) => {
  currentScan.value = item
}

// 최근 스캔 이력 로드
const loadHistory = async () => {
  try {
    const res = await fetchWaybills({ size: 10 })
    if (res.data.success) {
      scanHistory.value = res.data.data?.items || []
    }
  } catch (err) {
    console.error('이력 로드 실패:', err)
  }
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadHistory()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
/* =============================================
   Premium Glass Live View (HUD Style)
   ============================================= */

.live-view {
  height: 100%;
  padding: 20px 24px;
  display: flex;
  gap: 24px;
  overflow: hidden;
}

.live-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.live-right {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Panel Styles */
.panel {
  background: var(--glass-panel);
  backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
}

.panel:hover {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.video-panel {
  flex: 1;
  min-height: 0;
  background: rgba(15, 23, 42, 0.6);
  /* Darker for video focus */
}

.scan-panel {
  flex-shrink: 0;
}

.history-panel {
  flex: 1;
  min-height: 200px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--glass-border);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.02);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.panel-body {
  flex: 1;
  padding: 20px;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.cam-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-family: var(--font-family-mono);
  font-weight: 700;
  color: var(--color-primary);
  padding: 6px 12px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 6px;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.1);
}

.cam-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  box-shadow: 0 0 8px var(--color-primary);
}

/* Video Container */
.video-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0;
  /* Remove padding for immersive video */
}

.video-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: black;
  position: relative;
}

.video-feed {
  position: relative;
  background-color: #000;
  flex: 1;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* HUD Overlay */
.video-overlay {
  position: absolute;
  inset: 0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
  z-index: 10;
  background: radial-gradient(circle at center, transparent 60%, rgba(0, 0, 0, 0.6) 100%);
}

.overlay-top,
.overlay-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.record-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(239, 68, 68, 0.8);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 800;
  color: white;
  letter-spacing: 0.05em;
  backdrop-filter: blur(4px);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

.record-dot {
  width: 8px;
  height: 8px;
  background-color: white;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.3;
  }
}

.timestamp {
  padding: 6px 14px;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 700;
  text-shadow: 0 0 5px var(--color-primary);
  backdrop-filter: blur(4px);
}

.resolution,
.fps {
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  font-size: 11px;
  font-family: var(--font-family-mono);
  color: var(--text-muted);
  font-weight: 600;
  backdrop-filter: blur(4px);
}

/* Corner Brackets (HUD) */
.video-corners .corner {
  position: absolute;
  width: 60px;
  height: 60px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  z-index: 5;
  transition: all 0.3s;
}

.video-feed:hover .video-corners .corner {
  border-color: var(--color-primary);
  width: 80px;
  height: 80px;
  box-shadow: 0 0 20px var(--color-primary-glow);
}

.corner.top-left {
  top: 20px;
  left: 20px;
  border-right: none;
  border-bottom: none;
}

.corner.top-right {
  top: 20px;
  right: 20px;
  border-left: none;
  border-bottom: none;
}

.corner.bottom-left {
  bottom: 20px;
  left: 20px;
  border-right: none;
  border-top: none;
}

.corner.bottom-right {
  bottom: 20px;
  right: 20px;
  border-left: none;
  border-top: none;
}

/* Video Controls Bar */
.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--glass-header);
  border-top: 1px solid var(--glass-border);
  backdrop-filter: blur(12px);
  z-index: 20;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  backdrop-filter: blur(4px);
}

.badge-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.1);
}

.status-dot.online {
  background-color: var(--color-success);
  box-shadow: 0 0 10px var(--color-success);
  animation: pulse-status 2s infinite;
}

@keyframes pulse-status {

  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
}

/* Live Indicator */
.live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  color: var(--color-error);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.1);
}

.live-indicator::before {
  content: '';
  width: 6px;
  height: 6px;
  background-color: var(--color-error);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--color-error);
  animation: blink 1.5s infinite;
}

/* Scan Button (Header) */
.btn-scan {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px var(--color-primary-glow);
}

.btn-scan:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px var(--color-primary-glow);
}

.btn-scan:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Scan Empty State */
.scan-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-muted);
  text-align: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  border: 1px dashed var(--glass-border);
}

.scan-empty svg {
  opacity: 0.3;
  color: var(--text-secondary);
}

/* Scan Info Styling */
.scan-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: slide-up 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scan-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--glass-border);
}

.scan-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.scan-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.scan-status {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.scan-status.status-ready {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
}

.scan-status.status-moving {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.scan-status.status-completed {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.1);
}

.scan-status.status-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.scan-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.detail-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.detail-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Action Buttons */
.scan-actions {
  margin-top: 8px;
}

.btn-action {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-start {
  background: linear-gradient(135deg, var(--color-info), #4338ca);
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.btn-start:hover {
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.btn-complete {
  background: linear-gradient(135deg, var(--color-success), #059669);
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-complete:hover {
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  transform: translateY(-2px);
}

/* History List */
.history-body {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.history-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-id {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
}

.history-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.history-sub {
  text-align: right;
  font-size: 11px;
  color: var(--text-muted);
}

.history-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 13px;
  font-style: italic;
}

/* Responsive */
@media (max-width: 1024px) {
  .live-view {
    flex-direction: column;
  }

  .live-right {
    width: 100%;
    height: auto;
  }

  .video-container {
    aspect-ratio: 16/9;
    max-height: 50vh;
  }
}
</style>
