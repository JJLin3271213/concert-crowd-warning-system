<template>
  <div class="stats-dashboard">
    <!-- 概览卡片 -->
    <div class="overview-row">
      <div class="overview-card">
        <div class="ov-value">{{ overview.overall_rate }}%</div>
        <div class="ov-label">整体拥挤度</div>
      </div>
      <div class="overview-card">
        <div class="ov-value">{{ overview.latest_total }}</div>
        <div class="ov-label">实时总人数 / {{ overview.total_capacity }}</div>
      </div>
      <div class="overview-card accent-red">
        <div class="ov-value">{{ overview.red_zones }}</div>
        <div class="ov-label">红色预警分区</div>
      </div>
      <div class="overview-card accent-orange">
        <div class="ov-value">{{ overview.orange_zones }}</div>
        <div class="ov-label">橙色预警分区</div>
      </div>
      <div class="overview-card">
        <div class="ov-value">{{ overview.today_alerts }}</div>
        <div class="ov-label">今日预警次数</div>
      </div>
      <div class="overview-card">
        <div class="ov-value">{{ overview.pending_help }}</div>
        <div class="ov-label">待处理求助</div>
      </div>
    </div>

    <!-- 峰值信息 -->
    <div class="peak-info" v-if="overview.peak_zone">
      当前最拥堵分区：<strong>{{ overview.peak_zone }}</strong> ({{ overview.peak_rate }}%)
    </div>

    <div class="charts-row">
      <!-- 拥堵排行 -->
      <div class="chart-panel">
        <div class="panel-title">分区拥堵排行</div>
        <div class="rank-list">
          <div v-for="(z, i) in ranking" :key="i" class="rank-item">
            <span class="rank-pos">{{ i + 1 }}</span>
            <span class="rank-name">{{ z.zone_name }}</span>
            <div class="rank-bar-wrap">
              <div class="rank-bar" :style="{ width: z.congestion_rate + '%', background: levelColor(z.level) }"></div>
            </div>
            <span class="rank-val">{{ z.congestion_rate }}%</span>
            <span class="rank-alerts" v-if="z.alert_count">预警{{ z.alert_count }}次</span>
          </div>
        </div>
      </div>

      <!-- 预警趋势 -->
      <div class="chart-panel">
        <div class="panel-title">近7天预警趋势</div>
        <div ref="trendRef" class="trend-chart"></div>
      </div>
    </div>

    <!-- 系统数据概况 -->
    <div class="data-summary">
      <div class="panel-title">系统数据概况</div>
      <div class="summary-grid">
        <div class="summary-item">
          <span class="s-label">人流记录总数</span>
          <span class="s-value">{{ dataStats.total_crowd_records?.toLocaleString() }}</span>
        </div>
        <div class="summary-item">
          <span class="s-label">预警记录总数</span>
          <span class="s-value">{{ dataStats.total_alerts }}</span>
        </div>
        <div class="summary-item">
          <span class="s-label">求助记录总数</span>
          <span class="s-value">{{ dataStats.total_help_requests }}</span>
        </div>
        <div class="summary-item">
          <span class="s-label">最早记录时间</span>
          <span class="s-value">{{ dataStats.oldest_record }}</span>
        </div>
        <div class="summary-item">
          <span class="s-label">估算DB大小</span>
          <span class="s-value">{{ dataStats.estimated_db_size_mb }} MB</span>
        </div>
      </div>
      <div class="data-actions">
        <el-button size="small" @click="fetchAll">刷新全部</el-button>
        <el-popconfirm title="清理30天前的历史数据？" @confirm="cleanupData">
          <template #reference>
            <el-button size="small" type="warning">清理旧数据</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { API_URL } from '../config.js'

const props = defineProps({ venueId: { type: Number, default: 1 } })

const overview = ref({})
const ranking = ref([])
const dataStats = ref({})
const trendRef = ref(null)
let trendChart = null

