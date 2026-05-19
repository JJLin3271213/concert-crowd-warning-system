<template>
  <div class="heatmap-container">
    <div class="heatmap-header">
      <h3>🔥 分区拥堵热力图</h3>
      <span class="update-time">最后更新: {{ updateTime }}</span>
    </div>
    <div ref="chartRef" class="heatmap-chart"></div>
    <div class="legend">
      <div class="legend-item">
        <span class="legend-color green"></span>
        <span>畅通 (&lt;40%)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color yellow"></span>
        <span>较堵 (40%-60%)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color orange"></span>
        <span>拥堵 (60%-80%)</span>
      </div>
      <div class="legend-item">
        <span class="legend-color red"></span>
        <span>严重拥堵 (&gt;80%)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  zonesData: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chart = null
const updateTime = ref('')

// 获取等级颜色
function getLevelColor(level) {
  const colors = {
    'green': '#4CAF50',
    'yellow': '#FFC107',
    'orange': '#FF9800',
    'red': '#f44336'
  }
  return colors[level] || '#999'
}

// 获取等级文字
function getLevelText(level) {
  const texts = {
    'green': '畅通',
    'yellow': '较堵',
    'orange': '拥堵',
    'red': '严重拥堵'
  }
  return texts[level] || '未知'
}

const renderChart = () => {
  if (!chartRef.value || !props.zonesData.length) return
  
  const data = props.zonesData.map(zone => ({
    name: zone.zone_name,
    value: zone.congestion_rate,
    level: zone.level,
    count: zone.current_count,
    capacity: zone.capacity
  }))
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const item = data[params[0].dataIndex]
        return `<strong>${item.name}</strong><br/>
                <span style="color: #666;">人数: ${item.count} / ${item.capacity}</span><br/>
                <span style="color: #666;">拥挤度: ${item.value}%</span><br/>
                <span style="color: ${getLevelColor(item.level)};">状态: ${getLevelText(item.level)}</span>`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: {
        rotate: 30,
        interval: 0,
        fontSize: 11,
        fontWeight: '500'
      },
      axisLine: {
        lineStyle: { color: '#999' }
      }
    },
    yAxis: {
      type: 'value',
      name: '拥挤度 (%)',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: { type: 'dashed', color: '#e0e0e0' }
      }
    },
    series: [
      {
        name: '拥挤度',
        type: 'bar',
        data: data.map(d => ({
          value: d.value,
          itemStyle: {
            color: getLevelColor(d.level),
            borderRadius: [8, 8, 0, 0],
            shadowColor: 'rgba(0,0,0,0.1)',
            shadowBlur: 5
          }
        })),
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%',
          fontWeight: 'bold',
          fontSize: 11
        },
        barWidth: '50%',
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicOut'
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
  
  const now = new Date()
  updateTime.value = now.toLocaleTimeString()
}

watch(() => props.zonesData, () => {
  renderChart()
}, { deep: true })

onMounted(() => {
  renderChart()
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.heatmap-container {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.heatmap-header h3 {
  margin: 0;
  color: #333;
}

.update-time {
  font-size: 12px;
  color: #999;
}

.heatmap-chart {
  width: 100%;
  height: 350px;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.green { background: #4CAF50; }
.legend-color.yellow { background: #FFC107; }
.legend-color.orange { background: #FF9800; }
.legend-color.red { background: #f44336; }
</style>