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
        <h1 class="auth-hero-title">加入 Lexi<br />高效执业</h1>
        <p class="auth-hero-desc">注册账号即可免费体验 AI 文书生成、案件管理、客户通讯录等全部功能。</p>
      </div>

      <div class="auth-foot">© 2026 Lexi 莱希 · 让法律服务更高效</div>
    </div>

    <!-- 右：表单 -->
    <div class="auth-right">
      <div class="auth-form-wrap">
        <h2 class="auth-form-title">创建账号</h2>
        <p class="auth-form-sub">注册后即可开始使用</p>

        <form @submit.prevent="handleRegister">
          <div class="auth-group">
            <label class="auth-label">手机号 <span style="color:var(--danger)">*</span></label>
            <input v-model="form.phone" type="text" maxlength="11" placeholder="请输入手机号" class="auth-input" required />
          </div>
          <div class="auth-group">
            <label class="auth-label">邀请码 <span style="color:var(--danger)">*</span></label>
            <input v-model="form.invite_code" type="text" maxlength="12" style="text-transform:uppercase" placeholder="12位邀请码" class="auth-input" required />
          </div>
          <div class="auth-group">
            <label class="auth-label">密码 <span style="color:var(--danger)">*</span></label>
            <div class="auth-pwd">
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="至少6位" class="auth-input" required />
              <button type="button" @click="showPwd = !showPwd" class="auth-pwd-toggle" :title="showPwd ? '隐藏密码' : '显示密码'">
                <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
                  <path d="M1 10s3-7 9-7 9 7 9 7-3 7-9 7-9-7-9-7z"/><circle cx="10" cy="10" r="3"/>
                  <line v-if="!showPwd" x1="2" y1="18" x2="18" y2="2"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="auth-group">
            <label class="auth-label">验证码 <span style="color:var(--danger)">*</span></label>
            <div class="auth-sms">
              <input v-model="form.code" type="text" maxlength="6" placeholder="6位数字验证码" class="auth-input" />
              <button type="button" class="auth-sms-btn" @click="sendCode" :disabled="smsCountdown > 0">
                {{ smsCountdown > 0 ? smsCountdown + 's' : '获取验证码' }}
              </button>
            </div>
          </div>
          <div class="auth-group">
            <label class="auth-label">姓名 <span style="color:var(--danger)">*</span></label>
            <input v-model="form.name" type="text" placeholder="您的真实姓名" class="auth-input" required />
          </div>
          <div class="auth-group">
            <label class="auth-label">律所名称 <span style="color:var(--danger)">*</span></label>
            <input v-model="form.firm_name" type="text" placeholder="所在律所" class="auth-input" required />
          </div>

          <div v-if="error" class="auth-error">{{ error }}</div>
          <button type="submit" class="auth-submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
        </form>

        <div class="auth-switch">已有账号？<a href="/login">立即登录</a></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'; import { useRouter } from 'vue-router'; import api from '../api'
const router = useRouter(); const loading = ref(false); const error = ref(''); const showPwd = ref(false)
const form = reactive({ phone:'',password:'',code:'',invite_code:'',name:'',firm_name:'' })
const smsCountdown = ref(0)

async function sendCode() {
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { error.value = '请输入正确的手机号'; return }
  try {
    const r = await api.post('/sms/send', { phone: form.phone })
    error.value = ''
    smsCountdown.value = 60
    const timer = setInterval(() => {
      smsCountdown.value--
      if (smsCountdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch(e) { error.value = e.response?.data?.detail || '发送失败' }
}

async function handleRegister() {
  error.value = ''
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { error.value = '请输入正确的手机号'; return }
  if (!form.code || form.code.length !== 6) { error.value = '请输入6位验证码'; return }
  if (!form.invite_code || form.invite_code.length < 8) { error.value = '请输入有效的邀请码'; return }
  if (form.password.length < 6) { error.value = '密码至少6位'; return }
  if (!form.name.trim()) { error.value = '请输入姓名'; return }
  if (!form.firm_name.trim()) { error.value = '请输入律所名称'; return }
  loading.value = true; try { const r = await api.post('/user/register', form); localStorage.setItem('token', r.data.access_token); localStorage.setItem('user', JSON.stringify(r.data.user)); router.push('/') }
  catch(e) { error.value = e.response?.data?.detail||'注册失败' } finally { loading.value = false }
}
</script>
