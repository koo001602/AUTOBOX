<script setup>
import { computed, ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { useDashboard } from '../composables'
import { getDashboardBarChartOptions } from '../config/chartOptions'
import { FILTER_OPTIONS } from '../constants'

// Composable 사용
const {
  maxDate,
  selectedDate,
  chartSeries,
  chartMax,
  filteredLogisticsData,
  logisticsData,
  latestScan,
  filterRegion,
  filterStatus,
  loadData,
  todaySummary,
  alerts,
  downloadExcel
} = useDashboard()

// 목표 박스 수 (Box Count)
const targetBoxCount = ref(1000)

// 차트 옵션 (chartMax 반응형 연동)
const chartOptions = computed(() => getDashboardBarChartOptions(chartMax.value))

// 미해결 알림 수
const unresolvedAlertCount = computed(() => alerts.value.length)

// 평균 처리 시간 포맷
const formatProcessTime = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}초`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}분 ${secs}초`
}
</script>

<template>
  <div class="dashboard">
    <!-- Header Bar -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="control-group">
          <label class="control-label">DATE</label>
          <input type="date" v-model="selectedDate" :max="maxDate" class="glass-input date-input" />
        </div>
        
        <div class="control-divider"></div>

        <div class="control-group">
          <label class="control-label">TARGET BOXES</label>
          <div class="input-wrapper">
             <input type="number" v-model="targetBoxCount" class="glass-input box-input" min="0" placeholder="0" />
             <span class="input-unit">EA</span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-icon" @click="downloadExcel" title="엑셀 다운로드">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" x2="12" y1="15" y2="3"/>
          </svg>
        </button>
        <button class="btn-icon" @click="loadData" title="새로고침">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
            <path d="M16 16h5v5"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m7.5 4.27 9 5.15" />
            <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ todaySummary.total }}</span>
          <span class="stat-label">총 처리량</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value success">{{ todaySummary.completed }}</span>
          <span class="stat-label">완료</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rate">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20v-6M6 20V10M18 20V4"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ todaySummary.successRate }}<small>%</small></span>
          <span class="stat-label">성공률</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon time">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ formatProcessTime(todaySummary.avgProcessTime) }}</span>
          <span class="stat-label">평균 처리 시간</span>
        </div>
      </div>

      <div class="stat-card" :class="{ 'has-error': todaySummary.error > 0 }">
        <div class="stat-icon error">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value error">{{ todaySummary.error }}</span>
          <span class="stat-label">오류</span>
        </div>
      </div>
    </div>

    <!-- Main Content: 3열 레이아웃 (차트 | 최근인식 | 테이블) -->
    <div class="main-content">
      <!-- 차트 -->
      <section class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 3v18h18" />
              <path d="M18 17V9" />
              <path d="M13 17V5" />
              <path d="M8 17v-3" />
            </svg>
            지역별 현황
          </h2>
          <div class="chart-legend">
            <span class="legend-item"><span class="legend-dot completed"></span>완료</span>
            <span class="legend-item"><span class="legend-dot pending"></span>미완료</span>
          </div>
        </div>
        <div class="panel-body chart-body">
          <VueApexCharts type="bar" height="100%" :options="chartOptions" :series="chartSeries" />
        </div>
      </section>

      <!-- 최근 인식 -->
      <section class="panel scan-panel" v-if="latestScan">
        <div class="panel-header">
          <h2 class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            최근 인식
          </h2>
          <span class="scan-status" :class="latestScan.status.toLowerCase()">{{ latestScan.status }}</span>
        </div>
        <div class="panel-body scan-body">
          <div class="scan-main">
            <span class="scan-dest-label">목적지</span>
            <span class="scan-dest-value">{{ latestScan.destination }}</span>
          </div>
          <div class="scan-info-grid">
            <div class="scan-info-item">
              <span class="info-label">운송장</span>
              <span class="info-value">{{ latestScan.waybill }}</span>
            </div>
            <div class="scan-info-item">
              <span class="info-label">신뢰도</span>
              <span class="info-value highlight">{{ latestScan.matchRate }}</span>
            </div>
            <div class="scan-info-item">
              <span class="info-label">처리시간</span>
              <span class="info-value">{{ formatProcessTime(latestScan.processTime) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 물류 목록 -->
      <section class="panel table-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--color-info)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2" />
              <path d="M17 3h2a2 2 0 0 1 2 2v2" />
              <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
              <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
            </svg>
            물류 목록
            <span class="record-badge">{{ filteredLogisticsData.length }}건</span>
          </h2>
          <div class="table-filters">
            <select v-model="filterRegion" class="filter-select">
              <option v-for="opt in FILTER_OPTIONS.regions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
            <select v-model="filterStatus" class="filter-select">
              <option v-for="opt in FILTER_OPTIONS.statuses" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>
        <div class="panel-body table-body">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>운송장 번호</th>
                  <th>지역</th>
                  <th>상태</th>
                  <th>완료 시간</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in filteredLogisticsData" :key="item.id" class="table-row">
                  <td class="cell-id">{{ item.waybillId }}</td>
                  <td class="cell-waybill">{{ item.id }}</td>
                  <td class="cell-region">
                    <span class="region-badge">{{ item.target }}</span>
                  </td>
                  <td class="cell-status">
                    <span class="status-badge" :class="{
                      'status-complete': item.status === '완료',
                      'status-moving': item.status === '이동 중',
                      'status-ready': item.status === '대기 중',
                      'status-error': item.status === '오류'
                    }">{{ item.status }}</span>
                  </td>
                  <td class="cell-time">
                    <span v-if="item.status === '완료'">{{ item.dateTime ? item.dateTime.split('T')[1]?.substring(0, 8) : '-' }}</span>
                    <span v-else class="text-muted">--:--:--</span>
                  </td>
                </tr>
                <tr v-if="filteredLogisticsData.length === 0">
                  <td colspan="5" class="empty-row">데이터 없음</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* =============================================
   미니멀 대시보드 스타일
   ============================================= */

.dashboard {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 20px;
  gap: 12px;
  overflow: hidden;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.date-input {
  padding: 8px 14px;
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 15px;
  font-family: var(--font-family-mono);
  cursor: pointer;
}

.date-input:focus {
  outline: none;
  border-color: var(--text-muted);
}

.header-right {
  display: flex;
  gap: 8px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.btn-icon:hover {
  background-color: var(--bg-elevated);
  color: var(--text-primary);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  flex-shrink: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.stat-card.has-error {
  border-left: 3px solid var(--color-error);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 20px;
  height: 20px;
}

.stat-icon.total { color: var(--text-muted); }
.stat-icon.success { color: var(--color-success); }
.stat-icon.rate { color: var(--color-primary); }
.stat-icon.time { color: var(--color-warning); }
.stat-icon.error { color: var(--color-error); }

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  color: var(--text-primary);
  line-height: 1;
}

.stat-value small {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
}

.stat-value.success { color: var(--color-success); }
.stat-value.error { color: var(--color-error); }

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

/* Main Content - 3열 레이아웃 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 260px 1.3fr;
  gap: 12px;
  flex: 1;
  min-height: 0;
}

/* Panels */
.panel {
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.panel-title svg {
  opacity: 0.7;
}

.panel-body {
  flex: 1;
  padding: 12px;
  min-height: 0;
  overflow: hidden;
}

/* Chart Panel */
.chart-panel {
  min-height: 0;
}

.chart-body {
  padding: 8px;
}

.chart-legend {
  display: flex;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.legend-dot.completed { background-color: var(--color-success); }
.legend-dot.pending { background-color: var(--text-muted); }

/* Scan Panel (최근 인식) */
.scan-panel {
  min-height: 0;
}

.scan-status {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.scan-status.completed {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.scan-status.moving {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.scan-status.ready {
  background-color: var(--bg-elevated);
  color: var(--text-muted);
}

.scan-status.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.scan-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
}

.scan-main {
  text-align: center;
  padding: 16px;
  background-color: var(--bg-elevated);
  border-radius: 6px;
}

.scan-dest-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.scan-dest-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.scan-info-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.scan-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
}

.info-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.info-value {
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-family-mono);
  color: var(--text-primary);
}

.info-value.highlight {
  color: var(--color-success);
}

/* Table Panel */
.table-panel {
  min-height: 0;
  overflow: hidden;
}

.record-badge {
  margin-left: 6px;
  padding: 2px 6px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  font-size: 11px;
  font-family: var(--font-family-mono);
  color: var(--text-muted);
  font-weight: 500;
}

.table-filters {
  display: flex;
  gap: 6px;
}

.filter-select {
  padding: 4px 10px;
  min-height: 32px;
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--text-muted);
}

.table-body {
  padding: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  position: sticky;
  top: 0;
  padding: 10px 12px;
  background-color: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  z-index: 10;
}

.table-row {
  transition: background-color 0.1s;
}

.table-row:hover {
  background-color: var(--bg-hover);
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  white-space: nowrap;
}

.cell-id {
  font-family: var(--font-family-mono);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 12px;
}

.cell-waybill {
  font-family: var(--font-family-mono);
  font-size: 12px;
  color: var(--text-primary);
}

.cell-time {
  font-family: var(--font-family-mono);
  font-size: 12px;
  color: var(--text-muted);
}

.text-muted {
  color: var(--text-muted);
}

.region-badge {
  font-weight: 500;
  font-size: 13px;
  color: var(--text-primary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.status-complete {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.status-moving {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.status-ready {
  background-color: var(--bg-elevated);
  color: var(--text-muted);
}

.status-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.empty-row {
  text-align: center;
  padding: 24px !important;
  color: var(--text-muted);
  font-size: 13px;
}

/* 태블릿 세로 모드 대응 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .chart-panel {
    grid-column: 1;
    grid-row: 1;
  }
  
  .scan-panel {
    grid-column: 2;
    grid-row: 1;
  }
  
  .table-panel {
    grid-column: 1 / -1;
    grid-row: 2;
  }
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
    gap: 10px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card:last-child {
    grid-column: span 2;
  }
  
  .main-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }
  
  .chart-panel,
  .scan-panel,
  .table-panel {
    grid-column: 1;
  }
}
</style>
