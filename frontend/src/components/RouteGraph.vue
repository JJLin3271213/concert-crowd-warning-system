<template>
  <div class="rg-wrap">
    <div class="rg-top">
      <span>路网拓扑</span>
      <span class="rg-legend">
        <i class="ld green"></i>畅通 <i class="ld yellow"></i>较堵 <i class="ld orange"></i>拥堵 <i class="ld red"></i>严重
      </span>
    </div>
    <div class="rg-info" v-if="clickStart||clickEnd">
      <span v-if="clickStart">起点: <b>{{ clickStart.name }}</b></span>
      <span v-if="clickEnd">终点: <b>{{ clickEnd.name }}</b></span>
      <el-button size="small" v-if="clickStart&&clickEnd" type="primary" @click="$emit('planRoute',clickStart.id,clickEnd.id)">规划此路线</el-button>
      <el-button size="small" @click="clearSelection">清除选择</el-button>
    </div>
    <div ref="chartRef" class="rg-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { API_URL } from '../config.js'

const props = defineProps({ venueId: { type: Number, default: 1 }, highlightEdges: { type: Array, default: () => [] } })
defineEmits(['planRoute'])

const chartRef = ref(null)
let chart = null
const clickStart = ref(null)
const clickEnd = ref(null)
const graphData = ref({ nodes: [], edges: [] })

const LC = { green: '#22d67a', yellow: '#f5c842', orange: '#ff8c42', red: '#ff4d5a' }

function buildOption(data) {
  const selectedIds = [clickStart.value?.id, clickEnd.value?.id].filter(Boolean).map(String)
  return {
    backgroundColor: 'transparent',
    tooltip: { formatter(p) { if (p.dataType === 'node') { const n = data.nodes.find(x => String(x.id) === String(p.data.id)); if (n) return `${n.name}<br/>拥挤度: ${n.congestion_rate}%` } return p.name } },
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true,
      force: { repulsion: 600, edgeLength: [100, 250], gravity: 0.04 },
      data: (data.nodes || []).map(n => ({
        id: String(n.id), name: n.name, x: n.x, y: n.y,
        symbolSize: n.symbolSize || 32,
        itemStyle: { color: LC[n.level] || '#999', borderColor: selectedIds.includes(String(n.id)) ? '#fff' : 'transparent', borderWidth: selectedIds.includes(String(n.id)) ? 3 : 0, shadowBlur: selectedIds.includes(String(n.id)) ? 15 : 0, shadowColor: LC[n.level] },
        label: { show: true, fontSize: 11, color: '#c8c8e0' }
      })),
      edges: (data.edges || []).map(e => {
        const hl = props.highlightEdges.some(h => (String(h[0]) === String(e.source) && String(h[1]) === String(e.target)) || (String(h[0]) === String(e.target) && String(h[1]) === String(e.source)))
        return { source: String(e.source), target: String(e.target), lineStyle: { color: hl ? '#42a5f5' : 'rgba(255,255,255,0.12)', width: hl ? 3 : 1, curveness: 0.1 } }
      }),
      emphasis: { focus: 'adjacency', label: { fontSize: 14, fontWeight: 'bold' } }
    }]
  }
}

async function fetchGraph() {
  try {
    const r = await axios.get(`${API_URL}/api/route/network-graph`, { params: { venue_id: props.venueId } })
    graphData.value = r.data
    if (chart) { chart.setOption(buildOption(r.data), true); if (props.highlightEdges.length) autoFocus() }
  } catch (e) { /* ignore */ }
}

function autoFocus() {
  if (!chart || !props.highlightEdges.length) return
  const ids = new Set(); props.highlightEdges.forEach(e => { ids.add(String(e[0])); ids.add(String(e[1])) })
  // 简单聚焦：重新渲染时已高亮
}

function handleClick(params) {
  if (params.dataType !== 'node') return
  const id = parseInt(params.data.id)
  const name = params.data.name
  if (!clickStart.value) { clickStart.value = { id, name } }
  else if (!clickEnd.value && id !== clickStart.value.id) { clickEnd.value = { id, name } }
  else { clickStart.value = { id, name }; clickEnd.value = null }
  fetchGraph()
}

function clearSelection() { clickStart.value = null; clickEnd.value = null; fetchGraph() }

function handleResize() { chart?.resize() }

onMounted(async () => {
  await nextTick()
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.on('click', handleClick)
    window.addEventListener('resize', handleResize)
    await fetchGraph()
  }
})

onUnmounted(() => { window.removeEventListener('resize', handleResize); chart?.off('click'); chart?.dispose() })
watch(() => props.venueId, fetchGraph)
watch(() => props.highlightEdges, () => { fetchGraph() }, { deep: true })
</script>

<style scoped>
.rg-wrap { background: transparent; border-radius: var(--radius); }
.rg-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-weight: 700; font-size: 14px; color: #fff; }
.rg-legend { display: flex; gap: 8px; font-size: 10px; font-weight: 400; color: var(--text-secondary); }
.ld { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.ld.green { background: #22d67a; } .ld.yellow { background: #f5c842; }
.ld.orange { background: #ff8c42; } .ld.red { background: #ff4d5a; }
.rg-info { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; font-size: 12px; color: var(--text-secondary); }
.rg-info b { color: #fff; }
.rg-chart { width: 100%; height: 420px; }
</style>
