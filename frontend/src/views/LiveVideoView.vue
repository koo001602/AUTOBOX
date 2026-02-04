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
                <span class="status-badge" :class="isStreamConnected ? 'badge-success' : 'badge-error'"><span class="status-dot" :class="isStreamConnected ? 'online' : 'offline'"></span>{{ isStreamConnected ? '연결됨' : '연결 끊김' }}</span>
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
            <span class="vehicle-connect-badge" :class="isVehicleConnected ? 'connected' : 'disconnected'">
              <span class="vehicle-dot"></span>{{ isVehicleConnected ? 'RC카 연결됨' : 'RC카 미연결' }}
            </span>
            <button class="btn-zoom" @click="zoomIn3D" title="확대"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /><line x1="11" x2="11" y1="8" y2="14" /><line x1="8" x2="14" y1="11" y2="11" /></svg></button>
            <button class="btn-zoom" @click="zoomOut3D" title="축소"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /><line x1="8" x2="14" y1="11" y2="11" /></svg></button>
            <button class="btn-reset" @click="resetView3D" title="초기화"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M3 21v-5h5" /></svg></button>
          </div>
        </div>
        <div class="panel-body map-body">
          <div class="map-container-3d" ref="mapContainer3D">
            <!-- 맵 오버레이 삭제됨 -->
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
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { startWaybillScan, startSorting, completeSorting, fetchWaybills, fetchVehiclePosition, fetchMapData, fetchSensorStatus, getMockMode } from '../api'
import { useTheme } from '../composables/useTheme'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

// 스 테마 가져오기
const { theme, isDark } = useTheme()

// SLAM 맵 설정 (YAML 파일 메타데이터 기반)
const MAP_CONFIG = {
  resolution: 0.05,        // 1픽셀 = 0.05m
  origin: [-3.81, -20.7, 0], // 맵 원점 [x, y, z]
  wallHeight: 1.5,         // 벽 높이 (미터)
  occupiedThresh: 0.65     // 벽으로 인식할 임계값 (0~1)
}

const currentTime = ref('')
const isScanning = ref(false)
const currentScan = ref(null)
const scanHistory = ref([])
const isLoading = ref(true)
const isMockMode = getMockMode()

// 라이브 스트림 관련 상태
const isStreamConnected = ref(false)
const streamError = ref('')
// MediaMTX WebRTC 스트림 URL (nginx /stream/ 프록시 사용)
const streamUrl = ref('/stream/cam1/')

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

let timeInterval = null

// 3D 맵 객체들
const mapContainer3D = ref(null)
let scene, camera, renderer, controls, vehicleMesh, mapMesh, floorMesh
let animationFrameId = null

const vehicle = ref({ x: 0, y: 0, angle: 0 })
const vehicleStatus = ref({ mode: '-', speed: 0, battery: 0, distanceToTarget: 0, eta: 0 })

// RC카 연결 상태 (라즈베리파이 연동 여부)
const isVehicleConnected = ref(false)

const init3DMap = () => {
  if (!mapContainer3D.value) return
  const container = mapContainer3D.value
  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  // 테마별 씨 배경색
  const sceneBgColor = isDark() ? 0x1a1a2e : 0xe2e8f0
  scene.background = new THREE.Color(sceneBgColor)
  
  camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000)
  camera.position.set(5, 80, 60)  // 높이와 거리 증가
  camera.lookAt(5, 0, -5)         // 맵 중심 바라보기

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  container.insertBefore(renderer.domElement, container.firstChild)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.maxPolarAngle = Math.PI / 2.1
  
  addLights()
  
  // 이미지 분석 기반 SLAM 맵 생성
  createSlamMap()
  
  createVehicle()
  animate()
  window.addEventListener('resize', handleResize)
}

const addLights = () => {
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.8)
  mainLight.position.set(20, 50, 30)
  mainLight.castShadow = true
  mainLight.shadow.mapSize.set(2048, 2048)
  mainLight.shadow.camera.left = -50
  mainLight.shadow.camera.right = 50
  mainLight.shadow.camera.top = 50
  mainLight.shadow.camera.bottom = -50
  scene.add(mainLight)
}

