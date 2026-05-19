<template>
  <div class="manage-container">
    <h3>⚙️ 系统配置</h3>
    
    <el-form label-width="150px">
      <el-form-item label="邮件接收地址">
        <el-input v-model="config.email_receiver" placeholder="接收预警邮件的邮箱" />
        <el-button type="primary" size="small" @click="saveConfig('email_receiver', config.email_receiver)">保存</el-button>
      </el-form-item>
      
      <el-form-item label="预警阈值（%）">
        <el-input-number v-model="config.alert_threshold" :min="0" :max="100" />
        <el-button type="primary" size="small" @click="saveConfig('alert_threshold', config.alert_threshold)">保存</el-button>
      </el-form-item>
      
      <el-form-item label="自动刷新间隔（秒）">
        <el-input-number v-model="config.refresh_interval" :min="1" :max="60" />
        <el-button type="primary" size="small" @click="saveConfig('refresh_interval', config.refresh_interval)">保存</el-button>
      </el-form-item>
      
      <el-form-item label="数据保留天数">
        <el-input-number v-model="config.data_retention_days" :min="1" :max="365" />
        <el-button type="primary" size="small" @click="saveConfig('data_retention_days', config.data_retention_days)">保存</el-button>
      </el-form-item>
    </el-form>
    
    <el-divider />
    
    <h4>系统信息</h4>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="系统版本">1.0.0</el-descriptions-item>
      <el-descriptions-item label="后端状态">
        <el-tag type="success">运行中</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="数据库状态">
        <el-tag type="success">已连接</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="最后数据更新">{{ lastUpdateTime }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = 'https://secureachievement.up.railway.app'
const lastUpdateTime = ref('--')
const config = ref({
  email_receiver: '',
  alert_threshold: 80,
  refresh_interval: 5,
  data_retention_days: 30
})

async function loadConfig() {
  const keys = ['email_receiver', 'alert_threshold', 'refresh_interval', 'data_retention_days']
  for (const key of keys) {
    const res = await axios.get(`${API_URL}/api/config`, { params: { key } })
    if (res.data.value) {
      config.value[key] = res.data.value
    }
  }
}

async function saveConfig(key, value) {
  try {
    await axios.post(`${API_URL}/api/config`, null, { params: { key, value } })
    ElMessage.success('配置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

async function getLastUpdate() {
  const res = await axios.get(`${API_URL}/api/crowd/latest`)
  if (res.data.length > 0 && res.data[0].timestamp) {
    const date = new Date(res.data[0].timestamp)
    lastUpdateTime.value = date.toLocaleString()
  }
}

onMounted(() => {
  loadConfig()
  getLastUpdate()
})
</script>

<style scoped>
.manage-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
</style>