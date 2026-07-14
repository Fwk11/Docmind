import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

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

export const registerUser = (username, password) => api.post('/auth/register', { username, password })
export const login = (username, password) => {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  return api.post('/auth/token', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
}
export const getMe = () => api.get('/auth/me')

export const listDocuments = (skip = 0, limit = 20) => api.get('/documents', { params: { skip, limit } })
export const getDocument = (id) => api.get(`/documents/${id}`)
export const deleteDocument = (id) => api.delete(`/documents/${id}`)
export const uploadDocument = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const chatQuestion = (question) => api.post('/chat', { question })
export const chatStreamUrl = () => `${api.defaults.baseURL}/chat/stream`
export const searchQuestion = (question) => api.post('/search', { question })
export const listHistory = (skip = 0, limit = 50) => api.get('/history', { params: { skip, limit } })
export const healthCheck = () => api.get('/health')

export default api