// 이미지 파싱 및 복셀 맵 생성
const createSlamMap = () => {
  const loader = new THREE.TextureLoader()
  
  // public 폴더의 이미지 로드
  loader.load('/testMap12.png', (texture) => {
    const image = texture.image
    const width = image.width
    const height = image.height
    
    // 픽셀 데이터 추출
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const ctx = canvas.getContext('2d')
    ctx.drawImage(image, 0, 0)
    
    const imgData = ctx.getImageData(0, 0, width, height)
    const data = imgData.data // RGBA
    
    const wallPositions = []
    const res = MAP_CONFIG.resolution
    const originX = MAP_CONFIG.origin[0]
    const originY = MAP_CONFIG.origin[1]
    
    // 1. 바닥 생성 (테마별 색상)
    const floorWidth = width * res
    const floorHeight = height * res
    const floorCenterX = originX + (width * res) / 2
    const floorCenterY = originY + (height * res) / 2
    
    // 테마별 바닥 색상: 다크=어두운 회색, 라이트=밝은 회색
    const floorColor = isDark() ? 0x2a2a3d : 0xc8d1dc
    
    floorMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(floorWidth, floorHeight),
      new THREE.MeshStandardMaterial({ color: floorColor, roughness: 0.9 })
    )
    floorMesh.rotation.x = -Math.PI / 2
    // Three.js 좌표계: -Z 방향이 ROS의 Y축
    floorMesh.position.set(floorCenterX, -0.01, -floorCenterY)
    floorMesh.receiveShadow = true
    scene.add(floorMesh)

    // 카메라 중심 이동
    if (controls) {
        controls.target.set(floorCenterX, 0, -floorCenterY)
        controls.update()
    }
    // 2. 픽셀 루프: 검은색(벽) 찾기
    for (let row = 0; row < height; row++) {
      for (let col = 0; col < width; col++) {
        const index = (row * width + col) * 4
        const intensity = data[index] // 0(검정) ~ 255(흰색)
        
        // 검은색에 가까운 픽셀을 벽으로 인식
        if (intensity < 100) { 
          // 좌표 변환: Origin + (Pixel * Resolution)
          const worldX = originX + col * res
          // 이미지 Top-Down -> ROS Bottom-Up 변환
          const worldY = originY + (height - 1 - row) * res
          
          // Three.js 좌표계: (X, Y, Z) -> (ROS_X, Height, -ROS_Y)
          wallPositions.push({ x: worldX, z: -worldY })
        }
      }
    }
    
    // 3. InstancedMesh로 벽 생성 (성능 최적화)
    // 테마별 벽 색상: 다크=어두운 회색, 라이트=남색 계열
    const wallColor = isDark() ? 0x505060 : 0x64748b
    
    const wallGeo = new THREE.BoxGeometry(res, MAP_CONFIG.wallHeight, res)
    const wallMat = new THREE.MeshStandardMaterial({ 
      color: wallColor, 
      roughness: 0.7 
    })
    
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
  
  // 차체
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 0.3, 0.9), 
    new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.4, metalness: 0.4 })
  )
  body.position.y = 0.25
  body.castShadow = true
  vehicleMesh.add(body)

  // 센서 유닛
  const sensor = new THREE.Mesh(
    new THREE.BoxGeometry(0.4, 0.15, 0.5),
    new THREE.MeshStandardMaterial({ color: 0x0d9488, metalness: 0.5 })
  )
  sensor.position.y = 0.5
  vehicleMesh.add(sensor)

  // 바퀴
  const wheelGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.1, 12)
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1f2937 })
  const wheelPos = [[-0.35, -0.3], [0.35, -0.3], [-0.35, 0.3], [0.35, 0.3]]
  wheelPos.forEach(([x, z]) => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMat)
    wheel.rotation.z = Math.PI / 2
    wheel.position.set(x, 0.1, z)
    vehicleMesh.add(wheel)
  })

  // 헤드라이트 (방향 표시)
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

  if (vehicleMesh) {
    // RC카 연결 상태에 따라 차량 표시/숨김
    vehicleMesh.visible = isVehicleConnected.value
    
    if (isVehicleConnected.value) {
      vehicleMesh.position.x = vehicle.value.x
      vehicleMesh.position.z = -vehicle.value.y // Y축 반전 (ROS -> Three)
      vehicleMesh.rotation.y = vehicle.value.angle * (Math.PI / 180)
    }
  }

  renderer?.render(scene, camera)
}

