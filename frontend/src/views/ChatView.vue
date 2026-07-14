<template>
  <div class="page-panel">
    <div class="panel-header animate-fade-up">
      <h2>💬 AI 聊天</h2>
      <p>基于已上传文档内容，向 Ollama 发送智能问答请求。</p>
    </div>

    <div class="chat-container animate-fade-up delay-1">
      <div class="messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">🤖</div>
          <p>还没有对话，输入问题开始吧！</p>
          <div class="suggestions">
            <el-tag
              v-for="s in suggestions"
              :key="s"
              class="suggestion-tag"
              @click="question = s"
              effect="plain"
            >
              {{ s }}
            </el-tag>
          </div>
        </div>
        <transition-group name="msg" tag="div">
          <div
            v-for="(msg, i) in messages"
            :key="msg.id"
            class="message-row"
            :class="msg.role"
          >
            <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="bubble">
              <span style="white-space: pre-wrap">{{ msg.content }}</span>
              <span v-if="msg.typing" class="cursor">|</span>
            </div>
          </div>
        </transition-group>
        <div v-if="loading && !streamingAnswer" class="message-row assistant">
          <div class="avatar">🤖</div>
          <div class="bubble thinking">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="question"
          placeholder="输入你的问题..."
          @keyup.enter="submitChat"
          size="large"
          clearable
        >
          <template #append>
            <el-button :loading="loading" @click="submitChat" type="primary">
              {{ loading ? '思考中...' : '发送' }}
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { chatStreamUrl } from '../api'

const question = ref('')
const loading = ref(false)
const streamingAnswer = ref(false)
const messages = ref([])
const messagesRef = ref(null)
let msgIdCounter = 0

const suggestions = [
  '这个文档的核心结论是什么？',
  '文档中提到了哪些关键数据？',
  '请总结文档的主要内容',
]

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const submitChat = async () => {
  const q = question.value.trim()
  if (!q) {
    ElMessage.warning('请输入问题后再发送')
    return
  }

  messages.value.push({
    id: ++msgIdCounter,
    role: 'user',
    content: q,
    typing: false,
  })

  question.value = ''
  loading.value = true
  scrollToBottom()

  const assistantMsg = {
    id: ++msgIdCounter,
    role: 'assistant',
    content: '',
    typing: true,
  }
  messages.value.push(assistantMsg)
  scrollToBottom()

  const reactiveMsg = messages.value[messages.value.length - 1]

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(chatStreamUrl(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ question: q }),
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || '问答调用失败')
    }

    streamingAnswer.value = true
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data: ')) continue
        const data = trimmed.slice(6)
        if (data === '[DONE]') continue

        try {
          const parsed = JSON.parse(data)
          if (parsed.error) {
            reactiveMsg.content += '\n⚠️ ' + parsed.error
            break
          }
          if (parsed.content) {
            reactiveMsg.content += parsed.content
            scrollToBottom()
          }
        } catch {
          // skip malformed JSON
        }
      }
    }

    reactiveMsg.typing = false
    streamingAnswer.value = false
  } catch (error) {
    reactiveMsg.content = '⚠️ ' + (error.message || '问答调用失败')
    reactiveMsg.typing = false
    streamingAnswer.value = false
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.page-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 120px);
}

.panel-header h2 {
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #8f9bb3;
}

.empty-icon {
  font-size: 3.5rem;
  animation: floatIcon 3s ease-in-out infinite;
}

@keyframes floatIcon {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.suggestions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 20px;
}

.suggestion-tag:hover {
  background: rgba(79, 124, 255, 0.1);
  color: #4f7cff;
  border-color: #4f7cff;
}

.message-row {
  display: flex;
  gap: 12px;
  animation: msgIn 0.35s ease;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
  background: #f0f4f8;
}

.message-row.user .avatar {
  background: rgba(79, 124, 255, 0.1);
}

.bubble {
  max-width: 70%;
  padding: 14px 20px;
  border-radius: 18px;
  line-height: 1.7;
  font-size: 0.95rem;
  word-break: break-word;
}

.message-row.user .bubble {
  background: linear-gradient(135deg, #4f7cff, #3db5ff);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-row.assistant .bubble {
  background: #f0f4f8;
  color: #1a2332;
  border-bottom-left-radius: 4px;
}

.cursor {
  animation: blink 0.8s infinite;
  font-weight: 700;
  color: #4f7cff;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.thinking {
  display: flex;
  gap: 6px;
  padding: 18px 24px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4f7cff;
  animation: dotPulse 1.4s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  padding: 16px 24px;
  border-top: 1px solid #eef2f7;
  background: #fafcff;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>