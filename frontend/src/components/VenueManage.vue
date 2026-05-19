<template>
  <div class="manage-container">
    <h3>🏟️ 场馆管理</h3>
    
    <div class="toolbar">
      <el-button type="primary" @click="showAddDialog">+ 添加场馆</el-button>
    </div>
    
    <el-table :data="venues" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="场馆名称" />
      <el-table-column prop="address" label="地址" />
      <el-table-column prop="total_capacity" label="总容量" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" link @click="editVenue(row)">编辑</el-button>
          <el-button type="danger" link @click="deleteVenue(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="场馆名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="总容量">
          <el-input-number v-model="form.total_capacity" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVenue">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_URL = 'https://secureachievement.up.railway.app'
const venues = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加场馆')
const isEdit = ref(false)
const form = ref({ id: null, name: '', address: '', total_capacity: 0 })

async function fetchVenues() {
  const res = await axios.get(`${API_URL}/api/venues`)
  venues.value = res.data
}

async function saveVenue() {
  if (!form.value.name) {
    ElMessage.warning('请输入场馆名称')
    return
  }
  
  if (isEdit.value) {
    await axios.put(`${API_URL}/api/venues/${form.value.id}`, null, {
      params: {
        name: form.value.name,
        address: form.value.address,
        total_capacity: form.value.total_capacity
      }
    })
    ElMessage.success('更新成功')
  } else {
    await axios.post(`${API_URL}/api/venues`, null, {
      params: {
        name: form.value.name,
        address: form.value.address,
        total_capacity: form.value.total_capacity
      }
    })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
  fetchVenues()
}

function showAddDialog() {
  isEdit.value = false
  dialogTitle.value = '添加场馆'
  form.value = { id: null, name: '', address: '', total_capacity: 0 }
  dialogVisible.value = true
}

function editVenue(venue) {
  isEdit.value = true
  dialogTitle.value = '编辑场馆'
  form.value = { ...venue }
  dialogVisible.value = true
}

async function deleteVenue(id) {
  try {
    await ElMessageBox.confirm('确定删除该场馆吗？', '提示', { type: 'warning' })
    await axios.delete(`${API_URL}/api/venues/${id}`)
    ElMessage.success('删除成功')
    fetchVenues()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchVenues()
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