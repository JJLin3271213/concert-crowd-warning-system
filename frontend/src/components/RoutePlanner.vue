<template>
  <div class="route-planner">
    <div class="route-header">
      <h3>🗺️ 智能路线规划</h3>
      <p class="route-desc">根据实时拥堵情况，推荐最优路线</p>
    </div>

    <!-- 起点终点选择 -->
    <div class="route-selectors">
      <div class="selector">
        <label>📍 起点</label>
        <select v-model="startNode" class="node-select">
          <option v-for="node in nodes" :key="node.id" :value="node.id">
            {{ node.name }}
          </option>
        </select>
      </div>
      <div class="selector">
        <label>🏁 终点</label>
        <select v-model="endNode" class="node-select">
          <option v-for="node in nodes" :key="node.id" :value="node.id">
            {{ node.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- 规划按钮 -->
    <div class="route-actions">
      <button @click="planRoute" :disabled="loading" class="plan-btn">
        {{ loading ? '规划中...' : '开始规划' }}
      </button>
      <button @click="evacuate" :disabled="loading" class="evacuate-btn">
        🚨 应急出口
      </button>
    </div>

    <!-- 路线结果 -->
    <div v-if="routeResult" class="route-result">
      <div class="route-summary">
        <div class="summary-item">
          <span class="label">推荐路线</span>
          <span class="value route-path">{{ routeResult.path_names.join(' → ') }}</span>
        </div>
        <div class="summary-item">
          <span class="label">总步数</span>
          <span class="value">{{ routeResult.steps }} 步</span>
        </div>
        <div class="summary-item">
          <span class="label">平均拥堵</span>
          <span class="value" :class="getCongestionClass(routeResult.avg_congestion || 0)">
            {{ routeResult.avg_congestion || 0 }}%
          </span>
        </div>
        <div class="summary-item">
          <span class="label">预计通行时间</span>
          <span class="value">{{ estimatedTime }} 分钟</span>
        </div>
        <div class="summary-item">
          <span class="label">路线状态</span>
          <span class="value" :class="routeResult.is_congested ? 'red' : 'green'">
            {{ routeResult.is_congested ? '⚠️ 较拥堵' : '✅ 可通行' }}
          </span>
        </div>
      </div>

      <!-- 分步详情 -->
      <div class="step-details">
        <div class="step-title">📋 分步导航</div>
        <div v-for="(step, index) in routeSteps" :key="index" class="step-item">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-info">
            <div class="step-route">{{ step.from }} → {{ step.to }}</div>
            <div class="step-status">
              <span class="status-badge" :class="step.level">
                {{ step.level_text }}
              </span>
              <span class="step-congestion" v-if="step.congestion_rate > 0">
                拥挤度: {{ step.congestion_rate }}%
              </span>
              <span class="step-congestion" v-else>入口/出口</span>
            </div>
            <div class="step-suggestion">{{ step.suggestion }}</div>
            <div class="step-time" v-if="step.estimated_minutes">
              ⏱️ 约 {{ step.estimated_minutes }} 分钟
            </div>
          </div>
        </div>
      </div>

      <!-- 拥堵提示 -->
      <div v-if="routeResult.is_congested" class="warning-box">
        <span class="warning-icon">⚠️</span>
        <span>路线存在拥堵，建议预留更多时间或选择其他路线</span>
      </div>
    </div>

    <!-- 应急导航结果 -->
    <div v-if="evacuateResult" class="evacuate-result">
      <div class="evacuate-header">
        <span class="evacuate-icon">🚨</span>
        <span>应急导航</span>
      </div>
      <div class="evacuate-path">
        {{ evacuateResult.path_names.join(' → ') }}
      </div>
      <div class="evacuate-info">
        共 {{ evacuateResult.steps }} 步，约 {{ Math.round(evacuateResult.steps * 1.5) }} 分钟，请尽快撤离
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading && !routeResult" class="loading">
      <div class="spinner"></div>
      <span>正在计算最优路线...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

const API_URL = 'https://secureachievement.up.railway.app'

const props = defineProps({
  venueId: {
    type: Number,
    default: 1
  }
})

const nodes = ref([])
const startNode = ref(null)
const endNode = ref(null)
const loading = ref(false)
const routeResult = ref(null)
const evacuateResult = ref(null)

// 获取所有节点（根据场馆ID）
async function fetchNodes() {
  try {
    const venueId = props.venueId || 1
    console.log('当前场馆ID:', venueId)  // 添加这行
    const response = await axios.get(`${API_URL}/api/route/nodes`, {
      params: { venue_id: venueId }
    })
    console.log('返回的节点:', response.data)  // 添加这行
    if (response.data && response.data.nodes && response.data.nodes.length > 0) {
      nodes.value = response.data.nodes
      // 设置默认起点和终点
      const entrance = nodes.value.find(n => n.name.includes('入口'))
      const exit = nodes.value.find(n => n.name.includes('出口'))
      startNode.value = entrance ? entrance.id : nodes.value[0].id
      endNode.value = exit ? exit.id : nodes.value[nodes.value.length - 1].id
    } else {
      // 备用默认节点
      nodes.value = [
        { id: 1, name: "东看台" }, { id: 2, name: "西看台" },
        { id: 3, name: "南看台" }, { id: 4, name: "北看台" },
        { id: 5, name: "内场VIP区" }, { id: 6, name: "内场普通A区" },
        { id: 7, name: "内场普通B区" }, { id: 8, name: "入口" }, { id: 9, name: "出口" }
      ]
      startNode.value = 8
      endNode.value = 9
    }
  } catch (error) {
    console.error('获取节点失败:', error)
    // 备用默认节点
    nodes.value = [
      { id: 1, name: "东看台" }, { id: 2, name: "西看台" },
      { id: 3, name: "南看台" }, { id: 4, name: "北看台" },
      { id: 5, name: "内场VIP区" }, { id: 6, name: "内场普通A区" },
      { id: 7, name: "内场普通B区" }, { id: 8, name: "入口" }, { id: 9, name: "出口" }
    ]
    startNode.value = 8
    endNode.value = 9
  }
}

// 规划路线
async function planRoute() {
  if (!startNode.value || !endNode.value) {
    alert('请选择起点和终点')
    return
  }
  
  loading.value = true
  routeResult.value = null
  evacuateResult.value = null
  
  try {
    const venueId = props.venueId || 1
    const response = await axios.get(`${API_URL}/api/route/plan`, {
      params: {
        start: startNode.value,
        end: endNode.value,
        venue_id: venueId
      }
    })
    
    if (response.data.error) {
      alert(response.data.error)
    } else {
      routeResult.value = response.data
    }
  } catch (error) {
    console.error('路线规划失败:', error)
    alert('路线规划失败，请重试')
  } finally {
    loading.value = false
  }
}

// 应急导航
async function evacuate() {
  if (!startNode.value) {
    alert('请选择起点')
    return
  }
  
  loading.value = true
  routeResult.value = null
  evacuateResult.value = null
  
  try {
    const venueId = props.venueId || 1
    const response = await axios.get(`${API_URL}/api/route/evacuate/${startNode.value}`, {
      params: { venue_id: venueId }
    })
    
    if (response.data.error) {
      alert(response.data.error)
    } else {
      evacuateResult.value = response.data
    }
  } catch (error) {
    console.error('应急导航失败:', error)
    alert('应急导航失败，请重试')
  } finally {
    loading.value = false
  }
}

// 获取拥堵等级样式
function getCongestionClass(rate) {
  if (rate >= 80) return 'red'
  if (rate >= 60) return 'orange'
  if (rate >= 40) return 'yellow'
  return 'green'
}

// 计算预计通行时间（分钟）- 基于实时拥堵动态计算
const estimatedTime = computed(() => {
  if (!routeResult.value || !routeResult.value.path_details) return 0
  
  const details = routeResult.value.path_details
  let totalMinutes = 0
  
  for (let i = 0; i < details.length - 1; i++) {
    const toNode = details[i + 1]
    const rate = toNode.congestion_rate || 0
    const stepBaseTime = 1.2
    
    if (rate >= 80) {
      totalMinutes += stepBaseTime * 3.5
    } else if (rate >= 60) {
      totalMinutes += stepBaseTime * 2.5
    } else if (rate >= 40) {
      totalMinutes += stepBaseTime * 1.8
    } else if (rate > 0) {
      totalMinutes += stepBaseTime * 1.2
    } else {
      totalMinutes += 1
    }
  }
  
  return Math.round(totalMinutes)
})

// 计算分步详情
const routeSteps = computed(() => {
  if (!routeResult.value || !routeResult.value.path_details) return []
  
  const steps = []
  const details = routeResult.value.path_details
  
  for (let i = 0; i < details.length - 1; i++) {
    const from = details[i]
    const to = details[i + 1]
    const rate = to.congestion_rate || 0
    
    let level = 'green'
    let level_text = '畅通'
    let suggestion = '快速通行'
    let estimated_minutes = 1.2
    
    if (rate >= 80) {
      level = 'red'
      level_text = '严重拥堵'
      suggestion = '强烈建议绕行或耐心等待'
      estimated_minutes = 4.2
    } else if (rate >= 60) {
      level = 'orange'
      level_text = '拥堵'
      suggestion = '建议绕行或耐心等待'
      estimated_minutes = 3
    } else if (rate >= 40) {
      level = 'yellow'
      level_text = '较堵'
      suggestion = '通行较慢，注意安全'
      estimated_minutes = 2.2
    } else if (rate > 0) {
      level = 'green'
      level_text = '畅通'
      suggestion = '快速通行'
      estimated_minutes = 1.5
    } else {
      level = 'info'
      level_text = '入口/出口'
      suggestion = '正常通行'
      estimated_minutes = 1
    }
    
    steps.push({
      from: from.name,
      to: to.name,
      congestion_rate: rate,
      level: level,
      level_text: level_text,
      suggestion: suggestion,
      estimated_minutes: estimated_minutes
    })
  }
  
  return steps
})

// 监听场馆变化，重新获取节点
watch(() => props.venueId, () => {
  fetchNodes()
  routeResult.value = null
  evacuateResult.value = null
})

onMounted(() => {
  fetchNodes()
})
</script>

<style scoped>
.route-planner {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.route-header h3 {
  margin: 0 0 5px 0;
  color: #333;
}

.route-desc {
  font-size: 12px;
  color: #666;
  margin: 0 0 15px 0;
}

.route-selectors {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.selector {
  flex: 1;
  min-width: 120px;
}

.selector label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.node-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: white;
}

.route-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.plan-btn, .evacuate-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.plan-btn {
  background: #4CAF50;
  color: white;
}

.plan-btn:hover:not(:disabled) {
  background: #45a049;
}

.evacuate-btn {
  background: #f44336;
  color: white;
}

.evacuate-btn:hover:not(:disabled) {
  background: #d32f2f;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.route-result, .evacuate-result {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.route-summary {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 15px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #e0e0e0;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-item .label {
  font-size: 13px;
  color: #666;
}

.summary-item .value {
  font-weight: bold;
  font-size: 14px;
}

.route-path {
  font-size: 12px;
  word-break: break-all;
}

.value.green { color: #4CAF50; }
.value.yellow { color: #FFC107; }
.value.orange { color: #FF9800; }
.value.red { color: #f44336; }

.step-details {
  margin-bottom: 15px;
}

.step-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.step-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 10px;
  margin-bottom: 8px;
}

.step-number {
  width: 28px;
  height: 28px;
  background: #2196F3;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.step-info {
  flex: 1;
}

.step-route {
  font-weight: bold;
  margin-bottom: 5px;
}

.step-status {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 5px;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  color: white;
}

.status-badge.green { background: #4CAF50; }
.status-badge.yellow { background: #FFC107; color: #333; }
.status-badge.orange { background: #FF9800; }
.status-badge.red { background: #f44336; }
.status-badge.info { background: #999; }

.step-congestion {
  font-size: 12px;
  color: #666;
}

.step-suggestion {
  font-size: 12px;
  color: #f44336;
}

.step-time {
  font-size: 11px;
  color: #2196F3;
  margin-top: 4px;
}

.warning-box {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  padding: 10px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.warning-icon {
  font-size: 18px;
}

.evacuate-result {
  background: #ffebee;
  border-radius: 12px;
  padding: 15px;
}

.evacuate-header {
  font-weight: bold;
  color: #f44336;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.evacuate-icon {
  font-size: 20px;
}

.evacuate-path {
  font-weight: bold;
  margin-bottom: 8px;
  word-break: break-all;
}

.evacuate-info {
  font-size: 12px;
  color: #666;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-top-color: #4CAF50;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .route-planner {
    padding: 15px;
  }
  
  .summary-item .label,
  .summary-item .value {
    font-size: 12px;
  }
  
  .step-item {
    padding: 10px;
  }
  
  .step-number {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
}
</style>