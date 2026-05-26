<template>
  <div class="manage-container">
    <h3>📍 分区管理</h3>
    
    <div class="toolbar">
      <el-select v-model="selectedVenueId" placeholder="选择场馆" @change="fetchZones">
        <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
      </el-select>
      <el-button type="primary" @click="showAddDialog">+ 添加分区</el-button>
    </div>
    
    <el-table :data="zones" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分区名称" />
      <el-table-column prop="capacity" label="容量" />
      <el-table-column prop="is_exit" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_exit ? 'danger' : 'info'">
            {{ row.is_exit ? '出口' : '分区' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" link @click="editZone(row)">编辑</el-button>
          <el-button type="danger" link @click="deleteZone(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="分区名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="form.capacity" :min="0" />
        </el-form-item>
        <el-form-item label="是否为出口">
          <el-switch v-model="form.is_exit" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveZone">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

import { API_URL } from '../config.js'
const venues = ref([])
const zones = ref([])
const selectedVenueId = ref(1)
const dialogVisible = ref(false)
const dialogTitle = ref('添加分区')
const isEdit = ref(false)
const form = ref({ id: null, name: '', capacity: 0, is_exit: 0, sort_order: 0 })

async function fetchVenues() {
  const res = await axios.get(`${API_URL}/api/venues`)
  venues.value = res.data
}

async function fetchZones() {
  const res = await axios.get(`${API_URL}/api/venues/${selectedVenueId.value}/zones`)
  zones.value = res.data
}

async function saveZone() {
  if (!form.value.name) {
    ElMessage.warning('请输入分区名称')
    return
  }
  
  if (isEdit.value) {
    await axios.put(`${API_URL}/api/zones/${form.value.id}`, null, {
      params: {
        name: form.value.name,
        capacity: form.value.capacity,
        is_exit: form.value.is_exit,
        sort_order: form.value.sort_order
      }
    })
    ElMessage.success('更新成功')
  } else {
    await axios.post(`${API_URL}/api/zones`, null, {
      params: {
        venue_id: selectedVenueId.value,
        name: form.value.name,
        capacity: form.value.capacity,
        is_exit: form.value.is_exit,
        sort_order: form.value.sort_order
      }
    })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
  fetchZones()
}

function showAddDialog() {
  isEdit.value = false
  dialogTitle.value = '添加分区'
  form.value = { id: null, name: '', capacity: 0, is_exit: 0, sort_order: 0 }
  dialogVisible.value = true
}

function editZone(zone) {
  isEdit.value = true
  dialogTitle.value = '编辑分区'
  form.value = { ...zone }
  dialogVisible.value = true
}

async function deleteZone(id) {
  try {
    await ElMessageBox.confirm('确定删除该分区吗？', '提示', { type: 'warning' })
    await axios.delete(`${API_URL}/api/zones/${id}`)
    ElMessage.success('删除成功')
    fetchZones()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchVenues()
  fetchZones()
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
  display: flex;
  gap: 10px;
}
</style>