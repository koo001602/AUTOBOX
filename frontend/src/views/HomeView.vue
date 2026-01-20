<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { fetchDashboardStats } from '../api'

// 1. 날짜 설정
const getToday = () => {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  const today = new Date(now - offset);
  return today.toISOString().split('T')[0];
}
const maxDate = ref(getToday()) 
const selectedDate = ref('2026-01-19') 

// 2. 반응형 데이터
const chartSeries = ref([])
const logisticsData = ref([])
const latestScan = ref(null)
const chartMax = ref(10)
let refreshInterval = null

// 필터
const filterRegion = ref('전체')
const filterStatus = ref('전체')

// 3. 데이터 로드 함수
const loadData = async () => {
  try {
    const res = await fetchDashboardStats(selectedDate.value)
    const { summary, logs } = res.data

    const cities = ['서울', '부산', '광주', '대전', '대구']
    let totalDone = 0
    let totalLeft = 0
    const finishedArr = [] 
    const pendingArr = [] 

    cities.forEach(city => {
      const cityData = summary[city] || { done: 0, left: 0 }
      finishedArr.push({ x: city, y: cityData.done, fillColor: '#3b82f6' })
      pendingArr.push({ x: city, y: cityData.left, fillColor: '#475569' })
      totalDone += cityData.done
      totalLeft += cityData.left
    })

    finishedArr.unshift({ x: '전체', y: totalDone, fillColor: '#10b981' })
    pendingArr.unshift({ x: '전체', y: totalLeft, fillColor: '#475569' })

    const allValues = [...finishedArr.map(d => d.y), ...pendingArr.map(d => d.y)]
    const maxVal = Math.max(...allValues)
    chartMax.value = maxVal > 0 ? maxVal : 5

    chartSeries.value = [
      { name: '완료 건수', data: finishedArr },
      { name: '남은 건수', data: pendingArr }
    ]

    logisticsData.value = logs

    if (logs.length > 0) {
      const recentItem = logs[0]
      latestScan.value = {
        destination: recentItem.target,
        matchRate: '99.8%',
        camId: 'CAM:01',
        waybill: recentItem.id,
        category: 'General', 
        weight: 'N/A',
        priority: 'Normal'
      }
    } else {
      latestScan.value = null
    }

  } catch (error) {
    console.error("데이터 로드 실패:", error)
  }
}

const filteredLogisticsData = computed(() => {
  const filtered = logisticsData.value.filter(item => {
    const regionMatch = filterRegion.value === '전체' || item.target === filterRegion.value
    const statusMatch = filterStatus.value === '전체' || item.status === filterStatus.value
    return regionMatch && statusMatch
  })

  return filtered.sort((a, b) => {
    const priorityMap = { '이동 중': 1, '대기 중': 2, '완료': 3, '오류': 4 }
    const priorityA = priorityMap[a.status] || 99
    const priorityB = priorityMap[b.status] || 99

    if (priorityA !== priorityB) return priorityA - priorityB
    if (a.dateTime < b.dateTime) return 1
    if (a.dateTime > b.dateTime) return -1
    return 0
  })
})

const chartOptions = computed(() => ({
  chart: { 
    type: 'bar', 
    stacked: false, 
    toolbar: { show: false }, 
    background: 'transparent', 
    fontFamily: 'inherit', 
    height: '100%',
    parentHeightOffset: 0,
    animations: { enabled: false }
  },
  plotOptions: { 
    bar: { 
      horizontal: false, 
      columnWidth: '55%', 
      borderRadius: 4, 
      borderRadiusApplication: 'end' 
    } 
  },
  dataLabels: { enabled: false },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: { 
    labels: { style: { colors: '#94a3b8', fontSize: '14px', fontWeight: 600 } }, 
    axisBorder: { show: false }, axisTicks: { show: false } 
  },
  yaxis: { 
    min: 0, 
    max: chartMax.value, 
    tickAmount: 5, 
    labels: { 
      style: { colors: '#94a3b8', fontSize: '12px' },
      formatter: (val) => val.toFixed(0),
      minWidth: 40,
      maxWidth: 40
    } 
  },
  grid: { 
    borderColor: '#1e293b', 
    strokeDashArray: 4, 
    xaxis: { lines: { show: false } },
    padding: { top: 10, right: 0, bottom: 0, left: 20 }
  },
  theme: { mode: 'dark' }, 
  tooltip: { theme: 'dark' }, 
  legend: { show: false }
}))

