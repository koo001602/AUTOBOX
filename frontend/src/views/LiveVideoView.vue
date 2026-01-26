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

    <!-- Center: Real-time Map -->
    <div class="live-center">
      <section class="panel map-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
              <line x1="9" x2="9" y1="3" y2="18" />
              <line x1="15" x2="15" y1="6" y2="21" />
            </svg>
            실시간 맵
          </div>
          <div class="header-controls">
            <button class="btn-zoom" @click="zoomIn" title="확대">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
                <line x1="11" x2="11" y1="8" y2="14" />
                <line x1="8" x2="14" y1="11" y2="11" />
              </svg>
            </button>
            <button class="btn-zoom" @click="zoomOut" title="축소">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
                <line x1="8" x2="14" y1="11" y2="11" />
              </svg>
            </button>
            <button class="btn-reset" @click="resetView" title="초기화">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                <path d="M21 3v5h-5" />
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                <path d="M3 21v-5h5" />
              </svg>
            </button>
          </div>
        </div>

        <div class="panel-body map-body">
          <div class="map-container">
            <!-- SVG Map Canvas -->
            <svg class="map-canvas" :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
              @wheel.prevent="handleWheel" @mousedown="startPan" @mousemove="handlePan" @mouseup="endPan"
              @mouseleave="endPan">
              <!-- Grid Background -->
              <defs>
                <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                  <rect width="50" height="50" fill="none" />
                  <path d="M 50 0 L 0 0 0 50" fill="none" stroke="var(--glass-border)" stroke-width="0.5" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              <!-- Map Elements -->
              <g class="map-elements">
                <!-- Roads -->
                <line x1="100" y1="300" x2="900" y2="300" stroke="var(--text-muted)" stroke-width="8" opacity="0.3" />
                <line x1="500" y1="100" x2="500" y2="700" stroke="var(--text-muted)" stroke-width="8" opacity="0.3" />

                <!-- Buildings -->
                <rect v-for="building in buildings" :key="building.id" :x="building.x" :y="building.y"
                  :width="building.width" :height="building.height" fill="var(--text-muted)" opacity="0.5"
                  stroke="var(--glass-border)" stroke-width="1" />

                <!-- Waypoints -->
                <g v-for="waypoint in waypoints" :key="waypoint.id" class="waypoint">
                  <circle :cx="waypoint.x" :cy="waypoint.y" r="8" :fill="waypoint.color" opacity="0.3" />
                  <circle :cx="waypoint.x" :cy="waypoint.y" r="4" :fill="waypoint.color" />
                  <text :x="waypoint.x" :y="waypoint.y - 15" class="waypoint-label" fill="var(--text-primary)"
                    text-anchor="middle">{{ waypoint.label }}</text>
                </g>

                <!-- Vehicle Path -->
                <path v-if="vehiclePath.length > 0" :d="getPathString(vehiclePath)" fill="none"
                  stroke="var(--color-primary)" stroke-width="2" opacity="0.5" stroke-dasharray="5,5" />

                <!-- Vehicle -->
                <g :transform="`translate(${vehicle.x}, ${vehicle.y}) rotate(${vehicle.angle})`" class="vehicle">
                  <rect x="-15" y="-10" width="30" height="20" fill="var(--color-primary)"
                    stroke="var(--color-primary-glow)" stroke-width="2" rx="3" />
                  <polygon points="15,0 25,5 25,-5" fill="var(--color-primary)" />
                  <circle cx="0" cy="0" r="30" fill="none" stroke="var(--color-primary)" stroke-width="1"
                    opacity="0.3" class="vehicle-pulse" />
                </g>
              </g>
            </svg>

            <!-- Map Overlay Info -->
            <div class="map-overlay">
              <div class="overlay-top-map">
                <div class="coord-display">
                  <span class="coord-label">X</span>
                  <span class="coord-value">{{ vehicle.x.toFixed(1) }}</span>
                  <span class="coord-label">Y</span>
                  <span class="coord-value">{{ vehicle.y.toFixed(1) }}</span>
                  <span class="coord-label">θ</span>
                  <span class="coord-value">{{ vehicle.angle.toFixed(0) }}°</span>
                </div>
              </div>
              <div class="overlay-bottom-map">
                <span class="zoom-level">ZOOM {{ (zoom * 100).toFixed(0) }}%</span>
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

      <!-- Vehicle Status -->
      <section class="panel status-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
              <circle cx="7" cy="17" r="2" />
              <path d="M9 17h6" />
              <circle cx="17" cy="17" r="2" />
            </svg>
            차량 상태
          </div>
          <span class="vehicle-status-badge" :class="vehicleStatus.mode.toLowerCase()">{{ vehicleStatus.mode }}</span>
        </div>

        <div class="panel-body">
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">속도</span>
              <span class="status-value">{{ vehicleStatus.speed }}<small>km/h</small></span>
            </div>
            <div class="status-item">
              <span class="status-label">배터리</span>
              <span class="status-value" :class="{ 'text-error': vehicleStatus.battery < 20 }">{{
                vehicleStatus.battery }}<small>%</small></span>
            </div>
            <div class="status-item">
              <span class="status-label">목적지까지</span>
              <span class="status-value">{{ vehicleStatus.distanceToTarget }}<small>m</small></span>
            </div>
            <div class="status-item">
              <span class="status-label">예상 도착</span>
              <span class="status-value">{{ vehicleStatus.eta }}<small>초</small></span>
            </div>
          </div>

          <div class="sensor-info">
            <h3 class="sensor-title">센서 상태</h3>
            <div class="sensor-grid">
              <div v-for="sensor in sensors" :key="sensor.name" class="sensor-item">
                <div class="sensor-header">
                  <span class="sensor-name">{{ sensor.name }}</span>
                  <span class="sensor-status" :class="sensor.status">{{ sensor.status === 'ok' ? 'OK' : 'ERROR'
                    }}</span>
                </div>
                <div class="sensor-value">{{ sensor.value }}</div>
              </div>
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

