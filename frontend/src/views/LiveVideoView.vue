<template>
  <div class="live-view">
    <!-- Main Map Area (Left/Center) -->
    <div class="map-layer">
      <div class="map-container-3d" ref="mapContainer3D"></div>

      <!-- Map Overlay Controls (Minimal) -->
      <div class="map-overlay-header">
        <div class="map-title-badge">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="var(--color-primary)" stroke-width="2">
            <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
            <line x1="9" x2="9" y1="3" y2="18" />
            <line x1="15" x2="15" y1="6" y2="21" />
          </svg>
          <span>실시간 3D 맵</span>
        </div>
      </div>
    </div>

    <!-- Fixed Right Sidebar -->
    <aside class="monitoring-sidebar">
      <div class="sidebar-header">
        <h2>Monitoring</h2>
        <span class="live-indicator">LIVE</span>
      </div>

      <div class="sidebar-content">
        <!-- 1. Camera Feed Section -->
        <div class="sidebar-section camera-section">
          <div class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <path d="M23 7l-7 5 7 5V7z" />
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
            </svg>
            Camera Feed
          </div>
          <div class="camera-container">
            <!-- MediaMTX WebRTC Live Stream -->
            <iframe v-if="isStreamConnected" :src="streamUrl" class="video-stream" frameborder="0" allowfullscreen
              @load="onStreamLoad" @error="onStreamError"></iframe>

            <!-- Connection Placeholder -->
            <div class="video-placeholder" v-else>
              <div class="placeholder-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="1.5">
                  <path d="M15 10l5 5-5 5" />
                  <path d="M4 4v7a4 4 0 0 0 4 4h12" />
                </svg>
              </div>
              <span>Signal Lost</span>
              <button class="btn-retry-text" @click="connectStream">Reconnect</button>
            </div>

            <!-- Overlay Info -->
            <div class="camera-overlay">
              <span class="cam-id">CAM:01</span>
              <span class="timestamp-small">{{ currentTime }}</span>
            </div>
          </div>

          <div class="connection-status">
            <span class="status-dot-sm" :class="isStreamConnected ? 'online' : 'offline'"></span>
            {{ isStreamConnected ? 'Online' : 'Offline' }}
          </div>
        </div>

        <!-- 2. Vehicle Status Section -->
        <div class="sidebar-section status-section">
          <div class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
              <line x1="8" y1="21" x2="16" y2="21" />
              <line x1="12" y1="17" x2="12" y2="21" />
            </svg>
            Vehicle Status
          </div>

          <div class="status-card">
            <div class="status-row">
              <span class="label">Connection</span>
              <span class="value-badge" :class="isVehicleConnected ? 'connected' : 'disconnected'">
                {{ isVehicleConnected ? 'Connected' : 'Disconnected' }}
              </span>
            </div>
            <div class="status-row">
              <span class="label">Mode</span>
              <span class="value-text">{{ vehicleStatus.mode }}</span>
            </div>

            <div class="status-grid-compact">
              <div class="stat-item">
                <span class="stat-val">{{ vehicleStatus.speed }} <small>km/h</small></span>
                <span class="stat-label">Speed</span>
              </div>
              <div class="stat-item">
                <span class="stat-val" :class="{ 'text-red': vehicleStatus.battery < 20 }">
                  {{ vehicleStatus.battery }} <small>%</small>
                </span>
                <span class="stat-label">Battery</span>
              </div>
              <div class="stat-item">
                <span class="stat-val">{{ vehicleStatus.distanceToTarget }} <small>m</small></span>
                <span class="stat-label">Dist</span>
              </div>
              <div class="stat-item">
                <span class="stat-val">{{ vehicleStatus.eta }} <small>s</small></span>
                <span class="stat-label">ETA</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Map Controls Section -->
        <div class="sidebar-section control-section">
          <div class="section-title">Map Controls</div>
          <div class="control-buttons">
            <button class="ctrl-btn" @click="zoomIn3D" title="Zoom In">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                <line x1="11" y1="8" x2="11" y2="14" />
                <line x1="8" y1="11" x2="14" y2="11" />
              </svg>
            </button>
            <button class="ctrl-btn" @click="zoomOut3D" title="Zoom Out">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                <line x1="8" y1="11" x2="14" y2="11" />
              </svg>
            </button>
            <button class="ctrl-btn" @click="resetView3D" title="Reset View">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
            </button>
          </div>
        </div>

      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { startWaybillScan, startSorting, completeSorting, fetchWaybills, fetchVehiclePosition, fetchMapData, fetchSensorStatus, getMockMode } from '../api'
