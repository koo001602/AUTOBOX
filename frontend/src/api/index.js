import axios from 'axios'

// 백엔드 주소 설정
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 1. 대시보드 통계 데이터 가져오기
export const fetchDashboardStats = (dateStr) => {
  return apiClient.get('/logistics/stats', {
    params: { date: dateStr }
  })
}

// 2. 특정 기기 상태 가져오기
export const fetchDeviceStatus = (deviceId) => {
  return apiClient.get(`/device/status/${deviceId}`)
}