// Map-related state
const viewBox = ref({ x: 0, y: 0, width: 1000, height: 800 })
const zoom = ref(1)
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

// Vehicle State
const vehicle = ref({
  x: 200,
  y: 300,
  angle: 0
})

const vehiclePath = ref([
  { x: 200, y: 300 },
])

// Buildings
const buildings = ref([
  { id: 1, x: 150, y: 150, width: 100, height: 80 },
  { id: 2, x: 650, y: 150, width: 120, height: 100 },
  { id: 3, x: 150, y: 450, width: 90, height: 110 },
  { id: 4, x: 700, y: 450, width: 100, height: 90 },
])

// Waypoints
const waypoints = ref([
  { id: 1, label: 'A', x: 200, y: 300, color: 'var(--color-success)' },
  { id: 2, label: 'B', x: 500, y: 200, color: 'var(--color-warning)' },
  { id: 3, label: 'C', x: 750, y: 300, color: 'var(--color-error)' },
  { id: 4, label: 'D', x: 500, y: 600, color: 'var(--color-info)' },
])

const currentWaypointIndex = ref(0)

// Vehicle Status
const vehicleStatus = ref({
  mode: 'AUTO',
  speed: 12.5,
  battery: 85,
  distanceToTarget: 245,
  eta: 78
})

// Sensors
const sensors = ref([
  { name: 'LIDAR', status: 'ok', value: '정상 (360°)' },
  { name: 'Camera', status: 'ok', value: '정상 (1080p)' },
  { name: 'GPS', status: 'ok', value: '정확도 ±2m' },
  { name: 'IMU', status: 'ok', value: '정상' },
])

// Map functions
const getPathString = (path) => {
  if (path.length === 0) return ''
  return path.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value * 1.2, 3)
  updateViewBox()
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value / 1.2, 0.5)
  updateViewBox()
}

const resetView = () => {
  zoom.value = 1
  viewBox.value = { x: 0, y: 0, width: 1000, height: 800 }
}

const updateViewBox = () => {
  const baseWidth = 1000
  const baseHeight = 800
  const newWidth = baseWidth / zoom.value
  const newHeight = baseHeight / zoom.value

  viewBox.value = {
    x: vehicle.value.x - newWidth / 2,
    y: vehicle.value.y - newHeight / 2,
    width: newWidth,
    height: newHeight
  }
}

const handleWheel = (e) => {
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  zoom.value = Math.max(0.5, Math.min(3, zoom.value * delta))
  updateViewBox()
}

const startPan = (e) => {
  isPanning.value = true
  panStart.value = { x: e.clientX, y: e.clientY }
}

const handlePan = (e) => {
  if (!isPanning.value) return

  const dx = (e.clientX - panStart.value.x) * (viewBox.value.width / 1000)
  const dy = (e.clientY - panStart.value.y) * (viewBox.value.height / 800)

  viewBox.value.x -= dx
  viewBox.value.y -= dy

  panStart.value = { x: e.clientX, y: e.clientY }
}

const endPan = () => {
  isPanning.value = false
}

// Vehicle simulation
let simulationInterval = null

