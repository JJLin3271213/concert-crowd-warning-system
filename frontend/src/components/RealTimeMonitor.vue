<template>
  <div ref="monitorRoot" class="monitor-root">
    <div class="mon-top">
      <h3>实时人流监控</h3>
      <div class="mon-actions">
        <el-button v-if="autoRotate" size="small" class="ghost-xs" @click="autoRotate=false">停止轮播</el-button>
        <el-button v-else size="small" class="ghost-xs" @click="startRotate">自动轮播</el-button>
        <el-select v-model="currentVenueId" @change="onVenueChange" size="small" style="width:160px">
          <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
        </el-select>
        <el-button size="small" circle @click="toggleFullscreen">{{ isFs?'✕':'⛶' }}</el-button>
      </div>
    </div>

    <!-- 当前视图 -->
    <Transition name="fade" mode="out-in">
      <!-- 视图1: 概览统计 -->
      <div v-if="view==='overview'" key="ov" class="view-panel">
        <div class="stat-row">
          <div class="s-card"><span class="s-val">{{ totalCount }}</span><span class="s-lbl">实时总人数</span></div>
          <div class="s-card"><span class="s-val">{{ totalCapacity }}</span><span class="s-lbl">总容量</span></div>
          <div class="s-card"><span class="s-val t-red">{{ overallRate }}%</span><span class="s-lbl">拥挤指数</span></div>
          <div class="s-card warn"><span class="s-val t-red">{{ alertCount }}</span><span class="s-lbl">预警分区</span></div>
        </div>
        <div class="two-col">
          <div class="glass-card p-16">
            <h4>拥挤度排行 TOP5</h4>
            <div v-for="(z,i) in topZones" :key="i" class="rank-row">
              <span class="rk-pos">{{ i+1 }}</span><span>{{ z.zone_name }}</span>
              <div class="mini-bar"><div :style="{width:z.congestion_rate+'%',background:levelColor(z.level)}" /></div>
              <span class="rk-pct">{{ z.congestion_rate }}%</span>
            </div>
          </div>
          <div class="glass-card p-16">
            <h4>预警记录</h4>
            <div v-if="!alerts.length" class="no-data">暂无预警</div>
            <div v-for="a in alerts" :key="a.id" :class="['alert-row',a.level]">{{ a.message }}<small>{{ a.time }}</small></div>
          </div>
        </div>
      </div>

      <!-- 视图2: 分区卡片 -->
      <div v-else key="zc" class="view-panel">
        <div class="zone-grid-m">
          <div v-for="z in zones" :key="z.zone_id" :class="['z-card','glass-card',z.level]">
            <div class="zc-top"><span :class="['zc-dot',z.level]" /><strong>{{ z.zone_name }}</strong><span :class="['badge-sm',z.level]">{{ levelTxt(z.level) }}</span></div>
            <div class="zc-body"><span class="zc-num">{{ z.current_count }}<small>/{{ z.capacity }}</small></span></div>
            <div class="zc-bar"><div :class="['zc-fill',z.level]" :style="{width:z.congestion_rate+'%'}" /></div>
            <span class="zc-rate">{{ z.congestion_rate }}%</span>
          </div>
        </div>
      </div>
    </Transition>

    <div class="mon-foot">自动刷新 {{ refreshInterval }}s · 最后更新 {{ lastUpdateTime }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import axios from 'axios'
import { API_URL } from '../config.js'

const monitorRoot = ref(null)
const zones = ref([]); const venues = ref([]); const currentVenueId = ref(1)
const refreshInterval = ref(5); const lastUpdateTime = ref('')
const isFs = ref(false); const view = ref('overview'); const autoRotate = ref(true)
let timer = null; let rotateTimer = null

const totalCount = computed(() => zones.value.reduce((s, z) => s + z.current_count, 0))
const totalCapacity = computed(() => zones.value.reduce((s, z) => s + z.capacity, 0))
const overallRate = computed(() => totalCapacity.value ? Math.round(totalCount.value / totalCapacity.value * 100) : 0)
const alertCount = computed(() => zones.value.filter(z => z.level !== 'green').length)
const topZones = computed(() => [...zones.value].sort((a, b) => b.congestion_rate - a.congestion_rate).slice(0, 5))
const alerts = computed(() => {
  const a = []
  zones.value.forEach(z => {
    if (z.level === 'red') a.push({ id: Date.now() + z.zone_id, level: 'red', message: `${z.zone_name} 严重拥堵 ${z.congestion_rate}%`, time: new Date().toLocaleTimeString() })
    else if (z.level === 'orange') a.push({ id: Date.now() + z.zone_id, level: 'orange', message: `${z.zone_name} 拥堵 ${z.congestion_rate}%`, time: new Date().toLocaleTimeString() })
  })
  return a.slice(0, 8)
})

function levelColor(l) { return { green: '#22d67a', yellow: '#f5c842', orange: '#ff8c42', red: '#ff4d5a' }[l] || '#999' }
function levelTxt(l) { return { green: '畅通', yellow: '较堵', orange: '拥堵', red: '严重' }[l] || l }

async function fetchData() {
  try { const r = await axios.get(`${API_URL}/api/crowd/latest`, { params: { venue_id: currentVenueId.value } }); zones.value = r.data; lastUpdateTime.value = new Date().toLocaleTimeString() } catch (e) { /* */ }
}
async function fetchVenues() { try { const r = await axios.get(`${API_URL}/api/venues`); venues.value = r.data; if (venues.value.length) currentVenueId.value = venues.value[0].id } catch (e) { /* */ } }
async function onVenueChange() { await fetchData() }
function toggleFullscreen() { const el = monitorRoot.value; if (!document.fullscreenElement) { el?.requestFullscreen(); isFs.value = true } else { document.exitFullscreen(); isFs.value = false } }

function startRotate() { autoRotate.value = true; runRotate() }
function runRotate() { if (rotateTimer) clearInterval(rotateTimer); rotateTimer = setInterval(() => { if (autoRotate.value) view.value = view.value === 'overview' ? 'zones' : 'overview' }, 8000) }

onMounted(async () => { await fetchVenues(); fetchData(); timer = setInterval(fetchData, refreshInterval.value * 1000); runRotate() })
onUnmounted(() => { if (timer) clearInterval(timer); if (rotateTimer) clearInterval(rotateTimer) })
watch(refreshInterval, () => { if (timer) clearInterval(timer); timer = setInterval(fetchData, refreshInterval.value * 1000) })
</script>

<style scoped>
.monitor-root { background: transparent; }
.mon-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
.mon-top h3 { color: #fff; font-size: 16px; margin: 0; }
.mon-actions { display: flex; gap: 8px; align-items: center; }
.ghost-xs { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: var(--text-secondary) !important; font-size: 11px !important; }

.view-panel { min-height: 300px; }
.stat-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 16px; }
.s-card { background: var(--glass); border: 1px solid var(--border-glass); border-radius: 14px; padding: 18px; text-align: center; backdrop-filter: blur(20px); }
.s-card.warn { border-color: rgba(255,77,90,0.3); animation: pulse-warn 2s infinite; }
.s-val { display: block; font-size: 28px; font-weight: 800; color: #fff; }
.t-red { color: var(--red); }
.s-lbl { font-size: 11px; color: var(--text-secondary); margin-top: 4px; display: block; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.p-16 { padding: 16px; }
h4 { font-size: 13px; color: #fff; margin-bottom: 12px; }

.rank-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 12px; color: #c8c8e0; }
.rk-pos { width: 20px; height: 20px; border-radius: 50%; background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; }
.mini-bar { flex: 1; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.mini-bar div { height: 100%; border-radius: 3px; }
.rk-pct { font-weight: 700; font-size: 11px; }

.alert-row { padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; font-size: 11px; display: flex; justify-content: space-between; }
.alert-row.red { background: rgba(255,77,90,0.1); border-left: 3px solid var(--red); }
.alert-row.orange { background: rgba(255,140,66,0.1); border-left: 3px solid var(--orange); }
.alert-row small { color: var(--text-secondary); }
.no-data { text-align: center; color: var(--text-secondary); padding: 30px; font-size: 12px; }

.zone-grid-m { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
.z-card { padding: 14px; }
.z-card.red { border-color: rgba(255,77,90,0.3); animation: pulse-warn 2s infinite; }
.zc-top { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.zc-dot { width: 8px; height: 8px; border-radius: 50%; }
.zc-dot.green { background: #22d67a; } .zc-dot.yellow { background: #f5c842; }
.zc-dot.orange { background: #ff8c42; } .zc-dot.red { background: #ff4d5a; }
.zc-top strong { font-size: 13px; color: #fff; flex: 1; }
.badge-sm { font-size: 9px; padding: 2px 6px; border-radius: 8px; font-weight: 700; }
.badge-sm.green { background: rgba(34,214,122,.15); color: #22d67a; }
.badge-sm.yellow { background: rgba(245,200,66,.15); color: #f5c842; }
.badge-sm.orange { background: rgba(255,140,66,.15); color: #ff8c42; }
.badge-sm.red { background: rgba(255,77,90,.15); color: #ff4d5a; }
.zc-body { margin-bottom: 6px; }
.zc-num { font-size: 18px; font-weight: 800; color: #fff; }
.zc-num small { font-size: 11px; font-weight: 400; color: var(--text-secondary); }
.zc-bar { height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; margin-bottom: 4px; }
.zc-fill { height: 100%; border-radius: 3px; }
.zc-fill.green { background: #22d67a; } .zc-fill.yellow { background: #f5c842; }
.zc-fill.orange { background: #ff8c42; } .zc-fill.red { background: #ff4d5a; }
.zc-rate { font-size: 11px; color: var(--text-secondary); }

.mon-foot { text-align: center; font-size: 11px; color: var(--text-secondary); margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.04); }

.fade-enter-active, .fade-leave-active { transition: opacity .4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width:768px) { .stat-row { grid-template-columns: repeat(2,1fr); } .two-col { grid-template-columns: 1fr; } .zone-grid-m { grid-template-columns: 1fr 1fr; } }
</style>
