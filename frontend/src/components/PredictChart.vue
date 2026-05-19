<template>
  <div class="predict-container">
    <div class="predict-header">
      <h3>📈 人流预测 (未来10分钟)</h3>
      <div class="predict-controls">
        <el-select v-model="selectedZoneId" placeholder="选择分区" @change="loadPredict" clearable>
          <el-option v-for="zone in props.zones" :key="zone.zone_id" :label="zone.zone_name" :value="zone.zone_id" />
        </el-select>
        <el-button size="small" @click="loadPredict" :loading="loading">刷新预测</el-button>
      </div>
    </div>
    <div v-if="predictData && !predictData.error" class="predict-content">
      <div class="current-info">
        <span>当前人数: <strong>{{ predictData.current_count }}</strong></span>
        <span>容量: <strong>{{ predictData.capacity }}</strong></span>
        <span>当前拥挤度: <strong :class="getRateClass(predictData.current_count / predictData.capacity * 100)">
          {{ Math.round(predictData.current_count / predictData.capacity * 100) }}%
        </strong></span>
      </div>
      <div ref="chartRef" class="predict-chart"></div>
      <div class="predict-summary">
        <div class="summary-item">
          <span class="label">峰值预测</span>
          <span class="value">{{ maxPrediction }} 人</span>
        </div>
        <div class="summary-item">
          <span class="label">10分钟后</span>
          <span class="value">{{ lastPrediction }} 人</span>
        </div>
        <div class="summary-item">
          <span class="label">预测趋势</span>
          <span class="value" :class="trendClass">{{ trendText }}</span>
        </div>
      </div>
    </div>
    <div v-else-if="selectedZoneId && !loading" class="no-data">
      暂无预测数据
    </div>
    <div v-else class="no-data">
      请选择分区查看预测
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const props = defineProps({
  zones: {
    type: Array,
    default: () => []
  }
})

const API_URL = 'https://secureachievement.up.railway.app'
const chartRef = ref(null)
let chart = null
const selectedZoneId = ref(null)
const predictData = ref(null)
const loading = ref(false)

const maxPrediction = computed(() => {
  if (!predictData.value || !predictData.value.predictions) return 0
  return Math.max(...predictData.value.predictions.map(p => p.predicted_count))
})

const lastPrediction = computed(() => {
  if (!predictData.value || !predictData.value.predictions) return 0
  return predictData.value.predictions.slice(-1)[0]?.predicted_count || 0
})

const trendText = computed(() => {
  if (!predictData.value || !predictData.value.predictions) return ''
  const first = predictData.value.predictions[0]?.predicted_count
  const last = predictData.value.predictions.slice(-1)[0]?.predicted_count
  if (last > first) return '上升 📈'
  if (last < first) return '下降 📉'
  return '平稳 ➡️'
})

const trendClass = computed(() => {
  if (!predictData.value || !predictData.value.predictions) return ''
  const first = predictData.value.predictions[0]?.predicted_count
  const last = predictData.value.predictions.slice(-1)[0]?.predicted_count
  if (last > first) return 'up'
  if (last < first) return 'down'
  return 'stable'
})

function getRateClass(rate) {
  if (rate >= 80) return 'rate-red'
  if (rate >= 60) return 'rate-orange'
  if (rate >= 40) return 'rate-yellow'
  return 'rate-green'
}

async function loadPredict() {
  if (!selectedZoneId.value) return
  loading.value = true
  try {
    const response = await axios.get(`${API_URL}/api/predict/${selectedZoneId.value}`)
    predictData.value = response.data
    if (!predictData.value.error) {
      setTimeout(() => renderChart(), 100)
    }
  } catch (error) {
    console.error('预测失败:', error)
    predictData.value = { error: true }
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartRef.value || !predictData.value || !predictData.value.predictions) return
  
  const minutes = predictData.value.predictions.map(p => `${p.minute}min`)
  const counts = predictData.value.predictions.map(p => p.predicted_count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const idx = params[0].dataIndex
        const pred = predictData.value.predictions[idx]
        return `<strong>${pred.minute}分钟后</strong><br/>预测人数: ${pred.predicted_count} 人`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: minutes,
      name: '时间',
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: '预测人数',
      axisLabel: { fontSize: 11 }
    },
    series: [
      {
        name: '预测人数',
        type: 'line',
        data: counts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#ff9800', shadowBlur: 10, shadowColor: 'rgba(255,152,0,0.3)' },
        areaStyle: { opacity: 0.2, color: '#ff9800' },
        itemStyle: { color: '#ff9800', borderColor: '#fff', borderWidth: 2 }
      }
    ],
    backgroundColor: 'transparent'
  }
  
  if (chart) {
    chart.setOption(option)
  } else {
    chart = echarts.init(chartRef.value)
    chart.setOption(option)
    window.addEventListener('resize', () => chart?.resize())
  }
}

watch(selectedZoneId, () => {
  if (selectedZoneId.value) loadPredict()
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.predict-container {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}
.predict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}
.predict-header h3 {
  margin: 0;
  color: #333;
}
.predict-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}
.predict-content {
  margin-top: 10px;
}
.current-info {
  display: flex;
  gap: 20px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 12px;
  margin-bottom: 15px;
  font-size: 14px;
  flex-wrap: wrap;
}
.predict-chart {
  width: 100%;
  height: 250px;
}
.predict-summary {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 12px;
  flex-wrap: wrap;
}
.summary-item {
  flex: 1;
  text-align: center;
}
.summary-item .label {
  font-size: 12px;
  color: #666;
  display: block;
}
.summary-item .value {
  font-size: 18px;
  font-weight: bold;
  display: block;
  margin-top: 5px;
}
.value.up { color: #f44336; }
.value.down { color: #4CAF50; }
.value.stable { color: #FF9800; }
.rate-green { color: #4CAF50; }
.rate-yellow { color: #FFC107; }
.rate-orange { color: #FF9800; }
.rate-red { color: #f44336; }
.no-data {
  text-align: center;
  padding: 30px;
  color: #999;
}
</style>