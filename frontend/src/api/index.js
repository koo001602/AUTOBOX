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

// 5. 운송장 상세 조회 (scan_logs 포함)
export const fetchWaybillDetail = (waybillId) => {
  return apiClient.get(`/waybills/${waybillId}`)
}

// 6. 알림 목록 조회
export const fetchAlerts = (params = {}) => {
  return apiClient.get('/alerts', { params })
}

// 7. 알림 해결 처리
export const resolveAlert = (alertId) => {
  return apiClient.patch(`/alerts/${alertId}/resolve`)
}

// 8. 구역 목록 조회
export const fetchRegions = () => {
  return apiClient.get('/regions')
}

// 9. 카메라 목록 조회
export const fetchCameras = () => {
  return apiClient.get('/cameras')
}

// 10. 최신 인식 정보 조회
export const fetchLatestRecognition = () => {
  return apiClient.get('/recognition/latest')
}

// 11. 운송장 스캔 시작 (새 운송장 생성)
export const startWaybillScan = (cameraId = 'cam-capture') => {
  return apiClient.post('/waybills/scan', { camera_id: cameraId })
}

// 12. OCR 인식 결과 저장
export const saveRecognitionResult = (waybillId, data) => {
  return apiClient.put(`/waybills/${waybillId}/recognition`, data)
}

// 13. 분류 시작
export const startSorting = (waybillId) => {
  return apiClient.put(`/waybills/${waybillId}/start-sorting`)
}

// 14. 분류 완료
export const completeSorting = (waybillId) => {
  return apiClient.put(`/waybills/${waybillId}/complete`)
}

// 11. 엑셀 다운로드 URL 생성
export const getExportUrl = (dateStr) => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'
  return `${baseUrl}/stats/export${dateStr ? `?date=${dateStr}` : ''}`
}

// API 클라이언트 내보내기 (커스텀 요청용)
export default apiClient