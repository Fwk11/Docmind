/**
 * 前端路由配置
 * ===========
 * 定义所有页面的 URL 路径和对应的组件。
 *
 * 为什么用懒加载（() => import(...)）？
 * - 不一次性加载所有页面代码，访问时才加载
 * - 减小首页加载体积，加快首屏速度
 *
 * 路由守卫逻辑：
 * - 未登录访问受保护页面 → 跳转登录页
 * - 已登录访问登录页 → 跳转首页
 * - meta.guest = true 表示该页面只允许未登录用户访问
 */
import { createRouter, createWebHistory } from 'vue-router'

// 路由表：URL路径 → 页面组件
const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true }, // 只允许未登录用户访问
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('../views/UploadView.vue'),
  },
  {
    path: '/documents/:id',
    name: 'document-detail',
    component: () => import('../views/DocumentDetailView.vue'),
    props: true, // 把路由参数作为组件props传入
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('../views/ChatView.vue'),
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('../views/SearchView.vue'),
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../views/HistoryView.vue'),
  },
]

// 创建路由实例，使用 HTML5 History 模式（URL无#号）
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局路由守卫：控制页面访问权限
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.guest && !token) {
    // 未登录访问受保护页面 → 跳转登录
    next({ name: 'login' })
  } else if (to.meta.guest && token) {
    // 已登录访问登录页 → 跳转首页
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router