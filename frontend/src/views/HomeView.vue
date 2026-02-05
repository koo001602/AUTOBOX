<script setup>
import { computed, ref } from 'vue'
import { useDashboard } from '../composables'
import { getDashboardBarChartOptions } from '../config/chartOptions'
import { sendBoxCountCommand } from '../api'
import { StatsGrid, ChartPanel, RecentScanPanel, LogisticsTable } from '../components/dashboard'

// Composable 사용
const {
  maxDate,
  selectedDate,
  chartSeries,
  chartMax,
  filteredLogisticsData,
  latestScan,
  filterRegion,
  filterStatus,
  loadData,
  todaySummary,
  downloadExcel
} = useDashboard()

// 목표 박스 수
const targetBoxCount = ref(0)
const isSending = ref(false)

// 박스 개수 전송
const sendBoxCount = async () => {
  if (targetBoxCount.value <= 0) {
    alert('박스 개수를 1개 이상 입력해주세요.')
    return
  }
  
  isSending.value = true
  try {
    const response = await sendBoxCountCommand(targetBoxCount.value)
    const message = response?.data?.message || `박스 개수 ${targetBoxCount.value}개가 전송되었습니다.`
    alert(message)
  } catch (error) {
    console.error('박스 개수 전송 실패:', error)
    alert('전송에 실패했습니다. 다시 시도해주세요.')
  } finally {
    isSending.value = false
  }
}

// 차트 옵션
const chartOptions = computed(() => getDashboardBarChartOptions(chartMax.value))
</script>

<template>
  <div class="dashboard">
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

        <button class="btn-send" @click="sendBoxCount" :disabled="isSending" title="박스 개수 전송">
          <svg v-if="!isSending" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m22 2-7 20-4-9-9-4Z"/>
            <path d="M22 2 11 13"/>
          </svg>
          <svg v-else class="spinner" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
          <span>{{ isSending ? '전송 중...' : '전송' }}</span>
        </button>
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

    <StatsGrid :summary="todaySummary" />

    <div class="main-content">
      <ChartPanel :options="chartOptions" :series="chartSeries" />
      <LogisticsTable 
        :data="filteredLogisticsData" 
        :expanded="true"
        v-model:filterRegion="filterRegion"
        v-model:filterStatus="filterStatus"
      />
    </div>
  </div>
</template>

<style scoped>
/* =================================================================
   기본 레이아웃 (Desktop - 100% 배율)
   - 2열 그리드, 화면에 꽉 차게, 스크롤 없음
   ================================================================= */
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  min-height: 550px;
  padding: 12px 20px 0 20px;
  gap: 10px;
  box-sizing: border-box;
  overflow-y: auto; 
  overflow-x: hidden;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  gap: 12px;
  padding-bottom: 2px;
}

.header-left {
  display: flex;
  align-items: center;
  background: var(--overlay-dark);
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(8px);
  gap: 16px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.control-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin-left: 2px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.glass-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  font-size: 14px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  outline: none;
  transition: all 0.2s;
}

.glass-input:focus {
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.date-input {
  width: 130px;
  color: var(--text-primary);
  cursor: pointer;
}

.box-input {
  width: 80px;
  text-align: right;
  padding-right: 32px;
}

.box-input::-webkit-inner-spin-button,
.box-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-unit {
  position: absolute;
  right: 8px;
  font-size: 11px;
  color: var(--text-muted);
  pointer-events: none;
}

.control-divider {
  width: 1px;
  height: 24px;
  background: var(--glass-border);
  align-self: center;
}

.btn-send {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark, #4f46e5));
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px var(--color-primary-glow);
  align-self: center;
  white-space: nowrap;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--color-primary-glow);
}

.btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-send .spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-right {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--overlay-dark);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  color: var(--text-primary);
  border-color: var(--glass-border-hover);
  background: var(--overlay-lighter);
}

/* Main Content Layout (Desktop Grid - 2열) */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 12px;
  flex: 1;
  min-height: 0;
  padding-bottom: 20px;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

/* =================================================================
   반응형: 1열 레이아웃으로 변경 시 (확대 또는 작은 화면)
   - 하단 네비게이션과 여백 확보
   ================================================================= */

@media (max-width: 1200px) {
  .dashboard {
    /* [핵심] 1열 레이아웃에서는 고정 높이 해제 + 스크롤 허용 */
    height: auto;
    min-height: auto;
    overflow: visible;
    /* [핵심] 하단 여백 추가 - 네비게이션 바와의 간격 */
    padding-bottom: 30px;
  }

  .main-content {
    grid-template-columns: 1fr;
    gap: 12px;
    flex: none;
    height: auto;
    min-height: auto;
    /* 추가 하단 여백 */
    padding-bottom: 0;
    margin-bottom: 20px;
  }
}

/* 모바일 (Phone) */
@media (max-width: 768px) {
  .dashboard { 
    padding: 12px 16px 25px 16px; 
    gap: 14px;
    height: auto;
    overflow: visible;
    min-height: auto;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left { 
    padding: 8px 12px;
    gap: 12px;
    overflow-x: auto;
  }
  
  .header-right {
    justify-content: flex-end;
  }
  
  .control-label { 
    display: none;
  }
  
  .control-divider {
    display: none;
  }

  /* ▼▼▼ [수정됨] 차트 패널 모바일 최적화 ▼▼▼ */
  
  /* 1. 차트 패널 자체의 높이 설정 */
  .main-content > :first-child :deep(.panel) {
    min-height: 350px !important; /* iPhone SE 등 작은 화면을 위해 높이를 350px로 조정 */
    display: flex;
    flex-direction: column;
  }

  /* 2. 패널 바디: 상단 정렬로 변경 및 여백 제거 */
  .main-content > :first-child :deep(.panel-body) {
    /* [핵심 수정] 위쪽 여백 최소화 (기존 20px -> 10px) */
    padding: 10px 0 0 0 !important;      
    
    overflow: visible !important;
    display: flex !important;
    flex-direction: column !important;
    
    /* [핵심 수정] 수직 중앙 정렬(center) -> 상단 정렬(flex-start)로 변경하여 그래프 위쪽 공백 제거 */
    justify-content: flex-start !important; 
    
    align-items: center !important;
    height: 100% !important;
  }

  /* 3. 차트 캔버스 중앙 정렬 및 위치 보정 */
  .main-content > :first-child :deep(.apexcharts-canvas) {
    margin: 0 auto !important;
    /* 필요한 경우 미세 위치 조정 */
    transform: translateY(-5px); 
  }
}

/* 소형 모바일 */
@media (max-width: 480px) {
  .dashboard {
    padding: 8px 10px 20px 10px;
    gap: 10px;
  }
  
  .header-left {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .control-group {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
  
  .control-label {
    display: block;
  }
  
  .btn-send {
    width: 100%;
    justify-content: center;
  }
}
</style>