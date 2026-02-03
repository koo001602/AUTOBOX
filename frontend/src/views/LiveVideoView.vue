<template>
  <div class="live-view">
    <div class="live-item item-video">
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
            <span class="cam-label"><span class="cam-dot"></span>CAM:01</span>
            <span class="live-indicator">LIVE</span>
          </div>
        </div>
        <div class="panel-body video-body">
          <div class="video-container">
            <div class="video-feed">
              <div class="video-corners">
                <div class="corner top-left"></div>
                <div class="corner top-right"></div>
                <div class="corner bottom-left"></div>
                <div class="corner bottom-right"></div>
              </div>
              <!-- MediaMTX WebRTC 라이브 스트림 -->
              <iframe 
                v-if="isStreamConnected"
                :src="streamUrl"
                class="video-stream"
                frameborder="0"
                allowfullscreen
                @load="onStreamLoad"
                @error="onStreamError"
              ></iframe>
              <!-- 연결 실패 시 플레이스홀더 표시 -->
              <div class="video-placeholder" v-else>
                <div class="placeholder-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="m22 8-6 4 6 4V8Z" />
                    <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
                  </svg>
                </div>
                <span class="placeholder-text">Camera Feed Unavailable</span>
                <span class="placeholder-sub">{{ streamError || '연결 대기 중...' }}</span>
                <button class="btn-retry" @click="connectStream">재연결</button>
              </div>
              <div class="video-overlay">
                <div class="overlay-top">
                  <span class="record-indicator"><span class="record-dot"></span>REC</span>
                  <span class="timestamp font-mono">{{ currentTime }}</span>
                </div>
                <div class="overlay-bottom">
                  <span class="resolution">640 x 480</span>
                  <span class="fps">30 FPS</span>
                </div>
              </div>
            </div>
            
            <div class="video-controls">
              <div class="control-group">
                <button class="control-btn" title="전체화면"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3" /><path d="M21 8V5a2 2 0 0 0-2-2h-3" /><path d="M3 16v3a2 2 0 0 0 2 2h3" /><path d="M16 21h3a2 2 0 0 0 2-2v-3" /></svg></button>
                <button class="control-btn" title="스크린샷"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" /><circle cx="12" cy="13" r="3" /></svg></button>
                <button class="control-btn scan-btn" @click="handleScan" :disabled="isScanning" title="스캔 시작"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" /><path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" /><rect x="7" y="7" width="10" height="10" rx="1" /></svg></button>
              </div>
              <div class="control-group">
                <span class="status-badge badge-success"><span class="status-dot online"></span>연결됨</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="live-item item-map">
      <section class="panel map-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" /><line x1="9" x2="9" y1="3" y2="18" /><line x1="15" x2="15" y1="6" y2="21" /></svg>
            실시간 맵
          </div>
          <div class="header-controls">
            <button class="btn-zoom" @click="zoomIn" title="확대"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /><line x1="11" x2="11" y1="8" y2="14" /><line x1="8" x2="14" y1="11" y2="11" /></svg></button>
            <button class="btn-zoom" @click="zoomOut" title="축소"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /><line x1="8" x2="14" y1="11" y2="11" /></svg></button>
            <button class="btn-reset" @click="resetView" title="초기화"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M3 21v-5h5" /></svg></button>
          </div>
        </div>
        <div class="panel-body map-body">
          <div class="map-container">
            <svg class="map-canvas" :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`" @wheel.prevent="handleWheel" @mousedown="startPan" @mousemove="handlePan" @mouseup="endPan" @mouseleave="endPan">
              <defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><rect width="50" height="50" fill="none" /><path d="M 50 0 L 0 0 0 50" fill="none" stroke="var(--glass-border)" stroke-width="0.5" /></pattern></defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              <g class="map-elements">
                <line x1="100" y1="300" x2="900" y2="300" stroke="var(--text-muted)" stroke-width="8" opacity="0.3" />
                <line x1="500" y1="100" x2="500" y2="700" stroke="var(--text-muted)" stroke-width="8" opacity="0.3" />
                <rect v-for="building in buildings" :key="building.id" :x="building.x" :y="building.y" :width="building.width" :height="building.height" fill="var(--text-muted)" opacity="0.5" stroke="var(--glass-border)" stroke-width="1" />
                <g v-for="waypoint in waypoints" :key="waypoint.id" class="waypoint">
                  <circle :cx="waypoint.x" :cy="waypoint.y" r="8" :fill="waypoint.color" opacity="0.3" />
                  <circle :cx="waypoint.x" :cy="waypoint.y" r="4" :fill="waypoint.color" />
                  <text :x="waypoint.x" :y="waypoint.y - 15" class="waypoint-label" fill="var(--text-primary)" text-anchor="middle">{{ waypoint.label }}</text>
                </g>
                <path v-if="vehiclePath.length > 0" :d="getPathString(vehiclePath)" fill="none" stroke="var(--color-primary)" stroke-width="2" opacity="0.5" stroke-dasharray="5,5" />
                <g :transform="`translate(${vehicle.x}, ${vehicle.y}) rotate(${vehicle.angle})`" class="vehicle">
                  <rect x="-15" y="-10" width="30" height="20" fill="var(--color-primary)" stroke="var(--color-primary-glow)" stroke-width="2" rx="3" />
                  <polygon points="15,0 25,5 25,-5" fill="var(--color-primary)" />
                  <circle cx="0" cy="0" r="30" fill="none" stroke="var(--color-primary)" stroke-width="1" opacity="0.3" class="vehicle-pulse" />
                </g>
              </g>
            </svg>
            <div class="map-overlay">
              <div class="overlay-top-map"><div class="coord-display"><span class="coord-label">X</span><span class="coord-value">{{ vehicle.x.toFixed(1) }}</span><span class="coord-label">Y</span><span class="coord-value">{{ vehicle.y.toFixed(1) }}</span><span class="coord-label">θ</span><span class="coord-value">{{ vehicle.angle.toFixed(0) }}°</span></div></div>
              <div class="overlay-bottom-map"><span class="zoom-level">ZOOM {{ (zoom * 100).toFixed(0) }}%</span></div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="live-item item-right">
      <section class="panel scan-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="m7.5 4.27 9 5.15" /><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" /><path d="m3.3 7 8.7 5 8.7-5" /><path d="M12 22V12" /></svg>
            현재 스캔 정보
          </div>
          <button class="btn-scan" @click="handleScan" :disabled="isScanning"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" /><path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" /></svg>{{ isScanning ? '스캔 중...' : '스캔 시작' }}</button>
        </div>
        <div class="panel-body scan-body">
          <div class="scan-empty" v-if="!currentScan">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" /><path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" /></svg>
            <span>스캔 대기 중</span>
            <span class="scan-empty-sub">스캔 버튼을 눌러 물류를 등록하세요</span>
          </div>
          <div class="scan-info" v-else>
            <div class="scan-main">
              <div class="scan-id"><span class="scan-label">WAYBILL ID</span><span class="scan-value">{{ currentScan.waybill_id }}</span></div>
              <div class="scan-status" :class="getStatusClass(currentScan.status)">{{ getStatusText(currentScan.status) }}</div>
            </div>
            <div class="scan-detail">
              <div class="detail-item"><span class="detail-label">운송장 번호</span><span class="detail-value font-mono">{{ currentScan.tracking_number }}</span></div>
              <div class="detail-item"><span class="detail-label">목적지</span><span class="detail-value">{{ currentScan.destination || '인식 대기' }}</span></div>
              <div class="detail-item"><span class="detail-label">생성 시각</span><span class="detail-value font-mono">{{ formatTime(currentScan.created_at) }}</span></div>
            </div>
            <div class="recognized-region"><span class="region-label">인식된 지역</span><span class="region-value" :class="{ 'region-pending': !currentScan.destination }">{{ currentScan.destination || '지역 인식 대기 중...' }}</span></div>
            <div class="scan-actions" v-if="currentScan.status === 'READY'"><button class="btn-action btn-start" @click="handleStartSorting"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3" /></svg>분류 시작</button></div>
            <div class="scan-actions" v-else-if="currentScan.status === 'MOVING'"><button class="btn-action btn-complete" @click="handleComplete"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12" /></svg>분류 완료</button></div>
          </div>
        </div>
      </section>

      <section class="panel status-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" /><circle cx="7" cy="17" r="2" /><path d="M9 17h6" /><circle cx="17" cy="17" r="2" /></svg>
            차량 상태
          </div>
          <span class="vehicle-status-badge" :class="vehicleStatus.mode.toLowerCase()">{{ vehicleStatus.mode }}</span>
        </div>
        <div class="panel-body status-body">
          <div class="status-list">
            <div class="status-row"><span class="status-label">속도</span><span class="status-value">{{ vehicleStatus.speed }}<small>km/h</small></span></div>
            <div class="status-row"><span class="status-label">배터리</span><span class="status-value" :class="{ 'text-error': vehicleStatus.battery < 20 }">{{ vehicleStatus.battery }}<small>%</small></span></div>
            <div class="status-row"><span class="status-label">목적지까지</span><span class="status-value">{{ vehicleStatus.distanceToTarget }}<small>m</small></span></div>
            <div class="status-row"><span class="status-label">예상 도착</span><span class="status-value">{{ vehicleStatus.eta }}<small>초</small></span></div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { startWaybillScan, startSorting, completeSorting, fetchWaybills, fetchVehiclePosition, fetchMapData, fetchSensorStatus, getMockMode } from '../api'

const currentTime = ref('')
const isScanning = ref(false)
const currentScan = ref(null)
const scanHistory = ref([])
const isLoading = ref(true)
const isMockMode = getMockMode()
let timeInterval = null

// 라이브 스트림 관련 상태
const isStreamConnected = ref(false)
const streamError = ref('')
// MediaMTX WebRTC 스트림 URL (nginx /live/ 프록시 사용)
const streamUrl = ref('/live/')

const connectStream = () => {
  streamError.value = ''
  isStreamConnected.value = true
}

const onStreamLoad = () => {
  streamError.value = ''
  console.log('라이브 스트림 연결 성공')
}

const onStreamError = () => {
  isStreamConnected.value = false
  streamError.value = '스트림 연결에 실패했습니다'
  console.error('라이브 스트림 연결 실패')
}

const viewBox = ref({ x: 0, y: 0, width: 1000, height: 800 })
const zoom = ref(1)
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const vehicle = ref({ x: 0, y: 0, angle: 0 })
const vehiclePath = ref([])
const buildings = ref([])
const waypoints = ref([])
const currentWaypointIndex = ref(0)
const vehicleStatus = ref({ mode: '-', speed: 0, battery: 0, distanceToTarget: 0, eta: 0 })
const sensors = ref([])

const getPathString = (path) => path.length === 0 ? '' : path.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
const zoomIn = () => { zoom.value = Math.min(zoom.value * 1.2, 3); updateViewBox() }
const zoomOut = () => { zoom.value = Math.max(zoom.value / 1.2, 0.5); updateViewBox() }
const resetView = () => { zoom.value = 1; viewBox.value = { x: 0, y: 0, width: 1000, height: 800 } }

const updateViewBox = () => {
  const newWidth = 1000 / zoom.value, newHeight = 800 / zoom.value
  viewBox.value = { x: vehicle.value.x - newWidth / 2, y: vehicle.value.y - newHeight / 2, width: newWidth, height: newHeight }
}

const handleWheel = (e) => { zoom.value = Math.max(0.5, Math.min(3, zoom.value * (e.deltaY > 0 ? 0.9 : 1.1))); updateViewBox() }
const startPan = (e) => { isPanning.value = true; panStart.value = { x: e.clientX, y: e.clientY } }
const handlePan = (e) => { if (!isPanning.value) return; viewBox.value.x -= (e.clientX - panStart.value.x) * (viewBox.value.width / 1000); viewBox.value.y -= (e.clientY - panStart.value.y) * (viewBox.value.height / 800); panStart.value = { x: e.clientX, y: e.clientY } }
const endPan = () => { isPanning.value = false }

let simulationInterval = null, dataPollingInterval = null

const simulateVehicleMovement = () => {
  if (waypoints.value.length === 0) return
  if (currentWaypointIndex.value >= waypoints.value.length) { currentWaypointIndex.value = 0; vehiclePath.value = [{ x: waypoints.value[0].x, y: waypoints.value[0].y }] }
  const target = waypoints.value[currentWaypointIndex.value], dx = target.x - vehicle.value.x, dy = target.y - vehicle.value.y, distance = Math.sqrt(dx * dx + dy * dy)
  if (distance < 5) { currentWaypointIndex.value++; if (currentWaypointIndex.value < waypoints.value.length) { const nextTarget = waypoints.value[currentWaypointIndex.value]; vehicleStatus.value.distanceToTarget = Math.sqrt((nextTarget.x - vehicle.value.x) ** 2 + (nextTarget.y - vehicle.value.y) ** 2).toFixed(0); vehicleStatus.value.eta = (vehicleStatus.value.distanceToTarget / (vehicleStatus.value.speed / 3.6)).toFixed(0) } return }
  const speed = 2, vx = (dx / distance) * speed, vy = (dy / distance) * speed
  vehicle.value.x += vx; vehicle.value.y += vy; vehicle.value.angle = Math.atan2(dy, dx) * (180 / Math.PI)
  vehiclePath.value.push({ x: vehicle.value.x, y: vehicle.value.y }); if (vehiclePath.value.length > 100) vehiclePath.value.shift()
  vehicleStatus.value.distanceToTarget = distance.toFixed(0); vehicleStatus.value.eta = (distance / (vehicleStatus.value.speed / 3.6)).toFixed(0); updateViewBox()
}

const loadVehiclePosition = async () => { try { const res = await fetchVehiclePosition(); if (res.data?.success && res.data?.data) { const data = res.data.data; vehicle.value = { x: data.x || 0, y: data.y || 0, angle: data.angle || 0 }; vehicleStatus.value = { mode: data.mode || 'UNKNOWN', speed: parseFloat(data.speed) || 0, battery: data.battery || 0, distanceToTarget: vehicleStatus.value.distanceToTarget, eta: vehicleStatus.value.eta }; vehiclePath.value.push({ x: vehicle.value.x, y: vehicle.value.y }); if (vehiclePath.value.length > 100) vehiclePath.value.shift(); updateViewBox() } } catch (err) { console.error('차량 위치 로드 실패:', err) } }
const loadMapData = async () => { try { const res = await fetchMapData(); if (res.data?.success && res.data?.data) { const data = res.data.data; waypoints.value = (data.waypoints || []).map(wp => ({ ...wp, color: wp.color || 'var(--color-primary)' })); buildings.value = data.buildings || []; if (waypoints.value.length > 0 && vehicle.value.x === 0 && vehicle.value.y === 0) { vehicle.value.x = waypoints.value[0].x; vehicle.value.y = waypoints.value[0].y; vehiclePath.value = [{ x: vehicle.value.x, y: vehicle.value.y }] } } } catch (err) { console.error('맵 데이터 로드 실패:', err) } }
const loadSensorStatus = async () => { try { const res = await fetchSensorStatus(); if (res.data?.success && res.data?.data) sensors.value = res.data.data.sensors || [] } catch (err) { console.error('센서 상태 로드 실패:', err) } }
const loadInitialData = async () => { isLoading.value = true; try { await Promise.all([loadMapData(), loadVehiclePosition(), loadSensorStatus()]) } finally { isLoading.value = false } }
const startDataPolling = () => { dataPollingInterval = setInterval(async () => { await loadVehiclePosition() }, 1000); setInterval(async () => { await loadSensorStatus() }, 5000) }

const updateTime = () => { currentTime.value = new Date().toLocaleTimeString('ko-KR', { hour12: false }) }
const formatTime = (dateStr) => !dateStr ? '-' : new Date(dateStr).toLocaleTimeString('ko-KR', { hour12: false })
const getStatusText = (status) => ({ READY: '대기', MOVING: '이동 중', COMPLETED: '완료', ERROR: '오류' }[status] || status)
const getStatusClass = (status) => ({ 'status-ready': status === 'READY', 'status-moving': status === 'MOVING', 'status-completed': status === 'COMPLETED', 'status-error': status === 'ERROR' })

const handleScan = async () => { if (isScanning.value) return; isScanning.value = true; try { const res = await startWaybillScan('CAM:01'); if (res.data.success) { currentScan.value = res.data.data; scanHistory.value.unshift(res.data.data); if (scanHistory.value.length > 10) scanHistory.value.pop() } } catch (err) { console.error('스캔 실패:', err) } finally { isScanning.value = false } }
const handleStartSorting = async () => { if (!currentScan.value) return; try { const res = await startSorting(currentScan.value.waybill_id); if (res.data.success) { currentScan.value = { ...currentScan.value, ...res.data.data }; updateHistoryItem(res.data.data) } } catch (err) { console.error('분류 시작 실패:', err) } }
const handleComplete = async () => { if (!currentScan.value) return; try { const completeSorting = await completeSorting(currentScan.value.waybill_id); if (res.data.success) { currentScan.value = { ...currentScan.value, ...res.data.data }; updateHistoryItem(res.data.data) } } catch (err) { console.error('분류 완료 실패:', err) } }
const updateHistoryItem = (data) => { const idx = scanHistory.value.findIndex(h => h.waybill_id === data.waybill_id); if (idx >= 0) scanHistory.value[idx] = { ...scanHistory.value[idx], ...data } }
const loadHistory = async () => { try { const res = await fetchWaybills({ size: 10 }); if (res.data?.success || res.data?.data) scanHistory.value = res.data.data?.items || [] } catch (err) { console.error('이력 로드 실패:', err); scanHistory.value = [] } }

onMounted(async () => { updateTime(); timeInterval = setInterval(updateTime, 1000); loadHistory(); await loadInitialData(); if (isMockMode) simulationInterval = setInterval(simulateVehicleMovement, 50); else startDataPolling(); connectStream() })
onUnmounted(() => { if (timeInterval) clearInterval(timeInterval); if (simulationInterval) clearInterval(simulationInterval); if (dataPollingInterval) clearInterval(dataPollingInterval) })
</script>

<style scoped>
/* =================================================================
   디바이스별 반응형 레이아웃 분리 (Mobile First Strategy)
   ================================================================= */

/* 1. 모바일 (기본): 768px 미만
   - 1열 수직 배치 (Stack)
   - 높이 자동 (스크롤 허용)
   - 패딩 최소화
*/
.live-view { 
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  height: auto; 
  padding: 16px; 
  box-sizing: border-box;
  /* 모바일 네비게이션 고려하여 하단 여백 확보 */
  padding-bottom: 20px;
}

/* 추가된 부분: 모바일 레이아웃에서 아이템 간 간격 설정 */
.live-item {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 2. 패널 공통 스타일 (Mobile First) */
.panel { 
  background: var(--glass-panel); 
  backdrop-filter: blur(var(--blur-amount)); 
  border: 1px solid var(--glass-border); 
  border-radius: 12px; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  box-shadow: 0 8px 24px rgba(0,0,0,0.12); 
  transition: all 0.3s; 
  
  /* 모바일에서는 최소 높이를 작게 잡아 화면 짤림 방지 */
  min-height: 280px; 
  height: auto;
}

/* 각 패널별 모바일 최적화 */
.scan-panel, .status-panel {
  min-height: 200px;
}

/* 3. 태블릿 & 작은 노트북: 768px 이상 ~ 1279px 미만
   - 2열 그리드 배치
*/
@media (min-width: 768px) {
  .live-view {
    display: grid;
    grid-template-columns: 1fr 1fr; /* 2열 */
    align-items: stretch; /* 높이 맞춤 */
    padding-bottom: 20px;
  }

  .live-item {
    display: flex;
    flex-direction: column;
  }

  /* 2열 배치 순서 */
  .item-video { grid-column: 1; }
  .item-map   { grid-column: 2; }
  .item-right { 
    grid-column: 1 / -1; /* 하단 전체 차지 */
    flex-direction: row; 
    gap: 16px;
  }
  
  .scan-panel, .status-panel {
    flex: 1;
  }
  
  /* 태블릿에서는 패널 높이를 꽉 채움 */
  .item-video .panel, .item-map .panel {
    height: 100%;
  }
}

/* 4. 데스크탑: 1280px 이상 (기존 고정형 대시보드)
   - 3열 그리드 배치
   - 높이 100% 고정 (스크롤 최소화)
*/
@media (min-width: 1280px) {
  .live-view {
    display: grid;
    grid-template-columns: 1fr 1fr 340px; 
    /* 화면 높이에 딱 맞춤 */
    height: 100%;
    align-items: stretch;
    padding-bottom: 20px; /* 데스크탑은 여백 작게 */
  }

  /* 각 컬럼 컨테이너 */
  .live-item {
    height: 100%;
    min-height: 0; 
  }

  /* 배치 지정 */
  .item-video { grid-column: 1; }
  .item-map   { grid-column: 2; }
  
  .item-right { 
    grid-column: 3;
    flex-direction: column;
    height: 100%;
    gap: 16px;
  }

  /* 패널 높이 강제 (일직선 맞춤) */
  .item-video .panel,
  .item-map .panel {
    height: 100% !important; 
    flex: 1;
    min-height: 400px; /* 데스크탑 최소 높이 */
  }

  .item-right .scan-panel {
    flex: 1;
    min-height: 0;
  }

  .item-right .status-panel {
    flex: 0 0 auto;
    height: auto;
  }
}

/* =================================================================
   내부 컴포넌트 스타일 (공통)
   ================================================================= */
.panel:hover { border-color: rgba(255,255,255,0.2); }
.video-panel, .map-panel { background: var(--video-panel-bg); }

.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-bottom: 1px solid var(--glass-border); flex-shrink: 0; background: rgba(255,255,255,0.02); gap: 8px; }
.panel-title { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; }
.panel-body { flex: 1; padding: 12px; min-height: 0; overflow: auto; position: relative; }
.scan-body { padding: 12px; }

.status-body { 
  padding: 0; 
  display: flex; 
  flex-direction: column; 
  overflow: visible !important; 
  height: auto !important;
}

.video-container { 
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  background: #1a1a2e; 
  position: relative; 
  justify-content: center; 
}

/* Video Feed 스타일 */
.video-feed { 
  position: relative; 
  background-color: #000; 
  width: 100%; 
  aspect-ratio: 16/9; 
  max-height: 60vh;   
  margin: auto;
  overflow: hidden; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border-top: 1px solid #333;
  border-bottom: 1px solid #333;
}

.video-body { display: flex; flex-direction: column; padding: 0; background: #1a1a2e; }

/* ... (나머지 기존 스타일 유지) ... */
.status-list { display: flex; flex-direction: column; flex: 1; }
.status-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--glass-border); flex: 1; min-height: 50px; }
.status-row:last-child { border-bottom: none; }
.status-label { font-size: 12px; font-weight: 600; color: var(--text-muted); }
.status-value { font-size: 18px; font-weight: 800; font-family: var(--font-family-mono); color: var(--text-primary); }
.status-value small { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-left: 2px; }
.text-error { color: var(--color-error); }
.header-controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cam-label { display: flex; align-items: center; gap: 6px; font-size: 11px; font-family: var(--font-family-mono); font-weight: 700; color: var(--color-primary); padding: 4px 10px; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 4px; white-space: nowrap; }
.cam-dot { width: 6px; height: 6px; border-radius: 50%; background-color: var(--color-primary); box-shadow: 0 0 6px var(--color-primary); }
.video-overlay { position: absolute; inset: 0; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; pointer-events: none; z-index: 10; background: radial-gradient(circle at center, transparent 60%, rgba(0,0,0,0.6) 100%); }
.overlay-top, .overlay-bottom { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.record-indicator { display: flex; align-items: center; gap: 5px; padding: 3px 8px; background: rgba(239,68,68,0.8); border-radius: 3px; font-size: 10px; font-weight: 800; color: white; }
.record-dot { width: 5px; height: 5px; background-color: white; border-radius: 50%; animation: blink 1s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.timestamp { padding: 3px 8px; background: var(--overlay-darker); border: 1px solid var(--glass-border); border-radius: 3px; font-size: 11px; color: var(--color-primary); font-weight: 700; }
.resolution, .fps { padding: 2px 6px; background: var(--overlay-darker); border-radius: 3px; font-size: 9px; font-family: var(--font-family-mono); color: var(--text-muted); }
.video-corners .corner { position: absolute; width: 28px; height: 28px; border: 2px solid rgba(255,255,255,0.3); z-index: 5; }
.corner.top-left { top: 10px; left: 10px; border-right: none; border-bottom: none; }
.corner.top-right { top: 10px; right: 10px; border-left: none; border-bottom: none; }
.corner.bottom-left { bottom: 10px; left: 10px; border-right: none; border-top: none; }
.corner.bottom-right { bottom: 10px; right: 10px; border-left: none; border-top: none; }

.video-controls { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 8px 12px; 
  background: var(--glass-header); 
  border-top: 1px solid var(--glass-border); 
  flex-shrink: 0; 
}

.control-group { display: flex; align-items: center; gap: 6px; }
.control-btn { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: var(--overlay-lighter); border: 1px solid var(--glass-border); border-radius: 6px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; }
.control-btn:hover { background: var(--overlay-light); color: var(--text-primary); }
.status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 700; }
.badge-success { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); }
.status-dot { width: 5px; height: 5px; border-radius: 50%; }
.status-dot.online { background-color: var(--color-success); box-shadow: 0 0 6px var(--color-success); animation: pulse-status 2s infinite; }
@keyframes pulse-status { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
.live-indicator { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 3px; font-size: 9px; font-weight: 800; color: var(--color-error); }
.live-indicator::before { content: ''; width: 4px; height: 4px; background-color: var(--color-error); border-radius: 50%; animation: blink 1.5s infinite; }
.btn-scan { display: flex; align-items: center; gap: 5px; padding: 5px 12px; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); border: none; border-radius: 5px; color: white; font-size: 11px; font-weight: 700; cursor: pointer; }
.btn-scan:disabled { opacity: 0.6; cursor: not-allowed; }
.scan-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 16px; color: var(--text-muted); text-align: center; gap: 6px; background: var(--overlay-light); border-radius: 6px; border: 1px dashed var(--glass-border); font-size: 12px; }
.scan-empty svg { opacity: 0.3; }
.scan-empty-sub { font-size: 10px; opacity: 0.7; }
.scan-info { display: flex; flex-direction: column; gap: 8px; }
.scan-main { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 8px; border-bottom: 1px solid var(--glass-border); gap: 8px; }
.scan-label { font-size: 8px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 2px; }
.scan-value { font-size: 14px; font-weight: 800; color: var(--text-primary); font-family: var(--font-family-mono); }
.scan-status { padding: 3px 8px; border-radius: 3px; font-size: 9px; font-weight: 700; text-transform: uppercase; }
.scan-status.status-ready { background: var(--overlay-light); color: var(--text-muted); border: 1px solid var(--glass-border); }
.scan-status.status-moving { background: rgba(245,158,11,0.1); color: var(--color-warning); border: 1px solid rgba(245,158,11,0.3); }
.scan-status.status-completed { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); }
.scan-status.status-error { background: rgba(239,68,68,0.1); color: var(--color-error); border: 1px solid rgba(239,68,68,0.3); }
.scan-detail { display: flex; flex-direction: column; gap: 4px; }
.detail-item { display: flex; justify-content: space-between; align-items: center; padding: 6px 8px; background: var(--overlay-light); border-radius: 4px; }
.detail-label { font-size: 10px; color: var(--text-muted); }
.detail-value { font-size: 11px; font-weight: 600; color: var(--text-primary); }
.recognized-region { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(99,102,241,0.3); border-radius: 6px; margin-top: 4px; }
.region-label { font-size: 10px; font-weight: 700; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.05em; }
.region-value { font-size: 11px; font-weight: 700; color: var(--text-primary); }
.region-value.region-pending { color: var(--text-muted); font-style: italic; }
.vehicle-status-badge { padding: 3px 8px; border-radius: 3px; font-size: 9px; font-weight: 700; text-transform: uppercase; }
.vehicle-status-badge.auto { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); }
.vehicle-status-badge.manual { background: rgba(245,158,11,0.1); color: var(--color-warning); border: 1px solid rgba(245,158,11,0.3); }
.video-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; color: var(--text-muted); text-align: center; padding: 20px; }
.placeholder-icon { opacity: 0.3; }
.placeholder-text { font-size: 14px; font-weight: 600; }
.placeholder-sub { font-size: 11px; opacity: 0.6; }

/* 라이브 스트림 스타일 */
.video-stream { 
  width: 100%; 
  height: 100%; 
  position: absolute; 
  inset: 0; 
  object-fit: contain; 
  background: #000; 
  z-index: 1; 
}
.btn-retry { 
  margin-top: 8px; 
  padding: 8px 16px; 
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); 
  border: none; 
  border-radius: 6px; 
  color: white; 
  font-size: 12px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.2s; 
}
.btn-retry:hover { 
  transform: translateY(-1px); 
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); 
}
</style>