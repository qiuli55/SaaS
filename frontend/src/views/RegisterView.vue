<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-primary-700">法律AI助手</h1>
        <p class="mt-2 text-gray-500">创建您的账号</p>
      </div>

      <div class="card">
        <h2 class="text-xl font-semibold text-gray-800 mb-6">注册</h2>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="form-label">手机号 <span class="text-red-500">*</span></label>
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
            <label class="form-label">密码 <span class="text-red-500">*</span></label>
            <input
              v-model="form.password"
              type="password"
              placeholder="至少6位密码"
              class="input-field"
              required
            />
          </div>

          <div>
            <label class="form-label">姓名</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="您的真实姓名"
              class="input-field"
            />
          </div>

          <div>
            <label class="form-label">律所名称</label>
            <input
              v-model="form.firm_name"
              type="text"
              placeholder="所在律所名称"
              class="input-field"
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
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-500">
          已有账号？
          <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
            立即登录
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
  name: '',
  firm_name: '',
})

async function handleRegister() {
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
    const res = await api.post('/user/register', form)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
