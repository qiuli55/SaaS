<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="login-left">
      <div class="login-brand">
        <div class="login-brand-icon">法</div>
        <span class="login-brand-text">法律AI助手</span>
      </div>
      <h1 class="login-hero-title">让每份法律文书<br />都专业高效</h1>
      <p class="login-hero-desc">面向中小律所的轻量级 AI 文书生成 + 案件管理工具。打开浏览器就能用，让每位律师都能高效执业。</p>
      <div class="login-features">
        <div class="login-feature">
          <svg width="14" height="14" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 13l-4-4 4-4"/><path d="M11 5l4 4-4 4"/><path d="M10 3L8 15"/></svg>
          AI 智能生成起诉状、答辩状、律师函等标准法律文书
        </div>
        <div class="login-feature">
          <svg width="14" height="14" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="9" r="8"/><path d="M6 9l2 2 4-4"/></svg>
          法条引用自动校验，确保文书引用法条真实准确
        </div>
        <div class="login-feature">
          <svg width="14" height="14" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="14" height="11" rx="1"/><path d="M6 8h6M6 11h4"/></svg>
          一键导出 Word / PDF，排版符合法院文书标准
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-right">
      <div class="login-form-wrapper">
        <h2 class="login-form-title">{{ isRegister ? '创建账号' : '欢迎回来' }}</h2>
        <p class="login-form-subtitle">{{ isRegister ? '注册后即可开始使用' : '输入手机号和密码即可登录' }}</p>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">手机号</label>
            <input v-model="form.phone" type="text" maxlength="11" placeholder="请输入手机号" class="form-input" required />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码（至少6位）" class="form-input" required />
          </div>

          <template v-if="isRegister">
            <div class="form-group">
              <label class="form-label">姓名</label>
              <input v-model="form.name" type="text" placeholder="您的真实姓名" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">律所名称</label>
              <input v-model="form.firm_name" type="text" placeholder="所在律所名称" class="form-input" />
            </div>
          </template>

          <div v-if="error" style="padding:10px;border-radius:6px;background:#fef2f2;color:#dc2626;font-size:13px;margin-bottom:16px">{{ error }}</div>

          <button type="submit" class="btn btn-accent btn-lg" style="width:100%" :disabled="loading">
            {{ loading ? (isRegister ? '注册中...' : '登录中...') : (isRegister ? '注册' : '登录') }}
          </button>
        </form>

        <div style="text-align:center;margin-top:24px;font-size:13px;color:var(--text-muted)">
          {{ isRegister ? '已有账号？' : '还没有账号？' }}
          <a href="#" @click.prevent="isRegister = !isRegister; error = ''" style="color:var(--accent);font-weight:500">
            {{ isRegister ? '立即登录' : '立即注册' }}
          </a>
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
const isRegister = ref(false)

const form = reactive({ phone: '', password: '', name: '', firm_name: '' })

async function handleSubmit() {
  error.value = ''
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { error.value = '请输入正确的手机号'; return }
  if (form.password.length < 6) { error.value = '密码至少6位'; return }
  loading.value = true
  try {
    const endpoint = isRegister.value ? '/user/register' : '/user/login'
    const payload = isRegister.value ? form : { phone: form.phone, password: form.password }
    const res = await api.post(endpoint, payload)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || (isRegister.value ? '注册失败' : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
