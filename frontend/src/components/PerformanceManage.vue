<template>
  <div class="manage-container panel-purple">
    <h3>🎵 演出信息管理</h3>
    
    <div class="toolbar">
      <el-button type="primary" @click="showAddDialog">+ 添加演出</el-button>
    </div>
    
    <el-table :data="performances" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="artist_name" label="艺人/乐队" />
      <el-table-column prop="performance_date" label="演出日期" width="120" />
      <el-table-column prop="start_time" label="开始时间" width="100" />
      <el-table-column prop="end_time" label="结束时间" width="100" />
      <el-table-column prop="ticket_price" label="票价" width="120" />
      <el-table-column prop="description" label="简介" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" link @click="editPerformance(row)">编辑</el-button>
          <el-button type="danger" link @click="deletePerformance(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="艺人/乐队">
          <el-input v-model="form.artist_name" />
        </el-form-item>
        <el-form-item label="演出日期">
          <el-date-picker v-model="form.performance_date" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="票价">
          <el-input v-model="form.ticket_price" placeholder="如: 380-1280元" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePerformance">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

import { API_URL } from '../config.js'
const performances = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加演出')
const isEdit = ref(false)
const form = ref({ id: null, artist_name: '', performance_date: '', start_time: '', end_time: '', ticket_price: '', description: '' })

async function fetchPerformances() {
  const res = await axios.get(`${API_URL}/api/performances`)
  performances.value = res.data
}

async function savePerformance() {
  if (!form.value.artist_name) {
    ElMessage.warning('请输入艺人/乐队名称')
    return
  }
  
  const params = {
    venue_id: 1,
    artist_name: form.value.artist_name,
    performance_date: form.value.performance_date,
    start_time: form.value.start_time,
    end_time: form.value.end_time,
    ticket_price: form.value.ticket_price,
    description: form.value.description
  }
  
  if (isEdit.value) {
    await axios.put(`${API_URL}/api/performances/${form.value.id}`, null, { params })
    ElMessage.success('更新成功')
  } else {
    await axios.post(`${API_URL}/api/performances`, null, { params })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
  fetchPerformances()
}

function showAddDialog() {
  isEdit.value = false
  dialogTitle.value = '添加演出'
  form.value = { id: null, artist_name: '', performance_date: '', start_time: '', end_time: '', ticket_price: '', description: '' }
  dialogVisible.value = true
}

function editPerformance(performance) {
  isEdit.value = true
  dialogTitle.value = '编辑演出'
  form.value = { ...performance }
  dialogVisible.value = true
}

async function deletePerformance(id) {
  try {
    await ElMessageBox.confirm('确定删除该演出信息吗？', '提示', { type: 'warning' })
    await axios.delete(`${API_URL}/api/performances/${id}`)
    ElMessage.success('删除成功')
    fetchPerformances()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchPerformances()
})
</script>

<style scoped>
.manage-container {
  background: transparent;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
.toolbar {
  margin-bottom: 15px;
}
</style>