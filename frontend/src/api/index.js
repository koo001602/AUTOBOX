import axios from 'axios'

// 백엔드 주소 설정 (환경변수로 관리 - 배포 환경 대응)
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 1. 대시보드 통계 데이터 가져오기 (구역별 현황)
export const fetchDashboardStats = (dateStr) => {
  return apiClient.get('/stats/regions', {
    params: { date: dateStr }
  })
}

// 2. 일별 처리 통계 가져오기
export const fetchDailyStats = (startDate, endDate) => {
  return apiClient.get('/stats/daily', {
    params: { start_date: startDate, end_date: endDate }
  })
}

// 3. 시스템 상태 가져오기
export const fetchSystemStatus = () => {
  return apiClient.get('/system/status')
}

// 4. 운송장 목록 조회
export const fetchWaybills = (params = {}) => {
  return apiClient.get('/waybills', { params })
}

// 5. 알림 목록 조회
export const fetchAlerts = (params = {}) => {
  return apiClient.get('/alerts', { params })
}

// 6. 구역 목록 조회
export const fetchRegions = () => {
  return apiClient.get('/regions')
}

// 7. 카메라 목록 조회
export const fetchCameras = () => {
  return apiClient.get('/cameras')
}

// API 클라이언트 내보내기 (커스텀 요청용)
export default apiClient