import { useTheme } from '../composables/useTheme'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

// Theme
const { theme, isDark } = useTheme()

// Config
const MAP_CONFIG = {
  resolution: 0.05,
  origin: [-3.81, -20.7, 0],
  wallHeight: 1.5,
  occupiedThresh: 0.65
}

// State
const currentTime = ref('')
const isScanning = ref(false)
const isLoading = ref(true)
const isMockMode = getMockMode()

// Stream
const isStreamConnected = ref(false)
const streamError = ref('')
const streamUrl = ref('/stream/cam1/')

// Draggable Modal State
// Draggable Modal State (Removed)

// 3D Map
const mapContainer3D = ref(null)
let scene, camera, renderer, controls, vehicleMesh, mapMesh, floorMesh
let animationFrameId = null

const vehicle = ref({ x: 0, y: 0, angle: 0 })
const vehicleStatus = ref({ mode: 'IDLE', speed: 0, battery: 100, distanceToTarget: 0, eta: 0 })
const isVehicleConnected = ref(false)
const isVideoVisible = ref(true)
let timeInterval = null

// Functions
const connectStream = () => {
  streamError.value = ''
  isStreamConnected.value = true
}

const onStreamLoad = () => {
  streamError.value = ''
  console.log('Stream Connected')
}

const onStreamError = () => {
  isStreamConnected.value = false
  streamError.value = 'Stream Failed'
}

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString('ko-KR', { hour12: false })
}

const loadVehiclePosition = async () => {
  try {
    const res = await fetchVehiclePosition()
    if (res.data?.success && res.data?.data) {
      const data = res.data.data
      vehicle.value = { x: data.x || 0, y: data.y || 0, angle: data.angle || 0 }
      vehicleStatus.value = {
        mode: data.mode || 'IDLE',
        speed: parseFloat(data.speed) || 0,
        battery: data.battery || 100,
        distanceToTarget: data.distanceToTarget || 0,
        eta: data.eta || 0
      }

      const isDefaultPosition = Math.abs(data.x - 450) < 1 && Math.abs(data.y - 350) < 1
      const isIdleMode = data.mode === 'IDLE' || data.mode === '-' || !data.mode
      isVehicleConnected.value = !(isIdleMode && isDefaultPosition)
    } else {
      isVehicleConnected.value = false
    }
  } catch (err) {
    console.error('Vehicle Pos Error:', err)
    isVehicleConnected.value = false
  }
}

// 3D Setup
const init3DMap = () => {
  if (!mapContainer3D.value) return
  const container = mapContainer3D.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  const sceneBgColor = isDark() ? 0x1e1e2e : 0xe2e8f0
  scene.background = new THREE.Color(sceneBgColor)

  // Orthographic Camera for 2D Plan View
  const aspect = width / height
  const frustumSize = 60 // 맵 크기에 맞춰 조정 (대략 60m 범위 커버)
  camera = new THREE.OrthographicCamera(
    frustumSize * aspect / -2,
    frustumSize * aspect / 2,
    frustumSize / 2,
    frustumSize / -2,
    0.1,
    2000
  )

  // Top-down view (looking strictly from Y axis)
  camera.position.set(0, 100, 0)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  container.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableRotate = false // Disable rotation for strict 2D view
  controls.enableZoom = true
  controls.enablePan = true
  controls.screenSpacePanning = true // Pan up/down instead of forward/backward
  controls.dampingFactor = 0.05
  controls.enableDamping = true

  addLights()
  createSlamMap()
  createVehicle()
  animate()
  window.addEventListener('resize', handleResize)
}

const addLights = () => {
  scene.add(new THREE.AmbientLight(0xffffff, 0.6))
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.7)
  mainLight.position.set(20, 100, 30) // Light from top
  mainLight.castShadow = true
  mainLight.shadow.mapSize.set(2048, 2048)
  // Shadow camera frustum needs to cover the map area
  const d = 50
  mainLight.shadow.camera.left = -d
  mainLight.shadow.camera.right = d
  mainLight.shadow.camera.top = d
  mainLight.shadow.camera.bottom = -d
  scene.add(mainLight)
}

