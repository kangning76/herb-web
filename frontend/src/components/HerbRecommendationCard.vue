<template>
  <el-card
    shadow="hover"
    class="rec-card"
    :body-style="{ padding: '0' }"
    @click="goToDetail"
  >
    <!-- Image area -->
    <div class="rec-image-wrapper">
      <img
        v-if="recommendation.herb.image_url"
        :src="recommendation.herb.image_url"
        :alt="recommendation.herb.name_cn"
        class="rec-image"
      />
      <div v-else class="rec-image-placeholder">
        <el-icon :size="40" color="#a5d6a7"><Sugar /></el-icon>
      </div>
      <!-- Score badge -->
      <div class="score-badge">{{ Math.round(recommendation.similarity_score) }}%</div>
    </div>

    <!-- Content area -->
    <div class="rec-content">
      <h3 class="rec-name">{{ recommendation.herb.name_cn }}</h3>
      <p class="rec-pinyin">{{ recommendation.herb.name_pinyin }}</p>

      <!-- Match reason tags -->
      <div class="rec-reasons">
        <el-tag
          v-for="(reason, idx) in recommendation.match_reasons"
          :key="idx"
          size="small"
          :type="reasonTagType(reason.dimension)"
          effect="light"
          class="reason-tag"
        >
          {{ reason.label }}
        </el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  recommendation: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

function reasonTagType(dimension) {
  const map = {
    category: 'success',
    nature: 'warning',
    flavor: '',
    efficacy: 'info',
  }
  return map[dimension] ?? ''
}

function goToDetail() {
  router.push(`/herbs/${props.recommendation.herb.id}`)
}
</script>

<style scoped>
.rec-card {
  height: 280px;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.rec-card:hover {
  transform: translateY(-4px);
}

.rec-image-wrapper {
  height: 130px;
  overflow: hidden;
  background-color: #f5f5f5;
  flex-shrink: 0;
  position: relative;
}

.rec-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rec-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}

.score-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(46, 125, 50, 0.9);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

.rec-content {
  padding: 10px 12px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.rec-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 2px 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rec-pinyin {
  font-size: 12px;
  color: #999;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rec-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.reason-tag {
  font-size: 11px;
}
</style>
