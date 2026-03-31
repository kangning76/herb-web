import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/herbs',
    name: 'HerbList',
    component: () => import('../views/HerbListView.vue'),
  },
  {
    path: '/herbs/:id',
    name: 'HerbDetail',
    component: () => import('../views/HerbDetailView.vue'),
  },
  {
    path: '/visualization',
    name: 'Visualization',
    component: () => import('../views/VisualizationView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/admin/herbs',
    name: 'HerbManage',
    component: () => import('../views/admin/HerbManageView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/herbs/new',
    name: 'HerbCreate',
    component: () => import('../views/admin/HerbCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/herbs/:id/edit',
    name: 'HerbEdit',
    component: () => import('../views/admin/HerbEditView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/herbs/import',
    name: 'HerbImport',
    component: () => import('../views/admin/HerbImportView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router
