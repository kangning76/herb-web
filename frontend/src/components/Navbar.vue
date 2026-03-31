<template>
  <el-menu
    mode="horizontal"
    :default-active="activeIndex"
    :ellipsis="false"
    class="navbar"
    router
  >
    <!-- Left: App title -->
    <el-menu-item index="/" class="navbar-brand">
      <el-icon><Compass /></el-icon>
      <span class="brand-text">中药百科</span>
    </el-menu-item>

    <!-- Center nav links -->
    <el-menu-item index="/herbs">药材列表</el-menu-item>
    <el-menu-item index="/visualization">数据可视化</el-menu-item>

    <!-- Spacer -->
    <div class="flex-grow" />

    <!-- Right: Auth area -->
    <template v-if="authStore.isLoggedIn">
      <el-sub-menu index="admin" class="admin-menu">
        <template #title>
          <el-icon><User /></el-icon>
          <span>{{ authStore.user?.username ?? '管理员' }}</span>
        </template>
        <el-menu-item index="/admin/herbs">
          <el-icon><List /></el-icon>
          药材管理
        </el-menu-item>
        <el-menu-item index="/admin/herbs/import">
          <el-icon><Upload /></el-icon>
          CSV导入
        </el-menu-item>
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-menu-item>
      </el-sub-menu>
    </template>
    <template v-else>
      <el-menu-item index="/login">
        <el-icon><User /></el-icon>
        登录
      </el-menu-item>
    </template>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeIndex = computed(() => route.path)

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
  display: flex;
  align-items: center;
}

.navbar-brand {
  font-size: 20px;
  font-weight: 700;
  margin-right: 8px;
}

.navbar-brand .brand-text {
  margin-left: 6px;
  color: #2e7d32;
}

.flex-grow {
  flex: 1;
}

/* Green active / hover styling */
.navbar :deep(.el-menu-item.is-active) {
  color: #2e7d32 !important;
  border-bottom-color: #2e7d32 !important;
}

.navbar :deep(.el-menu-item:not(.is-disabled):hover) {
  color: #2e7d32 !important;
  background-color: #f1f8e9;
}

.navbar :deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #2e7d32 !important;
  border-bottom-color: #2e7d32 !important;
}

.navbar :deep(.el-sub-menu__title:hover) {
  color: #2e7d32 !important;
  background-color: #f1f8e9;
}

.admin-menu :deep(.el-menu-item:hover) {
  color: #2e7d32 !important;
  background-color: #f1f8e9;
}
</style>
