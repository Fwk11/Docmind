<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="brand-icon">🧠</span>
        <h2>DocMind</h2>
        <p>{{ isRegister ? '注册新账号' : '登录你的账号' }}</p>
      </div>
      <el-form @submit.prevent="handleSubmit" class="login-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button type="primary" size="large" round :loading="loading" @click="handleSubmit" style="width: 100%">
          {{ loading ? '请稍候...' : (isRegister ? '注册' : '登录') }}
        </el-button>
      </el-form>
      <div class="switch-mode">
        <span v-if="!isRegister">还没有账号？<el-button type="primary" link @click="isRegister = true">立即注册</el-button></span>
        <span v-else>已有账号？<el-button type="primary" link @click="isRegister = false">去登录</el-button></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { registerUser, login } from '../api'

const router = useRouter()
const isRegister = ref(false)
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const handleSubmit = async () => {
  if (!form.username.trim() || !form.password.trim()) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    if (isRegister.value) {
      await registerUser(form.username, form.password)
      ElMessage.success('注册成功，请登录')
      isRegister.value = false
    } else {
      const res = await login(form.username, form.password)
      const token = res.data.access_token
      localStorage.setItem('token', token)
      ElMessage.success('登录成功')
      router.push('/')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f4f8 0%, #e8eef5 100%);
}

.login-card {
  background: #fff;
  border-radius: 24px;
  padding: 48px 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.08);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon {
  font-size: 2.5rem;
}

.login-header h2 {
  font-size: 1.6rem;
  margin: 12px 0 4px;
  background: linear-gradient(135deg, #4f7cff, #3db5ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  color: #8f9bb3;
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.switch-mode {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9rem;
  color: #8f9bb3;
}
</style>