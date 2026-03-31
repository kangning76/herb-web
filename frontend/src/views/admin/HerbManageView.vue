<template>
  <div class="herb-manage">
    <div class="page-header">
      <h1>药材管理</h1>
      <div class="header-actions">
        <el-button type="success" @click="$router.push('/admin/herbs/new')">
          <el-icon><Plus /></el-icon>
          新增药材
        </el-button>
        <el-button type="primary" @click="$router.push('/admin/herbs/import')">
          <el-icon><Upload /></el-icon>
          CSV导入
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索药材名称、拼音、分类..."
        clearable
        :prefix-icon="Search"
        class="search-input"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <!-- 药材列表 -->
    <el-table
      v-loading="loading"
      :data="herbs"
      stripe
      border
      class="herb-table"
    >
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="name_cn" label="药材名称" min-width="120">
        <template #default="{ row }">
          <span class="herb-name">{{ row.name_cn }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name_pinyin" label="拼音" min-width="120" />
      <el-table-column prop="category" label="分类" width="140">
        <template #default="{ row }">
          <el-tag v-if="row.category" type="success" effect="plain">
            {{ row.category }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="nature" label="药性" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.nature" :type="natureTagType(row.nature)" size="small">
            {{ row.nature }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            text
            @click="$router.push(`/admin/herbs/${row.id}/edit`)"
          >
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            text
            @click="handleDelete(row)"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="fetchHerbs"
        @current-change="fetchHerbs"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHerbs, deleteHerb } from '../../api/herbs'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const herbs = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

function natureTagType(nature) {
  const map = {
    '寒': 'info',
    '凉': '',
    '平': 'warning',
    '温': 'danger',
    '热': 'danger',
  }
  return map[nature] || ''
}

async function fetchHerbs() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value.trim()) {
      params.q = searchQuery.value.trim()
    }
    const { data } = await getHerbs(params)
    herbs.value = data.items || data.results || data
    total.value = data.total ?? (Array.isArray(data) ? data.length : 0)
  } catch (error) {
    ElMessage.error('获取药材列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchHerbs()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除药材「${row.name_cn}」吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    loading.value = true
    await deleteHerb(row.id)
    ElMessage.success(`药材「${row.name_cn}」已删除`)
    await fetchHerbs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHerbs()
})
</script>

<style scoped>
.herb-manage {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  max-width: 400px;
}

.herb-table {
  width: 100%;
}

.herb-name {
  font-weight: 500;
  color: #2e7d32;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-bottom: 20px;
}
</style>
