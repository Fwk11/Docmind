<template>
  <div class="page-panel">
    <div class="panel-header animate-fade-up">
      <el-button text @click="$router.back()" class="back-btn">← 返回</el-button>
      <h2>📄 文档详情</h2>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="document" class="detail-container animate-fade-up delay-1">
      <div class="doc-header">
        <div class="doc-icon">{{ fileIcon }}</div>
        <div class="doc-meta">
          <h3 class="doc-name">{{ document.file_name }}</h3>
          <div class="doc-tags">
            <el-tag size="small" effect="plain">{{ document.file_type.toUpperCase() }}</el-tag>
            <span class="doc-time">上传于 {{ formatDate(document.upload_time) }}</span>
            <span class="doc-chunks">{{ document.chunks.length }} 个分块</span>
          </div>
        </div>
      </div>

      <div class="chunks-section">
        <h3 class="chunks-title">📝 文档分块</h3>
        <div class="chunks-grid">
          <div
            v-for="(chunk, i) in document.chunks"
            :key="chunk.id"
            class="chunk-card animate-fade-up"
            :style="{ animationDelay: `${0.1 + i * 0.05}s` }"
            @mouseenter="expandedChunk = expandedChunk === i ? null : i"
          >
            <div class="chunk-header">
              <span class="chunk-badge">段落 {{ chunk.chunk_index }}</span>
            </div>
            <p class="chunk-content" :class="{ collapsed: expandedChunk !== i }">
              {{ chunk.content }}
            </p>
            <div class="chunk-expand" v-if="expandedChunk !== i && chunk.content.length > 200">
              点击展开 ↓
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-else description="文档未找到" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getDocument } from '../api'

const route = useRoute()
const document = ref(null)
const loading = ref(true)
const expandedChunk = ref(null)

const fileIcon = computed(() => {
  if (!document.value) return '📄'
  const type = document.value.file_type?.toLowerCase()
  if (type === 'pdf') return '📕'
  if (type === 'docx') return '📘'
  return '📝'
})

const formatDate = (value) => {
  return new Date(value).toLocaleString()
}

onMounted(async () => {
  const id = route.params.id
  try {
    const response = await getDocument(id)
    document.value = response.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
})
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

.back-btn {
  margin-bottom: 8px;
  padding: 0;
  font-size: 0.95rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 60px;
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

.detail-container {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
  padding-bottom: 24px;
  border-bottom: 1px solid #eef2f7;
}

.doc-icon {
  font-size: 3rem;
}

.doc-meta {
  flex: 1;
}

.doc-name {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1a2332;
  margin-bottom: 10px;
}

.doc-tags {
  display: flex;
  align-items: center;
  gap: 14px;
}

.doc-time,
.doc-chunks {
  color: #8f9bb3;
  font-size: 0.9rem;
}

.chunks-title {
  font-size: 1.15rem;
  margin-bottom: 18px;
  color: #1a2332;
}

.chunks-grid {
  display: grid;
  gap: 14px;
}

.chunk-card {
  background: #f8fafc;
  border-radius: 18px;
  padding: 22px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  cursor: pointer;
}

.chunk-card:hover {
  background: #fff;
  border-color: rgba(79, 124, 255, 0.15);
  box-shadow: 0 4px 18px rgba(79, 124, 255, 0.08);
  transform: translateX(4px);
}

.chunk-header {
  margin-bottom: 10px;
}

.chunk-badge {
  background: linear-gradient(135deg, #4f7cff, #3db5ff);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: 10px;
}

.chunk-content {
  color: #3a4a64;
  line-height: 1.7;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.chunk-content.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chunk-expand {
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
</style>