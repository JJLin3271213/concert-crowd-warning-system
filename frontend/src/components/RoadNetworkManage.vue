<template>
  <div class="manage-container">
    <h3>🔗 路网管理</h3>
    
    <div class="toolbar">
      <el-select v-model="selectedVenueId" placeholder="选择场馆" @change="fetchRoads">
        <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
      </el-select>
      <el-button type="primary" @click="showAddDialog">+ 添加连接</el-button>
    </div>
    
    <el-table :data="roads" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="from_zone_id" label="起点ID" />
      <el-table-column prop="to_zone_id" label="终点ID" />
      <el-table-column label="起点名称" prop="from_name" />
      <el-table-column label="终点名称" prop="to_name" />
      <el-table-column prop="distance" label="距离" width="80" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="danger" link @click="deleteRoad(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog v-model="dialogVisible" title="添加路网连接" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="起点分区">
          <el-select v-model="form.from_zone_id" placeholder="选择起点">
            <el-option v-for="z in zones" :key="z.id" :label="z.name" :value="z.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="终点分区">
          <el-select v-model="form.to_zone_id" placeholder="选择终点">
            <el-option v-for="z in zones" :key="z.id" :label="z.name" :value="z.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="距离权重">
          <el-input-number v-model="form.distance" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRoad">保存</el-button>
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
const zones = ref([])
const roads = ref([])
const selectedVenueId = ref(1)
const dialogVisible = ref(false)
const form = ref({ from_zone_id: null, to_zone_id: null, distance: 1 })

async function fetchVenues() {
  const res = await axios.get(`${API_URL}/api/venues`)
  venues.value = res.data
}

async function fetchZones() {
  const res = await axios.get(`${API_URL}/api/venues/${selectedVenueId.value}/zones`)
  zones.value = res.data
}

async function fetchRoads() {
  const res = await axios.get(`${API_URL}/api/venues/${selectedVenueId.value}/road_network`)
  const zoneMap = {}
  zones.value.forEach(z => { zoneMap[z.id] = z.name })
  roads.value = res.data.map(r => ({
    ...r,
    from_name: zoneMap[r.from_zone_id] || '未知',
    to_name: zoneMap[r.to_zone_id] || '未知'
  }))
}

async function saveRoad() {
  if (!form.value.from_zone_id || !form.value.to_zone_id) {
    ElMessage.warning('请选择起点和终点')
    return
  }
  
  await axios.post(`${API_URL}/api/road_network`, null, {
    params: {
      venue_id: selectedVenueId.value,
      from_zone_id: form.value.from_zone_id,
      to_zone_id: form.value.to_zone_id,
      distance: form.value.distance
    }
  })
  ElMessage.success('添加成功')
  dialogVisible.value = false
  fetchRoads()
}

async function deleteRoad(id) {
  try {
    await ElMessageBox.confirm('确定删除该连接吗？', '提示', { type: 'warning' })
    await axios.delete(`${API_URL}/api/road_network/${id}`)
    ElMessage.success('删除成功')
    fetchRoads()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function showAddDialog() {
  form.value = { from_zone_id: null, to_zone_id: null, distance: 1 }
  dialogVisible.value = true
  fetchZones()
}

onMounted(() => {
  fetchVenues()
  fetchZones()
  fetchRoads()
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
  display: flex;
  gap: 10px;
}
</style>