const createSlamMap = () => {
  const loader = new THREE.TextureLoader()
  loader.load('/testMap12.png', (texture) => {
    const image = texture.image
    const width = 1000 // Approximate
    const height = 1000

    const canvas = document.createElement('canvas')
    canvas.width = image.width
    canvas.height = image.height
    const ctx = canvas.getContext('2d')
    ctx.drawImage(image, 0, 0)
    const imgData = ctx.getImageData(0, 0, image.width, image.height)
    const data = imgData.data

    const wallPositions = []
    const res = MAP_CONFIG.resolution
    const originX = MAP_CONFIG.origin[0]
    const originY = MAP_CONFIG.origin[1]

    // Floor
    const floorWidth = image.width * res
    const floorHeight = image.height * res
    const floorCenterX = originX + (image.width * res) / 2
    const floorCenterY = originY + (image.height * res) / 2

    const floorColor = isDark() ? 0x2a2a3d : 0xc8d1dc
    floorMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(floorWidth, floorHeight),
      new THREE.MeshStandardMaterial({ color: floorColor, roughness: 0.9 })
    )
    floorMesh.rotation.x = -Math.PI / 2
    floorMesh.position.set(floorCenterX, -0.01, -floorCenterY)
    floorMesh.receiveShadow = true
    scene.add(floorMesh)

    if (controls) {
      controls.target.set(floorCenterX, 0, -floorCenterY)
      controls.update()
    }

    // Walls
    for (let row = 0; row < image.height; row++) {
      for (let col = 0; col < image.width; col++) {
        const index = (row * image.width + col) * 4
        if (data[index] < 100) {
          const worldX = originX + col * res
          const worldY = originY + (image.height - 1 - row) * res
          wallPositions.push({ x: worldX, z: -worldY })
        }
      }
    }

    const wallColor = isDark() ? 0x505060 : 0x64748b
    const wallGeo = new THREE.BoxGeometry(res, MAP_CONFIG.wallHeight, res)
    const wallMat = new THREE.MeshStandardMaterial({ color: wallColor, roughness: 0.7 })
    mapMesh = new THREE.InstancedMesh(wallGeo, wallMat, wallPositions.length)
    mapMesh.castShadow = true
    mapMesh.receiveShadow = true

    const dummy = new THREE.Object3D()
    for (let i = 0; i < wallPositions.length; i++) {
      const pos = wallPositions[i]
      dummy.position.set(pos.x, MAP_CONFIG.wallHeight / 2, pos.z)
      dummy.updateMatrix()
      mapMesh.setMatrixAt(i, dummy.matrix)
    }
    mapMesh.instanceMatrix.needsUpdate = true
    scene.add(mapMesh)
  })
}

const createVehicle = () => {
  vehicleMesh = new THREE.Group()
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 0.3, 0.9),
    new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.4, metalness: 0.4 })
  )
  body.position.y = 0.25
  body.castShadow = true
  vehicleMesh.add(body)

  const wheelGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.1, 12)
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1f2937 })
  const wheelPos = [[-0.35, -0.3], [0.35, -0.3], [-0.35, 0.3], [0.35, 0.3]]
  wheelPos.forEach(([x, z]) => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMat)
    wheel.rotation.z = Math.PI / 2
    wheel.position.set(x, 0.1, z)
    vehicleMesh.add(wheel)
  })

  const light = new THREE.Mesh(
    new THREE.BoxGeometry(0.4, 0.05, 0.05),
    new THREE.MeshBasicMaterial({ color: 0xffff00 })
  )
  light.position.set(0, 0.3, -0.45)
  vehicleMesh.add(light)

  scene.add(vehicleMesh)
}

const animate = () => {
  animationFrameId = requestAnimationFrame(animate)
  controls?.update()
  if (vehicleMesh && isVehicleConnected.value) {
    vehicleMesh.visible = true
    vehicleMesh.position.x = vehicle.value.x
    vehicleMesh.position.z = -vehicle.value.y
    vehicleMesh.rotation.y = vehicle.value.angle * (Math.PI / 180)
  } else if (vehicleMesh) {
    vehicleMesh.visible = false
  }
  renderer?.render(scene, camera)
}

const handleResize = () => {
  if (!mapContainer3D.value || !camera || !renderer) return
  const w = mapContainer3D.value.clientWidth
  const h = mapContainer3D.value.clientHeight

  // Orthographic camera resize
  const aspect = w / h
  const frustumSize = 60
  camera.left = -frustumSize * aspect / 2
  camera.right = frustumSize * aspect / 2
  camera.top = frustumSize / 2
  camera.bottom = -frustumSize / 2

  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

const zoomIn3D = () => {
  if (camera) {
    const dir = new THREE.Vector3()
    camera.getWorldDirection(dir)
    camera.position.addScaledVector(dir, 5)
  }
}

const zoomOut3D = () => {
  if (camera) {
    const dir = new THREE.Vector3()
    camera.getWorldDirection(dir)
    camera.position.addScaledVector(dir, -5)
  }
}

const resetView3D = () => {
  if (camera && controls) {
    camera.position.set(5, 80, 5)
    controls.target.set(5, 0, -10)
    controls.update()
  }
}

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  await loadVehiclePosition()
  await nextTick()
  init3DMap()
  if (!isMockMode) {
    setInterval(loadVehiclePosition, 1000)
  }
  connectStream()
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
  if (renderer) renderer.dispose()
})

