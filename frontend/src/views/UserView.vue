<template>
  <div class="user-app">
    <!-- 背景装饰图 -->
    <div class="bg-decorations">
      <img src="/用户端左上.jpg" class="bg-img tl" alt="" />
      <img src="/用户端右上.jpg" class="bg-img tr" alt="" />
      <img src="/用户端中左.jpg" class="bg-img ml" alt="" />
      <img src="/用户端中右.jpg" class="bg-img mr" alt="" />
      <img src="/用户端左下.jpg" class="bg-img bl" alt="" />
      <img src="/用户端右下.jpg" class="bg-img br" alt="" />
    </div>
    <!-- 头部 -->
    <header class="header glass-card">
      <div class="logo-area">
        <div class="logo-ring"><span>林</span></div>
        <div>
          <h1>Concert Flow</h1>
          <p>智能人流预警系统</p>
        </div>
      </div>
      <div class="header-right">
        <MusicPlayer />
        <el-switch v-model="demoMode" active-text="演示" @change="toggleDemo" size="small" style="--el-switch-on-color:var(--accent)" />
        <el-button class="qr-btn" size="small" @click="showQR=true">扫码</el-button>
        <div class="venue-pill">
          <el-select v-model="currentVenueId" @change="switchVenue" popper-class="dark-drop">
            <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </div>
        <span class="live-tag"><i class="dot" />LIVE</span>
        <el-button v-if="!isLoggedIn" class="ghost-btn" @click="showLoginDialog = true">管理员</el-button>
        <el-button v-else class="ghost-btn" @click="goToAdmin">后台</el-button>
      </div>
    </header>

    <!-- 统计条 -->
    <div class="stat-bar">
      <div class="stat-item glass-card">
        <div class="stat-icon-box green"><span>{{ totalCount }}</span></div>
        <div class="stat-meta"><small>实时人数</small><span>/ {{ totalCapacity }}</span></div>
      </div>
      <div class="stat-item glass-card">
        <div class="stat-icon-box blue"><span>{{ overallRate }}%</span></div>
        <div class="stat-meta"><small>拥挤指数</small></div>
      </div>
      <div :class="['stat-item','glass-card',{warn:alertZones>0}]">
        <div class="stat-icon-box orange"><span>{{ alertZones }}</span></div>
        <div class="stat-meta"><small>预警分区</small></div>
      </div>
    </div>

    <!-- 演出信息 -->
    <div v-if="performances.length" class="perf-strip glass-card">
      <span class="perf-dot" />
      <span v-for="p in performances" :key="p.id">{{ p.artist_name }} — {{ p.performance_date }} {{ p.start_time }}</span>
    </div>

    <!-- 导航tab -->
    <div class="nav-tabs">
      <button :class="{active:activeTab==='overview'}" @click="activeTab='overview'">总览</button>
      <button :class="{active:activeTab==='zones'}" @click="activeTab='zones'">分区</button>
      <button :class="{active:activeTab==='charts'}" @click="activeTab='charts'">数据</button>
      <button :class="{active:activeTab==='route'}" @click="activeTab='route'">路线</button>
      <button :class="{active:activeTab==='help'}" @click="activeTab='help'">应急</button>
    </div>

    <!-- 分区状态 -->
    <!-- 全场馆总览 -->
    <section v-show="activeTab==='overview'" class="overview-section">
      <div v-for="v in allVenueData" :key="v.id" class="glass-card venue-summary" @click="currentVenueId=v.id;activeTab='zones';refresh();fetchPerformances()" style="cursor:pointer">
        <div class="vs-header"><strong>{{ v.name }}</strong><span :class="['vs-badge',v.worstLevel]">{{ v.worstLevel==='red'?'严重':v.worstLevel==='orange'?'拥堵':v.worstLevel==='yellow'?'较堵':'畅通' }}</span></div>
        <div class="vs-stats">
          <span>{{ v.totalPeople }}人 / {{ v.totalCap }}人</span>
          <span>拥挤度 {{ v.avgRate }}%</span>
          <span>{{ v.alertCount }}个预警分区</span>
        </div>
        <div class="vs-bar"><div :style="{width:v.avgRate+'%',background:levelColor(v.worstLevel)}" /></div>
      </div>
    </section>

    <section v-show="activeTab==='zones'">
      <div class="zone-grid">
        <div v-for="z in zones" :key="z.zone_id" :class="['zone-card','glass-card',z.level]">
          <div class="zone-top">
            <span :class="['zone-dot',z.level]" />
            <strong>{{ z.zone_name }}</strong>
            <span :class="['badge',z.level]">{{ levelText(z.level) }}</span>
          </div>
          <div class="zone-body">
            <span class="zone-count">{{ z.current_count }}<small> / {{ z.capacity }}</small>
              <span v-if="getTrend(z.zone_id)===1" class="trend-up">↑</span>
              <span v-else-if="getTrend(z.zone_id)===-1" class="trend-down">↓</span>
            </span>
            <div class="zone-bar"><div :class="['zone-fill',z.level]" :style="{width:z.congestion_rate+'%'}" /></div>
            <span class="zone-rate">{{ z.congestion_rate }}%</span>
          </div>
          <div class="zone-footer-info">
            <span class="zfi-evac">预计疏散 {{ z.evacuation_minutes }}分钟</span>
            <span class="zfi-action">{{ z.action }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 图表 -->
    <section v-show="activeTab==='charts'" class="charts-section">
      <div class="glass-card chart-wrap"><Heatmap :zones-data="zones" /></div>
      <div class="glass-card chart-wrap"><TrendChart :zones="zones" /></div>
      <div class="glass-card chart-wrap"><PredictChart :zones="zones" /></div>
    </section>

    <!-- 路线 -->
    <section v-show="activeTab==='route'" class="glass-card panel-purple" style="padding:20px">
      <RoutePlanner :venue-id="currentVenueId" />
    </section>

    <!-- 应急 -->
    <section v-show="activeTab==='help'" class="help-section">
      <div class="glass-card help-card">
        <h3>SOS 应急求助</h3>
        <el-select v-model="helpZoneId" popper-class="dark-drop" class="w-full" placeholder="选择位置">
          <el-option v-for="z in zones" :key="z.zone_id" :label="z.zone_name" :value="z.zone_id" />
        </el-select>
        <el-input v-model="helpMessage" type="textarea" :rows="2" placeholder="补充说明（选填）" />
        <el-button type="danger" class="sos-btn" @click="sendHelp" :loading="helpLoading">
          {{ helpLoading ? '发送中...' : '一键求助' }}
        </el-button>
        <div v-if="helpSent && helpResult" :class="['help-result',helpResult.status]">
          <span class="help-icon">{{ helpResult.status==='confirmed'?'✓':'⟳' }}</span>
          <span>{{ helpStatusText }}</span>
          <small>编号 #{{ helpResult.help_id }}</small>
        </div>
      </div>
      <div v-if="nearbyPoints.length" class="glass-card nearby-panel">
        <h3>附近应急点位</h3>
        <div v-for="p in nearbyPoints" :key="p.id" class="nearby-row">
          <span class="nearby-ico">{{ p.type==='medical'?'🏥':p.type==='security'?'👮':p.type==='fire'?'🧯':'🚪' }}</span>
          <div><strong>{{ p.name }}</strong><small>{{ p.description }} · {{ p.steps }}步</small></div>
        </div>
      </div>
    </section>

    <!-- 登录弹窗 -->
    <el-dialog v-model="showLoginDialog" title="管理员登录" width="380px">
      <el-form label-width="70px">
        <el-form-item label="用户名"><el-input v-model="loginForm.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="loginForm.password" type="password" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLoginDialog=false">取消</el-button>
        <el-button type="primary" @click="handleLogin">登录</el-button>
      </template>
    </el-dialog>

    <!-- 二维码弹窗 -->
    <el-dialog v-model="showQR" title="扫码进入系统" width="340px" center>
      <div style="text-align:center;padding:10px 0">
        <img :src="qrUrl" style="width:200px;height:200px;border-radius:12px;background:#fff;padding:8px" @error="qrError=true" />
        <p v-if="qrError" style="color:var(--red);font-size:12px;margin-top:10px">二维码加载失败，请检查网络</p>
        <p v-else style="color:var(--text-secondary);font-size:12px;margin-top:10px">扫描二维码直接进入人流预警系统</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import Heatmap from '../components/Heatmap.vue'
import TrendChart from '../components/TrendChart.vue'
import RoutePlanner from '../components/RoutePlanner.vue'
import PredictChart from '../components/PredictChart.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import { cachedFetch } from '../cache.js'
import { API_URL } from '../config.js'

const router = useRouter()
const activeTab = ref('zones')
const zones = ref([])
const venues = ref([])
const currentVenueId = ref(1)
const performances = ref([])
const isLoggedIn = ref(false)
const showLoginDialog = ref(false)
const loginForm = ref({ username: '林俊杰', password: '03271307' })
let timer = null
const demoMode = ref(false); let demoTimer = null
const showQR = ref(false); const qrError = ref(false)
const qrUrl = computed(()=>{qrError.value=false;return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(window.location.href)}`})

function toggleDemo(v){if(v){startDemo()}else{stopDemo()}}
function startDemo(){demoMode.value=true;let step=0;demoTimer=setInterval(()=>{step++;if(step%3===0){const vi=venues.value;if(vi.length){const idx=vi.findIndex(v=>v.id===currentVenueId.value);const next=vi[(idx+1)%vi.length];if(next)switchVenue(next.id)}}if(step%3===1)activeTab.value='charts';if(step%3===2)activeTab.value='zones'},8000)}
function stopDemo(){demoMode.value=false;if(demoTimer){clearInterval(demoTimer);demoTimer=null}}

const totalCount = computed(() => zones.value.reduce((s,z)=>s+z.current_count,0))
const totalCapacity = computed(() => zones.value.reduce((s,z)=>s+z.capacity,0))
const overallRate = computed(()=>totalCapacity.value?Math.round(totalCount.value/totalCapacity.value*100):0)
const alertZones = computed(()=>zones.value.filter(z=>z.level!=='green').length)

function levelColor(l){return{green:'#22d67a',yellow:'#f5c842',orange:'#ff8c42',red:'#ff4d5a'}[l]||'#999'}

const allVenueData = ref([])
async function fetchAllVenueOverview(){try{const vs=await axios.get(`${API_URL}/api/venues`);const data=[];for(const v of vs.data){const r=await axios.get(`${API_URL}/api/crowd/latest?venue_id=${v.id}`);const zones=r.data;if(!zones.length)continue;const tp=zones.reduce((s,z)=>s+z.current_count,0);const tc=zones.reduce((s,z)=>s+z.capacity,0);const ar=Math.round(tp/tc*100);const ac=zones.filter(z=>z.level!=='green').length;const wl=zones.some(z=>z.level==='red')?'red':zones.some(z=>z.level==='orange')?'orange':zones.some(z=>z.level==='yellow')?'yellow':'green';data.push({id:v.id,name:v.name,totalPeople:tp,totalCap:tc,avgRate:ar,alertCount:ac,worstLevel:wl})}allVenueData.value=data}catch(e){}}

const prevCounts = ref({})
function getTrend(zoneId){const prev=prevCounts.value[zoneId];const cur=zones.value.find(z=>z.zone_id===zoneId)?.current_count;if(prev===undefined||cur===undefined)return 0;return cur>prev?1:cur<prev?-1:0}

const helpZoneId = ref(null)
const helpMessage = ref('')
const helpLoading = ref(false)
const helpSent = ref(false)
const helpResult = ref(null)
const helpStatusText = ref('')
let helpPoll = null
const nearbyPoints = ref([])

function levelText(l){return {green:'畅通',yellow:'较堵',orange:'拥堵',red:'严重'}[l]||l}

async function refresh(){try{const url=`${API_URL}/api/crowd/latest?venue_id=${currentVenueId.value}`;const newData=await cachedFetch(url,8000);newData.forEach(z=>{prevCounts.value[z.zone_id]=zones.value.find(o=>o.zone_id===z.zone_id)?.current_count});zones.value=newData}catch(e){console.warn('数据加载失败')}}
async function fetchVenues(){try{const r=await axios.get(`${API_URL}/api/venues`);venues.value=r.data;if(venues.value.length)currentVenueId.value=venues.value[0].id}catch(e){}}
async function fetchPerformances(){try{const r=await axios.get(`${API_URL}/api/performances`,{params:{venue_id:currentVenueId.value}});performances.value=r.data}catch(e){}}
async function switchVenue(id){currentVenueId.value=id;await refresh();await fetchPerformances();await fetchNearby()}
async function handleLogin(){try{const r=await axios.post(`${API_URL}/api/login`,null,{params:loginForm.value});localStorage.setItem('token',r.data.access_token);isLoggedIn.value=true;showLoginDialog.value=false;ElMessage.success('登录成功')}catch(e){ElMessage.error('用户名或密码错误')}}
function goToAdmin(){router.push('/admin')}
function checkLogin(){isLoggedIn.value=!!localStorage.getItem('token')}

async function sendHelp(){
  if(!helpZoneId.value){ElMessage.warning('请选择您当前的位置');return}
  helpLoading.value=true;helpSent.value=false;helpResult.value=null
  try{const r=await axios.post(`${API_URL}/api/emergency/help`,null,{params:{zone_id:helpZoneId.value,message:helpMessage.value,venue_id:currentVenueId.value}});helpResult.value=r.data;helpSent.value=true;helpStatusText.value='管理员已收到求助，正在处理中...';ElMessage.success('求助已发送');helpMessage.value='';if(helpPoll)clearInterval(helpPoll);helpPoll=setInterval(()=>pollStatus(r.data.help_id),5000)}catch(e){ElMessage.error('发送失败')}finally{helpLoading.value=false}
}
async function pollStatus(id){try{const r=await axios.get(`${API_URL}/api/emergency/help/${id}/status`);if(r.data.status==='confirmed'){helpStatusText.value='管理员已确认，工作人员正赶往现场！';if(helpResult.value)helpResult.value.status='confirmed';if(helpPoll){clearInterval(helpPoll);helpPoll=null}}}catch(e){}}
async function fetchNearby(){if(!helpZoneId.value)return;try{const r=await axios.get(`${API_URL}/api/emergency/nearby`,{params:{zone_id:helpZoneId.value||zones.value[0]?.zone_id,venue_id:currentVenueId.value}});nearbyPoints.value=r.data}catch(e){}}

onMounted(()=>{checkLogin();fetchVenues();refresh();fetchPerformances();fetchAllVenueOverview();timer=setInterval(refresh,5000);fetchNearby()})
onUnmounted(()=>{if(timer)clearInterval(timer);if(helpPoll)clearInterval(helpPoll)})
watch(helpZoneId,()=>fetchNearby())
</script>

<style scoped>
.user-app { max-width: 800px; margin: 0 auto; padding: 16px 16px 100px; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; margin-bottom: 20px; }
.logo-area { display: flex; align-items: center; gap: 12px; }
.logo-ring { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, var(--accent), #a855f7); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 18px; color: #fff; box-shadow: 0 0 20px var(--accent-glow); }
.logo-area h1 { font-size: 18px; color: #fff; margin: 0; }
.logo-area p { font-size: 11px; color: var(--text-secondary); margin: 0; }
.header-right { display: flex; align-items: center; gap: 10px; }
.venue-pill :deep(.el-input__wrapper) { border-radius: 20px !important; min-width: 140px; }
.live-tag { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: var(--red); background: rgba(255,77,90,0.15); padding: 4px 12px; border-radius: 20px; letter-spacing: 1px; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--red); animation: pulse-dot 1.2s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(1.5)} }
.ghost-btn { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.12) !important; color: var(--text-secondary) !important; border-radius: 20px !important; font-size: 12px !important; }
.qr-btn { background: var(--purple-surface) !important; border: 1px solid rgba(140,110,230,0.25) !important; color: var(--text-secondary) !important; border-radius: 20px !important; font-size: 12px !important; }

.stat-bar { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 20px; }
.stat-item { padding: 16px; display: flex; align-items: center; gap: 14px; }
.stat-item.warn { border-color: rgba(255,77,90,0.3); animation: pulse-warn 2s infinite; }
.stat-icon-box { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: #fff; }
.stat-icon-box.green { background: linear-gradient(135deg, #22d67a, #0ea95a); }
.stat-icon-box.blue { background: linear-gradient(135deg, #42a5f5, #1e6fcc); }
.stat-icon-box.orange { background: linear-gradient(135deg, #ff8c42, #e06925); }
.stat-meta small { display: block; font-size: 11px; color: var(--text-secondary); }
.stat-meta span { font-size: 12px; color: var(--text-primary); }

.perf-strip { display: flex; align-items: center; gap: 10px; padding: 10px 18px; margin-bottom: 20px; font-size: 13px; color: var(--text-secondary); }
.perf-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); animation: pulse-dot 2s infinite; }

.nav-tabs { display: flex; gap: 6px; margin-bottom: 20px; background: rgba(255,255,255,0.03); border-radius: 14px; padding: 4px; }
.nav-tabs button { flex: 1; padding: 10px; border: none; border-radius: 12px; background: transparent; color: var(--text-secondary); font-size: 13px; font-weight: 600; cursor: pointer; transition: all .3s; }
.nav-tabs button.active { background: var(--accent); color: #fff; box-shadow: 0 4px 15px var(--accent-glow); }

.zone-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; }
.zone-card { padding: 16px; }
.zone-top { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.zone-dot { width: 9px; height: 9px; border-radius: 50%; }
.zone-dot.green { background: var(--green); box-shadow: 0 0 8px rgba(34,214,122,.4); }
.zone-dot.yellow { background: var(--yellow); box-shadow: 0 0 8px rgba(245,200,66,.4); }
.zone-dot.orange { background: var(--orange); box-shadow: 0 0 8px rgba(255,140,66,.4); }
.zone-dot.red { background: var(--red); box-shadow: 0 0 8px rgba(255,77,90,.4); animation: pulse-dot 1s infinite; }
.zone-top strong { font-size: 14px; color: #fff; flex: 1; }
.badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: 700; }
.badge.green { background: rgba(34,214,122,.15); color: var(--green); }
.badge.yellow { background: rgba(245,200,66,.15); color: var(--yellow); }
.badge.orange { background: rgba(255,140,66,.15); color: var(--orange); }
.badge.red { background: rgba(255,77,90,.15); color: var(--red); }
.zone-body { display: flex; align-items: center; gap: 8px; }
.zone-count { font-size: 22px; font-weight: 800; color: #fff; min-width: 90px; }
.zone-count small { font-size: 12px; font-weight: 400; color: var(--text-secondary); }
.trend-up { color: var(--red); font-size: 14px; margin-left: 4px; animation: pulse-dot 1s infinite; }
.trend-down { color: var(--green); font-size: 14px; margin-left: 4px; }
.zone-bar { flex: 1; height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; }
.zone-fill { height: 100%; border-radius: 3px; transition: width .6s; }
.zone-fill.green { background: var(--green); }
.zone-fill.yellow { background: var(--yellow); }
.zone-fill.orange { background: var(--orange); }
.zone-fill.red { background: var(--red); animation: pulse-bar 1s infinite; }
@keyframes pulse-bar { 0%,100%{opacity:1}50%{opacity:.5} }
.zone-rate { font-size: 12px; font-weight: 700; color: var(--text-secondary); min-width: 38px; text-align: right; }
.zone-footer-info { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 11px; }
.zfi-evac { color: var(--text-secondary); }
.zfi-action { color: var(--accent); font-weight: 600; }

.charts-section { display: flex; flex-direction: column; gap: 16px; }
.chart-wrap { padding: 20px; background: var(--purple-glass) !important; border: 1px solid rgba(140,110,230,0.12) !important; }

.overview-section { display: flex; flex-direction: column; gap: 14px; }
.venue-summary { padding: 18px; transition: all .3s; }
.venue-summary:hover { background: var(--purple-glass-strong); transform: translateY(-2px); }
.vs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.vs-header strong { font-size: 16px; color: #fff; }
.vs-badge { padding: 3px 10px; border-radius: 10px; font-size: 10px; font-weight: 700; }
.vs-badge.green { background: rgba(34,214,122,.15); color: #22d67a; }
.vs-badge.yellow { background: rgba(245,200,66,.15); color: #f5c842; }
.vs-badge.orange { background: rgba(255,140,66,.15); color: #ff8c42; }
.vs-badge.red { background: rgba(255,77,90,.15); color: #ff4d5a; }
.vs-stats { display: flex; gap: 20px; font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; flex-wrap: wrap; }
.vs-bar { height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.vs-bar div { height: 100%; border-radius: 3px; transition: width .6s; }

.help-section { display: flex; flex-direction: column; gap: 16px; }
.help-card { padding: 20px; }
.help-card h3, .nearby-panel h3 { margin-bottom: 14px; font-size: 16px; color: #fff; }
.w-full { width: 100%; margin-bottom: 12px; }
.nearby-panel { padding: 18px; }
.sos-btn { width: 100%; height: 46px; font-size: 15px; font-weight: 700; margin-top: 8px; background: linear-gradient(135deg, #ff4d5a, #e91e63) !important; border: none !important; border-radius: 12px !important; }
.help-result { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px; margin-top: 12px; border-radius: 12px; }
.help-result.pending { background: rgba(255,140,66,.1); border: 1px solid rgba(255,140,66,.3); }
.help-result.confirmed { background: rgba(34,214,122,.1); border: 1px solid rgba(34,214,122,.3); }
.help-icon { font-size: 22px; }
.help-result small { font-size: 11px; color: var(--text-secondary); }
.nearby-panel { padding: 18px; }
.nearby-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.nearby-row:last-child { border: none; }
.nearby-ico { font-size: 22px; }
.nearby-row strong { display: block; font-size: 13px; color: #fff; }
.nearby-row small { font-size: 11px; color: var(--text-secondary); }

/* 背景装饰图 */
.bg-decorations { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.bg-img { position: absolute; opacity: 0.80; transition: opacity 0.8s; object-fit: cover; animation: float-bg 6s ease-in-out infinite; }
.bg-img:hover { opacity: 0.95; }
.bg-img:nth-child(odd) { animation-duration: 7s; animation-delay: -2s; }
.bg-img:nth-child(even) { animation-duration: 5.5s; animation-delay: -1s; }
@keyframes float-bg {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(4px, -6px) rotate(0.5deg); }
  50% { transform: translate(-3px, 4px) rotate(-0.3deg); }
  75% { transform: translate(-5px, -3px) rotate(0.4deg); }
}
.bg-img.tl { top: 20px; left: 20px; width: 360px; height: 270px; border-radius: 16px; }
.bg-img.tr { top: 20px; right: 20px; width: 360px; height: 270px; border-radius: 16px; }
.bg-img.ml { top: calc(50% - 150px); left: 15px; width: 375px; height: 300px; border-radius: 14px; }
.bg-img.mr { top: calc(50% - 150px); right: 15px; width: 375px; height: 300px; border-radius: 14px; }
.bg-img.bl { bottom: 20px; left: 20px; width: 360px; height: 255px; border-radius: 16px; }
.bg-img.br { bottom: 20px; right: 20px; width: 360px; height: 255px; border-radius: 16px; object-position: 10% center; }

@media (max-width: 768px) {
  .user-app { padding: 10px 10px 110px; }
  .bg-img { width: 150px !important; height: 120px !important; opacity: 0.08; }
  .bg-img.tl { top: 5px; left: 5px; }
  .bg-img.tr { top: 5px; right: 5px; }
  .bg-img.ml { top: 50%; left: 3px; width: 140px !important; height: 110px !important; transform: translateY(-50%); }
  .bg-img.mr { top: 50%; right: 3px; width: 140px !important; height: 110px !important; transform: translateY(-50%); }
  .bg-img.bl { bottom: 5px; left: 5px; }
  .bg-img.br { bottom: 5px; right: 5px; }
  .stat-bar { grid-template-columns: repeat(3,1fr); gap: 8px; }
  .stat-icon-box { width: 40px; height: 40px; font-size: 16px; border-radius: 10px; }
  .stat-item { padding: 10px; gap: 10px; }
  .zone-grid { grid-template-columns: 1fr; }
  .zone-count { font-size: 18px; }
  .header { flex-wrap: wrap; gap: 10px; }
  .logo-area h1 { font-size: 16px; }
}
</style>
