<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">中药百科</h1>
        <p class="hero-subtitle">传承千年中医药智慧</p>
        <div class="hero-search">
          <el-input
            v-model="searchKeyword"
            size="large"
            placeholder="搜索药材名称、功效..."
            :prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
          />
        </div>
      </div>
    </section>

    <!-- Popular Herbs Section -->
    <section class="section popular-herbs">
      <div class="container">
        <h2 class="section-title">热门药材</h2>
        <el-row :gutter="20" v-loading="herbsLoading">
          <el-col
            v-for="herb in popularHerbs"
            :key="herb.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <HerbCard :herb="herb" />
          </el-col>
        </el-row>
        <div class="section-more">
          <el-button type="primary" plain @click="$router.push('/herbs')">
            查看全部药材
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </section>

    <!-- Quick Stats Section -->
    <section class="section stats-section">
      <div class="container">
        <h2 class="section-title">数据概览</h2>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="stat-card">
              <el-statistic :value="overview.total_herbs || 0" title="总药材数">
                <template #prefix>
                  <el-icon style="color: #2e7d32"><Collection /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="stat-card">
              <el-statistic :value="overview.total_categories || 0" title="分类数">
                <template #prefix>
                  <el-icon style="color: #4caf50"><Grid /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="stat-card">
              <el-statistic :value="latestAddedDisplay" title="最近更新">
                <template #prefix>
                  <el-icon style="color: #66bb6a"><Timer /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ArrowRight, Collection, Grid, Timer } from '@element-plus/icons-vue'
import { getHerbs } from '../api/herbs'
import { getOverview } from '../api/stats'
import HerbCard from '../components/HerbCard.vue'

const router = useRouter()

const searchKeyword = ref('')
const popularHerbs = ref([])
const herbsLoading = ref(false)
const overview = ref({})

const latestAddedDisplay = computed(() => {
  if (!overview.value.latest_added) return '-'
  return overview.value.latest_added.slice(0, 10)
})

function handleSearch() {
  const q = searchKeyword.value.trim()
  if (q) {
    router.push({ path: '/herbs', query: { q } })
  } else {
    router.push('/herbs')
  }
}

async function fetchPopularHerbs() {
  herbsLoading.value = true
  try {
    const { data } = await getHerbs({ page_size: 8, sort_by: 'created_at' })
    popularHerbs.value = data.items || data
  } catch (error) {
    console.error('获取热门药材失败:', error)
  } finally {
    herbsLoading.value = false
  }
}

async function fetchOverview() {
  try {
    const { data } = await getOverview()
    overview.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchPopularHerbs()
  fetchOverview()
})
</script>

<style scoped>
.home-view {
  min-height: 100vh;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #2e7d32, #4caf50);
  color: #fff;
  padding: 100px 20px 80px;
  text-align: center;
}

.hero-content {
  max-width: 680px;
  margin: 0 auto;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  margin: 0 0 16px;
  letter-spacing: 4px;
}

.hero-subtitle {
  font-size: 22px;
  margin: 0 0 40px;
  opacity: 0.9;
  font-weight: 300;
}

.hero-search {
  max-width: 520px;
  margin: 0 auto;
}

.hero-search :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

/* Sections */
.section {
  padding: 60px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  margin: 0 0 40px;
  color: #2e7d32;
  position: relative;
}

.section-title::after {
  content: '';
  display: block;
  width: 60px;
  height: 3px;
  background: #4caf50;
  margin: 12px auto 0;
  border-radius: 2px;
}

.section-more {
  text-align: center;
  margin-top: 32px;
}

/* Stats */
.stats-section {
  background: #f5f7f5;
}

.stat-card {
  text-align: center;
  margin-bottom: 20px;
}

.stat-card :deep(.el-statistic__head) {
  font-size: 14px;
  color: #666;
}

.stat-card :deep(.el-statistic__content) {
  font-size: 32px;
  color: #2e7d32;
}

/* Popular herbs */
.popular-herbs :deep(.el-col) {
  margin-bottom: 20px;
}
</style>
