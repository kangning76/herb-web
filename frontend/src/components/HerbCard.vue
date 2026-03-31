<template>
  <el-card
    shadow="hover"
    class="herb-card"
    :body-style="{ padding: '0' }"
    @click="goToDetail"
  >
    <!-- Image area -->
    <div class="herb-image-wrapper">
      <img
        v-if="herb.image_url"
        :src="herb.image_url"
        :alt="herb.name_cn"
        class="herb-image"
      />
      <div v-else class="herb-image-placeholder">
        <el-icon :size="48" color="#a5d6a7"><Sugar /></el-icon>
      </div>
    </div>

    <!-- Content area -->
    <div class="herb-content">
      <h3 class="herb-name">{{ herb.name_cn }}</h3>
      <p class="herb-pinyin">{{ herb.name_pinyin }}</p>

      <div class="herb-tags">
        <el-tag v-if="herb.category" size="small" type="info" effect="plain">
          {{ herb.category }}
        </el-tag>
        <el-tag
          v-if="herb.nature"
          size="small"
          :color="natureColor"
          effect="dark"
          class="nature-tag"
        >
          {{ herb.nature }}
        </el-tag>
        <el-tag
          v-for="f in flavorList"
          :key="f"
          size="small"
          effect="plain"
          class="flavor-tag"
        >
          {{ f }}
        </el-tag>
      </div>

      <p class="herb-efficacy">{{ herb.efficacy }}</p>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  herb: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

const natureColorMap = {
  寒: '#1565c0',
  热: '#d32f2f',
  温: '#ff7043',
  凉: '#42a5f5',
  平: '#8d6e63',
}

const natureColor = computed(() => natureColorMap[props.herb.nature] ?? '#909399')

const flavorList = computed(() => {
  if (!props.herb.flavor) return []
  if (Array.isArray(props.herb.flavor)) return props.herb.flavor
  return props.herb.flavor.split(/[,、，\s]+/).filter(Boolean)
})

function goToDetail() {
  router.push(`/herbs/${props.herb.id}`)
}
</script>

<style scoped>
.herb-card {
  height: 320px;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.herb-card:hover {
  transform: translateY(-4px);
}

.herb-image-wrapper {
  height: 160px;
  overflow: hidden;
  background-color: #f5f5f5;
  flex-shrink: 0;
}

.herb-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.herb-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}

.herb-content {
  padding: 12px 14px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.herb-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 2px 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.herb-pinyin {
  font-size: 12px;
  color: #999;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.herb-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.nature-tag {
  border: none;
  color: #fff;
}

.flavor-tag {
  color: #666;
}

.herb-efficacy {
  font-size: 13px;
  color: #666;
  margin: 0;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-overflow: ellipsis;
}
</style>
