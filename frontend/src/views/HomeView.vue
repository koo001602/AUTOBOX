<script setup>
import { computed } from 'vue'
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
    <!-- Control Bar -->
    <div class="control-bar">
      <div class="control-left">
        <div class="control-group">
          <label class="control-label">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
              <line x1="16" x2="16" y1="2" y2="6" />
              <line x1="8" x2="8" y1="2" y2="6" />
              <line x1="3" x2="21" y1="10" y2="10" />
            </svg>
            DATE
          </label>
          <input type="date" v-model="selectedDate" :max="maxDate" class="control-input" />
        </div>

        <div class="control-group">
          <label class="control-label">REGION</label>
          <select v-model="filterRegion" class="control-select">
            <option 
              v-for="option in FILTER_OPTIONS.regions" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>

        <div class="control-group">
          <label class="control-label">STATUS</label>
          <select v-model="filterStatus" class="control-select">
            <option 
              v-for="option in FILTER_OPTIONS.statuses" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="control-right">
        <button class="btn-export" @click="downloadExcel">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" x2="12" y1="15" y2="3"/>
          </svg>
          엑셀 다운로드
        </button>
        <button class="btn-refresh" @click="loadData">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
            <path d="M16 16h5v5"/>
          </svg>
          새로고침
        </button>
      </div>
    </div>

    <!-- Today Summary Stats -->
    <div class="summary-bar">
      <div class="summary-item">
        <div class="summary-icon total">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m7.5 4.27 9 5.15" />
            <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
          </svg>
        </div>
        <div class="summary-content">
          <span class="summary-label">총 처리량</span>
          <span class="summary-value">{{ todaySummary.total }}</span>
        </div>
      </div>

      <div class="summary-item">
        <div class="summary-icon success">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="summary-content">
          <span class="summary-label">완료</span>
          <span class="summary-value success">{{ todaySummary.completed }}</span>
        </div>
      </div>

      <div class="summary-item">
        <div class="summary-icon rate">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20v-6M6 20V10M18 20V4"/>
          </svg>
        </div>
        <div class="summary-content">
          <span class="summary-label">성공률</span>
          <span class="summary-value">{{ todaySummary.successRate }}%</span>
        </div>
      </div>

      <div class="summary-item">
        <div class="summary-icon time">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="summary-content">
          <span class="summary-label">평균 처리 시간</span>
          <span class="summary-value">{{ formatProcessTime(todaySummary.avgProcessTime) }}</span>
        </div>
      </div>

      <div class="summary-item">
        <div class="summary-icon error">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="summary-content">
          <span class="summary-label">오류</span>
          <span class="summary-value error">{{ todaySummary.error }}</span>
        </div>
      </div>

      <div class="summary-item" v-if="unresolvedAlertCount > 0">
        <div class="summary-icon alert">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
          </svg>
        </div>
        <div class="summary-content">
          <span class="summary-label">미해결 알림</span>
          <span class="summary-value alert">{{ unresolvedAlertCount }}</span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      <!-- Left Column: Chart + Table -->
      <div class="grid-left">
        <!-- Chart Panel -->
        <section class="panel chart-panel">
          <div class="panel-header">
            <div class="panel-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18" />
                <path d="M18 17V9" />
                <path d="M13 17V5" />
                <path d="M8 17v-3" />
              </svg>
              물류 현황 모니터
            </div>
            <div class="chart-legend">
              <span class="legend-item">
                <span class="legend-dot" style="background: var(--color-success);"></span>
                완료
              </span>
              <span class="legend-item">
                <span class="legend-dot" style="background: var(--color-primary);"></span>
                지역별
              </span>
              <span class="legend-item">
                <span class="legend-dot" style="background: var(--text-muted);"></span>
                미완료
              </span>
            </div>
          </div>
          <div class="panel-body chart-body">
            <VueApexCharts type="bar" height="100%" :options="chartOptions" :series="chartSeries" />
          </div>
        </section>

        <!-- Table Panel -->
        <section class="panel table-panel">
          <div class="panel-header">
            <div class="panel-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 7V5a2 2 0 0 1 2-2h2" />
                <path d="M17 3h2a2 2 0 0 1 2 2v2" />
                <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
                <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
                <line x1="7" x2="17" y1="12" y2="12" />
              </svg>
              지역별 물류 현황
            </div>
            <span class="record-count">{{ filteredLogisticsData.length }} records</span>
          </div>
          <div class="panel-body table-body">
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>운송장 번호</th>
                    <th>목표 지역</th>
                    <th>상태</th>
                    <th class="text-center">완료 시간</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in filteredLogisticsData" :key="item.id">
                    <td class="font-mono id-cell">{{ item.waybillId }}</td>
                    <td class="font-mono">{{ item.id }}</td>
                    <td>
                      <span class="region-indicator"></span>
                      {{ item.target }}
                    </td>
                    <td>
                      <span class="status-badge" 
                        :class="{
                          'badge-success': item.status === '완료', 
                          'badge-info': item.status === '이동 중', 
                          'badge-neutral': item.status === '대기 중',
                          'badge-error': item.status === '오류'
                        }">
                        {{ item.status }}
                      </span>
                    </td>
                    <td class="text-center font-mono">
                      <span v-if="item.status === '완료'">{{ item.dateTime.split(' ')[1] }}</span>
                      <span v-else class="text-muted">--:--:--</span>
                    </td>
                  </tr>
                  <tr v-if="filteredLogisticsData.length === 0">
                    <td colspan="4" class="empty-state">
                      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                      </svg>
                      {{ logisticsData.length === 0 ? '해당 날짜의 데이터가 없습니다.' : '조건에 맞는 데이터가 없습니다.' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>

      <!-- Right Column: Scanner + Info -->
      <div class="grid-right">
        <!-- Scanner Panel -->
        <section class="panel scanner-panel">
          <div class="panel-header">
            <div class="panel-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m22 8-6 4 6 4V8Z" />
                <rect width="14" height="12" x="2" y="6" rx="2" ry="2" />
              </svg>
              스캔 모니터
            </div>
            <span class="live-indicator">LIVE</span>
          </div>
          <div class="panel-body scanner-body">
            <div class="scanner-view">
              <div class="scanner-corners">
                <div class="corner top-left"></div>
                <div class="corner top-right"></div>
                <div class="corner bottom-left"></div>
                <div class="corner bottom-right"></div>
              </div>
              <div class="scan-line"></div>
              <div class="scanner-content">
                <div class="scanner-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m7.5 4.27 9 5.15" />
                    <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
                    <path d="m3.3 7 8.7 5 8.7-5" />
                    <path d="M12 22v-9" />
                  </svg>
                </div>
                <span class="scanner-text">Scanning...</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Detection Info Panel -->
        <section class="panel info-panel">
          <div class="panel-header">
            <div class="panel-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="m9 12 2 2 4-4" />
              </svg>
              최근 인식 정보
            </div>
          </div>
          <div class="panel-body info-body" v-if="latestScan">
            <div class="detection-card">
              <span class="detection-label">DETECTED DESTINATION</span>
              <div class="detection-value">{{ latestScan.destination }}</div>
              <div class="detection-tags">
                <span class="tag tag-success" v-if="latestScan.matchRate !== '-'">{{ latestScan.matchRate }} Match</span>
                <span class="tag tag-info">{{ latestScan.camId }}</span>
                <span class="tag" :class="latestScan.status === 'COMPLETED' ? 'tag-success' : latestScan.status === 'ERROR' ? 'tag-error' : 'tag-warning'">
                  {{ latestScan.status }}
                </span>
              </div>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">ID</span>
                <span class="info-value font-mono">{{ latestScan.waybillId }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">WAYBILL NO.</span>
                <span class="info-value font-mono">{{ latestScan.waybill }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">처리 시간</span>
                <span class="info-value font-mono">{{ formatProcessTime(latestScan.processTime) }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">스캔 시각</span>
                <span class="info-value font-mono">{{ latestScan.scannedAt || '-' }}</span>
              </div>
            </div>
          </div>
          <div class="panel-body info-body info-empty" v-else>
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>데이터 대기 중...</span>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Dashboard Layout */
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

/* Control Bar */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  flex-shrink: 0;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-label);
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.control-input,
.control-select {
  padding: 10px 16px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: var(--font-size-base);
  font-family: inherit;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
}

.control-input:focus,
.control-select:focus {
  border-color: var(--color-primary);
}

.control-input:hover,
.control-select:hover {
  border-color: var(--border-color-light);
}

.btn-refresh,
.btn-export {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover,
.btn-export:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--color-primary);
}

.btn-export {
  background-color: var(--color-success-light);
  border-color: var(--color-success);
  color: var(--color-success);
}

.btn-export:hover {
  background-color: var(--color-success);
  color: white;
}

/* Summary Bar */
.summary-bar {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.summary-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.summary-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  flex-shrink: 0;
}

.summary-icon.total {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.summary-icon.success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.summary-icon.rate {
  background-color: var(--color-info-light);
  color: var(--color-info);
}

.summary-icon.time {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.summary-icon.error {
  background-color: var(--color-error-light);
  color: var(--color-error);
}

.summary-icon.alert {
  background-color: var(--color-error-light);
  color: var(--color-error);
  animation: pulse-alert 2s infinite;
}

@keyframes pulse-alert {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-label {
  font-size: var(--font-size-label);
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: var(--font-size-h3);
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.summary-value.success {
  color: var(--color-success);
}

.summary-value.error {
  color: var(--color-error);
}

.summary-value.alert {
  color: var(--color-error);
}

.control-right {
  display: flex;
  gap: 10px;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.grid-left,
.grid-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow: hidden;
}

/* Panels */
.panel {
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.panel-body {
  flex: 1;
  padding: 20px;
  min-height: 0;
  overflow: hidden;
}

/* Chart Panel */
.chart-panel {
  flex: 0 0 320px;
}

.chart-body {
  padding: 8px;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

/* Table Panel */
.table-panel {
  flex: 1;
  min-height: 0;
}

.table-body {
  padding: 0;
}

.record-count {
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  color: var(--text-muted);
  padding: 6px 12px;
  background-color: var(--bg-elevated);
  border-radius: 4px;
}

.table-wrapper {
  height: 100%;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-base);
}

.data-table th {
  position: sticky;
  top: 0;
  padding: 16px 20px;
  background-color: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: var(--font-size-label);
  font-weight: 600;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  z-index: 10;
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.data-table td.id-cell {
  color: var(--color-primary);
  font-weight: 600;
}

.data-table tbody tr:hover {
  background-color: var(--bg-hover);
}

.text-center {
  text-align: center;
}

.text-muted {
  color: var(--text-muted);
}

.font-mono {
  font-family: var(--font-family-mono);
}

.region-indicator {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-primary);
  margin-right: 8px;
}

/* Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.badge-success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.badge-info {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.badge-neutral {
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.badge-error {
  background-color: var(--color-error-light);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.empty-state {
  text-align: center;
  padding: 40px !important;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

/* Scanner Panel */
.scanner-panel {
  flex: 0 0 auto;
}

.scanner-body {
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-view {
  position: relative;
  /* 4:3 비율 고정 (640x480) */
  aspect-ratio: 4 / 3;
  width: 100%;
  max-width: 400px;
  background-color: #000;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-corners .corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-primary);
}

.corner.top-left { top: 16px; left: 16px; border-right: none; border-bottom: none; }
.corner.top-right { top: 16px; right: 16px; border-left: none; border-bottom: none; }
.corner.bottom-left { bottom: 16px; left: 16px; border-right: none; border-top: none; }
.corner.bottom-right { bottom: 16px; right: 16px; border-left: none; border-top: none; }

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
  animation: scan 2.5s linear infinite;
  opacity: 0.8;
}

@keyframes scan {
  0% { top: 10%; }
  100% { top: 90%; }
}

.scanner-content {
  text-align: center;
  color: var(--text-muted);
  z-index: 1;
}

.scanner-icon {
  width: 100px;
  height: 100px;
  border: 2px dashed var(--border-color-light);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  background-color: rgba(15, 23, 42, 0.5);
}

.scanner-text {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-base);
}

/* Info Panel */
.info-panel {
  flex: 1;
  min-height: 0;
}

.info-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.info-empty {
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  gap: 12px;
}

.detection-card {
  background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-input) 100%);
  padding: 28px;
  border-radius: 10px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.detection-label {
  display: block;
  font-size: var(--font-size-label);
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}

.detection-value {
  font-size: var(--font-size-data-xl);
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin-bottom: 14px;
}

.detection-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.tag {
  padding: 8px 14px;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  font-weight: 600;
}

.tag-success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.tag-info {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.tag-error {
  background-color: var(--color-error-light);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.tag-warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  padding: 20px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.info-label {
  display: block;
  font-size: var(--font-size-label);
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.info-value {
  display: block;
  font-size: var(--font-size-data-lg);
  font-weight: 600;
  color: var(--text-primary);
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .grid-right {
    flex-direction: row;
  }
  
  .scanner-panel,
  .info-panel {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .control-left {
    flex-wrap: wrap;
  }
  
  .grid-right {
    flex-direction: column;
  }
}
</style>
