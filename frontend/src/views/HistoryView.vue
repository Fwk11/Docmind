<template>
  <div class="page-panel">
    <div class="panel-header animate-fade-up">
      <h2>📋 历史记录</h2>
      <p>查看最近的 AI 问答历史，便于复查与继续会话。</p>
    </div>

    <div class="history-container animate-fade-up delay-1">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <el-empty v-else-if="items.length === 0" description="暂无历史记录">
        <el-button type="primary" @click="goto('/chat')">去提问</el-button>
      </el-empty>

      <div v-else class="history-list">
        <div
          v-for="(item, i) in items"
          :key="item.id"
          class="history-item animate-fade-up"
          :style="{ animationDelay: `${i * 0.06}s` }"
        >
          <div class="item-time">
            <span class="time-icon">🕐</span>
            {{ formatDate(item.create_time) }}
          </div>
          <div class="item-body">
            <div class="item-question">
              <span class="q-badge">Q</span>
              {{ item.question }}
            </div>
            <div class="item-answer">
              <span class="a-badge">A</span>
              {{ item.answer }}
            </div>
          </div>
          <div class="item-actions">
            <el-button text size="small" @click="reuseQuestion(item.question)">重新提问</el-button>
          </div>
        </div>
      </div>

      <div v-if="items.length > 0 && hasMore" class="load-more">
        <el-button text @click="loadMore" :loading="loadingMore">
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { listHistory } from '../api'

const router = useRouter()
const goto = (path) => router.push(path)

const items = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const skip = ref(0)
const limit = 20

const formatDate = (value) => {
  return new Date(value).toLocaleString()
}

const reuseQuestion = (question) => {
  router.push({ path: '/chat', query: { q: question } })
}

const fetchHistory = async (isLoadMore = false) => {
  if (isLoadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  try {
    const response = await listHistory(skip.value, limit)
    const newItems = response.data || []
    if (isLoadMore) {
      items.value.push(...newItems)
    } else {
      items.value = newItems
    }
    hasMore.value = newItems.length === limit
    skip.value += newItems.length
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => fetchHistory(true)

onMounted(() => fetchHistory())
</script>

<style scoped>
.page-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header h2 {
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.history-container {
  background: #fff;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 40px;
  color: #8f9bb3;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e8eef5;
  border-top-color: #4f7cff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  border-radius: 18px;
  padding: 22px;
  background: #f8fafc;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.history-item:hover {
  background: #fff;
  border-color: rgba(79, 124, 255, 0.15);
  box-shadow: 0 4px 18px rgba(79, 124, 255, 0.08);
  transform: translateX(4px);
}

.item-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #8f9bb3;
  font-size: 0.85rem;
  margin-bottom: 12px;
}

.time-icon {
  font-size: 0.9rem;
}

.item-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-question,
.item-answer {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.6;
}

.q-badge,
.a-badge {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
}

.q-badge {
  background: rgba(79, 124, 255, 0.1);
  color: #4f7cff;
}

.a-badge {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.item-question {
  font-weight: 600;
  color: #1a2332;
}

.item-answer {
  color: #5f6f90;
}

.item-actions {
  margin-top: 10px;
  text-align: right;
}

.load-more {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #eef2f7;
  margin-top: 8px;
}

.animate-fade-up {
  animation: fadeUp 0.5s ease both;
}

.delay-1 { animation-delay: 0.1s; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>