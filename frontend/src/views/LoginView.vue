<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-primary-700">法律AI助手</h1>
        <p class="mt-2 text-gray-500">AI 文书生成 + 案件管理</p>
      </div>

      <div class="card">
        <h2 class="text-xl font-semibold text-gray-800 mb-6">登录</h2>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="form-label">手机号</label>
            <input
              v-model="form.phone"
              type="text"
              maxlength="11"
              placeholder="请输入手机号"
              class="input-field"
              required
            />
          </div>

          <div>
            <label class="form-label">密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              class="input-field"
              required
            />
          </div>

          <div v-if="error" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">
            {{ error }}
          </div>

          <button
            type="submit"
            class="btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-500">
          还没有账号？
          <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
            立即注册
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  phone: '',
  password: '',
})

async function handleLogin() {
  error.value = ''
  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    error.value = '请输入正确的手机号'
    return
  }
  if (form.password.length < 6) {
    error.value = '密码至少6位'
    return
  }

  loading.value = true
  try {
    const res = await api.post('/user/login', {
      phone: form.phone,
      password: form.password,
    })
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
