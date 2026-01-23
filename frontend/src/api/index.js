import axios from 'axios'
import {
  mockRegionStats,
  mockWaybills,
  mockDailyStats,
  mockAlerts,
  mockSystemStatus,
  mockCameras,
  mockRegions,
  mockLatestRecognition,
  mockWaybillDetail
} from './mockData'

// 목업 모드 확인 (환경변수 VITE_MOCK_MODE=true로 설정)
const isMockMode = import.meta.env.VITE_MOCK_MODE === 'true'

// 콘솔에 현재 모드 표시
if (isMockMode) {
  console.log('🎭 목업 모드로 실행 중입니다. 백엔드 연결 없이 샘플 데이터가 표시됩니다.')
}

// 백엔드 주소 설정 (환경변수로 관리 - 배포 환경 대응)
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 목업 응답 딜레이 (실제 API처럼 느끼도록)
const mockDelay = (data, delay = 200) => {
  return new Promise(resolve => setTimeout(() => resolve(data), delay))
}

// 1. 대시보드 통계 데이터 가져오기 (구역별 현황)
export const fetchDashboardStats = (dateStr) => {
  if (isMockMode) {
    return mockDelay(mockRegionStats)
  }
  return apiClient.get('/stats/regions', {
    params: { date: dateStr }
  })
}

// 2. 일별 처리 통계 가져오기
export const fetchDailyStats = (startDate, endDate) => {
  if (isMockMode) {
    return mockDelay(mockDailyStats)
  }
  return apiClient.get('/stats/daily', {
    params: { start_date: startDate, end_date: endDate }
  })
}

// 3. 시스템 상태 가져오기
export const fetchSystemStatus = () => {
  if (isMockMode) {
    // 목업에서 배터리 레벨을 랜덤하게 변동
    const mockData = { ...mockSystemStatus }
    mockData.data.data.battery_level = Math.min(100, Math.max(70, mockSystemStatus.data.data.battery_level + Math.floor(Math.random() * 5) - 2))
    mockData.data.data.last_updated = new Date().toISOString()
    return mockDelay(mockData)
  }
  return apiClient.get('/system/status')
}

// 4. 운송장 목록 조회
export const fetchWaybills = (params = {}) => {
  if (isMockMode) {
    return mockDelay(mockWaybills)
  }
  return apiClient.get('/waybills', { params })
}

// 5. 운송장 상세 조회 (scan_logs 포함)
export const fetchWaybillDetail = (waybillId) => {
  if (isMockMode) {
    return mockDelay(mockWaybillDetail)
  }
  return apiClient.get(`/waybills/${waybillId}`)
}

// 6. 알림 목록 조회
export const fetchAlerts = (params = {}) => {
  if (isMockMode) {
    return mockDelay(mockAlerts)
  }
  return apiClient.get('/alerts', { params })
}

// 7. 알림 해결 처리
export const resolveAlert = (alertId) => {
  if (isMockMode) {
    return mockDelay({ data: { success: true, message: '알림이 해결되었습니다.' } })
  }
  return apiClient.patch(`/alerts/${alertId}/resolve`)
}

// 8. 구역 목록 조회
export const fetchRegions = () => {
  if (isMockMode) {
    return mockDelay(mockRegions)
  }
  return apiClient.get('/regions')
}

// 9. 카메라 목록 조회
export const fetchCameras = () => {
  if (isMockMode) {
    return mockDelay(mockCameras)
  }
  return apiClient.get('/cameras')
}

// 10. 최신 인식 정보 조회
export const fetchLatestRecognition = () => {
  if (isMockMode) {
    return mockDelay(mockLatestRecognition)
  }
  return apiClient.get('/recognition/latest')
}

// 11. 운송장 스캔 시작 (새 운송장 생성)
export const startWaybillScan = (cameraId = 'cam-capture') => {
  if (isMockMode) {
    return mockDelay({
      data: {
        success: true,
        data: {
          waybill_id: `WB-MOCK-${Date.now()}`,
          status: 'SCANNING'
        }
      }
    })
  }
  return apiClient.post('/waybills/scan', { camera_id: cameraId })
}

// 12. OCR 인식 결과 저장
export const saveRecognitionResult = (waybillId, data) => {
  if (isMockMode) {
    return mockDelay({ data: { success: true, waybill_id: waybillId } })
  }
  return apiClient.put(`/waybills/${waybillId}/recognition`, data)
}

// 13. 분류 시작
export const startSorting = (waybillId) => {
  if (isMockMode) {
    return mockDelay({ data: { success: true, status: 'MOVING' } })
  }
  return apiClient.put(`/waybills/${waybillId}/start-sorting`)
}

// 14. 분류 완료
export const completeSorting = (waybillId) => {
  if (isMockMode) {
    return mockDelay({ data: { success: true, status: 'COMPLETED' } })
  }
  return apiClient.put(`/waybills/${waybillId}/complete`)
}

// 15. 엑셀 다운로드 URL 생성
export const getExportUrl = (dateStr) => {
  if (isMockMode) {
    console.log('🎭 목업 모드: 엑셀 다운로드는 실제 백엔드 연결 시 사용 가능합니다.')
    return '#'
  }
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'
  return `${baseUrl}/stats/export${dateStr ? `?date=${dateStr}` : ''}`
}

// 목업 모드 여부 내보내기 (UI에서 표시용)
export const getMockMode = () => isMockMode

// API 클라이언트 내보내기 (커스텀 요청용)
export default apiClient