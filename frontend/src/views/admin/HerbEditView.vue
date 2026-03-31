<template>
  <div class="herb-edit">
    <div class="page-header">
      <el-button text @click="$router.push('/admin/herbs')">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h1>编辑药材</h1>
    </div>

    <el-card v-loading="pageLoading" class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
        size="large"
      >
        <el-form-item label="药材名称" prop="name_cn">
          <el-input v-model="form.name_cn" placeholder="请输入中文名称" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="拼音名称" prop="name_pinyin">
          <el-input v-model="form.name_pinyin" placeholder="请输入拼音名称" maxlength="100" />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择药材分类" filterable class="full-width">
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="药性" prop="nature">
          <el-select v-model="form.nature" placeholder="请选择药性" clearable class="full-width">
            <el-option
              v-for="n in natureOptions"
              :key="n"
              :label="n"
              :value="n"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="药味" prop="flavor">
          <el-select v-model="form.flavor" multiple placeholder="请选择药味（可多选）" class="full-width">
            <el-option
              v-for="f in flavorOptions"
              :key="f"
              :label="f"
              :value="f"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="功效" prop="efficacy">
          <el-input
            v-model="form.efficacy"
            type="textarea"
            :rows="4"
            placeholder="请输入功效描述"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="当前图片">
          <div v-if="currentImageUrl" class="current-image">
            <el-image
              :src="currentImageUrl"
              fit="contain"
              :preview-src-list="[currentImageUrl]"
              class="image-preview"
            />
          </div>
          <el-text v-else type="info">暂无图片</el-text>
        </el-form-item>

        <el-form-item label="更换图片">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleExceed"
            accept="image/jpeg,image/png,image/webp"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">支持 JPG、PNG、WebP 格式，上传后将替换当前图片</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="success" :loading="submitting" @click="handleSubmit">
            <el-icon><Check /></el-icon>
            保存修改
          </el-button>
          <el-button @click="$router.push('/admin/herbs')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getHerb, updateHerb, uploadHerbImage } from '../../api/herbs'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const herbId = route.params.id

const categories = [
  '解表药', '清热药', '泻下药', '祛风湿药', '化湿药', '利水渗湿药',
  '温里药', '理气药', '消食药', '驱虫药', '止血药', '活血化瘀药',
  '化痰止咳平喘药', '安神药', '平肝息风药', '开窍药',
  '补气药', '补血药', '补阴药', '补阳药', '收涩药', '涌吐药', '外用药',
]

const natureOptions = ['寒', '热', '温', '凉', '平']
const flavorOptions = ['甘', '苦', '辛', '酸', '咸']

const formRef = ref(null)
const uploadRef = ref(null)
const pageLoading = ref(false)
const submitting = ref(false)
const imageFile = ref(null)
const currentImageUrl = ref('')

const form = reactive({
  name_cn: '',
  name_pinyin: '',
  category: '',
  nature: '',
  flavor: [],
  efficacy: '',
})

const rules = {
  name_cn: [
    { required: true, message: '请输入药材名称', trigger: 'blur' },
    { max: 50, message: '名称不能超过50个字符', trigger: 'blur' },
  ],
  name_pinyin: [
    { max: 100, message: '拼音不能超过100个字符', trigger: 'blur' },
  ],
  category: [
    { required: true, message: '请选择药材分类', trigger: 'change' },
  ],
}

async function fetchHerb() {
  pageLoading.value = true
  try {
    const { data } = await getHerb(herbId)
    form.name_cn = data.name_cn || ''
    form.name_pinyin = data.name_pinyin || ''
    form.category = data.category || ''
    form.nature = data.nature || ''
    form.flavor = Array.isArray(data.flavor) ? data.flavor : []
    form.efficacy = data.efficacy || ''
    currentImageUrl.value = data.image_url || ''
  } catch (error) {
    ElMessage.error('获取药材信息失败：' + (error.response?.data?.detail || error.message))
    router.push('/admin/herbs')
  } finally {
    pageLoading.value = false
  }
}

function handleFileChange(uploadFile) {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!validTypes.includes(uploadFile.raw.type)) {
    ElMessage.error('请上传 JPG、PNG 或 WebP 格式的图片')
    uploadRef.value?.clearFiles()
    return
  }
  if (uploadFile.raw.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    uploadRef.value?.clearFiles()
    return
  }
  imageFile.value = uploadFile.raw
}

function handleFileRemove() {
  imageFile.value = null
}

function handleExceed() {
  ElMessage.warning('只能上传一张图片，请先删除已有图片')
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      name_cn: form.name_cn,
      name_pinyin: form.name_pinyin || undefined,
      category: form.category,
      nature: form.nature || undefined,
      flavor: form.flavor.length > 0 ? form.flavor : undefined,
      efficacy: form.efficacy || undefined,
    }

    await updateHerb(herbId, payload)
    ElMessage.success(`药材「${form.name_cn}」更新成功`)

    if (imageFile.value) {
      try {
        await uploadHerbImage(herbId, imageFile.value)
        ElMessage.success('图片上传成功')
      } catch (imgErr) {
        ElMessage.warning('药材已更新，但图片上传失败：' + (imgErr.response?.data?.detail || imgErr.message))
      }
    }

    router.push('/admin/herbs')
  } catch (error) {
    ElMessage.error('更新失败：' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchHerb()
})
</script>

<style scoped>
.herb-edit {
  max-width: 800px;
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

.form-card {
  margin-bottom: 40px;
}

.full-width {
  width: 100%;
}

.current-image {
  display: flex;
  align-items: center;
}

.image-preview {
  width: 148px;
  height: 148px;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
}
</style>
