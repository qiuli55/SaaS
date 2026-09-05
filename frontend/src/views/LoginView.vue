<template>
  <div class="auth-page">
    <!-- 左：品牌区 -->
    <div class="auth-left">
      <div class="auth-brand">
        <span class="seal">莱</span>
        <div>
          <div class="auth-brand-name">Lexi 莱希</div>
          <div class="auth-brand-sub">Legal Intelligence</div>
        </div>
      </div>

      <div>
        <h1 class="auth-hero-title">AI 驱动的<br />法律文书生成平台</h1>
        <p class="auth-hero-desc">面向中小律所的轻量级 AI 文书生成 + 案件管理工具。打开浏览器就能用，让每位律师都能高效执业。</p>
        <div class="auth-features">
          <div class="auth-feature"><span class="ic">✶</span><span>AI 一键生成起诉状、答辩状、律师函等标准法律文书</span></div>
          <div class="auth-feature"><span class="ic">✓</span><span>法条引用自动校验，确保文书引用法条真实准确</span></div>
          <div class="auth-feature"><span class="ic">⤓</span><span>一键导出 Word / PDF，排版符合法院文书标准</span></div>
          <div class="auth-feature"><span class="ic">▤</span><span>案件全流程管理，文书、文档、日程一目了然</span></div>
        </div>
      </div>

      <div class="auth-foot">© 2026 Lexi 莱希 · 让法律服务更高效</div>
    </div>

    <!-- 右：表单 -->
    <div class="auth-right">
      <div class="auth-form-wrap">
        <h2 class="auth-form-title">欢迎回来</h2>
        <p class="auth-form-sub">输入手机号和密码即可登录</p>

        <form @submit.prevent="handleSubmit">
          <div class="auth-group">
            <label class="auth-label">手机号</label>
            <input v-model="form.phone" type="text" maxlength="11" placeholder="请输入手机号" class="auth-input" required />
          </div>

          <div class="auth-group">
            <label class="auth-label">密码</label>
            <div class="auth-pwd">
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码（至少6位）" class="auth-input" required />
              <button type="button" @click="showPwd = !showPwd" class="auth-pwd-toggle" :title="showPwd ? '隐藏密码' : '显示密码'">
                <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
                  <path d="M1 10s3-7 9-7 9 7 9 7-3 7-9 7-9-7-9-7z"/>
                  <circle cx="10" cy="10" r="3"/>
                  <line v-if="!showPwd" x1="2" y1="18" x2="18" y2="2"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="auth-error">{{ error }}</div>

          <button type="submit" class="auth-submit" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="auth-switch">
          <span>还没有账号？</span>
          <a href="/register">立即注册</a>
        </div>
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
const showPwd = ref(false)

const form = reactive({ phone: '', password: '' })

async function handleSubmit() {
  error.value = ''
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { error.value = '请输入正确的手机号'; return }
  if (form.password.length < 6) { error.value = '密码至少6位'; return }
  loading.value = true
  try {
    const res = await api.post('/user/login', { phone: form.phone, password: form.password })
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>
