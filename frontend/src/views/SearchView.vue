<template>
  <div class="page-panel">
    <div class="panel-header animate-fade-up">
      <h2>🔍 知识检索</h2>
      <p>输入问题，系统将基于文档向量知识库检索并返回结果。</p>
    </div>

    <div class="search-box animate-fade-up delay-1">
      <el-input
        v-model="query"
        placeholder="输入检索问题，例如：这份文档的主要结论是什么？"
        size="large"
        clearable
        @keyup.enter="submitSearch"
      >
        <template #prefix>
          <span style="font-size: 1.2rem;">🔎</span>
        </template>
        <template #append>
          <el-button type="primary" :loading="loading" @click="submitSearch">
            {{ loading ? '检索中...' : '检索' }}
          </el-button>
        </template>
      </el-input>
    </div>

    <transition name="slide-up">
      <div v-if="result" class="result-section">
        <div class="answer-card animate-fade-up">
          <div class="answer-header">
            <span class="answer-icon">💡</span>
            <span class="answer-label">AI 回答</span>
          </div>
          <p class="answer-text">{{ result.answer }}</p>
        </div>

        <div v-if="result.sources?.length" class="sources-section">
          <h3 class="sources-title">📎 参考来源 <el-tag size="small" round>{{ result.sources.length }}</el-tag></h3>
          <div class="sources-grid">
            <div
              v-for="(source, i) in result.sources"
              :key="i"
              class="source-card animate-fade-up"
              :style="{ animationDelay: `${i * 0.08}s` }"
              @click="expandedSource = expandedSource === i ? null : i"
            >
              <div class="source-header">
                <span class="source-badge">#{{ i + 1 }}</span>
                <span class="source-filename">{{ source.metadata?.filename || '未知文档' }}</span>
              </div>
              <p class="source-text" :class="{ collapsed: expandedSource !== i }">
                {{ source.text }}
              </p>
              <div class="source-expand" v-if="expandedSource !== i">
                点击展开全文 ↓
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { searchQuestion } from '../api'

const query = ref('')
const result = ref(null)
const loading = ref(false)
const expandedSource = ref(null)

const submitSearch = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入检索问题')
    return
  }
  loading.value = true
  result.value = null
  expandedSource.value = null
  try {
    const response = await searchQuestion(query.value)
    result.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '检索失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.panel-header h2 {
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.search-box {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.answer-card {
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  border-left: 4px solid #4f7cff;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.answer-icon {
  font-size: 1.4rem;
}

.answer-label {
  font-weight: 700;
  font-size: 1.1rem;
  color: #1a2332;
}

.answer-text {
  line-height: 1.8;
  color: #3a4a64;
  font-size: 1rem;
}

.sources-section {
  margin-top: 8px;
}

.sources-title {
  font-size: 1.1rem;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1a2332;
}

.sources-grid {
  display: grid;
  gap: 14px;
}

.source-card {
  background: #fff;
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 2px 14px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.source-card:hover {
  border-color: rgba(79, 124, 255, 0.2);
  box-shadow: 0 6px 24px rgba(79, 124, 255, 0.1);
  transform: translateY(-2px);
}

.source-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.source-badge {
  background: linear-gradient(135deg, #4f7cff, #3db5ff);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 10px;
}

.source-filename {
  font-weight: 600;
  color: #3a4a64;
  font-size: 0.95rem;
}

.source-text {
  color: #5f6f90;
  line-height: 1.7;
  font-size: 0.92rem;
  transition: all 0.3s;
}

.source-text.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.source-expand {
  margin-top: 8px;
  color: #4f7cff;
  font-size: 0.85rem;
  font-weight: 500;
}

.animate-fade-up {
  animation: fadeUp 0.5s ease both;
}

.delay-1 { animation-delay: 0.1s; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-up-enter-active {
  animation: slideUp 0.4s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>