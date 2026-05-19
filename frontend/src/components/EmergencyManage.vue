<template>
  <div class="manage-container">
    <h3>🚨 应急点位管理</h3>
    
    <div class="toolbar">
      <el-button type="primary" @click="showAddDialog">+ 添加应急点位</el-button>
    </div>
    
    <el-table :data="points" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="点位名称" />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.type)">
            {{ getTypeName(row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="zone_id" label="关联分区" width="100" />
      <el-table-column prop="phone" label="联系电话" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" link @click="editPoint(row)">编辑</el-button>
          <el-button type="danger" link @click="deletePoint(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="点位名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="医疗急救" value="medical" />
            <el-option label="安保点" value="security" />
            <el-option label="消防点" value="fire" />
            <el-option label="应急出口" value="exit" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联分区">
          <el-select v-model="form.zone_id" clearable>
            <el-option v-for="z in zones" :key="z.id" :label="z.name" :value="z.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePoint">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_URL = 'https://secureachievement.up.railway.app'
const points = ref([])
const zones = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加应急点位')
const isEdit = ref(false)
const form = ref({ id: null, name: '', type: 'medical', zone_id: null, phone: '', description: '', status: 1 })

async function fetchPoints() {
  const res = await axios.get(`${API_URL}/api/emergency/points`)
  points.value = res.data
}

async function fetchZones() {
  const res = await axios.get(`${API_URL}/api/venues/1/zones`)
  zones.value = res.data
}

async function savePoint() {
  if (!form.value.name) {
    ElMessage.warning('请输入点位名称')
    return
  }
  
  if (isEdit.value) {
    await axios.put(`${API_URL}/api/emergency/points/${form.value.id}`, null, {
      params: form.value
    })
    ElMessage.success('更新成功')
  } else {
    await axios.post(`${API_URL}/api/emergency/points`, null, {
      params: { ...form.value, venue_id: 1 }
    })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
  fetchPoints()
}

function showAddDialog() {
  isEdit.value = false
  dialogTitle.value = '添加应急点位'
  form.value = { id: null, name: '', type: 'medical', zone_id: null, phone: '', description: '', status: 1 }
  dialogVisible.value = true
}

function editPoint(point) {
  isEdit.value = true
  dialogTitle.value = '编辑应急点位'
  form.value = { ...point }
  dialogVisible.value = true
}

async function deletePoint(id) {
  try {
    await ElMessageBox.confirm('确定删除该应急点位吗？', '提示', { type: 'warning' })
    await axios.delete(`${API_URL}/api/emergency/points/${id}`)
    ElMessage.success('删除成功')
    fetchPoints()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function getTypeName(type) {
  const map = { medical: '医疗急救', security: '安保点', fire: '消防点', exit: '应急出口' }
  return map[type] || type
}

function getTypeTag(type) {
  const map = { medical: 'danger', security: 'warning', fire: 'danger', exit: 'info' }
  return map[type] || 'info'
}

onMounted(() => {
  fetchPoints()
  fetchZones()
})
</script>

<style scoped>
.manage-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
.toolbar {
  margin-bottom: 15px;
}
</style>