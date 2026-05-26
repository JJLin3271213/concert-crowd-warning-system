<template>
  <div class="manage-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="应急点位" name="points">
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
      </el-tab-pane>

      <el-tab-pane name="helpRequests">
        <template #label>
          <span>应急求助记录 <el-badge :value="pendingCount" :hidden="pendingCount === 0" /></span>
        </template>
        <div class="toolbar">
          <el-button type="primary" @click="fetchHelpRequests" :loading="helpLoading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
          <el-select v-model="helpFilter" @change="fetchHelpRequests" placeholder="筛选状态" clearable style="width: 150px; margin-left: 10px;">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </div>

        <el-table :data="helpRequests" stripe>
          <el-table-column prop="id" label="编号" width="70">
            <template #default="{ row }">#{{ row.id }}</template>
          </el-table-column>
          <el-table-column prop="zone_name" label="求助位置" />
          <el-table-column prop="venue_name" label="所属场馆" />
          <el-table-column prop="message" label="补充说明">
            <template #default="{ row }">{{ row.message || '无' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'confirmed' ? 'success' : 'warning'">
                {{ row.status === 'confirmed' ? '已确认' : '待处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="求助时间" width="170" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'pending'"
                type="success"
                size="small"
                @click="confirmHelp(row.id)"
                :loading="confirmLoading === row.id"
              >
                确认收到
              </el-button>
              <span v-else class="confirmed-text">{{ row.confirmed_at }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加/编辑应急点位对话框 -->
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
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

import { API_URL } from '../config.js'

const activeTab = ref('points')
const points = ref([])
const zones = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加应急点位')
const isEdit = ref(false)
const form = ref({ id: null, name: '', type: 'medical', zone_id: null, phone: '', description: '', status: 1 })

// 应急求助记录
const helpRequests = ref([])
const helpLoading = ref(false)
const helpFilter = ref('')
const confirmLoading = ref(null)

const pendingCount = computed(() => helpRequests.value.filter(r => r.status === 'pending').length)

async function fetchPoints() {
  const res = await axios.get(`${API_URL}/api/emergency/points`)
  points.value = res.data
}

async function fetchZones() {
  const res = await axios.get(`${API_URL}/api/venues/1/zones`)
  zones.value = res.data
}

async function fetchHelpRequests() {
  helpLoading.value = true
  try {
    const params = {}
    if (helpFilter.value) params.status = helpFilter.value
    const res = await axios.get(`${API_URL}/api/emergency/help/requests`, { params })
    helpRequests.value = res.data
  } catch (e) {
    console.error('获取求助记录失败:', e)
  } finally {
    helpLoading.value = false
  }
}

async function confirmHelp(helpId) {
  try {
    await ElMessageBox.confirm('确认已收到该求助并正在处理？', '确认回执', { type: 'warning' })
  } catch (e) {
    return
  }
  confirmLoading.value = helpId
  try {
    await axios.put(`${API_URL}/api/emergency/help/${helpId}/confirm`)
    ElMessage.success('已确认收到求助，回执邮件已发送')
    await fetchHelpRequests()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    confirmLoading.value = null
  }
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
  fetchHelpRequests()
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
.confirmed-text {
  font-size: 12px;
  color: #999;
}
</style>
