<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-bg">
        <div v-for="i in 20" :key="i" class="particle" :style="particleStyle(i)"></div>
      </div>
      <div class="hero-content">
        <h1 class="hero-title animate-fade-up">DocMind</h1>
        <p class="hero-subtitle animate-fade-up delay-1">基于文档的智能检索与 AI 问答平台</p>
        <div class="hero-actions animate-fade-up delay-2">
          <el-button type="primary" size="large" round @click="goto('/upload')">
            📤 上传文档
          </el-button>
          <el-button size="large" round @click="goto('/chat')">
            💬 开始对话
          </el-button>
        </div>
      </div>
    </div>

    <div class="stats-row animate-fade-up delay-3">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-value">{{ stat.displayValue }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <div class="features-grid">
      <div
        v-for="(feature, index) in features"
        :key="feature.title"
        class="feature-card animate-fade-up"
        :style="{ animationDelay: `${0.4 + index * 0.1}s` }"
        @mouseenter="hoveredFeature = index"
        @mouseleave="hoveredFeature = null"
      >
        <div class="feature-icon" :class="{ bounce: hoveredFeature === index }">{{ feature.icon }}</div>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-desc">{{ feature.desc }}</p>
        <el-button text type="primary" @click="goto(feature.link)">
          {{ feature.action }} →
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { listDocuments, listHistory, healthCheck } from '../api'

const router = useRouter()
const goto = (path) => router.push(path)

const hoveredFeature = ref(null)

const stats = reactive([
  { label: '已上传文档', value: 0, displayValue: '0', suffix: '' },
  { label: '问答记录', value: 0, displayValue: '0', suffix: '' },
  { label: '服务状态', value: 1, displayValue: '检测中...', suffix: '' },
])

const features = [
  {
    icon: '📄',
    title: '文档管理',
    desc: '上传 PDF、DOCX、Markdown 文档，自动解析分块并构建知识向量库。',
    action: '去上传',
    link: '/upload',
  },
  {
    icon: '🤖',
    title: 'AI 智能问答',
    desc: '基于 RAG 架构，结合 Ollama 大模型与 ChromaDB 向量检索，精准回答文档相关问题。',
    action: '去提问',
    link: '/chat',
  },
  {
    icon: '🔎',
    title: '知识检索',
    desc: '输入问题即可检索最相关的文档片段，快速定位关键信息。',
    action: '去检索',
    link: '/search',
  },
  {
    icon: '📊',
    title: '历史追溯',
    desc: '完整保留每次问答记录，随时回溯复查，支持分页浏览。',
    action: '查看历史',
    link: '/history',
  },
]

const particleStyle = (i) => {
  const size = Math.random() * 6 + 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDuration: `${Math.random() * 6 + 4}s`,
    animationDelay: `${Math.random() * 4}s`,
  }
}

const animateNumber = (stat, target) => {
  const duration = 800
  const start = performance.now()
  const from = 0
  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    const current = Math.round(from + (target - from) * eased)
    stat.displayValue = current + stat.suffix
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

onMounted(async () => {
  try {
    const docRes = await listDocuments()
    const docCount = docRes.data?.length || 0
    stats[0].value = docCount
    stats[0].suffix = ' 篇'
    animateNumber(stats[0], docCount)
  } catch {
    stats[0].displayValue = '—'
  }

  try {
    const histRes = await listHistory()
    const histCount = histRes.data?.length || 0
    stats[1].value = histCount
    stats[1].suffix = ' 条'
    animateNumber(stats[1], histCount)
  } catch {
    stats[1].displayValue = '—'
  }

  try {
    await healthCheck()
    stats[2].displayValue = '✅ 运行中'
    stats[2].suffix = ''
  } catch {
    stats[2].displayValue = '❌ 离线'
    stats[2].suffix = ''
  }
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.hero-section {
  position: relative;
  padding: 56px 48px;
  border-radius: 24px;
  background: linear-gradient(135deg, #4f7cff 0%, #3db5ff 50%, #6ee7b7 100%);
  color: #fff;
  overflow: hidden;
  min-height: 260px;
  display: flex;
  align-items: center;
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  animation: float linear infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-30px) scale(1.5);
    opacity: 0.7;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 900;
  margin-bottom: 12px;
  letter-spacing: -1px;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 28px;
  max-width: 500px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 14px;
}

.hero-actions .el-button {
  font-weight: 600;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(79, 124, 255, 0.12);
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #4f7cff, #3db5ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}

.stat-label {
  color: #8f9bb3;
  font-size: 0.95rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feature-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 40px rgba(79, 124, 255, 0.15);
}

.feature-icon {
  font-size: 2.4rem;
  margin-bottom: 14px;
  display: inline-block;
  transition: transform 0.3s;
}

.feature-icon.bounce {
  animation: iconBounce 0.5s ease;
}

@keyframes iconBounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3) rotate(10deg); }
}

.feature-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1a2332;
}

.feature-desc {
  color: #5f6f90;
  line-height: 1.7;
  margin-bottom: 16px;
}

.animate-fade-up {
  animation: fadeUp 0.6s ease both;
}

.delay-1 { animation-delay: 0.15s; }
.delay-2 { animation-delay: 0.3s; }
.delay-3 { animation-delay: 0.45s; }

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media screen and (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  .stats-row {
    grid-template-columns: 1fr;
  }
  .hero-section {
    padding: 36px 24px;
  }
  .hero-title {
    font-size: 2.2rem;
  }
}
</style>