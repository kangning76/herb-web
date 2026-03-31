<template>
  <div class="herb-import">
    <div class="page-header">
      <el-button text @click="$router.push('/admin/herbs')">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h1>CSV批量导入</h1>
    </div>

    <!-- 格式说明 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>CSV格式要求</span>
        </div>
      </template>
      <div class="format-info">
        <p>CSV文件需包含以下列（首行为表头）：</p>
        <el-table :data="formatColumns" border size="small" class="format-table">
          <el-table-column prop="field" label="字段名" width="140" />
          <el-table-column prop="desc" label="说明" width="160" />
          <el-table-column prop="required" label="必填" width="80" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.required" type="danger" size="small">必填</el-tag>
              <el-tag v-else type="info" size="small">选填</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="example" label="示例" />
        </el-table>
        <p class="tip-text">
          <el-icon><Warning /></el-icon>
          注意：药味（flavor）多个值之间使用 <code>|</code> 分隔，例如：<code>甘|苦</code>
        </p>
        <el-button type="primary" text @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载示例模板
        </el-button>
      </div>
    </el-card>

    <!-- 上传区域 -->
    <el-card class="upload-card">
      <template #header>
        <span>上传CSV文件</span>
      </template>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :on-exceed="handleExceed"
        accept=".csv"
        drag
        :disabled="importing"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将CSV文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">仅支持 .csv 格式文件</div>
        </template>
      </el-upload>
    </el-card>

    <!-- 预览表格 -->
    <el-card v-if="previewData.length > 0" class="preview-card">
      <template #header>
        <div class="card-header">
          <span>数据预览（前{{ Math.min(previewData.length, 10) }}行，共{{ totalRows }}行）</span>
          <el-button type="success" :loading="importing" @click="handleImport">
            <el-icon><Upload /></el-icon>
            确认导入
          </el-button>
        </div>
      </template>
      <el-table :data="previewData.slice(0, 10)" border stripe size="small" max-height="400">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="name_cn" label="药材名称" min-width="100" />
        <el-table-column prop="name_pinyin" label="拼音" min-width="100" />
        <el-table-column prop="category" label="分类" width="130" />
        <el-table-column prop="nature" label="药性" width="70" align="center" />
        <el-table-column prop="flavor" label="药味" width="120">
          <template #default="{ row }">
            {{ row.flavor }}
          </template>
        </el-table-column>
        <el-table-column prop="efficacy" label="功效" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>

    <!-- 导入结果 -->
    <el-card v-if="importResult" class="result-card">
      <template #header>
        <span>导入结果</span>
      </template>
      <div class="result-summary">
        <el-statistic title="成功导入" :value="importResult.success_count ?? 0">
          <template #suffix>
            <span class="stat-suffix">条</span>
          </template>
        </el-statistic>
        <el-statistic title="失败数量" :value="importResult.error_count ?? 0" class="error-stat">
          <template #suffix>
            <span class="stat-suffix">条</span>
          </template>
        </el-statistic>
      </div>

      <el-alert
        v-if="(importResult.success_count ?? 0) > 0 && (importResult.error_count ?? 0) === 0"
        title="全部导入成功！"
        type="success"
        show-icon
        class="result-alert"
      />
      <el-alert
        v-else-if="(importResult.error_count ?? 0) > 0"
        title="部分数据导入失败，请查看错误详情"
        type="warning"
        show-icon
        class="result-alert"
      />

      <!-- 错误详情表 -->
      <el-table
        v-if="importResult.errors && importResult.errors.length > 0"
        :data="importResult.errors"
        border
        stripe
        size="small"
        class="error-table"
      >
        <el-table-column prop="row" label="行号" width="80" align="center" />
        <el-table-column prop="name_cn" label="药材名称" width="120" />
        <el-table-column prop="message" label="错误原因" min-width="250">
          <template #default="{ row }">
            <el-text type="danger">{{ row.message || row.error || row.detail }}</el-text>
          </template>
        </el-table-column>
      </el-table>

      <div class="result-actions">
        <el-button type="primary" @click="resetImport">
          <el-icon><RefreshRight /></el-icon>
          重新导入
        </el-button>
        <el-button @click="$router.push('/admin/herbs')">返回药材列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { importHerbsCsv } from '../../api/herbs'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const uploadRef = ref(null)
const csvFile = ref(null)
const previewData = ref([])
const totalRows = ref(0)
const importing = ref(false)
const importResult = ref(null)

