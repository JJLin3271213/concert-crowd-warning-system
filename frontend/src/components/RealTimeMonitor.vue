<template>
  <div class="monitor-container">
    <div class="monitor-header">
      <h3>📊 实时人流监控大屏</h3>
      <div class="venue-selector">
        <el-select v-model="currentVenueId" @change="onVenueChange" placeholder="选择场馆" size="default">
          <el-option 
            v-for="venue in venues" 
            :key="venue.id" 
            :label="venue.name" 
            :value="venue.id"
          />
        </el-select>
      </div>
    </div>
    
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ totalCount }}</div>
        <div class="stat-label">实时总人数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ totalCapacity }}</div>
        <div class="stat-label">总容量</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ overallRate }}%</div>
        <div class="stat-label">整体拥挤度</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-value">{{ alertCount }}</div>
        <div class="stat-label">预警分区</div>
      </div>
    </div>
    
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">分区拥挤度排行</div>
        <div class="rank-list">
          <div v-for="(zone, index) in topZones" :key="zone.zone_id" class="rank-item">
            <span class="rank-num">{{ index + 1 }}</span>
            <span class="rank-name">{{ zone.zone_name }}</span>
            <div class="rank-bar">
              <div class="rank-fill" :style="{ width: zone.congestion_rate + '%', background: getLevelColor(zone.level) }"></div>
            </div>
            <span class="rank-rate">{{ zone.congestion_rate }}%</span>
          </div>
          <div v-if="topZones.length === 0" class="no-data">暂无数据</div>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-title">预警记录</div>
        <div class="alert-list">
          <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.level">
            <span class="alert-icon">{{ getLevelIcon(alert.level) }}</span>
            <span class="alert-text">{{ alert.message }}</span>
            <span class="alert-time">{{ alert.time }}</span>
          </div>
          <div v-if="alerts.length === 0" class="no-alert">
            暂无预警记录
          </div>
        </div>
      </div>
    </div>
    
    <div class="refresh-info">
      自动刷新: 每 {{ refreshInterval }} 秒 | 最后更新: {{ lastUpdateTime }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'

const API_URL = 'https://secureachievement.up.railway.app'
const venues = ref([])
const currentVenueId = ref(1)
const zones = ref([])
const totalCount = ref(0)
const totalCapacity = ref(0)
const overallRate = ref(0)
const alertCount = ref(0)
const topZones = ref([])
const alerts = ref([])
const refreshInterval = ref(5)
const lastUpdateTime = ref('')
let timer = null

async function fetchVenues() {
  try {
    const response = await axios.get(`${API_URL}/api/venues`)
    venues.value = response.data
    if (venues.value.length > 0) {
      currentVenueId.value = venues.value[0].id
    }
  } catch (error) {
    console.error('获取场馆失败:', error)
  }
}

async function fetchData() {
  try {
    const res = await axios.get(`${API_URL}/api/crowd/latest`, {
      params: { venue_id: currentVenueId.value }
    })
    zones.value = res.data
    
    let count = 0, capacity = 0, alertCnt = 0
    zones.value.forEach(zone => {
      count += zone.current_count
      capacity += zone.capacity
      if (zone.level !== 'green') alertCnt++
    })
    totalCount.value = count
    totalCapacity.value = capacity
    overallRate.value = Math.round((count / capacity) * 100)
    alertCount.value = alertCnt
    
    // 按拥挤度排序
    topZones.value = [...zones.value].sort((a, b) => b.congestion_rate - a.congestion_rate).slice(0, 5)
    
    // 生成预警记录
    const newAlerts = []
    zones.value.forEach(zone => {
      if (zone.level === 'red') {
        newAlerts.push({
          id: Date.now() + zone.zone_id,
          level: 'red',
          message: `${zone.zone_name} 严重拥堵，拥挤度 ${zone.congestion_rate}%`,
          time: new Date().toLocaleTimeString()
        })
      } else if (zone.level === 'orange') {
        newAlerts.push({
          id: Date.now() + zone.zone_id,
          level: 'orange',
          message: `${zone.zone_name} 拥堵，拥挤度 ${zone.congestion_rate}%`,
          time: new Date().toLocaleTimeString()
        })
      }
    })
    alerts.value = newAlerts.slice(0, 10)
    
    lastUpdateTime.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

async function onVenueChange() {
  await fetchData()
}

function getLevelColor(level) {
  const colors = { green: '#4CAF50', yellow: '#FFC107', orange: '#FF9800', red: '#f44336' }
  return colors[level] || '#999'
}

function getLevelIcon(level) {
  const icons = { red: '🔴', orange: '🟠', yellow: '🟡', green: '🟢' }
  return icons[level] || '⚪'
}

async function loadConfig() {
  const res = await axios.get(`${API_URL}/api/config`, { params: { key: 'refresh_interval' } })
  if (res.data.value) {
    refreshInterval.value = parseInt(res.data.value)
  }
}

function startTimer() {
  if (timer) clearInterval(timer)
  timer = setInterval(fetchData, refreshInterval.value * 1000)
}

watch(refreshInterval, () => {
  startTimer()
})

onMounted(() => {
  fetchVenues()
  loadConfig()
  fetchData()
  startTimer()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.monitor-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.monitor-header h3 {
  margin: 0;
  color: #333;
}

.venue-selector {
  min-width: 200px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  color: white;
}

.stat-card.warning {
  background: linear-gradient(135deg, #f44336, #e91e63);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  margin-top: 5px;
  opacity: 0.9;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 15px;
}

.chart-title {
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank-num {
  width: 28px;
  height: 28px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.rank-name {
  width: 100px;
  font-size: 14px;
}

.rank-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}

.rank-fill {
  height: 100%;
  border-radius: 10px;
}

.rank-rate {
  width: 40px;
  font-size: 12px;
  font-weight: bold;
}

.alert-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item {
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.alert-item.red {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.alert-item.orange {
  background: #fff3e0;
  border-left: 4px solid #FF9800;
}

.alert-icon {
  font-size: 16px;
}

.alert-text {
  flex: 1;
  font-size: 13px;
}

.alert-time {
  font-size: 11px;
  color: #999;
}

.no-alert, .no-data {
  text-align: center;
  padding: 20px;
  color: #999;
}

.refresh-info {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .monitor-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .venue-selector {
    width: 100%;
  }
  
  .rank-name {
    width: 70px;
    font-size: 12px;
  }
}
</style>