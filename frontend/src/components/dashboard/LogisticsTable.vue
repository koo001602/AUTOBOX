<script setup>
import { FILTER_OPTIONS } from '../../constants'

defineProps({
  data: {
    type: Array,
    required: true
  },
  expanded: {
    type: Boolean,
    default: false
  }
})

const filterRegion = defineModel('filterRegion', { default: '전체' })
const filterStatus = defineModel('filterStatus', { default: '전체' })
</script>

<template>
  <section class="panel table-panel" :class="{ 'table-panel-expanded': expanded }">
    <div class="panel-header">
      <h2 class="panel-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-info)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 7V5a2 2 0 0 1 2-2h2" />
          <path d="M17 3h2a2 2 0 0 1 2 2v2" />
          <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
          <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
        </svg>
        물류 목록
        <span class="record-badge">{{ data.length }}건</span>
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
            <tr v-for="item in data" :key="item.id" class="table-row">
              <td class="cell-id">{{ item.waybillId }}</td>
              <td class="cell-waybill">{{ item.id }}</td>
              <td class="cell-region">
                <span class="region-badge" :class="{
                  'region-seoul': item.target === '서울',
                  'region-busan': item.target === '부산',
                  'region-gwangju': item.target === '광주',
                  'region-daejeon': item.target === '대전',
                  'region-daegu': item.target === '대구'
                }">{{ item.target }}</span>
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
            <tr v-if="data.length === 0">
              <td colspan="5" class="empty-state-cell">
                <div class="empty-state">
                  <div class="empty-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
                      <path d="m3.3 7 8.7 5 8.7-5"/>
                      <path d="M12 22V12"/>
                    </svg>
                  </div>
                  <p class="empty-title">등록된 물류가 없습니다</p>
                  <p class="empty-subtitle">새로운 물류가 등록되면 이곳에 표시됩니다</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.panel {
  background: var(--glass-panel);
  backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s;
  overflow: hidden;
}

.panel:hover {
  border-color: rgba(255, 255, 255, 0.15);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid var(--glass-border);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.02);
  flex-wrap: wrap;
  gap: 12px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
  margin: 0;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
  letter-spacing: 0.05em;
}

.panel-body {
  flex: 1;
  padding: 16px;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.table-panel-expanded {
  grid-column: 2 / -1;
}

.record-badge {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
}

.table-filters {
  display: flex;
  gap: 8px;
}

/* 테마 대응 - CSS 변수 사용 */
.filter-select {
  padding: 6px 12px;
  min-height: 32px;
  background-color: var(--overlay-dark);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 32px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888888' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
}

.filter-select:hover {
  border-color: var(--color-primary);
  background-color: var(--overlay-lighter);
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-glow);
}

/* 옵션 배경색 테마 대응 */
.filter-select option {
  background-color: var(--bg-base);
  color: var(--text-primary);
  padding: 10px 12px;
}

/* Table Styling */
.table-body {
  padding: 0;
  min-height: 0;
  flex: 1;
}

.table-wrapper {
  overflow-y: auto;
  height: 100%;
  width: 100%;
}

.data-table {
  width: 100%;
  min-width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  table-layout: fixed;
}

.data-table th {
  position: sticky;
  top: 0;
  padding: 12px 16px;
  background: var(--table-header-bg);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--glass-border);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  z-index: 10;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 13px;
  vertical-align: middle;
}

.table-row {
  transition: all 0.15s;
}

.table-row:hover {
  background: var(--table-row-hover);
}

.cell-id {
  font-family: var(--font-family-mono);
  color: var(--text-muted);
  font-size: 11px;
}

.cell-waybill {
  font-family: var(--font-family-mono);
  font-weight: 600;
  color: var(--text-primary);
}

.region-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary);
}

/* 지역별 색상 (파이 차트와 동일) */
.region-seoul { background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); color: #10b981; }
.region-busan { background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.3); color: #3b82f6; }
.region-gwangju { background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3); color: #f59e0b; }
.region-daejeon { background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.3); color: #ef4444; }
.region-daegu { background: rgba(139, 92, 246, 0.15); border-color: rgba(139, 92, 246, 0.3); color: #8b5cf6; }

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

.status-complete { background: rgba(16, 185, 129, 0.1); color: var(--color-success); border: 1px solid rgba(16, 185, 129, 0.2); }
.status-moving { background: rgba(245, 158, 11, 0.1); color: var(--color-warning); border: 1px solid rgba(245, 158, 11, 0.2); }
.status-ready { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.1); }
.status-error { background: rgba(239, 68, 68, 0.1); color: var(--color-error); border: 1px solid rgba(239, 68, 68, 0.2); }

/* 빈 상태 셀 높이 유동적 조정 */
.empty-state-cell {
  padding: 0 !important;
  border: none !important;
  height: 100%; 
  min-height: 200px;
  width: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  text-align: center;
  height: 100%;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
  color: var(--color-info);
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.text-muted {
  color: var(--text-muted);
}

.cell-time {
  font-family: var(--font-family-mono);
  font-size: 12px;
}

/* 태블릿 및 작은 데스크톱 (기존 코드 유지) */
@media (max-width: 1200px) {
  .table-panel { 
    grid-column: 1 / -1; 
    grid-row: 2; 
    display: flex;
    flex-direction: column;
  }
  
  .table-panel-expanded { 
    grid-column: 1 / -1; 
    grid-row: 2; 
  }

  /* 1200px 이하에서는 600px로 고정되어 있음 (문제의 원인) */
  .table-body {
    height: 600px;
    min-height: 600px;
  }
  
  .empty-state-cell {
    height: 100%;
  }
  
  .empty-state {
    height: 100%;
    min-height: 500px;
  }
}

/* 모바일 (Phone) - [수정됨] */
@media (max-width: 768px) {
  .table-panel, .table-panel-expanded { grid-column: 1; }
  .panel-header { padding: 12px 14px; }
  .panel-body { padding: 14px; }

  /* [수정] 위 1200px 미디어 쿼리에서 강제한 600px 높이를 덮어씌움 */
  .table-body {
    height: 350px !important;    /* 모바일에 맞는 적당한 높이로 변경 (350px) */
    min-height: 350px !important;
  }

  /* 테이블 셀 폰트 크기 및 가독성 개선 */
  .data-table th {
    padding: 10px 8px;
    font-size: 10px;
    background: var(--table-header-bg);
  }

  .data-table td {
    padding: 10px 8px;
    font-size: 12px;
    border-bottom: 1px solid var(--glass-border);
  }

  .table-row:nth-child(even) {
    background: var(--overlay-light, rgba(0, 0, 0, 0.02));
  }

  .cell-id {
    font-size: 11px;
    font-weight: 600;
  }

  .cell-waybill {
    font-size: 11px;
    max-width: 90px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .region-badge {
    padding: 4px 8px;
    font-size: 10px;
  }

  .status-badge {
    padding: 4px 8px;
    font-size: 10px;
  }

  .cell-time {
    font-size: 11px;
    font-weight: 500;
  }

  /* [수정] 빈 상태일 때의 높이도 축소 */
  .empty-state {
    min-height: auto !important;
    height: 100% !important;
    padding: 20px !important;
  }
}
</style>