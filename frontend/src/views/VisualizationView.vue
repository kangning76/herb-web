<template>
  <div class="visualization-view">
    <div class="container">
      <h1 class="page-title">数据可视化</h1>

      <!-- Stats Row -->
      <el-row :gutter="20" class="stats-row">
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

      <!-- Charts Row 1: Category (pie) + Nature (bar) -->
      <el-row :gutter="20" class="chart-row">
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <span class="chart-title">药材分类分布</span>
            </template>
            <div class="chart-wrapper" v-loading="categoryLoading">
              <VChart :option="categoryOption" autoresize class="chart" />
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <span class="chart-title">药性分布</span>
            </template>
            <div class="chart-wrapper" v-loading="natureLoading">
              <VChart :option="natureOption" autoresize class="chart" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Charts Row 2: Flavor (radar) -->
      <el-row :gutter="20" class="chart-row">
        <el-col :xs="24" :md="{ span: 12, offset: 6 }">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <span class="chart-title">药味分析</span>
            </template>
            <div class="chart-wrapper" v-loading="flavorLoading">
              <VChart :option="flavorOption" autoresize class="chart" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Collection, Grid, Timer } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import {
  getOverview,
  getCategoryDistribution,
  getNatureDistribution,
  getFlavorDistribution,
} from '../api/stats'

use([
  PieChart,
  BarChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent,
  CanvasRenderer,
])

const GREEN_PALETTE = [
  '#2e7d32', '#388e3c', '#43a047', '#4caf50',
  '#66bb6a', '#81c784', '#a5d6a7', '#c8e6c9',
  '#1b5e20', '#00796b', '#00897b', '#26a69a',
]

const overview = ref({})

const latestAddedDisplay = computed(() => {
  if (!overview.value.latest_added) return '-'
  return overview.value.latest_added.slice(0, 10)
})

const categoryData = ref([])
const natureData = ref([])
const flavorData = ref([])

const categoryLoading = ref(false)
const natureLoading = ref(false)
const flavorLoading = ref(false)

// Category Pie Chart
const categoryOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    textStyle: { fontSize: 13 },
  },
  color: GREEN_PALETTE,
  series: [
    {
      name: '分类分布',
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: {
        show: false,
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
        },
      },
      labelLine: { show: false },
      data: categoryData.value.map(item => ({
        name: item.name || item.category,
        value: item.count || item.value,
      })),
    },
  ],
}))

// Nature Bar Chart
const natureOption = computed(() => {
  const names = natureData.value.map(item => item.name || item.nature)
  const values = natureData.value.map(item => item.count || item.value)
  const barColors = {
    '寒': '#1565c0',
    '热': '#c62828',
    '温': '#e65100',
    '凉': '#0277bd',
    '平': '#4e342e',
  }
  const colors = names.map(n => barColors[n] || '#4caf50')

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { fontSize: 14 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 12 },
    },
    series: [
      {
        name: '药材数量',
        type: 'bar',
        barWidth: '50%',
        data: values.map((v, i) => ({
          value: v,
          itemStyle: { color: colors[i], borderRadius: [6, 6, 0, 0] },
        })),
      },
    ],
  }
})

// Flavor Radar Chart
const flavorOption = computed(() => {
  const indicators = flavorData.value.map(item => ({
    name: item.name || item.flavor,
    max: Math.max(...flavorData.value.map(d => d.count || d.value || 0)) * 1.2 || 100,
  }))
  const values = flavorData.value.map(item => item.count || item.value)

  return {
    tooltip: {
      trigger: 'item',
    },
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#333',
        fontSize: 14,
      },
      splitArea: {
        areaStyle: {
          color: ['#e8f5e9', '#c8e6c9', '#a5d6a7', '#81c784'],
          opacity: 0.3,
        },
      },
      splitLine: {
        lineStyle: { color: '#a5d6a7' },
      },
      axisLine: {
        lineStyle: { color: '#81c784' },
      },
    },
    series: [
      {
        name: '药味分析',
        type: 'radar',
        data: [
          {
            value: values,
            name: '药味数量',
            areaStyle: {
              color: 'rgba(76, 175, 80, 0.25)',
            },
            lineStyle: {
              color: '#2e7d32',
              width: 2,
            },
            itemStyle: {
              color: '#2e7d32',
            },
          },
        ],
      },
    ],
  }
})

async function fetchOverview() {
  try {
    const { data } = await getOverview()
    overview.value = data
  } catch (error) {
    console.error('获取概览数据失败:', error)
  }
}

async function fetchCategoryDistribution() {
  categoryLoading.value = true
  try {
    const { data } = await getCategoryDistribution()
    categoryData.value = data
  } catch (error) {
    console.error('获取分类分布失败:', error)
  } finally {
    categoryLoading.value = false
  }
}

async function fetchNatureDistribution() {
  natureLoading.value = true
  try {
    const { data } = await getNatureDistribution()
    natureData.value = data
  } catch (error) {
    console.error('获取药性分布失败:', error)
  } finally {
    natureLoading.value = false
  }
}

async function fetchFlavorDistribution() {
  flavorLoading.value = true
  try {
    const { data } = await getFlavorDistribution()
    flavorData.value = data
  } catch (error) {
    console.error('获取药味分布失败:', error)
  } finally {
    flavorLoading.value = false
  }
}

onMounted(() => {
  fetchOverview()
  fetchCategoryDistribution()
  fetchNatureDistribution()
  fetchFlavorDistribution()
})
</script>

<style scoped>
.visualization-view {
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

/* Stats */
.stats-row {
  margin-bottom: 24px;
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

/* Charts */
.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chart-wrapper {
  width: 100%;
  height: 380px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
