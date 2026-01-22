<template>
  <div class="live-view">
    <!-- Left: Video Panel -->
    <div class="live-left">
      <section class="panel video-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
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
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8 3H5a2 2 0 0 0-2 2v3"/>
                    <path d="M21 8V5a2 2 0 0 0-2-2h-3"/>
                    <path d="M3 16v3a2 2 0 0 0 2 2h3"/>
                    <path d="M16 21h3a2 2 0 0 0 2-2v-3"/>
                  </svg>
                </button>
                <button class="control-btn" title="스크린샷">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
                    <circle cx="12" cy="13" r="3"/>
                  </svg>
                </button>
                <button class="control-btn scan-btn" @click="handleScan" :disabled="isScanning" title="스캔 시작">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
                    <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
                    <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
                    <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
                    <rect x="7" y="7" width="10" height="10" rx="1"/>
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
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m7.5 4.27 9 5.15"/>
              <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
              <path d="m3.3 7 8.7 5 8.7-5"/>
              <path d="M12 22V12"/>
            </svg>
            현재 스캔 정보
          </div>
          <button class="btn-scan" @click="handleScan" :disabled="isScanning">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
              <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
              <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
              <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
            </svg>
            {{ isScanning ? '스캔 중...' : '스캔 시작' }}
          </button>
        </div>

        <div class="panel-body">
          <!-- 스캔 대기 상태 -->
          <div class="scan-empty" v-if="!currentScan">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
              <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
              <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
              <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                분류 시작
              </button>
            </div>
            <div class="scan-actions" v-else-if="currentScan.status === 'MOVING'">
              <button class="btn-action btn-complete" @click="handleComplete">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
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
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
              <path d="M3 3v5h5"/>
              <path d="M12 7v5l4 2"/>
            </svg>
            최근 스캔 이력
          </div>
          <span class="history-count">{{ scanHistory.length }}건</span>
        </div>

        <div class="panel-body history-body">
          <div class="history-list" v-if="scanHistory.length > 0">
            <div 
              class="history-item" 
              v-for="item in scanHistory" 
              :key="item.waybill_id"
              @click="selectScan(item)"
            >
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
.live-view {
  height: 100%;
  padding: 20px;
  display: flex;
  gap: 20px;
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
  gap: 16px;
  flex-shrink: 0;
}

/* Panel Styles */
.panel {
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.video-panel {
  flex: 1;
  min-height: 0;
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
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.panel-body {
  flex: 1;
  padding: 20px;
  min-height: 0;
  overflow: hidden;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cam-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-data-base);
  font-family: var(--font-family-mono);
  font-weight: 600;
  color: var(--text-secondary);
  padding: 8px 14px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.cam-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-primary);
}

/* Video Container */
.video-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.video-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.video-feed {
  position: relative;
  background-color: #000;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 4:3 비율 유지 (640x480) */
  aspect-ratio: 4 / 3;
  width: 100%;
  max-height: calc(100vh - 250px);
}

/* Corner Brackets */
.video-corners .corner {
  position: absolute;
  width: 32px;
  height: 32px;
  border: 2px solid var(--color-primary);
  z-index: 5;
}

.corner.top-left { top: 24px; left: 24px; border-right: none; border-bottom: none; }
.corner.top-right { top: 24px; right: 24px; border-left: none; border-bottom: none; }
.corner.bottom-left { bottom: 24px; left: 24px; border-right: none; border-top: none; }
.corner.bottom-right { bottom: 24px; right: 24px; border-left: none; border-top: none; }

/* Video Placeholder */
.video-placeholder {
  text-align: center;
  color: var(--text-muted);
  z-index: 1;
}

.placeholder-icon {
  margin-bottom: 16px;
  opacity: 0.4;
}

.placeholder-text {
  display: block;
  font-size: var(--font-size-h3);
  font-weight: 500;
  margin-bottom: 8px;
}

.placeholder-sub {
  display: block;
  font-size: var(--font-size-base);
  opacity: 0.7;
}

/* Video Overlay */
.video-overlay {
  position: absolute;
  inset: 0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
  z-index: 4;
}

.overlay-top,
.overlay-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background-color: rgba(239, 68, 68, 0.9);
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: white;
  letter-spacing: 0.05em;
}

.record-dot {
  width: 6px;
  height: 6px;
  background-color: white;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.timestamp {
  padding: 8px 14px;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 6px;
  font-size: var(--font-size-data-base);
  color: white;
}

.resolution,
.fps {
  padding: 8px 14px;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  color: var(--text-muted);
}

/* Video Controls */
.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  flex-shrink: 0;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--color-primary);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: var(--font-size-base);
  font-weight: 600;
}

.badge-success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.online {
  background-color: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
  animation: pulse-status 2s infinite;
}

@keyframes pulse-status {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Live Indicator */
.live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background-color: var(--color-error-light);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--color-error);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.live-indicator::before {
  content: '';
  width: 6px;
  height: 6px;
  background-color: var(--color-error);
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

.font-mono {
  font-family: var(--font-family-mono);
}

/* Scan Button in Video Controls */
.scan-btn {
  background-color: var(--color-primary-light) !important;
  border-color: var(--color-primary) !important;
  color: var(--color-primary) !important;
}

.scan-btn:hover {
  background-color: var(--color-primary) !important;
  color: white !important;
}

/* Scan Panel Header Button */
.btn-scan {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: var(--color-primary);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-scan:hover {
  background-color: var(--color-primary-hover);
}

.btn-scan:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Scan Empty State */
.scan-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--text-muted);
  text-align: center;
  gap: 8px;
}

.scan-empty svg {
  opacity: 0.4;
  margin-bottom: 8px;
}

.scan-empty-sub {
  font-size: var(--font-size-sm);
  opacity: 0.7;
}

/* Scan Info */
.scan-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scan-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.scan-id {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.scan-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

.scan-value {
  font-size: var(--font-size-h2);
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.scan-status {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.status-ready {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.status-moving {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.status-completed {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.status-error {
  background-color: var(--color-error-light);
  color: var(--color-error);
}

/* Scan Detail */
.scan-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background-color: var(--bg-elevated);
  border-radius: 6px;
}

.detail-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
}

/* Scan Actions */
.scan-actions {
  display: flex;
  gap: 10px;
  padding-top: 8px;
}

.btn-action {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 6px;
  font-size: var(--font-size-base);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-start {
  background-color: var(--color-primary);
  color: white;
}

.btn-start:hover {
  background-color: var(--color-primary-hover);
}

.btn-complete {
  background-color: var(--color-success);
  color: white;
}

.btn-complete:hover {
  background-color: #059669;
}

/* History Panel */
.history-count {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-muted);
  padding: 4px 10px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
}

.history-body {
  padding: 0;
  overflow-y: auto;
}

.history-list {
  display: flex;
  flex-direction: column;
}

.history-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background-color: var(--bg-hover);
}

.history-item:last-child {
  border-bottom: none;
}

.history-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-id {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.history-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.history-sub {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.history-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

/* Responsive */
@media (max-width: 1200px) {
  .live-view {
    flex-direction: column;
  }
  
  .live-right {
    width: 100%;
    flex-direction: row;
  }
  
  .scan-panel,
  .history-panel {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .live-right {
    flex-direction: column;
  }
}
</style>
