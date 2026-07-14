<!--
  App.vue — 根组件
  ==================
  整个应用的布局框架，包含：
  1. 顶部导航栏（品牌Logo + 页面链接 + 退出按钮）
  2. 主内容区（<router-view> 根据URL显示不同页面）
  3. 页面切换动画（fade效果）
-->
<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <header class="nav-header">
      <!-- 点击Logo回到首页 -->
      <div class="nav-brand" @click="$router.push('/')">
        <span class="brand-icon">🧠</span>
        <span class="brand-text">DocMind</span>
      </div>
      <!-- 导航链接 -->
      <nav class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: activeRoute === item.path }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
        <!-- 已登录时显示退出按钮 -->
        <el-button v-if="isLoggedIn" class="logout-btn" text @click="handleLogout">
          🚪 退出
        </el-button>
      </nav>
    </header>
    <!-- 主内容区：router-view 根据URL显示对应页面 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <!-- 页面切换时的淡入淡出动画 -->
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
/**
 * App.vue 逻辑部分
 * - activeRoute：当前路由路径，用于高亮导航链接
 * - isLoggedIn：是否已登录，控制退出按钮显示
 * - navItems：导航菜单项配置
 * - handleLogout：退出登录，清除token并跳转登录页
 */
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const activeRoute = computed(() => route.path)  // 当前路径
const isLoggedIn = computed(() => !!localStorage.getItem('token'))  // 是否登录

// 导航菜单项
const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/upload', label: '上传文档', icon: '📤' },
  { path: '/chat', label: 'AI 聊天', icon: '💬' },
  { path: '/search', label: '知识检索', icon: '🔍' },
  { path: '/history', label: '历史记录', icon: '📋' },
]

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')  // 清除JWT令牌
  router.push('/login')  // 跳转登录页
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f4f8;
}

.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.nav-brand:hover {
  transform: scale(1.05);
}

.brand-icon {
  font-size: 1.6rem;
}

.brand-text {
  font-size: 1.3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #4f7cff, #3db5ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 12px;
  text-decoration: none;
  color: #5f6f90;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.25s ease;
  position: relative;
}

.nav-link:hover {
  color: #4f7cff;
  background: rgba(79, 124, 255, 0.06);
}

.nav-link.active {
  color: #4f7cff;
  background: rgba(79, 124, 255, 0.1);
  font-weight: 600;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #4f7cff, #3db5ff);
}

.nav-icon {
  font-size: 1.1rem;
}

.logout-btn {
  margin-left: 8px;
  color: #8f9bb3;
  font-size: 0.9rem;
}

.logout-btn:hover {
  color: #f56c6c;
}

.main-content {
  flex: 1;
  padding: 28px 32px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.page-fade-enter-active {
  animation: pageIn 0.35s ease;
}

.page-fade-leave-active {
  animation: pageOut 0.2s ease;
}

@keyframes pageIn {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pageOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
    transform: translateY(-8px);
  }
}
</style>