watch(selectedDate, () => {
  loadData()
})

onMounted(() => { 
  loadData() 
  refreshInterval = setInterval(loadData, 3000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<template>
  <div class="dashboard-wrapper">
    <div class="filter-bar">
      <div class="filter-group">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f8aff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
          <line x1="16" x2="16" y1="2" y2="6" />
          <line x1="8" x2="8" y1="2" y2="6" />
          <line x1="3" x2="21" y1="10" y2="10" />
        </svg>
        <span class="filter-label">날짜별 조회</span>
        <input type="date" v-model="selectedDate" :max="maxDate" class="date-input" />
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="left-col">
        <section class="panel chart-panel">
          <div class="panel-header">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18" /><path d="M18 17V9" /><path d="M13 17V5" /><path d="M8 17v-3" /></svg>
              물류 관리 전체 현황
            </h3>
            <div class="legend">
              <span class="dot green"></span> 전체 완료
              <span class="dot blue"></span> 지역 완료
              <span class="dot grey"></span> 미완료
            </div>
          </div>
          <div class="chart-container">
            <VueApexCharts type="bar" height="100%" :options="chartOptions" :series="chartSeries" />
          </div>
        </section>

        <section class="panel table-panel">
          <div class="panel-header">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" /><path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" /><line x1="7" x2="17" y1="12" y2="12" /></svg>
              지역별 물류 세부 내용
            </h3>
            
            <div class="table-controls">
              <select v-model="filterRegion" class="custom-select">
                <option value="전체">지역: 전체</option>
                <option value="서울">서울</option>
                <option value="부산">부산</option>
                <option value="대구">대구</option>
                <option value="광주">광주</option>
                <option value="대전">대전</option>
              </select>

              <select v-model="filterStatus" class="custom-select">
                <option value="전체">상태: 전체</option>
                <option value="완료">완료</option>
                <option value="이동 중">이동 중</option>
                <option value="대기 중">대기 중</option>
              </select>

              <button class="btn-small" @click="loadData">↻</button>
            </div>
          </div>

          <div class="table-wrapper custom-scrollbar">
            <table class="dark-table">
              <thead>
                <tr>
                  <th>운송장 번호</th>
                  <th>목표 분류 지역</th>
                  <th>현재 상태</th>
                  <th class="text-center">완료 시간</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in filteredLogisticsData" :key="item.id">
                  <td class="code">{{ item.id }}</td>
                  <td><span class="dot-sm">●</span> {{ item.target }}</td>
                  <td>
                    <span class="status-badge" 
                      :class="{
                        'done': item.status === '완료', 
                        'moving': item.status === '이동 중', 
                        'wait': item.status === '대기 중',
                        'error': item.status === '오류'
                      }">
                      {{ item.status }}
                    </span>
                  </td>
                  <td class="time text-center">
                    <span v-if="item.status === '완료'">{{ item.dateTime.split(' ')[1] }}</span>
                    <span v-else style="color: #64748b;">-</span>
                  </td>
                </tr>
                
                <tr v-if="filteredLogisticsData.length === 0">
                  <td colspan="4" class="text-center" style="padding: 20px; color: #64748b;">
                    {{ logisticsData.length === 0 ? '해당 날짜의 데이터가 없습니다.' : '조건에 맞는 데이터가 없습니다.' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <div class="right-col">
        <section class="panel camera-panel">
          <div class="panel-header">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 8-6 4 6 4V8Z" /><rect width="14" height="12" x="2" y="6" rx="2" ry="2" /></svg>
              운송장 캡쳐
            </h3>
            <span class="live-badge">LIVE</span>
          </div>
          <div class="camera-view">
            <div class="overlay-bracket top-left"></div><div class="overlay-bracket top-right"></div><div class="overlay-bracket bottom-left"></div><div class="overlay-bracket bottom-right"></div>
            <div class="scan-line-anim"></div>
            <div class="scan-box">
              <div class="icon-circle">
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15" /><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" /><path d="m3.3 7 8.7 5 8.7-5" /><path d="M12 22v-9" /></svg>
              </div>
              <p>Scanning...</p>
            </div>
          </div>
        </section>

        <section class="panel info-panel">
          <div class="panel-header">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><path d="m9 12 2 2 4-4" /></svg>
              최근 인식 정보
            </h3>
          </div>
          <div class="info-content" v-if="latestScan">
            <div class="info-body custom-scrollbar">
              <div class="detection-card">
                <span class="sub-label">DETECTED DESTINATION</span>
                <div class="dest-text">{{ latestScan.destination }}</div>
                <div class="match-rate">
                  <span class="tag green">{{ latestScan.matchRate }} Match</span>
                  <span class="tag dark">{{ latestScan.camId }}</span>
                </div>
              </div>
              <div class="detail-row">
                <div class="detail-box"><span class="lbl">WAYBILL NO.</span><span class="val">{{ latestScan.waybill }}</span></div>
                <div class="detail-box"><span class="lbl">CATEGORY</span><span class="val">{{ latestScan.category }}</span></div>
              </div>
              <div class="detail-row">
                <div class="detail-box"><span class="lbl">WEIGHT</span><span class="val">{{ latestScan.weight }}</span></div>
                <div class="detail-box"><span class="lbl">PRIORITY</span><span class="val">{{ latestScan.priority }}</span></div>
              </div>
            </div>
          </div>
          <div class="info-content" v-else>
             <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #64748b;">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 10px; opacity: 0.5;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <p>데이터 대기 중...</p>
             </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper { 
  display: flex; 
  flex-direction: column; 
  width: 100%; 
  height: 100%;
  box-sizing: border-box; 
  overflow: hidden; /* 전체 페이지 스크롤 방지 */
  padding: 20px; 
  gap: 16px; 
}

.filter-bar { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  background-color: var(--bg-panel); 
  padding: 12px 24px; 
  border-radius: 12px; 
  border: 1px solid #1e293b; 
  flex-shrink: 0;
}

/* 그리드 설정: 남은 높이를 모두 차지 */
.dashboard-grid { 
  display: grid; 
  grid-template-columns: 2fr 1fr; 
  gap: 20px; 
  width: 100%; 
  flex: 1;
  min-height: 0;
  box-sizing: border-box; 
  overflow: hidden; 
}

/* 컬럼 설정 */
.left-col, .right-col { 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
  height: 100%;
  min-width: 0; 
  overflow: hidden;
}

/* 1. 상단 패널: 400px 고정 */
.chart-panel { flex: 0 0 400px; height: 400px; }
.camera-panel { flex: 0 0 400px; height: 400px; padding: 4px; }

/* 2. 하단 패널: 남은 공간 채우기 */
.table-panel { 
  flex: 1; 
  min-height: 0; /* 내용이 많아도 패널이 늘어나지 않게 함 */
  display: flex; 
  flex-direction: column;
  overflow: hidden; 
} 
.info-panel { 
  flex: 1; 
  min-height: 0; 
  display: flex; 
  flex-direction: column;
  overflow: hidden;
}

/* 패널 공통 스타일 */
.panel { background-color: var(--bg-panel); border-radius: 16px; padding: 24px; display: flex; flex-direction: column; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid #1e293b; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-shrink: 0; }
.panel-header h3 { margin: 0; font-size: 1.2rem; color: #fff; display: flex; align-items: center; gap: 10px; font-weight: 700; }

/* 차트 컨테이너 */
.chart-container { flex: 1; min-height: 0; width: 100%; position: relative; }

/* 테이블 내부 스크롤 처리 */
.table-wrapper { 
  flex: 1; /* 부모의 남은 높이 차지 */
  overflow-y: auto; /* 세로 스크롤 생성 */
  margin-top: 10px; 
}

/* 정보 패널 내부 스크롤 처리 */
.info-content { 
  display: flex; 
  flex-direction: column; 
  flex: 1; 
  min-height: 0; 
  justify-content: flex-start; /* 상단 정렬 */
  overflow: hidden; 
}
.info-body { 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
  width: 100%; 
  overflow-y: auto; /* 내용 많으면 스크롤 */
  padding-right: 4px; 
}

.filter-group { display: flex; align-items: center; gap: 12px; }
.filter-label { font-weight: 700; color: #fff; font-size: 1rem; }
.date-input { background-color: #0b1120; border: 1px solid #334155; color: white; padding: 6px 12px; border-radius: 6px; font-family: inherit; font-size: 0.95rem; outline: none; cursor: pointer; margin-left: 8px; }
.date-input:focus { border-color: #3b82f6; }
.legend { font-size: 0.9rem; color: var(--text-sub); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; margin-left: 10px; }
.dot.blue { background-color: #3b82f6; }
.dot.green { background-color: #10b981; }
.dot.grey { background-color: #475569; }
.dark-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 1rem; }
.dark-table th { text-align: left; color: var(--text-sub); padding: 16px 20px; border-bottom: 1px solid #334155; font-weight: 600; position: sticky; top: 0; background-color: var(--bg-panel); z-index: 10; white-space: nowrap; }
.dark-table th.text-center { text-align: center; }
.dark-table td { padding: 16px 20px; border-bottom: 1px solid #1e293b; color: #cbd5e1; white-space: nowrap; }
.text-center { text-align: center; }
.table-controls { display: flex; align-items: center; gap: 10px; }
.custom-select { background-color: #0b1120; border: 1px solid #334155; color: #cbd5e1; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; outline: none; cursor: pointer; }
.custom-select:hover { border-color: #4f8aff; }
.btn-small { background: #1e293b; border: none; color: #94a3b8; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; min-width: 32px; }
.btn-small:hover { color: white; background: #334155; }
.code { color: #cbd5e1; font-family: monospace; }
.status-badge { padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 500; display: inline-block; border: 1px solid transparent; }
.status-badge.done { background-color: rgba(16, 185, 129, 0.05); color: #34d399; border-color: rgba(16, 185, 129, 0.2); }
.status-badge.moving { background-color: rgba(59, 130, 246, 0.05); color: #60a5fa; border-color: rgba(59, 130, 246, 0.2); }
.status-badge.wait { background-color: rgba(100, 116, 139, 0.05); color: #94a3b8; border-color: rgba(100, 116, 139, 0.2); }
.status-badge.error { background-color: rgba(239, 68, 68, 0.05); color: #f87171; border-color: rgba(239, 68, 68, 0.2); }
.live-badge { background-color: #ef4444; color: white; padding: 4px 8px; font-size: 0.75rem; border-radius: 4px; font-weight: bold; animation: pulse 2s infinite; }
.camera-view { flex: 1; background-color: #000; border-radius: 8px; position: relative; display: flex; justify-content: center; align-items: center; border: 1px solid #334155; overflow: hidden; min-height: 0; }
.overlay-bracket { position: absolute; width: 24px; height: 24px; border: 2px solid #3b82f6; z-index: 5; }
.top-left { top: 24px; left: 24px; border-right: none; border-bottom: none; }
.top-right { top: 24px; right: 24px; border-left: none; border-bottom: none; }
.bottom-left { bottom: 24px; left: 24px; border-right: none; border-top: none; }
.bottom-right { bottom: 24px; right: 24px; border-left: none; border-top: none; }
.scan-box { text-align: center; color: #64748b; z-index: 2; transform: scale(1.2); }
.icon-circle { width: 120px; height: 120px; border: 2px dashed #475569; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; background-color: rgba(15, 23, 42, 0.5); }
.scan-box p { font-size: 1rem; margin: 0; font-family: monospace; }
.scan-line-anim { position: absolute; top: 0; left: 0; width: 100%; height: 2px; background-color: #3b82f6; box-shadow: 0 0 20px rgba(59,130,246,0.8); animation: scan 2.5s linear infinite; opacity: 0.5; z-index: 1; }
.detection-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 16px; text-align: center; border: 1px solid #334155; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2); }
.sub-label { color: #94a3b8; font-size: 0.85rem; letter-spacing: 0.1em; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 8px; }
.dest-text { font-size: 3.5rem; font-weight: 900; color: white; margin: 8px 0; letter-spacing: -0.05em; drop-shadow: 0 4px 6px rgba(0,0,0,0.5); }
.match-rate { display: flex; justify-content: center; gap: 12px; margin-top: 12px; }
.tag { font-size: 0.9rem; padding: 6px 12px; border-radius: 6px; font-family: monospace; border: 1px solid; }
.tag.green { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border-color: rgba(16, 185, 129, 0.2); }
.tag.dark { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; border-color: rgba(59, 130, 246, 0.2); }
.detail-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.detail-box { background-color: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 20px; border-radius: 12px; }
.detail-box .lbl { display: block; font-size: 0.75rem; color: #64748b; margin-bottom: 6px; text-transform: uppercase; font-weight: 600; }
.detail-box .val { display: block; font-size: 1.1rem; font-weight: 700; color: white; font-family: monospace; }
@keyframes scan { 0% { top: 0%; opacity: 0.5; } 50% { opacity: 1; } 100% { top: 100%; opacity: 0.5; } }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #0f172a; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>