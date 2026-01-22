/**
 * 대시보드 데이터 관리 Composable
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { fetchDashboardStats, fetchWaybills, fetchDailyStats, fetchAlerts, getExportUrl } from '../api'
import { STATUS_MAP, STATUS_PRIORITY, CITIES, CHART_COLORS, POLLING_INTERVALS } from '../constants'
import { getToday } from '../utils/date'

export function useDashboard() {
  // 날짜 설정
  const maxDate = ref(getToday())
  const selectedDate = ref(getToday())

  // 반응형 데이터
  const chartSeries = ref([])
  const logisticsData = ref([])
  const latestScan = ref(null)
  const chartMax = ref(10)
  const isLoading = ref(false)
  const error = ref(null)

  // 추가 통계 데이터
  const dailyStats = ref(null)
  const alerts = ref([])
  const todaySummary = ref({
    total: 0,
    completed: 0,
    error: 0,
    avgProcessTime: null,
    successRate: 0
  })

  // 필터
  const filterRegion = ref('전체')
  const filterStatus = ref('전체')

  // 폴링 인터벌
  let refreshInterval = null

  /**
   * 대시보드 데이터 로드
   */
  const loadData = async () => {
    isLoading.value = true
    error.value = null

    try {
      // 구역별 통계, 운송장 목록, 일별 통계, 알림을 병렬로 호출
      const [statsRes, waybillsRes, dailyRes, alertsRes] = await Promise.all([
        fetchDashboardStats(selectedDate.value),
        fetchWaybills({ date: selectedDate.value, size: 100 }),
        fetchDailyStats(selectedDate.value, selectedDate.value),
        fetchAlerts({ resolved: false, size: 50 })
      ])

      // 구역별 통계 처리
      const regionStats = statsRes.data.data || []
      let totalDone = 0
      let totalLeft = 0
      let totalError = 0
      let totalAll = 0
      const finishedArr = []
      const pendingArr = []

      CITIES.forEach(city => {
        const cityData = regionStats.find(r => r.region_name === city) || {
          completed: 0,
          ready: 0,
          moving: 0,
          error: 0
        }
        const done = cityData.completed || 0
        const left = (cityData.ready || 0) + (cityData.moving || 0)
        const err = cityData.error || 0

        finishedArr.push({ x: city, y: done, fillColor: CHART_COLORS.completed })
        pendingArr.push({ x: city, y: left + err, fillColor: CHART_COLORS.pending })

        totalDone += done
        totalLeft += left
        totalError += err
        totalAll += done + left + err
      })

      // 전체 데이터 추가 (맨 앞)
      finishedArr.unshift({ x: '전체', y: totalDone, fillColor: CHART_COLORS.totalCompleted })
      pendingArr.unshift({ x: '전체', y: totalLeft + totalError, fillColor: CHART_COLORS.pending })

      // Y축 최대값 계산
      const allValues = [...finishedArr.map(d => d.y), ...pendingArr.map(d => d.y)]
      const maxVal = Math.max(...allValues)
      chartMax.value = maxVal > 0 ? maxVal : 5

      // 차트 시리즈 설정
      chartSeries.value = [
        { name: '완료 건수', data: finishedArr },
        { name: '남은 건수', data: pendingArr }
      ]

      // 일별 통계 처리
      const dailyData = dailyRes.data.data?.[0] || null
      dailyStats.value = dailyData
      
      // 오늘 요약 정보 업데이트
      todaySummary.value = {
        total: totalAll,
        completed: totalDone,
        error: totalError,
        avgProcessTime: dailyData?.avg_process_time_sec || null,
        successRate: totalAll > 0 ? Math.round((totalDone / totalAll) * 100) : 0
      }

      // 알림 데이터
      alerts.value = alertsRes.data.data?.items || alertsRes.data.data || []

      // 운송장 목록 처리
      const waybillItems = waybillsRes.data.data?.items || []
      logisticsData.value = waybillItems.map(item => ({
        id: item.tracking_number,
        waybillId: item.waybill_id,
        target: item.destination || '-',
        status: STATUS_MAP[item.status] || item.status,
        rawStatus: item.status,
        dateTime: item.completed_at || item.created_at || '',
        processTime: item.process_time_sec || null,
        confidenceScore: item.confidence_score || null
      }))

      // 최근 인식 정보 (실제 데이터 활용)
      if (waybillItems.length > 0) {
        const recentItem = waybillItems[0]
        latestScan.value = {
          waybillId: recentItem.waybill_id,
          destination: recentItem.destination || '-',
          matchRate: recentItem.confidence_score 
            ? `${recentItem.confidence_score.toFixed(1)}%` 
            : '-',
          camId: 'CAM:01',
          waybill: recentItem.tracking_number,
          status: recentItem.status,
          processTime: recentItem.process_time_sec,
          scannedAt: recentItem.created_at
        }
      } else {
        latestScan.value = null
      }
    } catch (err) {
      console.error('데이터 로드 실패:', err)
      error.value = err.message || '데이터를 불러오는데 실패했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 엑셀 다운로드
   */
  const downloadExcel = () => {
    const url = getExportUrl(selectedDate.value)
    window.open(url, '_blank')
  }

  /**
   * 필터링된 물류 데이터 (computed)
   */
  const filteredLogisticsData = computed(() => {
    const filtered = logisticsData.value.filter(item => {
      const regionMatch = filterRegion.value === '전체' || item.target === filterRegion.value
      const statusMatch = filterStatus.value === '전체' || item.status === filterStatus.value
      return regionMatch && statusMatch
    })

    // 상태 우선순위 및 시간순 정렬
    return filtered.sort((a, b) => {
      const priorityA = STATUS_PRIORITY[a.status] || 99
      const priorityB = STATUS_PRIORITY[b.status] || 99

      if (priorityA !== priorityB) return priorityA - priorityB
      if (a.dateTime < b.dateTime) return 1
      if (a.dateTime > b.dateTime) return -1
      return 0
    })
  })

  /**
   * 폴링 시작
   */
  const startPolling = () => {
    stopPolling()
    refreshInterval = setInterval(loadData, POLLING_INTERVALS.dashboard)
  }

  /**
   * 폴링 중지
   */
  const stopPolling = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }

  // 날짜 변경 감시
  watch(selectedDate, () => {
    loadData()
  })

  // 컴포넌트 마운트 시 초기화
  onMounted(() => {
    loadData()
    startPolling()
  })

  // 컴포넌트 언마운트 시 정리
  onUnmounted(() => {
    stopPolling()
  })

  return {
    // 상태
    maxDate,
    selectedDate,
    chartSeries,
    chartMax,
    logisticsData,
    filteredLogisticsData,
    latestScan,
    isLoading,
    error,

    // 추가 통계
    dailyStats,
    alerts,
    todaySummary,

    // 필터
    filterRegion,
    filterStatus,

    // 메서드
    loadData,
    startPolling,
    stopPolling,
    downloadExcel
  }
}
