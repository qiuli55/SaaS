<template>
  <div class="login-page">
    <div class="login-left">
      <div class="login-brand"><div class="login-brand-icon">法</div><span class="login-brand-text">法律AI助手</span></div>
      <h1 class="login-hero-title">加入我们<br />高效执业</h1>
      <p class="login-hero-desc">注册账号即可免费体验 AI 文书生成、案件管理、客户通讯录等全部功能。</p>
    </div>
    <div class="login-right">
      <div class="login-form-wrapper">
        <h2 class="login-form-title">创建账号</h2>
        <p class="login-form-subtitle">注册后即可开始使用</p>
        <form @submit.prevent="handleRegister">
          <div class="form-group"><label class="form-label">手机号 <span style="color:var(--error)">*</span></label><input v-model="form.phone" type="text" maxlength="11" placeholder="请输入手机号" class="form-input" required /></div>
          <div class="form-group"><label class="form-label">密码 <span style="color:var(--error)">*</span></label>
            <div style="position:relative">
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="至少6位" class="form-input" required style="padding-right:40px" />
              <button type="button" @click="showPwd = !showPwd" class="pwd-toggle" :title="showPwd ? '隐藏密码' : '显示密码'">
                <svg v-if="showPwd" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
                  <path d="M1 10s3-7 9-7 9 7 9 7-3 7-9 7-9-7-9-7z"/><circle cx="10" cy="10" r="3"/>
                </svg>
                <svg v-else viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
                  <path d="M1 10s3-7 9-7 9 7 9 7-3 7-9 7-9-7-9-7z"/><circle cx="10" cy="10" r="3"/>
                  <line x1="2" y1="18" x2="18" y2="2"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="form-group"><label class="form-label">姓名</label><input v-model="form.name" type="text" placeholder="您的真实姓名" class="form-input" /></div>
          <div class="form-group"><label class="form-label">律所名称</label><input v-model="form.firm_name" type="text" placeholder="所在律所" class="form-input" /></div>
          <div v-if="error" style="padding:10px;border-radius:6px;background:#fef2f2;color:var(--error);font-size:13px;margin-bottom:16px">{{ error }}</div>
          <button type="submit" class="btn btn-accent btn-lg" style="width:100%" :disabled="loading">{{ loading?'注册中...':'注册' }}</button>
        </form>
        <div style="text-align:center;margin-top:24px;font-size:13px;color:var(--text-muted)">已有账号？<a href="#" @click.prevent="$router.push('/login')" style="color:var(--accent);font-weight:500">立即登录</a></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'; import { useRouter } from 'vue-router'; import api from '../api'
const router = useRouter(); const loading = ref(false); const error = ref(''); const showPwd = ref(false)
const form = reactive({ phone:'',password:'',name:'',firm_name:'' })

async function handleRegister() {
  error.value = ''; if(!/^1[3-9]\d{9}$/.test(form.phone)){error.value='请输入正确的手机号';return}; if(form.password.length<6){error.value='密码至少6位';return}
  loading.value=true; try { const r = await api.post('/user/register',form); localStorage.setItem('token',r.data.access_token); localStorage.setItem('user',JSON.stringify(r.data.user)); router.push('/') }
  catch(e) { error.value = e.response?.data?.detail||'注册失败' } finally { loading.value = false }
}
</script>
