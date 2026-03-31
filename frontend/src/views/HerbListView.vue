<template>
  <div class="herb-list-view">
    <div class="container">
      <h1 class="page-title">药材列表</h1>

      <!-- Search Bar -->
      <HerbSearchBar
        :categories="categories"
        @search="handleSearch"
      />

      <!-- Loading Skeleton -->
      <template v-if="loading">
        <el-row :gutter="20">
          <el-col
            v-for="i in 8"
            :key="i"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <el-card class="skeleton-card" shadow="hover">
              <el-skeleton :rows="4" animated />
            </el-card>
          </el-col>
        </el-row>
      </template>

      <!-- Herb Grid -->
      <template v-else-if="herbs.length > 0">
        <el-row :gutter="20">
          <el-col
            v-for="herb in herbs"
            :key="herb.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <HerbCard :herb="herb" />
          </el-col>
        </el-row>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <Pagination
            :total="total"
            :page="page"
            :page-size="pageSize"
            @update:page="handlePageChange"
            @update:page-size="handlePageSizeChange"
          />
        </div>
      </template>

      <!-- Empty State -->
      <template v-else>
        <el-empty description="暂无数据">
          <el-button type="primary" @click="resetSearch">清除筛选条件</el-button>
        </el-empty>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getHerbs, getCategories } from '../api/herbs'
import HerbCard from '../components/HerbCard.vue'
import HerbSearchBar from '../components/HerbSearchBar.vue'
import Pagination from '../components/Pagination.vue'

const route = useRoute()
const router = useRouter()

const herbs = ref([])
const categories = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(Number(route.query.page) || 1)
const pageSize = ref(Number(route.query.page_size) || 12)

const searchParams = ref({
  q: route.query.q || '',
  category: route.query.category || '',
  nature: route.query.nature || '',
})

async function fetchHerbs() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (searchParams.value.q) params.q = searchParams.value.q
    if (searchParams.value.category) params.category = searchParams.value.category
    if (searchParams.value.nature) params.nature = searchParams.value.nature

    const { data } = await getHerbs(params)
    herbs.value = data.items || data
    total.value = data.total || 0
  } catch (error) {
    console.error('获取药材列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const { data } = await getCategories()
    categories.value = data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

function handleSearch({ q, category, nature }) {
  searchParams.value = { q: q || '', category: category || '', nature: nature || '' }
  page.value = 1
  updateRouteQuery()
  fetchHerbs()
}

function handlePageChange(newPage) {
  page.value = newPage
  updateRouteQuery()
  fetchHerbs()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handlePageSizeChange(newSize) {
  pageSize.value = newSize
  page.value = 1
  updateRouteQuery()
  fetchHerbs()
}

function resetSearch() {
  searchParams.value = { q: '', category: '', nature: '' }
  page.value = 1
  updateRouteQuery()
  fetchHerbs()
}

function updateRouteQuery() {
  const query = {}
  if (searchParams.value.q) query.q = searchParams.value.q
  if (searchParams.value.category) query.category = searchParams.value.category
  if (searchParams.value.nature) query.nature = searchParams.value.nature
  if (page.value > 1) query.page = page.value
  if (pageSize.value !== 12) query.page_size = pageSize.value
  router.replace({ query })
}

watch(
  () => route.query,
  (newQuery) => {
    const newQ = newQuery.q || ''
    const newCategory = newQuery.category || ''
    const newNature = newQuery.nature || ''
    const newPage = Number(newQuery.page) || 1
    if (
      newQ !== searchParams.value.q ||
      newCategory !== searchParams.value.category ||
      newNature !== searchParams.value.nature ||
      newPage !== page.value
    ) {
      searchParams.value = { q: newQ, category: newCategory, nature: newNature }
      page.value = newPage
      fetchHerbs()
    }
  }
)

onMounted(() => {
  fetchCategories()
  fetchHerbs()
})
</script>

<style scoped>
.herb-list-view {
  min-height: 100vh;
  background: #f5f7f5;
  padding: 24px 0 60px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #2e7d32;
  margin: 0 0 24px;
}

.skeleton-card {
  margin-bottom: 20px;
}

.herb-list-view :deep(.el-col) {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding: 20px 0;
}
</style>