const simulateVehicleMovement = () => {
  if (currentWaypointIndex.value >= waypoints.value.length) {
    currentWaypointIndex.value = 0
    vehiclePath.value = [{ x: waypoints.value[0].x, y: waypoints.value[0].y }]
  }

  const target = waypoints.value[currentWaypointIndex.value]
  const dx = target.x - vehicle.value.x
  const dy = target.y - vehicle.value.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (distance < 5) {
    currentWaypointIndex.value++
    if (currentWaypointIndex.value < waypoints.value.length) {
      const nextTarget = waypoints.value[currentWaypointIndex.value]
      const nextDx = nextTarget.x - vehicle.value.x
      const nextDy = nextTarget.y - vehicle.value.y
      vehicleStatus.value.distanceToTarget = Math.sqrt(nextDx * nextDx + nextDy * nextDy).toFixed(0)
      vehicleStatus.value.eta = (vehicleStatus.value.distanceToTarget / (vehicleStatus.value.speed / 3.6)).toFixed(0)
    }
    return
  }

  const speed = 2
  const vx = (dx / distance) * speed
  const vy = (dy / distance) * speed

  vehicle.value.x += vx
  vehicle.value.y += vy
  vehicle.value.angle = Math.atan2(dy, dx) * (180 / Math.PI)

  vehiclePath.value.push({ x: vehicle.value.x, y: vehicle.value.y })
  if (vehiclePath.value.length > 100) {
    vehiclePath.value.shift()
  }

  // Update status
  vehicleStatus.value.distanceToTarget = distance.toFixed(0)
  vehicleStatus.value.eta = (distance / (vehicleStatus.value.speed / 3.6)).toFixed(0)

  updateViewBox()
}

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
  simulationInterval = setInterval(simulateVehicleMovement, 50)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (simulationInterval) {
    clearInterval(simulationInterval)
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
  display: grid;
  grid-template-columns: 1fr 1fr 380px;
  gap: 24px;
  overflow: hidden;
}

.live-left {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.live-center {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.live-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  background: var(--video-panel-bg);
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
  box-shadow: 0 0 10px var(--color-primary-glow);
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
  background: var(--overlay-darker);
  border: 1px solid var(--glass-border);
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
  background: var(--overlay-darker);
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
  background: var(--overlay-lighter);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.control-btn:hover {
  background: var(--overlay-light);
  color: var(--text-primary);
  border-color: var(--glass-border-hover);
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
  background: var(--overlay-light);
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
  background: var(--overlay-light);
  color: var(--text-muted);
  border: 1px solid var(--glass-border);
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
  background: var(--overlay-light);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.detail-item:hover {
  background: var(--overlay-lighter);
  border-color: var(--glass-border);
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
  background: var(--overlay-light);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: var(--overlay-lighter);
  border-color: var(--glass-border);
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

/* Map Panel Styles */
.map-panel {
  flex: 1;
  min-height: 0;
}

.map-body {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.map-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--overlay-dark);
  border-radius: 12px;
  overflow: hidden;
}

.map-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.map-canvas:active {
  cursor: grabbing;
}

/* Vehicle Animation */
.vehicle {
  transition: transform 0.05s linear;
}

.vehicle-pulse {
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% {
    opacity: 0.5;
    r: 20;
  }

  100% {
    opacity: 0;
    r: 40;
  }
}

/* Map Overlay */
.map-overlay {
  position: absolute;
  inset: 0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}

.overlay-top-map {
  display: flex;
  justify-content: flex-end;
}

.overlay-bottom-map {
  display: flex;
  justify-content: flex-end;
}

.coord-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--overlay-darker);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  backdrop-filter: blur(4px);
}

.coord-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.coord-value {
  font-size: 13px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  color: var(--color-primary);
}

.zoom-level {
  padding: 6px 12px;
  background: var(--overlay-darker);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  color: var(--text-muted);
  backdrop-filter: blur(4px);
}

/* Waypoint Labels */
.waypoint-label {
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

/* Zoom Buttons */
.btn-zoom,
.btn-reset {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--overlay-lighter);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-zoom:hover,
.btn-reset:hover {
  background: var(--overlay-light);
  color: var(--text-primary);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
}

/* Vehicle Status Panel */
.status-panel {
  flex-shrink: 0;
}

.vehicle-status-badge {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.vehicle-status-badge.auto {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.1);
}

.vehicle-status-badge.manual {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

/* Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  background: var(--overlay-light);
  border-radius: 8px;
  border: 1px solid var(--glass-border);
}

.status-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-value {
  font-size: 20px;
  font-weight: 800;
  font-family: var(--font-family-mono);
  color: var(--text-primary);
}

.status-value small {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  margin-left: 2px;
}

.text-error {
  color: var(--color-error);
}

/* Sensor Info */
.sensor-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sensor-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.sensor-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sensor-item {
  padding: 10px 12px;
  background: var(--overlay-light);
  border-radius: 6px;
  border: 1px solid var(--glass-border);
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3px;
}

.sensor-name {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
}

.sensor-status {
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
}

.sensor-status.ok {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.sensor-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.sensor-value {
  font-size: 10px;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 1400px) {
  .live-view {
    grid-template-columns: 1fr 1fr 320px;
  }
}

@media (max-width: 1024px) {
  .live-view {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }

  .live-left,
  .live-center,
  .live-right {
    width: 100%;
    height: auto;
  }

  .video-container {
    aspect-ratio: 16/9;
    max-height: 40vh;
  }

  .map-container {
    aspect-ratio: 16/9;
    max-height: 40vh;
  }
}
</style>