const handleResize = () => {
  if (!mapContainer3D.value || !camera || !renderer) return
  const w = mapContainer3D.value.clientWidth
  const h = mapContainer3D.value.clientHeight
  camera.aspect = w / h
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
    // 맵 전체가 보이도록 초기 위치로 리셋
    camera.position.set(5, 80, 60)
    controls.target.set(5, 0, -5)
    controls.update()
  }
}

// API 통신 및 데이터 로드
const loadVehiclePosition = async () => { 
  try { 
    const res = await fetchVehiclePosition()
    if (res.data?.success && res.data?.data) { 
      const data = res.data.data
      vehicle.value = { x: data.x || 0, y: data.y || 0, angle: data.angle || 0 }
      vehicleStatus.value = { 
        mode: data.mode || 'UNKNOWN', 
        speed: parseFloat(data.speed) || 0, 
        battery: data.battery || 0, 
        distanceToTarget: data.distanceToTarget || 0, 
        eta: data.eta || 0 
      }
      
      // RC카 연결 상태 판단: mode가 IDLE이고 기본 좌표(450, 350)이면 미연결
      const isDefaultPosition = Math.abs(data.x - 450) < 1 && Math.abs(data.y - 350) < 1
      const isIdleMode = data.mode === 'IDLE' || data.mode === '-' || !data.mode
      isVehicleConnected.value = !(isIdleMode && isDefaultPosition)
    } else {
      isVehicleConnected.value = false
    }
  } catch (err) { 
    console.error('차량 위치 로드 실패:', err)
    isVehicleConnected.value = false
  } 
}
const updateTime = () => { currentTime.value = new Date().toLocaleTimeString('ko-KR', { hour12: false }) }
const formatTime = (dateStr) => !dateStr ? '-' : new Date(dateStr).toLocaleTimeString('ko-KR', { hour12: false })
const getStatusText = (status) => ({ READY: '대기', MOVING: '이동 중', COMPLETED: '완료', ERROR: '오류' }[status] || status)
const getStatusClass = (status) => ({ 'status-ready': status === 'READY', 'status-moving': status === 'MOVING', 'status-completed': status === 'COMPLETED', 'status-error': status === 'ERROR' })

const handleScan = async () => { if (isScanning.value) return; isScanning.value = true; try { const res = await startWaybillScan('CAM:01'); if (res.data.success) { currentScan.value = res.data.data; scanHistory.value.unshift(res.data.data); if (scanHistory.value.length > 10) scanHistory.value.pop() } } catch (err) { console.error('스캔 실패:', err) } finally { isScanning.value = false } }
const handleStartSorting = async () => { if (!currentScan.value) return; try { const res = await startSorting(currentScan.value.waybill_id); if (res.data.success) { currentScan.value = { ...currentScan.value, ...res.data.data }; updateHistoryItem(res.data.data) } } catch (err) { console.error('분류 시작 실패:', err) } }
const handleComplete = async () => { if (!currentScan.value) return; try { const res = await completeSorting(currentScan.value.waybill_id); if (res.data.success) { currentScan.value = { ...currentScan.value, ...res.data.data }; updateHistoryItem(res.data.data) } } catch (err) { console.error('분류 완료 실패:', err) } }
const updateHistoryItem = (data) => { const idx = scanHistory.value.findIndex(h => h.waybill_id === data.waybill_id); if (idx >= 0) scanHistory.value[idx] = { ...scanHistory.value[idx], ...data } }
const loadHistory = async () => { try { const res = await fetchWaybills({ size: 10 }); if (res.data?.success || res.data?.data) scanHistory.value = res.data.data?.items || [] } catch (err) { console.error('이력 로드 실패:', err); scanHistory.value = [] } }
const loadInitialData = async () => { isLoading.value = true; try { await loadVehiclePosition() } finally { isLoading.value = false } }
const startDataPolling = () => { timeInterval = setInterval(async () => { await loadVehiclePosition() }, 1000) }

onMounted(async () => { 
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadHistory()
  await loadInitialData()
  await nextTick()
  init3DMap()
  if (!isMockMode) startDataPolling()
  connectStream()  // 스트림 연결 시도
})

