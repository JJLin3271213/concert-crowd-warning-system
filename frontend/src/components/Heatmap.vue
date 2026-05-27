<template>
  <div class="heatmap-container">
    <div class="heatmap-header">
      <h3>拥堵热力分布图</h3>
      <span class="update-time">最后更新: {{ updateTime }}</span>
    </div>
    <div ref="chartRef" class="heatmap-chart" style="width:100%"></div>
    <div class="legend">
      <span class="legend-item"><i class="ld green"></i>畅通</span>
      <span class="legend-item"><i class="ld yellow"></i>较堵</span>
      <span class="legend-item"><i class="ld orange"></i>拥堵</span>
      <span class="legend-item"><i class="ld red"></i>严重</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ zonesData: { type: Array, default: () => [] } })
const chartRef = ref(null)
let chart = null
const updateTime = ref('')

const LC = { green: '#22d67a', yellow: '#f5c842', orange: '#ff8c42', red: '#ff4d5a' }

const renderChart = () => {
  if (!chartRef.value || !props.zonesData.length) return

  const el = chartRef.value
  const data = props.zonesData.map((z, i) => ({
    value: [0, i, z.congestion_rate],
    name: z.zone_name,
    level: z.level,
    count: z.current_count,
    capacity: z.capacity,
    itemStyle: { color: LC[z.level] || '#999' }
  }))

  const option = {
    tooltip: {
      formatter: (p) => {
        const d = data[p.dataIndex]
        if (!d) return ''
        return `<strong>${d.name}</strong><br/>人数: ${d.count}/${d.capacity}<br/>拥挤度: ${d.value[2]}%`
      }
    },
    grid: { left: 5, right: 20, bottom: 50, top: 10 },
    xAxis: { type: 'category', data: [''], show: false },
    yAxis: {
      type: 'category',
      data: props.zonesData.map(z => z.zone_name),
      axisLabel: { fontSize: 12, color: '#c8c8e0' },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    visualMap: {
      min: 0, max: 100,
      orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#22d67a', '#f5c842', '#ff8c42', '#ff4d5a'] },
      textStyle: { color: '#c8c8e0' },
      show: false
    },
    series: [{
      type: 'heatmap',
      data: data.map((d, i) => [0, i, d.value[2]]),
      label: {
        show: true,
        formatter: (p) => {
          const z = props.zonesData[p.dataIndex]
          return z ? `${z.congestion_rate}%` : ''
        },
        fontSize: 12,
        fontWeight: 'bold',
        color: '#fff'
      },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } },
      itemStyle: { borderWidth: 1, borderColor: 'rgba(0,0,0,0.2)', borderRadius: 6 },
      animation: true,
      animationDuration: 800
    }],
    backgroundColor: 'transparent'
  }

  if (!chart) {
    chart = echarts.init(el)
    window.addEventListener('resize', () => chart?.resize())
    const ro = new ResizeObserver(() => chart?.resize())
    ro.observe(el)
  }
  chart.setOption(option, true)
  setTimeout(() => chart?.resize(), 100)
  updateTime.value = new Date().toLocaleTimeString()
}

watch(() => props.zonesData, renderChart, { deep: true })
onMounted(renderChart)
onUnmounted(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.heatmap-container { background: transparent; border-radius: 0; padding: 0; margin-bottom: 0; }
.heatmap-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.heatmap-header h3 { margin: 0; color: #fff; font-size: 15px; }
.update-time { font-size: 11px; color: var(--text-secondary); }
.heatmap-chart { width: 100%; height: 340px; }
.legend { display: flex; justify-content: center; gap: 16px; margin-top: 8px; flex-wrap: wrap; }
.legend-item { font-size: 11px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; }
.ld { display: inline-block; width: 10px; height: 10px; border-radius: 3px; }
.ld.green { background: #22d67a; } .ld.yellow { background: #f5c842; }
.ld.orange { background: #ff8c42; } .ld.red { background: #ff4d5a; }
</style>
