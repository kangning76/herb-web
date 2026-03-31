<template>
  <div class="herb-search-bar">
    <el-input
      v-model="searchText"
      placeholder="搜索药材名称、功效..."
      clearable
      :prefix-icon="Search"
      class="search-input"
      @clear="emitSearch"
    />

    <el-select
      v-model="selectedCategory"
      placeholder="药材分类"
      clearable
      class="filter-select"
      @change="emitSearch"
    >
      <el-option
        v-for="cat in categories"
        :key="cat"
        :label="cat"
        :value="cat"
      />
    </el-select>

    <el-select
      v-model="selectedNature"
      placeholder="药性"
      clearable
      class="filter-select filter-select--nature"
      @change="emitSearch"
    >
      <el-option
        v-for="n in natureOptions"
        :key="n"
        :label="n"
        :value="n"
      />
    </el-select>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
  categories: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['search'])

const natureOptions = ['寒', '热', '温', '凉', '平']

const searchText = ref('')
const selectedCategory = ref('')
const selectedNature = ref('')

let debounceTimer = null

function emitSearch() {
  emit('search', {
    q: searchText.value.trim(),
    category: selectedCategory.value || '',
    nature: selectedNature.value || '',
  })
}

watch(searchText, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emitSearch()
  }, 300)
})
</script>

<style scoped>
.herb-search-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 220px;
}

.filter-select {
  width: 160px;
}

.filter-select--nature {
  width: 120px;
}
</style>
