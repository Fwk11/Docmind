<template>
  <div class="page-panel">
    <div class="panel-header animate-fade-up">
      <h2>📤 上传文档</h2>
      <p>支持 PDF、DOCX、Markdown 文档上传，自动构建知识向量。</p>
    </div>

    <div class="upload-area animate-fade-up delay-1">
      <div
        class="drop-zone"
        :class="{ dragging: isDragging, 'has-file': selectedFile }"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input ref="fileInput" type="file" :accept="acceptTypes" @change="handleFileSelect" hidden />
        <transition name="fade" mode="out-in">
          <div v-if="!selectedFile" key="empty" class="drop-content">
            <div class="drop-icon">📁</div>
            <p class="drop-text">将文件拖到此处，或点击选择</p>
            <p class="drop-tip">支持 PDF、DOCX、Markdown，最大 100MB</p>
          </div>
          <div v-else key="selected" class="file-preview">
            <div class="file-icon">{{ fileIcon }}</div>
            <div class="file-info">
              <div class="file-name">{{ selectedFile.name }}</div>
              <div class="file-size">{{ formatSize(selectedFile.size) }}</div>
            </div>
            <el-button circle size="small" @click.stop="clearFile">✕</el-button>
          </div>
        </transition>
      </div>

      <div class="upload-actions">
        <el-button type="primary" size="large" round :loading="loading" :disabled="!selectedFile" @click="submitUpload">
          <span v-if="!loading">🚀 开始上传</span>
          <span v-else>上传中 {{ progress }}%</span>
        </el-button>
      </div>

      <div v-if="loading" class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>

    <transition name="slide-up">
      <div v-if="result" class="result-card animate-fade-up">
        <div class="result-icon">✅</div>
        <div class="result-info">
          <div class="result-title">上传成功！</div>
          <div class="result-detail">文件名：{{ result.filename }}</div>
          <div class="result-detail">文档 ID：{{ result.document_id }}</div>
        </div>
        <el-button type="primary" text @click="goto('/chat')">去提问 →</el-button>
      </div>
    </transition>

    <div class="recent-section animate-fade-up delay-2" v-if="recentFiles.length">
      <h3>最近上传</h3>
      <div class="recent-list">
        <div v-for="(file, i) in recentFiles" :key="i" class="recent-item" :style="{ animationDelay: `${i * 0.08}s` }">
          <span class="recent-icon">{{ file.icon }}</span>
          <span class="recent-name">{{ file.name }}</span>
          <span class="recent-time">{{ file.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { uploadDocument } from '../api'

const router = useRouter()
const goto = (path) => router.push(path)

const fileInput = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const progress = ref(0)
const result = ref(null)
const isDragging = ref(false)
const recentFiles = ref([])

const acceptTypes = '.pdf,.docx,.md,.markdown'

const fileIcon = computed(() => {
  if (!selectedFile.value) return '📄'
  const name = selectedFile.value.name.toLowerCase()
  if (name.endsWith('.pdf')) return '📕'
  if (name.endsWith('.docx')) return '📘'
  return '📝'
})

const triggerFileInput = () => fileInput.value?.click()

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (file) selectedFile.value = file
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) {
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (['.pdf', '.docx', '.md', '.markdown'].includes(ext)) {
      selectedFile.value = file
    } else {
      ElMessage.warning('不支持的文件类型')
    }
  }
}

const clearFile = () => {
  selectedFile.value = null
  result.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const submitUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的文档')
    return
  }

  loading.value = true
  progress.value = 0
  result.value = null

  const progressTimer = setInterval(() => {
    if (progress.value < 90) progress.value += Math.random() * 15
  }, 300)

  try {
    const response = await uploadDocument(selectedFile.value)
    progress.value = 100
    result.value = response.data
    ElMessage.success('上传成功！')
    recentFiles.value.unshift({
      name: selectedFile.value.name,
      icon: fileIcon.value,
      time: new Date().toLocaleTimeString(),
    })
    if (recentFiles.value.length > 5) recentFiles.value.pop()
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '上传失败，请重试')
  } finally {
    clearInterval(progressTimer)
    loading.value = false
    setTimeout(() => { progress.value = 0 }, 1000)
  }
}
</script>

<style scoped>
.page-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-header h2 {
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.upload-area {
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.drop-zone {
  border: 2px dashed #d0dff5;
  border-radius: 20px;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafcff;
}

.drop-zone:hover {
  border-color: #4f7cff;
  background: rgba(79, 124, 255, 0.03);
}

.drop-zone.dragging {
  border-color: #4f7cff;
  background: rgba(79, 124, 255, 0.08);
  transform: scale(1.01);
  box-shadow: 0 0 0 4px rgba(79, 124, 255, 0.1);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: #67c23a;
  background: rgba(103, 194, 58, 0.04);
}

.drop-content {
  text-align: center;
}

.drop-icon {
  font-size: 3rem;
  margin-bottom: 12px;
  animation: floatIcon 3s ease-in-out infinite;
}

@keyframes floatIcon {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.drop-text {
  font-size: 1.1rem;
  color: #3a4a64;
  margin-bottom: 6px;
}

.drop-tip {
  color: #8f9bb3;
  font-size: 0.9rem;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
}

.file-icon {
  font-size: 2.4rem;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #1a2332;
  font-size: 1.05rem;
}

.file-size {
  color: #8f9bb3;
  font-size: 0.9rem;
  margin-top: 4px;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.progress-bar {
  margin-top: 16px;
  height: 6px;
  background: #e8eef5;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f7cff, #3db5ff);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.result-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border-radius: 20px;
  padding: 24px 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  border-left: 4px solid #67c23a;
}

.result-icon {
  font-size: 2rem;
}

.result-info {
  flex: 1;
}

.result-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: #1a2332;
  margin-bottom: 4px;
}

.result-detail {
  color: #5f6f90;
  font-size: 0.9rem;
}

.recent-section h3 {
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #3a4a64;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 14px;
  padding: 14px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  animation: slideIn 0.4s ease both;
}

.recent-icon {
  font-size: 1.4rem;
}

.recent-name {
  flex: 1;
  font-weight: 500;
  color: #1a2332;
}

.recent-time {
  color: #8f9bb3;
  font-size: 0.85rem;
}

.animate-fade-up {
  animation: fadeUp 0.5s ease both;
}

.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-16px); }
  to { opacity: 1; transform: translateX(0); }
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.slide-up-enter-active {
  animation: slideUp 0.4s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>