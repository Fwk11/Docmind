<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <div class="brand">DocMind</div>
      <nav class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/upload">上传</router-link>
        <router-link to="/chat">AI 聊天</router-link>
        <router-link to="/search">知识检索</router-link>
        <router-link to="/history">历史记录</router-link>
      </nav>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: linear-gradient(180deg, #f5f8ff 0%, #ffffff 100%);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  min-height: 72px;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid #e8eaf6;
  backdrop-filter: blur(14px);
}

.brand {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1d3b70;
}

.nav-links {
  display: flex;
  gap: 24px;
  font-size: 0.95rem;
  color: #3b4a68;
}

.nav-links a {
  color: #3b4a68;
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav-links a.router-link-active {
  color: #409eff;
  font-weight: 600;
}

.app-main {
  padding: 24px 40px 32px;
  max-width: 1400px;
  margin: 0 auto;
}

@media screen and (max-width: 1366px) {
  .app-main {
    padding: 20px 20px 28px;
  }

  .app-header {
    padding: 0 20px;
  }
}
</style>