function levelColor(l) {
  return { green: '#4CAF50', yellow: '#FFC107', orange: '#FF9800', red: '#f44336' }[l] || '#999'
}

async function fetchOverview() {
  const res = await axios.get(`${API_URL}/api/stats/overview`, { params: { venue_id: props.venueId } })
  overview.value = res.data
}

async function fetchRanking() {
  const res = await axios.get(`${API_URL}/api/stats/congestion-ranking`, { params: { venue_id: props.venueId } })
  ranking.value = res.data
}

async function fetchDataStats() {
  const res = await axios.get(`${API_URL}/api/data/stats`)
  dataStats.value = res.data
}

async function fetchAlertTrend() {
  const res = await axios.get(`${API_URL}/api/stats/alert-trend`, { params: { venue_id: props.venueId, days: 7 } })
  if (trendChart) {
    trendChart.setOption({
      xAxis: { type: 'category', data: res.data.map(d => d.date) },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        data: res.data.map(d => d.count),
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.15 },
        lineStyle: { color: '#f44336', width: 2 },
        itemStyle: { color: '#f44336' }
      }],
      grid: { top: 10, right: 20, bottom: 30, left: 40 },
      tooltip: { trigger: 'axis' }
    }, true)
  }
}

function initTrendChart() {
  if (trendRef.value && !trendChart) {
    trendChart = echarts.init(trendRef.value)
    fetchAlertTrend()
  }
}

async function cleanupData() {
  try {
    const res = await axios.post(`${API_URL}/api/data/cleanup`, null, { params: { days: 30 } })
    ElMessage.success(res.data.message)
    fetchDataStats()
  } catch (e) {
    ElMessage.error('清理失败')
  }
}

async function fetchAll() {
  await Promise.all([fetchOverview(), fetchRanking(), fetchDataStats(), fetchAlertTrend()])
}

onMounted(async () => {
  await fetchAll()
  await nextTick()
  initTrendChart()
})

watch(() => props.venueId, async () => {
  await fetchAll()
})
</script>

<style scoped>
.stats-dashboard { padding: 4px; }
.overview-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }
.overview-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px; padding: 16px; text-align: center; color: #fff;
}
.overview-card.accent-red { background: linear-gradient(135deg, #f44336, #e91e63); }
.overview-card.accent-orange { background: linear-gradient(135deg, #FF9800, #f57c00); }
.ov-value { font-size: 26px; font-weight: bold; }
.ov-label { font-size: 11px; opacity: .85; margin-top: 4px; }
.peak-info {
  background: var(--purple-glass); border-left: 4px solid var(--accent);
  padding: 10px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 13px;
  color: var(--text-primary);
}
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-panel { background: var(--purple-glass); border-radius: 12px; padding: 16px; border: 1px solid rgba(140,110,230,0.12); }
.panel-title { font-weight: bold; font-size: 14px; margin-bottom: 12px; color: var(--text-primary); }
.rank-list { display: flex; flex-direction: column; gap: 6px; max-height: 350px; overflow-y: auto; }
.rank-item { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.rank-pos { width: 22px; height: 22px; background: #667eea; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; }
.rank-name { width: 80px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-bar-wrap { flex: 1; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; }
.rank-bar { height: 100%; border-radius: 4px; min-width: 2px; }
.rank-val { width: 38px; font-size: 12px; font-weight: bold; }
.rank-alerts { font-size: 10px; color: #f44336; }
.trend-chart { width: 100%; height: 280px; }
.data-summary { background: var(--purple-glass); border: 1px solid rgba(140,110,230,0.12); border-radius: 12px; padding: 16px; }
.summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
.summary-item { padding: 10px; background: var(--purple-surface); border-radius: 8px; text-align: center; }
.s-label { font-size: 11px; color: var(--text-secondary); display: block; }
.s-value { font-size: 16px; font-weight: bold; color: var(--text-primary); }
.data-actions { display: flex; gap: 8px; }
@media (max-width: 768px) {
  .overview-row { grid-template-columns: repeat(3, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
