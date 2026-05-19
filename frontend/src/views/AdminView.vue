<template>
  <div class="admin-container">
    <!-- 背景动画 -->
    <div class="bg-animation">
      <div class="moving-gradient"></div>
    </div>

    <!-- 主内容 -->
    <div class="content-wrapper">
      <!-- 头部 -->
      <header class="admin-header">
        <div class="logo">
          <div class="logo-icon">🔧</div>
          <div class="logo-text">
            <h1>演唱会人流预警系统</h1>
            <p>管理后台 - 场馆运营控制中心</p>
          </div>
        </div>
        <div class="header-actions">
          <div class="user-info">
            <el-icon><User /></el-icon>
            <span>管理员</span>
          </div>
          <el-button class="logout-btn" @click="logout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </header>

      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">🏟️</div>
          <div class="stat-info">
            <div class="stat-value">{{ venueCount }}</div>
            <div class="stat-label">场馆总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📍</div>
          <div class="stat-info">
            <div class="stat-value">{{ zoneCount }}</div>
            <div class="stat-label">分区总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔗</div>
          <div class="stat-info">
            <div class="stat-value">{{ roadCount }}</div>
            <div class="stat-label">路网连接</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🚨</div>
          <div class="stat-info">
            <div class="stat-value">{{ emergencyCount }}</div>
            <div class="stat-label">应急点位</div>
          </div>
        </div>
      </div>

      <!-- 管理标签页 -->
      <div class="tabs-container">
        <el-tabs v-model="activeTab" class="admin-tabs">
          <el-tab-pane name="monitor">
            <template #label>
              <span class="tab-label">
                <el-icon><DataLine /></el-icon>
                实时监控
              </span>
            </template>
            <RealTimeMonitor />
          </el-tab-pane>
          
          <el-tab-pane name="performance">
            <template #label>
              <span class="tab-label">
                <el-icon><Mic /></el-icon>
                演出管理
              </span>
            </template>
            <PerformanceManage />
          </el-tab-pane>
          
          <el-tab-pane name="venue">
            <template #label>
              <span class="tab-label">
                <el-icon><OfficeBuilding /></el-icon>
                场馆管理
              </span>
            </template>
            <VenueManage @update:count="fetchStats" />
          </el-tab-pane>
          
          <el-tab-pane name="zone">
            <template #label>
              <span class="tab-label">
                <el-icon><Location /></el-icon>
                分区管理
              </span>
            </template>
            <ZoneManage @update:count="fetchStats" />
          </el-tab-pane>
          
          <el-tab-pane name="road">
            <template #label>
              <span class="tab-label">
                <el-icon><Connection /></el-icon>
                路网管理
              </span>
            </template>
            <RoadNetworkManage @update:count="fetchStats" />
          </el-tab-pane>
          
          <el-tab-pane name="emergency">
            <template #label>
              <span class="tab-label">
                <el-icon><Warning /></el-icon>
                应急点位
              </span>
            </template>
            <EmergencyManage />
          </el-tab-pane>
          
          <el-tab-pane name="config">
            <template #label>
              <span class="tab-label">
                <el-icon><Setting /></el-icon>
                系统配置
              </span>
            </template>
            <SystemConfig />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { 
  User, SwitchButton, DataLine, OfficeBuilding, 
  Location, Connection, Warning, Setting, Mic
} from '@element-plus/icons-vue'
import VenueManage from '../components/VenueManage.vue'
import ZoneManage from '../components/ZoneManage.vue'
import RoadNetworkManage from '../components/RoadNetworkManage.vue'
import RealTimeMonitor from '../components/RealTimeMonitor.vue'
import EmergencyManage from '../components/EmergencyManage.vue'
import SystemConfig from '../components/SystemConfig.vue'
import PerformanceManage from '../components/PerformanceManage.vue'

const router = useRouter()
const API_URL = 'https://secureachievement.up.railway.app'

const activeTab = ref('monitor')
const venueCount = ref(0)
const zoneCount = ref(0)
const roadCount = ref(0)
const emergencyCount = ref(0)

async function fetchStats() {
  try {
    const venues = await axios.get(`${API_URL}/api/venues`)
    venueCount.value = venues.data.length
    
    const zones = await axios.get(`${API_URL}/api/venues/1/zones`)
    zoneCount.value = zones.data.length
    
    const roads = await axios.get(`${API_URL}/api/venues/1/road_network`)
    roadCount.value = roads.data.length
    
    const emergency = await axios.get(`${API_URL}/api/emergency/points`)
    emergencyCount.value = emergency.data.length
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

function logout() {
  localStorage.removeItem('token')
  ElMessage.success('已退出登录')
  router.push('/')
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.admin-container {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 背景动画 */
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
    #1a1a2e 0%, 
    #16213e 50%, 
    #0f3460 100%
  );
  animation: moveGradient 15s ease infinite;
}

@keyframes moveGradient {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(3%, 3%) rotate(1deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

/* 主内容 */
.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* 头部 */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 15px 25px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

.logo {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 36px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.logo-text h1 {
  font-size: 22px;
  color: #333;
  margin: 0;
}

.logo-text p {
  font-size: 12px;
  color: #888;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 20px;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border-radius: 25px;
  color: #333;
  font-size: 14px;
}

.logout-btn {
  background: #f44336;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 8px 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logout-btn:hover {
  background: #d32f2f;
  transform: translateY(-2px);
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.stat-icon {
  font-size: 40px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #888;
  margin-top: 5px;
}

/* 标签页容器 */
.tabs-container {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.admin-tabs {
  --el-tabs-header-height: 50px;
}

.admin-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 5px;
}

.admin-tabs :deep(.el-tabs__nav-wrap) {
  background: transparent;
}

.admin-tabs :deep(.el-tabs__item) {
  border-radius: 10px;
  margin: 0 5px;
  transition: all 0.3s;
  font-weight: 500;
}

.admin-tabs :deep(.el-tabs__item.is-active) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.admin-tabs :deep(.el-tabs__active-bar) {
  display: none;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .admin-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .content-wrapper {
    padding: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 24px;
  }
}
</style>