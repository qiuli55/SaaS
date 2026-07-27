<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
    <!-- Hero -->
    <div class="max-w-6xl mx-auto px-4 pt-16 pb-12 text-center">
      <h1 class="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight mb-4">
        AI 驱动的<br class="sm:hidden" />法律文书生成平台
      </h1>
      <p class="text-lg text-gray-500 max-w-2xl mx-auto">
        面向中小律所的轻量级 AI 文书生成 + 案件管理工具。<br />打开浏览器就能用，让每位律师都能高效执业。
      </p>
    </div>

    <!-- 功能亮点 -->
    <div class="max-w-5xl mx-auto px-4 pb-12">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 text-center">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-2xl mx-auto mb-3">📝</div>
          <h3 class="font-semibold text-gray-800 mb-1">AI 智能生成</h3>
          <p class="text-sm text-gray-500">一键生成起诉状、答辩状、律师函等标准法律文书</p>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 text-center">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-2xl mx-auto mb-3">✅</div>
          <h3 class="font-semibold text-gray-800 mb-1">法条自动校验</h3>
          <p class="text-sm text-gray-500">引用法条自动核对，确保文书引用法条真实准确</p>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 text-center">
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-2xl mx-auto mb-3">📄</div>
          <h3 class="font-semibold text-gray-800 mb-1">一键导出</h3>
          <p class="text-sm text-gray-500">支持 Word/PDF 格式，排版符合法院诉讼文书标准</p>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 text-center">
          <div class="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center text-2xl mx-auto mb-3">📊</div>
          <h3 class="font-semibold text-gray-800 mb-1">案件管理</h3>
          <p class="text-sm text-gray-500">案件全流程跟踪，文书、文档、日程一目了然</p>
        </div>
      </div>
    </div>

    <!-- 登录区域 -->
    <div class="max-w-md mx-auto px-4 pb-20">
      <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
        <h2 class="text-xl font-bold text-gray-800 mb-6 text-center">欢迎回来</h2>
        <p class="text-sm text-gray-500 text-center -mt-4 mb-6">输入手机号和密码即可登录</p>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block">手机号</label>
            <input v-model="form.phone" type="text" maxlength="11" placeholder="请输入手机号"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-gray-900" required />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block">密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition-all text-gray-900" required />
          </div>

          <div v-if="error" class="text-sm text-red-600 bg-red-50 px-4 py-2 rounded-lg">{{ error }}</div>

          <button type="submit" :disabled="loading"
            class="w-full py-3 rounded-xl font-semibold text-white bg-primary-600 hover:bg-primary-700 transition-colors disabled:opacity-50">
            {{ loading ? '登录中...' : '登录 / 注册' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-500">
          还没有账号？
          <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">立即注册</router-link>
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
    const res = await api.post('/user/login', { phone: form.phone, password: form.password })
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
