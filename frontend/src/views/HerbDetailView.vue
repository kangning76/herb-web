<template>
  <div class="herb-detail-view">
    <div class="container">
      <!-- Breadcrumb -->
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/herbs' }">药材列表</el-breadcrumb-item>
        <el-breadcrumb-item>{{ herb?.name_cn || '加载中...' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <!-- Loading Skeleton -->
      <template v-if="loading">
        <el-card class="detail-card">
          <el-row :gutter="40">
            <el-col :xs="24" :md="10">
              <el-skeleton style="width: 100%" animated>
                <template #template>
                  <el-skeleton-item variant="image" style="width: 100%; height: 360px; border-radius: 8px;" />
                </template>
              </el-skeleton>
            </el-col>
            <el-col :xs="24" :md="14">
              <el-skeleton :rows="8" animated />
            </el-col>
          </el-row>
        </el-card>
      </template>

      <!-- Herb Detail -->
      <template v-else-if="herb">
        <el-card class="detail-card" shadow="never">
          <el-row :gutter="40">
            <!-- Left: Image -->
            <el-col :xs="24" :md="10">
              <div class="herb-image-wrapper">
                <el-image
                  v-if="herb.image_url"
                  :src="herb.image_url"
                  :alt="herb.name_cn"
                  fit="cover"
                  class="herb-image"
                >
                  <template #error>
                    <div class="image-placeholder">
                      <el-icon :size="64" color="#a5d6a7"><SetUp /></el-icon>
                      <span>暂无图片</span>
                    </div>
                  </template>
                </el-image>
                <div v-else class="image-placeholder">
                  <el-icon :size="64" color="#a5d6a7"><SetUp /></el-icon>
                  <span>暂无图片</span>
                </div>
              </div>
            </el-col>

            <!-- Right: Info -->
            <el-col :xs="24" :md="14">
              <div class="herb-info">
                <h1 class="herb-name">{{ herb.name_cn }}</h1>
                <p class="herb-pinyin" v-if="herb.name_pinyin">{{ herb.name_pinyin }}</p>

                <el-divider />

                <!-- Tags -->
                <div class="herb-tags">
                  <div class="tag-group" v-if="herb.category">
                    <span class="tag-label">分类：</span>
                    <el-tag type="success" effect="plain" size="large">{{ herb.category }}</el-tag>
                  </div>

                  <div class="tag-group" v-if="herb.nature">
                    <span class="tag-label">药性：</span>
                    <el-tag
                      :color="natureColorMap[herb.nature]?.bg"
                      :style="{ color: natureColorMap[herb.nature]?.text, borderColor: natureColorMap[herb.nature]?.border }"
                      effect="plain"
                      size="large"
                    >
                      {{ herb.nature }}
                    </el-tag>
                  </div>

                  <div class="tag-group" v-if="herb.flavor && herb.flavor.length">
                    <span class="tag-label">药味：</span>
                    <el-tag
                      v-for="f in herb.flavor"
                      :key="f"
                      type="success"
                      effect="light"
                      size="large"
                      class="flavor-tag"
                    >
                      {{ f }}
                    </el-tag>
                  </div>
                </div>

                <el-divider />

                <!-- Efficacy -->
                <div class="herb-section" v-if="herb.efficacy">
                  <h3 class="section-label">功效</h3>
                  <p class="section-content">{{ herb.efficacy }}</p>
                </div>


              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- Back Button -->
        <div class="back-wrapper">
          <el-button @click="goBack" size="large">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>
      </template>

      <!-- Error State -->
      <template v-else>
        <el-empty description="未找到该药材信息">
          <el-button type="primary" @click="$router.push('/herbs')">返回药材列表</el-button>
        </el-empty>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, SetUp } from '@element-plus/icons-vue'
import { getHerb } from '../api/herbs'

const route = useRoute()
const router = useRouter()

const herb = ref(null)
const loading = ref(true)

const natureColorMap = {
  '寒': { bg: '#e3f2fd', text: '#1565c0', border: '#90caf9' },
  '热': { bg: '#ffebee', text: '#c62828', border: '#ef9a9a' },
  '温': { bg: '#fff3e0', text: '#e65100', border: '#ffcc80' },
  '凉': { bg: '#e1f5fe', text: '#0277bd', border: '#81d4fa' },
  '平': { bg: '#efebe9', text: '#4e342e', border: '#bcaaa4' },
}

async function fetchHerb() {
  loading.value = true
  try {
    const { data } = await getHerb(route.params.id)
    herb.value = data
  } catch (error) {
    console.error('获取药材详情失败:', error)
    herb.value = null
  } finally {
    loading.value = false
  }
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/herbs')
  }
}

onMounted(() => {
  fetchHerb()
})
</script>

<style scoped>
.herb-detail-view {
  min-height: 100vh;
  background: #f5f7f5;
  padding: 24px 0 60px;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

.breadcrumb {
  margin-bottom: 24px;
}

.detail-card {
  border-radius: 12px;
}

.detail-card :deep(.el-card__body) {
  padding: 32px;
}

/* Image */
.herb-image-wrapper {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  margin-bottom: 20px;
}

.herb-image {
  width: 100%;
  height: 360px;
  display: block;
}

.image-placeholder {
  width: 100%;
  height: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #e8f5e9;
  gap: 12px;
  color: #81c784;
  font-size: 16px;
}

/* Info */
.herb-info {
  padding-top: 4px;
}

.herb-name {
  font-size: 36px;
  font-weight: 700;
  color: #2e7d32;
  margin: 0 0 8px;
}

.herb-pinyin {
  font-size: 18px;
  color: #999;
  margin: 0 0 4px;
  font-style: italic;
}

/* Tags */
.herb-tags {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tag-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-label {
  font-size: 14px;
  color: #666;
  min-width: 56px;
}

.flavor-tag {
  margin-right: 0;
}

/* Sections */
.herb-section {
  margin-bottom: 20px;
}

.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px;
}

.section-content {
  font-size: 15px;
  color: #555;
  line-height: 1.8;
  margin: 0;
}

/* Back */
.back-wrapper {
  margin-top: 24px;
}

@media (max-width: 768px) {
  .herb-name {
    font-size: 28px;
    margin-top: 20px;
  }

  .herb-image,
  .image-placeholder {
    height: 260px;
  }
}
</style>