watch(theme, () => {
  if (!scene) return
  const isDarkMode = isDark()
  scene.background = new THREE.Color(isDarkMode ? 0x1a1a2e : 0xe2e8f0)
  if (floorMesh) floorMesh.material.color.setHex(isDarkMode ? 0x2a2a3d : 0xc8d1dc)
  if (mapMesh) mapMesh.material.color.setHex(isDarkMode ? 0x505060 : 0x64748b)
})
</script>

<style scoped>
.live-view {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--bg-primary);
}

/* Map Layer (Background) */
.map-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.map-panel {
  width: 100%;
  height: 100%;
  position: relative;
  background: var(--bg-secondary);
}

.map-container-3d {
  width: 100%;
  height: 100%;
}

/* Map specific controls floating on top left/right */
.map-controls {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
}

.map-title-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--glass-panel);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  color: var(--text-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.divider {
  color: var(--glass-border);
  font-weight: 300;
}

.vehicle-status-text {
  font-size: 12px;
  font-weight: 600;
}

.vehicle-status-text.connected {
  color: var(--color-success);
}

.vehicle-status-text.disconnected {
  color: var(--text-muted);
}

.map-btn-group {
  display: flex;
  gap: 4px;
  background: var(--glass-panel);
  padding: 4px;
  border-radius: 10px;
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(8px);
}

.map-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.map-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

/* Layout */
.live-view {
  display: flex;
  height: calc(100vh - 64px);
  background: var(--bg-primary);
  overflow: hidden;
  position: relative;
}

.map-layer {
  flex: 1;
  position: relative;
  background: #e2e8f0;
}

.dark-mode .map-layer {
  background: #1e1e2e;
}

.map-container-3d {
  width: 100%;
  height: 100%;
}

/* Sidebar */
.monitoring-sidebar {
  width: 320px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 10;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.sidebar-header h2 {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.live-indicator {
  background: #ef4444;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  animation: pulse 2s infinite;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Sections */
.sidebar-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid var(--border-color);
}

/* Camera */
.camera-container {
  width: 100%;
  aspect-ratio: 4/3;
  background: #000;
  position: relative;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #52525b;
  gap: 8px;
}

.camera-overlay {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  gap: 6px;
  pointer-events: none;
}

.cam-id {
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

.timestamp-small {
  background: rgba(0, 0, 0, 0.6);
  color: #10b981;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-family: monospace;
}

.connection-status {
  padding: 8px 12px;
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px solid var(--border-color);
}

.status-dot-sm {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot-sm.online {
  background: #10b981;
  box-shadow: 0 0 4px #10b981;
}

.status-dot-sm.offline {
  background: #52525b;
}

/* Status Card */
.status-card {
  padding: 12px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 12px;
  align-items: center;
}

.status-row .label {
  color: var(--text-muted);
}

.value-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.value-badge.connected {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.value-badge.disconnected {
  background: rgba(244, 63, 94, 0.1);
  color: #f43f5e;
}

.value-text {
  font-weight: 600;
  color: var(--text-primary);
}

.status-grid-compact {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-item {
  background: var(--bg-tertiary);
  padding: 8px;
  border-radius: 6px;
  text-align: center;
}

.stat-val {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-val.text-red {
  color: #f43f5e;
}

.stat-val small {
  font-size: 10px;
  color: var(--text-muted);
}

.stat-label {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 2px;
  display: block;
}

/* Map Controls in Sidebar */
.control-buttons {
  padding: 12px;
  display: flex;
  justify-content: space-around;
  gap: 8px;
}

.ctrl-btn {
  flex: 1;
  height: 36px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.ctrl-btn:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

/* Map Overlay */
.map-overlay-header {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 5;
  pointer-events: none;
}

.map-title-badge {
  background: var(--glass-panel);
  backdrop-filter: blur(8px);
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: var(--text-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  pointer-events: auto;
}

.placeholder-icon {
  margin-bottom: 8px;
  opacity: 0.5;
}

.btn-retry-text {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}

.btn-retry-text:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

@keyframes pulse {
  0% {
    opacity: 1;
  }

  50% {
    opacity: 0.6;
  }

  100% {
    opacity: 1;
  }
}
</style>