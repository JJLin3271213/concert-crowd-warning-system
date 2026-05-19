<template>
  <div class="app-container">
    <!-- 背景动画 -->
    <div class="bg-animation">
      <div class="moving-gradient"></div>
      <div class="music-notes">
        <span>♪</span><span>♫</span><span>♪</span><span>♫</span><span>♪</span>
      </div>
    </div>

    <!-- 主内容 -->
    <div class="content-wrapper">
      <!-- 头部 -->
      <header class="main-header">
        <div class="logo">
          <div class="logo-icon">🎤</div>
          <div class="logo-text">
            <h1>演唱会人流预警系统</h1>
            <p>Concert Crowd Warning System</p>
          </div>
        </div>
        <div class="header-actions">
          <div class="venue-selector">
            <el-select v-model="currentVenueId" @change="switchVenue" placeholder="选择场馆" size="default">
              <el-option 
                v-for="venue in venues" 
                :key="venue.id" 
                :label="venue.name" 
                :value="venue.id"
              />
            </el-select>
          </div>
          <div class="live-badge">
            <span class="live-dot"></span>
            <span>实时监控</span>
          </div>
          <el-button class="admin-login-btn" @click="showLoginDialog = true" v-if="!isLoggedIn">
            <el-icon><User /></el-icon>
            管理员登录
          </el-button>
          <el-button class="admin-dashboard-btn" @click="goToAdmin" v-if="isLoggedIn" type="primary">
            <el-icon><Setting /></el-icon>
            管理后台
          </el-button>
        </div>
      </header>

      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalCount }}</div>
            <div class="stat-label">总人数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏟️</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalCapacity }}</div>
            <div class="stat-label">总容量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ overallRate }}%</div>
            <div class="stat-label">整体拥挤度</div>
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-icon">⚠️</div>
          <div class="stat-info">
            <div class="stat-value alert-count">{{ alertZones }}</div>
            <div class="stat-label">预警分区</div>
          </div>
        </div>
      </div>

      <!-- 演出信息 -->
      <div class="performance-card" v-if="performances.length > 0">
        <div class="performance-header">
          <span class="performance-title">🎵 近期演出</span>
          <span class="performance-count">共 {{ performances.length }} 场</span>
        </div>
        <div class="performance-list">
          <div v-for="perf in performances" :key="perf.id" class="performance-item">
            <div class="perf-artist">{{ perf.artist_name }}</div>
            <div class="perf-date">{{ perf.performance_date }} {{ perf.start_time }} - {{ perf.end_time }}</div>
            <div class="perf-price">🎫 {{ perf.ticket_price }}</div>
            <div class="perf-desc">{{ perf.description }}</div>
          </div>
        </div>
      </div>

      <!-- 分区实时状态 -->
      <div class="section-header">
        <h2>📍 分区实时状态</h2>
        <p>各区域人流量实时监测数据</p>
      </div>

      <div class="zones-grid">
        <div 
          v-for="zone in zones" 
          :key="zone.zone_id"
          class="zone-card"
          :class="zone.level"
        >
          <div class="card-glow" :class="zone.level"></div>
          <div class="card-content">
            <div class="zone-header">
              <span class="zone-icon" :class="zone.level">
                {{ getZoneIcon(zone.level) }}
              </span>
              <span class="zone-name">{{ zone.zone_name }}</span>
              <span class="level-badge" :class="zone.level">
                {{ getLevelText(zone.level) }}
              </span>
            </div>
            <div class="zone-stats">
              <div class="stat-item">
                <span class="stat-key">当前人数</span>
                <span class="stat-num">{{ zone.current_count }}</span>
                <span class="stat-unit">/ {{ zone.capacity }}</span>
              </div>
              <div class="progress-container">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: zone.congestion_rate + '%' }"
                    :class="zone.level"
                  ></div>
                </div>
                <span class="progress-label">{{ zone.congestion_rate }}%</span>
              </div>
            </div>
            <div class="zone-footer">
              <span class="update-time">
                <el-icon><Timer /></el-icon>
                {{ formatTime(zone.timestamp) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 热力图和趋势图 -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">🔥 分区拥堵热力图</span>
            <el-button text size="small" @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          <Heatmap :zones-data="zones" />
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">📈 人流趋势图</span>
            <span class="auto-refresh-badge">自动刷新 5s</span>
          </div>
          <TrendChart :zones="zones" />
        </div>
      </div>

      <!-- 人流预测 -->
      <PredictChart :zones="zones" />

    <!-- 路线规划 -->
<div class="route-card">
  <div class="route-card-header">
    <span class="route-title">🗺️ 智能路线规划</span>
    <span class="route-desc">基于实时拥堵情况，推荐最优路线</span>
  </div>
  <RoutePlanner :venue-id="currentVenueId" />
</div>

      <!-- 应急求助 -->
      <div class="emergency-card">
        <div class="emergency-header">
          <span class="emergency-title">🚨 应急求助</span>
          <span class="emergency-desc">紧急情况请立即求助</span>
        </div>
        <div class="emergency-content">
          <el-select v-model="helpZoneId" placeholder="选择当前位置" class="help-select">
            <el-option v-for="zone in zones" :key="zone.zone_id" :label="zone.zone_name" :value="zone.zone_id" />
          </el-select>
          <el-input v-model="helpMessage" type="textarea" placeholder="补充说明（选填）" :rows="2" />
          <el-button type="danger" class="help-btn" @click="sendHelp" :loading="helpLoading">
            🚨 一键求助
          </el-button>
        </div>
      </div>

      <!-- 附近应急点位 -->
      <div class="nearby-card" v-if="nearbyPoints.length > 0">
        <div class="nearby-header">
          <span class="nearby-title">📍 附近应急点位</span>
        </div>
        <div class="nearby-list">
          <div v-for="point in nearbyPoints" :key="point.id" class="nearby-item">
            <span class="nearby-icon">{{ getPointIcon(point.type) }}</span>
            <div class="nearby-info">
              <div class="nearby-name">{{ point.name }}</div>
              <div class="nearby-desc">{{ point.description || getPointTypeName(point.type) }} | 距您约{{ point.steps }}步</div>
              <div class="nearby-phone" v-if="point.phone">📞 {{ point.phone }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 登录对话框 -->
      <el-dialog v-model="showLoginDialog" title="管理员登录" width="420px" class="login-dialog">
        <el-form :model="loginForm" label-width="80px">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" prefix-icon="User" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" prefix-icon="Lock" placeholder="请输入密码" show-password />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showLoginDialog = false">取消</el-button>
          <el-button type="primary" @click="handleLogin">登录</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { User, Setting, Refresh, Timer } from '@element-plus/icons-vue'
import Heatmap from '../components/Heatmap.vue'
import TrendChart from '../components/TrendChart.vue'
import RoutePlanner from '../components/RoutePlanner.vue'
import PredictChart from '../components/PredictChart.vue'

const router = useRouter()
const API_URL = 'https://secure-achievement.up.railway.app'

const zones = ref([])
const loading = ref(false)
let timer = null
const isLoggedIn = ref(false)
const showLoginDialog = ref(false)
const loginForm = ref({ username: 'admin', password: 'admin123' })

// 场馆相关
const venues = ref([])
const currentVenueId = ref(1)

// 演出信息
const performances = ref([])

// 应急求助相关
const helpZoneId = ref(1)
const helpMessage = ref('')
const helpLoading = ref(false)
const nearbyPoints = ref([])

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

async function fetchPerformances() {
  try {
    const response = await axios.get(`${API_URL}/api/performances`, {
      params: { venue_id: currentVenueId.value }
    })
    performances.value = response.data
  } catch (error) {
    console.error('获取演出信息失败:', error)
  }
}

async function refreshData() {
  loading.value = true
  try {
    const response = await axios.get(`${API_URL}/api/crowd/latest`, {
      params: { venue_id: currentVenueId.value }
    })
    zones.value = response.data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

async function switchVenue(venueId) {
  currentVenueId.value = venueId
  await refreshData()
  await fetchPerformances()
  await fetchNearbyPoints()
}

async function handleLogin() {
  try {
    const response = await axios.post(`${API_URL}/api/login`, null, {
      params: {
        username: loginForm.value.username,
        password: loginForm.value.password
      }
    })
    localStorage.setItem('token', response.data.access_token)
    isLoggedIn.value = true
    showLoginDialog.value = false
    ElMessage.success('登录成功')
  } catch (error) {
    ElMessage.error('用户名或密码错误')
  }
}

function goToAdmin() {
  router.push('/admin')
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

function getLevelText(level) {
  const map = {
    'green': '畅通',
    'yellow': '较堵',
    'orange': '拥堵',
    'red': '严重拥堵'
  }
  return map[level] || level
}

function getZoneIcon(level) {
  const icons = {
    'green': '🟢',
    'yellow': '🟡',
    'orange': '🟠',
    'red': '🔴'
  }
  return icons[level] || '⚪'
}

function getPointIcon(type) {
  const icons = { medical: '🏥', security: '👮', fire: '🔥', exit: '🚪' }
  return icons[type] || '📍'
}

function getPointTypeName(type) {
  const map = { medical: '医疗急救点', security: '安保点', fire: '消防点', exit: '应急出口' }
  return map[type] || '应急点位'
}

async function sendHelp() {
  if (!helpZoneId.value) {
    ElMessage.warning('请选择您当前的位置')
    return
  }
  helpLoading.value = true
  try {
    await axios.post(`${API_URL}/api/emergency/help`, null, {
      params: { zone_id: helpZoneId.value, message: helpMessage.value }
    })
    ElMessage.success('求助已发送，工作人员将尽快联系您')
    helpMessage.value = ''
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  } finally {
    helpLoading.value = false
  }
}

async function fetchNearbyPoints() {
  if (!helpZoneId.value) return
  try {
    const res = await axios.get(`${API_URL}/api/emergency/nearby`, {
      params: { zone_id: helpZoneId.value, venue_id: currentVenueId.value }
    })
    nearbyPoints.value = res.data
  } catch (error) {
    console.error('获取附近点位失败:', error)
  }
}

function checkLogin() {
  const token = localStorage.getItem('token')
  isLoggedIn.value = !!token
}

const totalCount = ref(0)
const totalCapacity = ref(0)
const overallRate = ref(0)
const alertZones = ref(0)

function updateStats() {
  if (zones.value.length === 0) return
  
  let count = 0, capacity = 0, alertCount = 0
  zones.value.forEach(zone => {
    count += zone.current_count
    capacity += zone.capacity
    if (zone.level !== 'green') alertCount++
  })
  totalCount.value = count
  totalCapacity.value = capacity
  overallRate.value = Math.round((count / capacity) * 100)
  alertZones.value = alertCount
}

watch(zones, () => updateStats(), { deep: true })
watch(helpZoneId, () => {
  fetchNearbyPoints()
})

onMounted(() => {
  checkLogin()
  fetchVenues()
  refreshData()
  fetchPerformances()
  timer = setInterval(refreshData, 5000)
  fetchNearbyPoints()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.bg-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.moving-gradient {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(135deg, 
    #0f0c29 0%, 
    #302b63 25%, 
    #24243e 50%,
    #1a1a2e 75%,
    #0f0c29 100%
  );
  animation: moveGradient 20s ease infinite;
}

@keyframes moveGradient {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(5%, 5%) rotate(2deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

.music-notes {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.music-notes span {
  position: absolute;
  font-size: 20px;
  color: rgba(255,255,255,0.1);
  animation: floatUp 8s linear infinite;
}

.music-notes span:nth-child(1) { left: 10%; animation-delay: 0s; font-size: 30px; }
.music-notes span:nth-child(2) { left: 25%; animation-delay: 2s; font-size: 24px; }
.music-notes span:nth-child(3) { left: 50%; animation-delay: 4s; font-size: 36px; }
.music-notes span:nth-child(4) { left: 70%; animation-delay: 1s; font-size: 28px; }
.music-notes span:nth-child(5) { left: 85%; animation-delay: 3s; font-size: 32px; }

@keyframes floatUp {
  0% { bottom: -10%; opacity: 0; transform: rotate(0deg); }
  10% { opacity: 0.3; }
  90% { opacity: 0.3; }
  100% { bottom: 100%; opacity: 0; transform: rotate(360deg); }
}

.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 15px 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  flex-wrap: wrap;
  gap: 15px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 40px;
  animation: bounce 2s ease infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.logo-text h1 {
  font-size: 24px;
  color: #fff;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.logo-text p {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.venue-selector {
  min-width: 180px;
}

.venue-selector :deep(.el-input__wrapper) {
  background: rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 25px;
}

.venue-selector :deep(.el-input__inner) {
  color: white;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,0,0,0.5);
  padding: 8px 16px;
  border-radius: 30px;
  color: #fff;
  font-size: 14px;
}

.live-dot {
  width: 10px;
  height: 10px;
  background: #f44336;
  border-radius: 50%;
  animation: pulse 1.5s ease infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.admin-login-btn, .admin-dashboard-btn {
  border-radius: 25px;
  padding: 8px 20px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid rgba(255,255,255,0.2);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0,0,0,0.2);
}

.stat-icon {
  font-size: 40px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  margin-top: 5px;
}

.stat-card.warning .stat-value {
  color: #ff9800;
}

/* 演出信息卡片 */
.performance-card {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.performance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.performance-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.performance-count {
  font-size: 12px;
  color: #999;
}

.performance-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.performance-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.perf-artist {
  font-weight: bold;
  font-size: 16px;
  color: #333;
  margin-bottom: 5px;
}

.perf-date {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.perf-price {
  font-size: 14px;
  color: #f44336;
  font-weight: bold;
  margin-bottom: 5px;
}

.perf-desc {
  font-size: 12px;
  color: #888;
}

.section-header {
  text-align: center;
  margin-bottom: 25px;
}

.section-header h2 {
  font-size: 28px;
  color: #fff;
  margin-bottom: 5px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.section-header p {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
}

.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.zone-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.zone-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.card-glow.green { background: linear-gradient(90deg, #4CAF50, #81c784); }
.card-glow.yellow { background: linear-gradient(90deg, #FFC107, #ffd54f); }
.card-glow.orange { background: linear-gradient(90deg, #FF9800, #ffb74d); }
.card-glow.red { background: linear-gradient(90deg, #f44336, #ef9a9a); }

.card-content {
  background: rgba(255,255,255,0.95);
  padding: 20px;
}

.zone-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.zone-icon {
  font-size: 24px;
}

.zone-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.level-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.level-badge.green { background: #4CAF50; }
.level-badge.yellow { background: #FFC107; color: #333; }
.level-badge.orange { background: #FF9800; }
.level-badge.red { background: #f44336; }

.zone-stats {
  margin-bottom: 15px;
}

.stat-item {
  margin-bottom: 10px;
}

.stat-key {
  font-size: 12px;
  color: #999;
  display: block;
}

.stat-num {
  font-size: 28px;
  font-weight: bold;
  color: #2196F3;
}

.stat-unit {
  font-size: 14px;
  color: #888;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.3s;
}

.progress-fill.green { background: #4CAF50; }
.progress-fill.yellow { background: #FFC107; }
.progress-fill.orange { background: #FF9800; }
.progress-fill.red { background: #f44336; }

.progress-label {
  font-size: 12px;
  font-weight: bold;
  min-width: 40px;
}

.zone-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.update-time {
  font-size: 11px;
  color: #aaa;
  display: flex;
  align-items: center;
  gap: 4px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.chart-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.auto-refresh-badge {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 4px 12px;
  border-radius: 20px;
}

.route-card {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  margin-bottom: 30px;
  overflow: hidden;
}

.route-card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px 20px;
  color: white;
}

.route-title {
  font-size: 18px;
  font-weight: bold;
  display: block;
}

.route-desc {
  font-size: 12px;
  opacity: 0.9;
}

.emergency-card {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  border-radius: 20px;
  margin-bottom: 20px;
  overflow: hidden;
  border: 1px solid #ffcdd2;
}

.emergency-header {
  background: linear-gradient(135deg, #f44336 0%, #e91e63 100%);
  padding: 15px 20px;
  color: white;
}

.emergency-title {
  font-size: 18px;
  font-weight: bold;
  display: block;
}

.emergency-desc {
  font-size: 12px;
  opacity: 0.9;
}

.emergency-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.help-select {
  width: 100%;
}

.help-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: bold;
}

.nearby-card {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  margin-bottom: 30px;
  overflow: hidden;
}

.nearby-header {
  background: linear-gradient(135deg, #4CAF50 0%, #2196F3 100%);
  padding: 15px 20px;
  color: white;
}

.nearby-title {
  font-size: 18px;
  font-weight: bold;
  display: block;
}

.nearby-list {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nearby-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 12px;
  transition: all 0.3s;
}

.nearby-item:hover {
  transform: translateX(5px);
  background: #e8e8e8;
}

.nearby-icon {
  font-size: 28px;
}

.nearby-info {
  flex: 1;
}

.nearby-name {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.nearby-desc {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.nearby-phone {
  font-size: 12px;
  color: #2196F3;
  margin-top: 4px;
}

:deep(.login-dialog .el-dialog) {
  border-radius: 16px;
}

:deep(.login-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  margin: 0;
  padding: 20px;
  border-radius: 16px 16px 0 0;
}

:deep(.login-dialog .el-dialog__title) {
  color: white;
}
/* ========== 移动端适配 ========== */

/* 平板设备 (768px - 1024px) */
@media (max-width: 1024px) {
  .content-wrapper {
    padding: 15px;
  }
  
  .stats-row {
    gap: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-icon {
    font-size: 32px;
  }
}

/* 手机设备 (小于768px) */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 12px;
  }
  
  /* 头部调整 */
  .main-header {
    flex-direction: column;
    text-align: center;
    padding: 12px;
    gap: 10px;
  }
  
  .logo {
    justify-content: center;
  }
  
  .logo-icon {
    font-size: 32px;
  }
  
  .logo-text h1 {
    font-size: 18px;
  }
  
  .logo-text p {
    font-size: 10px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .venue-selector {
    width: 100%;
    min-width: unset;
  }
  
  .live-badge {
    padding: 5px 12px;
    font-size: 12px;
  }
  
  .admin-login-btn, .admin-dashboard-btn {
    padding: 6px 15px;
    font-size: 12px;
  }
  
  /* 统计卡片 */
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 20px;
  }
  
  .stat-card {
    padding: 12px;
    gap: 10px;
  }
  
  .stat-icon {
    font-size: 28px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 11px;
  }
  
  /* 演出信息卡片 */
  .performance-card {
    padding: 12px;
    margin-bottom: 20px;
  }
  
  .performance-title {
    font-size: 16px;
  }
  
  .perf-artist {
    font-size: 14px;
  }
  
  .perf-date, .perf-price, .perf-desc {
    font-size: 11px;
  }
  
  /* 分区卡片 */
  .section-header h2 {
    font-size: 20px;
  }
  
  .section-header p {
    font-size: 12px;
  }
  
  .zones-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .zone-card .card-content {
    padding: 12px;
  }
  
  .zone-name {
    font-size: 15px;
  }
  
  .stat-num {
    font-size: 22px;
  }
  
  .stat-unit {
    font-size: 12px;
  }
  
  .level-badge {
    padding: 3px 8px;
    font-size: 10px;
  }
  
  .progress-label {
    font-size: 11px;
    min-width: 35px;
  }
  
  .update-time {
    font-size: 10px;
  }
  
  /* 图表卡片 */
  .charts-row {
    grid-template-columns: 1fr;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .chart-card {
    padding: 12px;
  }
  
  .chart-title {
    font-size: 14px;
  }
  
  .auto-refresh-badge {
    font-size: 10px;
    padding: 3px 8px;
  }
  
  /* 预测模块 */
  .predict-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .predict-controls {
    width: 100%;
  }
  
  .predict-controls .el-select {
    flex: 1;
  }
  
  .current-info {
    font-size: 12px;
    gap: 10px;
  }
  
  .predict-summary {
    gap: 10px;
  }
  
  .summary-item .value {
    font-size: 14px;
  }
  
  /* 路线规划 */
  .route-card-header {
    padding: 10px 15px;
  }
  
  .route-title {
    font-size: 16px;
  }
  
  .route-desc {
    font-size: 11px;
  }
  
  .route-selectors {
    flex-direction: column;
    gap: 10px;
  }
  
  .selector {
    min-width: unset;
  }
  
  .node-select {
    padding: 8px;
    font-size: 13px;
  }
  
  .route-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .plan-btn, .evacuate-btn {
    padding: 10px;
    font-size: 13px;
  }
  
  .route-summary {
    padding: 10px;
  }
  
  .summary-item .label,
  .summary-item .value {
    font-size: 12px;
  }
  
  .route-path {
    font-size: 10px;
  }
  
  .step-item {
    padding: 10px;
    gap: 8px;
  }
  
  .step-number {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
  
  .step-route {
    font-size: 13px;
  }
  
  .status-badge {
    padding: 2px 6px;
    font-size: 10px;
  }
  
  .step-congestion, .step-suggestion, .step-time {
    font-size: 10px;
  }
  
  /* 应急求助 */
  .emergency-header {
    padding: 12px 15px;
  }
  
  .emergency-title {
    font-size: 16px;
  }
  
  .emergency-desc {
    font-size: 11px;
  }
  
  .emergency-content {
    padding: 12px;
    gap: 10px;
  }
  
  .help-btn {
    height: 40px;
    font-size: 14px;
  }
  
  /* 附近点位 */
  .nearby-header {
    padding: 12px 15px;
  }
  
  .nearby-title {
    font-size: 16px;
  }
  
  .nearby-list {
    padding: 12px;
    gap: 8px;
  }
  
  .nearby-item {
    padding: 8px;
    gap: 10px;
  }
  
  .nearby-icon {
    font-size: 24px;
  }
  
  .nearby-name {
    font-size: 14px;
  }
  
  .nearby-desc, .nearby-phone {
    font-size: 10px;
  }
  
  /* 底部统计 */
  .summary {
    padding: 12px;
  }
  
  .summary h3 {
    font-size: 16px;
  }
  
  .summary-stats {
    gap: 12px;
  }
  
  .stat {
    padding: 8px 15px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 10px;
  }
}

/* 小屏手机 (小于480px) */
@media (max-width: 480px) {
  .content-wrapper {
    padding: 8px;
  }
  
  .stat-card {
    padding: 8px;
  }
  
  .stat-icon {
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .zone-name {
    font-size: 14px;
  }
  
  .count {
    font-size: 24px;
  }
  
  .level-badge {
    padding: 2px 6px;
    font-size: 9px;
  }
  
  .progress-label {
    font-size: 10px;
    min-width: 30px;
  }
  
  .summary-item .label,
  .summary-item .value {
    font-size: 11px;
  }
  
  .step-route {
    font-size: 12px;
  }
}
</style>