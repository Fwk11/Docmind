/**
 * API 请求封装模块
 * =================
 * 统一管理所有与后端通信的 API 请求。
 *
 * 核心功能：
 * 1. 创建 axios 实例，统一配置 baseURL 和超时时间
 * 2. 请求拦截器：自动在每个请求头中添加 JWT 令牌
 * 3. 响应拦截器：401 未授权时自动跳转登录页
 * 4. 导出所有 API 函数，组件中直接调用
 *
 * 为什么用拦截器？
 * - 不用每个请求手动写 token 和错误处理
 * - 统一管理，改一处全局生效
 */
import axios from 'axios'

// 创建 axios 实例，baseURL 指向后端 API 地址
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000, // 30秒超时
})

// 请求拦截器：每次请求自动带上 JWT 令牌
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：401未授权时清除令牌并跳转登录页
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

// ========== 认证相关 API ==========
// 注册：POST /auth/register
export const registerUser = (username, password) => api.post('/auth/register', { username, password })
// 登录：POST /auth/token（OAuth2标准，用URLSearchParams构造表单数据）
export const login = (username, password) => {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  return api.post('/auth/token', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
}
// 获取当前用户信息：GET /auth/me
export const getMe = () => api.get('/auth/me')

// ========== 文档相关 API ==========
// 文档列表：GET /documents?skip=0&limit=20
export const listDocuments = (skip = 0, limit = 20) => api.get('/documents', { params: { skip, limit } })
// 文档详情：GET /documents/:id
export const getDocument = (id) => api.get(`/documents/${id}`)
// 删除文档：DELETE /documents/:id
export const deleteDocument = (id) => api.delete(`/documents/${id}`)
// 上传文档：POST /upload（FormData格式，支持文件上传）
export const uploadDocument = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ========== 聊天相关 API ==========
// 普通聊天：POST /chat（等待完整回答）
export const chatQuestion = (question) => api.post('/chat', { question })
// 流式聊天URL（用fetch+ReadableStream实现SSE，不用axios）
export const chatStreamUrl = () => `${api.defaults.baseURL}/chat/stream`
// 知识检索：POST /search
export const searchQuestion = (question) => api.post('/search', { question })
// 聊天历史：GET /history?skip=0&limit=50
export const listHistory = (skip = 0, limit = 50) => api.get('/history', { params: { skip, limit } })
// 健康检查：GET /health
export const healthCheck = () => api.get('/health')

export default api