const formatColumns = [
  { field: 'name_cn', desc: '药材中文名称', required: true, example: '黄芪' },
  { field: 'name_pinyin', desc: '拼音名称', required: false, example: 'huangqi' },
  { field: 'category', desc: '药材分类', required: true, example: '补气药' },
  { field: 'nature', desc: '药性', required: false, example: '温' },
  { field: 'flavor', desc: '药味（多值用|分隔）', required: false, example: '甘' },
  { field: 'efficacy', desc: '功效描述', required: false, example: '补气升阳，固表止汗' },
]

function downloadTemplate() {
  const header = 'name_cn,name_pinyin,category,nature,flavor,efficacy'
  const row1 = '黄芪,huangqi,补气药,温,甘,补气升阳、固表止汗、利水消肿、生津养血、托毒排脓'
  const row2 = '金银花,jinyinhua,清热药,寒,甘|苦,清热解毒、疏散风热'
  const csvContent = [header, row1, row2].join('\n')

  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'herb_import_template.csv'
  link.click()
  URL.revokeObjectURL(url)
}

function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter((line) => line.trim() !== '')
  if (lines.length < 2) return []

  const headers = lines[0].split(',').map((h) => h.trim())
  const rows = []

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i])
    const row = {}
    headers.forEach((header, index) => {
      row[header] = values[index]?.trim() || ''
    })
    rows.push(row)
  }
  return rows
}

function parseCSVLine(line) {
  const result = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    if (inQuotes) {
      if (char === '"' && line[i + 1] === '"') {
        current += '"'
        i++
      } else if (char === '"') {
        inQuotes = false
      } else {
        current += char
      }
    } else {
      if (char === '"') {
        inQuotes = true
      } else if (char === ',') {
        result.push(current)
        current = ''
      } else {
        current += char
      }
    }
  }
  result.push(current)
  return result
}

function handleFileChange(uploadFile) {
  if (!uploadFile.name.endsWith('.csv')) {
    ElMessage.error('请上传 CSV 格式文件')
    uploadRef.value?.clearFiles()
    return
  }

  csvFile.value = uploadFile.raw
  importResult.value = null

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const text = e.target.result
      const parsed = parseCSV(text)
      totalRows.value = parsed.length
      previewData.value = parsed

      if (parsed.length === 0) {
        ElMessage.warning('CSV文件中没有数据行')
      } else {
        ElMessage.success(`已解析 ${parsed.length} 条数据`)
      }
    } catch (err) {
      ElMessage.error('CSV文件解析失败：' + err.message)
      previewData.value = []
    }
  }
  reader.readAsText(uploadFile.raw, 'UTF-8')
}

function handleFileRemove() {
  csvFile.value = null
  previewData.value = []
  totalRows.value = 0
}

function handleExceed() {
  ElMessage.warning('只能上传一个CSV文件，请先删除已有文件')
}

async function handleImport() {
  if (!csvFile.value) {
    ElMessage.warning('请先上传CSV文件')
    return
  }

  importing.value = true
  try {
    const { data } = await importHerbsCsv(csvFile.value)
    importResult.value = data
    const successCount = data.success_count ?? 0
    const errorCount = data.error_count ?? 0

    if (errorCount === 0) {
      ElMessage.success(`成功导入 ${successCount} 条药材数据`)
    } else {
      ElMessage.warning(`导入完成：成功 ${successCount} 条，失败 ${errorCount} 条`)
    }
  } catch (error) {
    ElMessage.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    importing.value = false
  }
}

function resetImport() {
  csvFile.value = null
  previewData.value = []
  totalRows.value = 0
  importResult.value = null
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.herb-import {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 12px 0 0 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .el-icon {
  margin-right: 6px;
}

.info-card {
  margin-bottom: 20px;
}

.format-info p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.format-table {
  margin-bottom: 16px;
}

.tip-text {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #e6a23c;
  font-size: 13px;
  margin-bottom: 12px;
}

.tip-text code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: #409eff;
}

.upload-card {
  margin-bottom: 20px;
}

.preview-card {
  margin-bottom: 20px;
}

.result-card {
  margin-bottom: 40px;
}

.result-summary {
  display: flex;
  gap: 60px;
  margin-bottom: 20px;
  padding: 16px 0;
}

.error-stat :deep(.el-statistic__number) {
  color: #f56c6c;
}

.stat-suffix {
  font-size: 14px;
  color: #909399;
}

.result-alert {
  margin-bottom: 16px;
}

.error-table {
  margin-bottom: 20px;
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
</style>
