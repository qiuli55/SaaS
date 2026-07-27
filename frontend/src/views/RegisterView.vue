<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-6">
        <h1 class="text-3xl font-extrabold text-gray-900">法律AI助手</h1>
        <p class="text-gray-500 mt-1">创建您的账号，开始高效办公</p>
      </div>

      <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
        <h2 class="text-xl font-bold text-gray-800 mb-6 text-center">注册</h2>
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block">手机号 <span class="text-red-500">*</span></label>
            <input v-model="form.phone" type="text" maxlength="11" placeholder="请输入手机号"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all" required />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block">密码 <span class="text-red-500">*</span></label>
            <input v-model="form.password" type="password" placeholder="至少6位密码"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all" required />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block">姓名</label>
            <input v-model="form.name" type="text" placeholder="您的真实姓名"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block">律所名称</label>
            <input v-model="form.firm_name" type="text" placeholder="所在律所名称"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all" />
          </div>
          <div v-if="error" class="text-sm text-red-600 bg-red-50 px-4 py-2 rounded-lg">{{ error }}</div>
          <button type="submit" :disabled="loading"
            class="w-full py-3 rounded-xl font-semibold text-white bg-primary-600 hover:bg-primary-700 transition-colors disabled:opacity-50">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
        <p class="mt-4 text-center text-sm text-gray-500">
          已有账号？<router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">立即登录</router-link>
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
const form = reactive({ phone: '', password: '', name: '', firm_name: '' })

async function handleRegister() {
  error.value = ''
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { error.value = '请输入正确的手机号'; return }
  if (form.password.length < 6) { error.value = '密码至少6位'; return }
  loading.value = true
  try {
    const res = await api.post('/user/register', form)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>
