<template>
  <div class="recommendation-view">
    <div class="container">
      <h1 class="page-title">智能推荐</h1>
      <p class="page-desc">选择药材属性条件，发现相似药材</p>

      <!-- Filter Panel -->
      <el-card class="filter-card" shadow="never">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="分类">
            <el-select
              v-model="filters.category"
              placeholder="选择分类"
              clearable
              class="filter-select"
            >
              <el-option
                v-for="cat in categories"
                :key="cat"
                :label="cat"
                :value="cat"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="药性">
            <el-select
              v-model="filters.nature"
              placeholder="选择药性"
              clearable
              class="filter-select--nature"
            >
              <el-option v-for="n in natureOptions" :key="n" :label="n" :value="n" />
            </el-select>
          </el-form-item>

          <el-form-item label="药味">
            <el-select
              v-model="filters.flavors"
              placeholder="选择药味"
              clearable
              multiple
              class="filter-select"
            >
              <el-option v-for="f in flavorOptions" :key="f" :label="f" :value="f" />
            </el-select>
          </el-form-item>

          <el-form-item label="功效关键词">
            <el-input
              v-model="filters.efficacyKeywords"
              placeholder="如：补气 活血（空格分隔）"
              clearable
              class="filter-input"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading">
              搜索推荐
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Loading -->
      <template v-if="loading">
        <el-row :gutter="16" class="result-grid">
          <el-col v-for="i in 8" :key="i" :xs="12" :sm="8" :md="6">
            <el-card class="skeleton-card" shadow="hover">
              <el-skeleton :rows="4" animated />
            </el-card>
          </el-col>
        </el-row>
      </template>

      <!-- Results -->
      <template v-else-if="results.length > 0">
        <p class="result-count">找到 {{ results.length }} 个相似药材</p>
        <el-row :gutter="16" class="result-grid">
          <el-col
            v-for="rec in results"
            :key="rec.herb.id"
            :xs="12"
            :sm="8"
            :md="6"
          >
            <HerbRecommendationCard :recommendation="rec" />
          </el-col>
        </el-row>
      </template>

      <!-- Empty / Initial State -->
      <template v-else>
        <el-empty :description="emptyText" />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getCategories, exploreRecommendations } from '../api/herbs'
import HerbRecommendationCard from '../components/HerbRecommendationCard.vue'

const natureOptions = ['寒', '热', '温', '凉', '平']
const flavorOptions = ['甘', '苦', '辛', '酸', '咸']

const categories = ref([])
const results = ref([])
const loading = ref(false)
const searched = ref(false)

const filters = ref({
  category: '',
  nature: '',
  flavors: [],
  efficacyKeywords: '',
})

const emptyText = computed(() =>
  searched.value ? '未找到匹配的药材，请调整筛选条件' : '请选择筛选条件来发现相似药材'
)

async function fetchCategories() {
  try {
    const { data } = await getCategories()
    categories.value = data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

async function handleSearch() {
  loading.value = true
  searched.value = true
  try {
    const params = {}
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.nature) params.nature = filters.value.nature
    if (filters.value.flavors.length > 0) params.flavor = filters.value.flavors
    if (filters.value.efficacyKeywords.trim()) {
      params.efficacy_keywords = filters.value.efficacyKeywords.trim()
    }
    params.limit = 20

    const { data } = await exploreRecommendations(params)
    results.value = data.items || []
  } catch (error) {
    console.error('获取推荐结果失败:', error)
    results.value = []
  } finally {
    loading.value = false
  }
}

function handleReset() {
  filters.value = { category: '', nature: '', flavors: [], efficacyKeywords: '' }
  results.value = []
  searched.value = false
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.recommendation-view {
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
  margin: 0 0 8px;
}

.page-desc {
  font-size: 14px;
  color: #888;
  margin: 0 0 24px;
}

.filter-card {
  border-radius: 12px;
  margin-bottom: 24px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

.filter-select {
  width: 180px;
}

.filter-select--nature {
  width: 120px;
}

.filter-input {
  width: 240px;
}

.result-count {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px;
}

.result-grid :deep(.el-col) {
  margin-bottom: 16px;
}

.skeleton-card {
  margin-bottom: 16px;
}
</style>