// 테마 변경 감지 및 3D 맵 색상 실시간 업데이트
watch(theme, () => {
  if (!scene) return

  const isDarkMode = isDark()
  
  // 1. 씬 배경
  const sceneBgColor = isDarkMode ? 0x1a1a2e : 0xe2e8f0
  scene.background = new THREE.Color(sceneBgColor)
  
  // 2. 바닥 색상
  if (floorMesh) {
    const floorColor = isDarkMode ? 0x2a2a3d : 0xc8d1dc
    floorMesh.material.color.setHex(floorColor)
  }
  
  // 3. 벽 색상
  if (mapMesh) {
    const wallColor = isDarkMode ? 0x505060 : 0x64748b
    mapMesh.material.color.setHex(wallColor)
  }
})

onUnmounted(() => { 
  if (timeInterval) clearInterval(timeInterval)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (renderer) {
    renderer.dispose()
    if (mapContainer3D.value?.contains(renderer.domElement)) {
      mapContainer3D.value.removeChild(renderer.domElement)
    }
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.live-view { display: flex; flex-direction: column; gap: 16px; width: 100%; height: auto; padding: 16px; box-sizing: border-box; padding-bottom: 20px; }
.live-item { display: flex; flex-direction: column; gap: 16px; }
.panel { background: var(--glass-panel); backdrop-filter: blur(var(--blur-amount)); border: 1px solid var(--glass-border); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.12); transition: all 0.3s; min-height: 280px; height: auto; }
.scan-panel, .status-panel { min-height: 200px; }
@media (min-width: 768px) { .live-view { display: grid; grid-template-columns: 1fr 1fr; align-items: stretch; padding-bottom: 20px; } .live-item { display: flex; flex-direction: column; } .item-video { grid-column: 1; } .item-map { grid-column: 2; } .item-right { grid-column: 1 / -1; flex-direction: row; gap: 16px; } .scan-panel, .status-panel { flex: 1; } .item-video .panel, .item-map .panel { height: 100%; } }
@media (min-width: 1280px) { .live-view { display: grid; grid-template-columns: 1fr 1fr 340px; height: 100%; align-items: stretch; padding-bottom: 20px; } .live-item { height: 100%; min-height: 0; } .item-video { grid-column: 1; } .item-map { grid-column: 2; } .item-right { grid-column: 3; flex-direction: column; height: 100%; gap: 16px; } .item-video .panel, .item-map .panel { height: 100% !important; flex: 1; min-height: 400px; } .item-right .scan-panel { flex: 1; min-height: 0; } .item-right .status-panel { flex: 0 0 auto; height: auto; } }
.panel:hover { border-color: rgba(255,255,255,0.2); } .video-panel, .map-panel { background: var(--video-panel-bg); } .panel-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-bottom: 1px solid var(--glass-border); flex-shrink: 0; background: rgba(255,255,255,0.02); gap: 8px; } .panel-title { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; } .panel-body { flex: 1; padding: 12px; min-height: 0; overflow: auto; position: relative; } .scan-body { padding: 12px; } .status-body { padding: 0; display: flex; flex-direction: column; overflow: visible !important; height: auto !important; } .video-container { display: flex; flex-direction: column; height: 100%; background: var(--video-container-bg); position: relative; justify-content: center; } .video-feed { position: relative; background-color: var(--video-feed-bg); width: 100%; aspect-ratio: 16/9; max-height: 60vh; margin: auto; overflow: hidden; display: flex; align-items: center; justify-content: center; border-top: 1px solid var(--video-feed-border); border-bottom: 1px solid var(--video-feed-border); } .video-stream { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; background: var(--video-feed-bg); z-index: 1; } .video-body { display: flex; flex-direction: column; padding: 0; background: var(--video-container-bg); } .status-list { display: flex; flex-direction: column; flex: 1; } .status-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--glass-border); flex: 1; min-height: 50px; } .status-row:last-child { border-bottom: none; } .status-label { font-size: 12px; font-weight: 600; color: var(--text-muted); } .status-value { font-size: 18px; font-weight: 800; font-family: var(--font-family-mono); color: var(--text-primary); } .status-value small { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-left: 2px; } .text-error { color: var(--color-error); } .header-controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; } .cam-label { display: flex; align-items: center; gap: 6px; font-size: 11px; font-family: var(--font-family-mono); font-weight: 700; color: var(--color-primary); padding: 4px 10px; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 4px; white-space: nowrap; } .cam-dot { width: 6px; height: 6px; border-radius: 50%; background-color: var(--color-primary); box-shadow: 0 0 6px var(--color-primary); } .video-overlay { position: absolute; inset: 0; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; pointer-events: none; z-index: 10; background: radial-gradient(circle at center, transparent 60%, rgba(0,0,0,0.3) 100%); } .overlay-top, .overlay-bottom { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; } .record-indicator { display: flex; align-items: center; gap: 5px; padding: 3px 8px; background: rgba(239,68,68,0.8); border-radius: 3px; font-size: 10px; font-weight: 800; color: white; } .record-dot { width: 5px; height: 5px; background-color: white; border-radius: 50%; animation: blink 1s infinite; } @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } } .timestamp { padding: 3px 8px; background: var(--overlay-darker); border: 1px solid var(--glass-border); border-radius: 3px; font-size: 11px; color: var(--color-primary); font-weight: 700; } .resolution, .fps { padding: 2px 6px; background: var(--overlay-darker); border-radius: 3px; font-size: 9px; font-family: var(--font-family-mono); color: var(--text-muted); } .video-corners .corner { position: absolute; width: 28px; height: 28px; border: 2px solid var(--glass-border); z-index: 5; } .corner.top-left { top: 10px; left: 10px; border-right: none; border-bottom: none; } .corner.top-right { top: 10px; right: 10px; border-left: none; border-bottom: none; } .corner.bottom-left { bottom: 10px; left: 10px; border-right: none; border-top: none; } .corner.bottom-right { bottom: 10px; right: 10px; border-left: none; border-top: none; } .video-controls { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: var(--glass-header); border-top: 1px solid var(--glass-border); flex-shrink: 0; } .control-group { display: flex; align-items: center; gap: 6px; } .control-btn { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: var(--overlay-lighter); border: 1px solid var(--glass-border); border-radius: 6px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; } .control-btn:hover { background: var(--overlay-light); color: var(--text-primary); } .status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 700; } .badge-success { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); } .status-dot { width: 5px; height: 5px; border-radius: 50%; } .status-dot.online { background-color: var(--color-success); box-shadow: 0 0 6px var(--color-success); animation: pulse-status 2s infinite; } @keyframes pulse-status { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } } .live-indicator { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 3px; font-size: 9px; font-weight: 800; color: var(--color-error); } .live-indicator::before { content: ''; width: 4px; height: 4px; background-color: var(--color-error); border-radius: 50%; animation: blink 1.5s infinite; } .btn-scan { display: flex; align-items: center; gap: 5px; padding: 5px 12px; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); border: none; border-radius: 5px; color: white; font-size: 11px; font-weight: 700; cursor: pointer; } .btn-scan:disabled { opacity: 0.6; cursor: not-allowed; } .scan-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 16px; color: var(--text-muted); text-align: center; gap: 6px; background: var(--overlay-light); border-radius: 6px; border: 1px dashed var(--glass-border); font-size: 12px; } .scan-empty svg { opacity: 0.3; } .scan-empty-sub { font-size: 10px; opacity: 0.7; } .scan-info { display: flex; flex-direction: column; gap: 8px; } .scan-main { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 8px; border-bottom: 1px solid var(--glass-border); gap: 8px; } .scan-label { font-size: 8px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 2px; } .scan-value { font-size: 14px; font-weight: 800; color: var(--text-primary); font-family: var(--font-family-mono); } .scan-status { padding: 3px 8px; border-radius: 3px; font-size: 9px; font-weight: 700; text-transform: uppercase; } .scan-status.status-ready { background: var(--overlay-light); color: var(--text-muted); border: 1px solid var(--glass-border); } .scan-status.status-moving { background: rgba(245,158,11,0.1); color: var(--color-warning); border: 1px solid rgba(245,158,11,0.3); } .scan-status.status-completed { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); } .scan-status.status-error { background: rgba(239,68,68,0.1); color: var(--color-error); border: 1px solid rgba(239,68,68,0.3); } .scan-detail { display: flex; flex-direction: column; gap: 4px; } .detail-item { display: flex; justify-content: space-between; align-items: center; padding: 6px 8px; background: var(--overlay-light); border-radius: 4px; } .detail-label { font-size: 10px; color: var(--text-muted); } .detail-value { font-size: 11px; font-weight: 600; color: var(--text-primary); } .recognized-region { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid rgba(99,102,241,0.3); border-radius: 6px; margin-top: 4px; } .region-label { font-size: 10px; font-weight: 700; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.05em; } .region-value { font-size: 11px; font-weight: 700; color: var(--text-primary); } .region-value.region-pending { color: var(--text-muted); font-style: italic; } .vehicle-status-badge { padding: 3px 8px; border-radius: 3px; font-size: 9px; font-weight: 700; text-transform: uppercase; } .vehicle-status-badge.auto { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); } .vehicle-status-badge.manual { background: rgba(245,158,11,0.1); color: var(--color-warning); border: 1px solid rgba(245,158,11,0.3); } .scan-actions { margin-top: 8px; } .btn-action { display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; padding: 10px; border: none; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s; } .btn-start { background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); color: white; } .btn-start:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); } .btn-complete { background: linear-gradient(135deg, var(--color-success), #059669); color: white; } .btn-complete:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); } .map-body { padding: 0; overflow: hidden; } .map-container-3d { position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--map-container-bg); } .map-container-3d canvas { display: block; width: 100% !important; height: 100% !important; } .map-overlay { position: absolute; inset: 0; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; pointer-events: none; z-index: 10; } .overlay-top-map, .overlay-bottom-map { display: flex; justify-content: space-between; align-items: center; } .coord-display { display: flex; align-items: center; gap: 8px; padding: 6px 10px; background: var(--overlay-darker); border: 1px solid var(--glass-border); border-radius: 6px; backdrop-filter: blur(8px); } .coord-label { font-size: 10px; font-weight: 700; color: var(--text-muted); } .coord-value { font-size: 12px; font-weight: 700; font-family: var(--font-family-mono); color: var(--color-primary); } .zoom-level { padding: 4px 8px; background: var(--overlay-darker); border: 1px solid var(--glass-border); border-radius: 4px; font-size: 10px; font-weight: 700; font-family: var(--font-family-mono); color: var(--text-muted); backdrop-filter: blur(8px); } .zoom-level.slam-label { color: #10b981; } .btn-zoom, .btn-reset { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: var(--overlay-lighter); border: 1px solid var(--glass-border); border-radius: 6px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; } .btn-zoom:hover, .btn-reset:hover { background: var(--overlay-light); color: var(--text-primary); }

/* 라이브 스트림 플레이스홀더 및 재연결 버튼 스타일 */
.video-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; color: var(--text-muted); text-align: center; padding: 20px; width: 100%; height: 100%; }
.placeholder-icon { opacity: 0.3; }
.placeholder-text { font-size: 14px; font-weight: 600; }
.placeholder-sub { font-size: 11px; opacity: 0.6; }
.btn-retry { margin-top: 8px; padding: 8px 16px; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); border: none; border-radius: 6px; color: white; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-retry:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
.badge-error { background: rgba(239,68,68,0.1); color: var(--color-error); border: 1px solid rgba(239,68,68,0.3); }
.status-dot.offline { background-color: var(--color-error); box-shadow: 0 0 6px var(--color-error); }

/* RC카 연결 상태 배지 스타일 */
.vehicle-connect-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-right: 8px; }
.vehicle-connect-badge.connected { background: rgba(16,185,129,0.1); color: var(--color-success); border: 1px solid rgba(16,185,129,0.3); }
.vehicle-connect-badge.disconnected { background: rgba(107,114,128,0.1); color: var(--text-muted); border: 1px solid var(--glass-border); }
.vehicle-dot { width: 5px; height: 5px; border-radius: 50%; }
.vehicle-connect-badge.connected .vehicle-dot { background-color: var(--color-success); box-shadow: 0 0 6px var(--color-success); animation: pulse-status 2s infinite; }
.vehicle-connect-badge.disconnected .vehicle-dot { background-color: var(--text-muted); }
</style>