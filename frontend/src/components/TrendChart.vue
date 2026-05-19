<template>
  <div class="trend-container">
    <div class="trend-header">
      <h3>📈 人流趋势图</h3>
      <select v-model="selectedZone" @change="loadTrend" class="zone-select">
        <option v-for="zone in zones" :key="zone.zone_id" :value="zone.zone_id">
          {{ zone.zone_name }}
        </option>
      </select>
    </div>
    <div ref="chartRef" class="trend-chart"></div>
    <div class="trend-info" v-if="trendData.length > 0">
      <span>📊 当前: {{ currentCount }} / {{ capacity }}</span>
      <span>📈 峰值: {{ maxCount }}</span>
      <span>📉 均值: {{ avgCount }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
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
const selectedZone = ref(1)
const trendData = ref([])
const capacity = ref(0)
const currentCount = ref(0)
const maxCount = ref(0)
const avgCount = ref(0)

const loadTrend = async () => {
  if (!selectedZone.value) return
  
  try {
    const response = await axios.get(`${API_URL}/api/trend/${selectedZone.value}?minutes=30`)
    trendData.value = response.data.data
    capacity.value = response.data.capacity
    
    // 计算统计信息
    const counts = trendData.value.map(d => d.count)
    if (counts.length > 0) {
      currentCount.value = counts[counts.length - 1]
      maxCount.value = Math.max(...counts)
      avgCount.value = Math.round(counts.reduce((a, b) => a + b, 0) / counts.length)
    }
    
    renderChart()
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
}

const renderChart = () => {
  if (!chartRef.value || !trendData.value.length) return
  
  const times = trendData.value.map(d => d.time)
  const counts = trendData.value.map(d => d.count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const time = params[0].axisValue
        const count = params[0].value
        const rate = Math.round((count / capacity.value) * 100)
        return `<strong>${time}</strong><br/>人数: ${count}<br/>拥挤度: ${rate}%`
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
      data: times,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(times.length / 10)
      }
    },
    yAxis: {
      type: 'value',
      name: '人数',
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: { type: 'dashed' }
      }
    },
    series: [
      {
        name: '人流数',
        type: 'line',
        data: counts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#667eea',
          shadowColor: 'rgba(102,126,234,0.3)',
          shadowBlur: 10
        },
        areaStyle: {
          opacity: 0.2,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        itemStyle: {
          color: '#667eea',
          borderColor: '#fff',
          borderWidth: 2
        },
        emphasis: {
          scale: 1.2
        }
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

watch(() => props.zones, () => {
  if (props.zones.length > 0 && !selectedZone.value) {
    selectedZone.value = props.zones[0]?.zone_id
    loadTrend()
  }
}, { immediate: true })

watch(selectedZone, () => {
  loadTrend()
})

onMounted(() => {
  if (props.zones.length > 0) {
    selectedZone.value = props.zones[0]?.zone_id
    loadTrend()
  }
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.trend-container {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.trend-header h3 {
  margin: 0;
  color: #333;
}

.zone-select {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
  font-size: 14px;
  cursor: pointer;
}

.trend-chart {
  width: 100%;
  height: 300px;
}

.trend-info {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 14px;
  flex-wrap: wrap;
  gap: 15px;
}

.trend-info span {
  color: #333;
}
</style>