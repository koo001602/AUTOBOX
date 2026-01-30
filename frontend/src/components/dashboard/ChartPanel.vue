<script setup>
import VueApexCharts from 'vue3-apexcharts'

defineProps({
  options: {
    type: Object,
    required: true
  },
  series: {
    type: Array,
    required: true
  }
})
</script>

<template>
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
      <VueApexCharts type="bar" height="100%" :options="options" :series="series" />
    </div>
  </section>
</template>

<style scoped>
.panel {
  background: var(--glass-panel);
  backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
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
  padding: 16px 20px;
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
  padding: 20px;
  min-height: 350px;
  overflow-y: auto;
  position: relative;
}

.chart-body {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  min-height: 320px;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.legend-dot.completed { background: var(--color-success); }
.legend-dot.pending { background: rgba(255, 255, 255, 0.2); }

@media (max-width: 1200px) {
  .chart-panel { grid-column: 1; grid-row: 1; }
}

@media (max-width: 768px) {
  .chart-panel { grid-column: 1; }
}
</style>
