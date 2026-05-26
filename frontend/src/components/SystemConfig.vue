<template>
  <div class="cfg-wrap">
    <el-tabs v-model="tab">
      <el-tab-pane label="系统参数" name="params">
        <div class="cfg-grid">
          <div class="cfg-item glass-card">
            <label>邮件接收地址</label>
            <div class="cfg-row"><el-input v-model="config.email_receiver" /><el-button size="small" type="primary" @click="saveConfig('email_receiver',config.email_receiver)">保存</el-button></div>
          </div>
          <div class="cfg-item glass-card">
            <label>预警阈值 (%)</label>
            <div class="cfg-row"><el-input-number v-model="config.alert_threshold" :min="0" :max="100" size="small" /><el-button size="small" type="primary" @click="saveConfig('alert_threshold',config.alert_threshold)">保存</el-button></div>
          </div>
          <div class="cfg-item glass-card">
            <label>刷新间隔 (秒)</label>
            <div class="cfg-row"><el-input-number v-model="config.refresh_interval" :min="1" :max="60" size="small" /><el-button size="small" type="primary" @click="saveConfig('refresh_interval',config.refresh_interval)">保存</el-button></div>
          </div>
          <div class="cfg-item glass-card">
            <label>数据保留 (天)</label>
            <div class="cfg-row"><el-input-number v-model="config.data_retention_days" :min="1" :max="365" size="small" /><el-button size="small" type="primary" @click="saveConfig('data_retention_days',config.data_retention_days)">保存</el-button></div>
          </div>
          <div class="cfg-item glass-card">
            <label>拥堵权重系数 α</label>
            <div class="cfg-row"><el-input-number v-model="config.congestion_alpha" :min="0.5" :max="5" :step="0.1" :precision="1" size="small" /><el-button size="small" type="primary" @click="saveConfig('congestion_alpha',config.congestion_alpha)">保存</el-button></div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="修改密码" name="password">
        <div class="glass-card pwd-card">
          <h4>修改管理员密码</h4>
          <el-form :model="pwdForm" label-width="80px" style="max-width:400px">
            <el-form-item label="原密码"><el-input v-model="pwdForm.old" type="password" show-password /></el-form-item>
            <el-form-item label="新密码"><el-input v-model="pwdForm.new1" type="password" show-password /></el-form-item>
            <el-form-item label="确认密码"><el-input v-model="pwdForm.new2" type="password" show-password /></el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="pwdLoading">修改密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <el-tab-pane label="系统信息" name="info">
        <div class="glass-card" style="padding:20px">
          <div class="info-grid">
            <div class="info-item"><span>系统版本</span><strong>2.0.0</strong></div>
            <div class="info-item"><span>后端状态</span><strong class="g">运行中</strong></div>
            <div class="info-item"><span>数据库</span><strong class="g">已连接</strong></div>
            <div class="info-item"><span>最后更新</span><strong>{{ lastUpdateTime }}</strong></div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { API_URL } from '../config.js'

const tab = ref('params')
const lastUpdateTime = ref('--')
const config = ref({ email_receiver: '', alert_threshold: 80, refresh_interval: 5, data_retention_days: 30, congestion_alpha: 2.0 })
const pwdForm = ref({ old: '', new1: '', new2: '' })
const pwdLoading = ref(false)

async function loadConfig() {
  const keys = ['email_receiver', 'alert_threshold', 'refresh_interval', 'data_retention_days', 'congestion_alpha']
  for (const key of keys) {
    try { const r = await axios.get(`${API_URL}/api/config`, { params: { key } }); if (r.data.value) config.value[key] = isNaN(r.data.value) ? r.data.value : Number(r.data.value) } catch (e) { /* */ }
  }
}
async function saveConfig(key, value) {
  try { await axios.post(`${API_URL}/api/config`, null, { params: { key, value: String(value) } }); ElMessage.success('已保存') } catch (e) { ElMessage.error('保存失败') }
}
async function changePassword() {
  if (!pwdForm.value.old || !pwdForm.value.new1) { ElMessage.warning('请填写完整'); return }
  if (pwdForm.value.new1 !== pwdForm.value.new2) { ElMessage.warning('两次新密码不一致'); return }
  if (pwdForm.value.new1.length < 6) { ElMessage.warning('新密码至少6位'); return }
  pwdLoading.value = true
  try {
    const token = localStorage.getItem('token')
    await axios.put(`${API_URL}/api/change-password`, null, { params: { old_password: pwdForm.value.old, new_password: pwdForm.value.new1 }, headers: { Authorization: `Bearer ${token}` } })
    ElMessage.success('密码修改成功')
    pwdForm.value = { old: '', new1: '', new2: '' }
  } catch (e) { ElMessage.error(e.response?.data?.detail || '修改失败') }
  finally { pwdLoading.value = false }
}
async function getLastUpdate() {
  try { const r = await axios.get(`${API_URL}/api/crowd/latest`); if (r.data.length && r.data[0].timestamp) lastUpdateTime.value = new Date(r.data[0].timestamp).toLocaleString() } catch (e) { /* */ }
}
onMounted(() => { loadConfig(); getLastUpdate() })
</script>

<style scoped>
.cfg-wrap { background: transparent; }
.cfg-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.cfg-item { padding: 16px; }
.cfg-item label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
.cfg-row { display: flex; gap: 8px; align-items: center; }
.pwd-card { padding: 20px; }
.pwd-card h4 { color: #fff; margin-bottom: 16px; }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.info-item { display: flex; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 10px; font-size: 13px; }
.info-item span { color: var(--text-secondary); }
.info-item strong { color: #fff; }
.info-item .g { color: var(--green); }
@media (max-width: 768px) { .cfg-grid { grid-template-columns: 1fr; } }
</style>
