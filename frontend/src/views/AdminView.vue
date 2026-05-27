<template>
  <div class="admin-app">
    <header class="admin-header glass-card">
      <div class="h-left">
        <div class="logo-dot">林</div>
        <div><strong>Concert Flow</strong><small>管理控制台</small></div>
      </div>
      <div class="h-right">
        <MusicPlayer />
        <el-select v-model="adminVenueId" size="small" style="width:160px" popper-class="dark-drop">
          <el-option v-for="v in venueList" :key="v.id" :label="v.name" :value="v.id" />
        </el-select>
        <span class="h-badge">{{ venueCount }}场馆 · {{ zoneCount }}分区 · {{ roadCount }}路网</span>
        <el-button class="ghost-sm" @click="logout">退出</el-button>
      </div>
    </header>

    <div class="admin-tabs">
      <button v-for="t in tabs" :key="t.key" :class="{active:activeTab===t.key}" @click="activeTab=t.key">{{ t.label }}</button>
    </div>

    <div class="admin-body">
      <RealTimeMonitor v-show="activeTab==='monitor'" />
      <AdminStats v-show="activeTab==='stats'" :venue-id="adminVenueId" />
      <div v-show="activeTab==='topology'" class="glass-card" style="padding:20px">
        <RouteGraph :venue-id="1" :highlight-edges="[]" />
        <div style="display:flex;gap:12px;align-items:center;margin-top:14px">
          <el-button type="primary" @click="checkConnectivity" :loading="checkingConn">连通性校验</el-button>
          <div v-if="connResult" :class="['conn-tag',connResult.connected?'ok':'fail']">{{ connResult.message }}</div>
        </div>
      </div>
      <PerformanceManage v-show="activeTab==='perf'" />
      <VenueManage v-show="activeTab==='venue'" @update:count="fetchStats" />
      <ZoneManage v-show="activeTab==='zone'" @update:count="fetchStats" />
      <RoadNetworkManage v-show="activeTab==='road'" @update:count="fetchStats" />
      <EmergencyManage v-show="activeTab==='emergency'" />
      <SystemConfig v-show="activeTab==='config'" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import RealTimeMonitor from '../components/RealTimeMonitor.vue'
import AdminStats from '../components/AdminStats.vue'
import RouteGraph from '../components/RouteGraph.vue'
import PerformanceManage from '../components/PerformanceManage.vue'
import VenueManage from '../components/VenueManage.vue'
import ZoneManage from '../components/ZoneManage.vue'
import RoadNetworkManage from '../components/RoadNetworkManage.vue'
import EmergencyManage from '../components/EmergencyManage.vue'
import SystemConfig from '../components/SystemConfig.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { API_URL } from '../config.js'

const router = useRouter()
const activeTab = ref('monitor')
const tabs = [
  {key:'monitor',label:'实时监控'},{key:'stats',label:'数据统计'},{key:'topology',label:'路网拓扑'},
  {key:'perf',label:'演出'},{key:'venue',label:'场馆'},{key:'zone',label:'分区'},
  {key:'road',label:'路网'},{key:'emergency',label:'应急'},{key:'config',label:'配置'}
]
const venueCount=ref(0);const zoneCount=ref(0);const roadCount=ref(0);const emergencyCount=ref(0)
const adminVenueId=ref(1);const venueList=ref([])

async function fetchVenueList(){try{const r=await axios.get(`${API_URL}/api/venues`);venueList.value=r.data}catch(e){}}
const checkingConn=ref(false);const connResult=ref(null)

async function fetchStats(){
  try{const v=await axios.get(`${API_URL}/api/venues`);venueCount.value=v.data.length;const z=await axios.get(`${API_URL}/api/venues/1/zones`);zoneCount.value=z.data.length;const r=await axios.get(`${API_URL}/api/venues/1/road_network`);roadCount.value=r.data.length}catch(e){}
}
async function checkConnectivity(){checkingConn.value=true;connResult.value=null;try{const r=await axios.get(`${API_URL}/api/road/check-connectivity`);connResult.value=r.data;ElMessage[r.data.connected?'success':'warning'](r.data.message)}catch(e){ElMessage.error('校验失败')}finally{checkingConn.value=false}}
function logout(){localStorage.removeItem('token');ElMessage.success('已退出');router.push('/')}
onMounted(()=>{fetchStats();fetchVenueList()})
</script>

<style scoped>
.admin-app { max-width: 1400px; margin: 0 auto; padding: 16px; min-height: 100vh; }
.admin-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; margin-bottom: 16px; }
.h-left { display: flex; align-items: center; gap: 10px; }
.logo-dot { width: 32px; height: 32px; border-radius: 10px; background: linear-gradient(135deg,var(--accent),#a855f7); box-shadow: 0 0 15px var(--accent-glow); display:flex; align-items:center; justify-content:center; font-weight:900; font-size:16px; color:#fff; }
.h-left strong { font-size: 15px; color: #fff; display: block; }
.h-left small { font-size: 10px; color: var(--text-secondary); }
.h-right { display: flex; align-items: center; gap: 12px; }
.h-badge { font-size: 11px; color: var(--text-secondary); background: rgba(255,255,255,0.04); padding: 4px 12px; border-radius: 10px; }
.ghost-sm { background: rgba(255,77,90,0.1)!important;border:1px solid rgba(255,77,90,0.2)!important;color:var(--red)!important;border-radius:10px!important;font-size:12px!important; }

.admin-tabs { display: flex; gap: 4px; margin-bottom: 16px; overflow-x: auto; padding-bottom: 4px; }
.admin-tabs button { white-space: nowrap; padding: 8px 16px; border: none; border-radius: 10px; background: transparent; color: var(--text-secondary); font-size: 12px; font-weight: 600; cursor: pointer; transition: all .25s; }
.admin-tabs button.active { background: var(--accent); color: #fff; }
.admin-body { min-height: 60vh; }

.conn-tag { padding: 6px 14px; border-radius: 8px; font-size: 12px; }
.conn-tag.ok { background: rgba(34,214,122,.1); color: var(--green); }
.conn-tag.fail { background: rgba(255,77,90,.1); color: var(--red); }

@media (max-width:768px){.admin-app{padding:8px}.admin-tabs button{padding:6px 10px;font-size:11px}}
</style>
