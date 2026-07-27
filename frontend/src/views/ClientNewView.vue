<template>
  <div>
    <div class="page-header"><h1 class="page-title">添加客户</h1></div>
    <div class="card" style="max-width:640px">
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-row">
            <div class="form-group"><label class="form-label">姓名 <span style="color:var(--error)">*</span></label><input v-model="form.name" type="text" placeholder="客户姓名" class="form-input" required /></div>
            <div class="form-group"><label class="form-label">手机号</label><input v-model="form.phone" type="text" placeholder="手机号码" class="form-input" /></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">微信</label><input v-model="form.wechat" type="text" placeholder="微信号" class="form-input" /></div>
            <div class="form-group"><label class="form-label">身份证号</label><input v-model="form.id_card" type="text" placeholder="身份证号码" class="form-input" /></div>
          </div>
          <div class="form-group"><label class="form-label">所在公司</label><input v-model="form.company" type="text" placeholder="公司名称" class="form-input" /></div>
          <div class="form-group">
            <label class="form-label">标签</label>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">
              <button type="button" v-for="t in presetTags" :key="t" @click="toggleTag(t)"
                :style="{ padding:'4px 10px', fontSize:'12px', borderRadius:'9999px', border:'1px solid '+(selectedTags.includes(t)?'var(--accent)':'var(--border)'), background:selectedTags.includes(t)?'#eff6ff':'var(--surface)', color:selectedTags.includes(t)?'var(--accent)':'var(--text-secondary)', cursor:'pointer' }">{{ t }}</button>
            </div>
            <input v-model="customTag" @keydown.enter.prevent="addCustomTag" type="text" placeholder="输入自定义标签回车" class="form-input" />
          </div>
          <div class="form-group"><label class="form-label">备注</label><textarea v-model="form.remark" rows="3" placeholder="客户备注" class="form-textarea"></textarea></div>
          <div v-if="error" style="padding:10px;border-radius:6px;background:#fef2f2;color:var(--error);font-size:13px;margin-bottom:16px">{{ error }}</div>
          <div style="display:flex;justify-content:flex-end;gap:8px">
            <button type="button" @click="$router.back()" class="btn btn-outline">取消</button>
            <button type="submit" class="btn btn-accent" :disabled="submitting">{{ submitting ? '添加中...' : '添加客户' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'; import { useRouter } from 'vue-router'; import api from '../api'
const router = useRouter(); const submitting = ref(false); const error = ref('')
const presetTags = ['VIP客户','风险客户','企业客户','个人客户','长期合作','新客户']
const selectedTags = ref([]); const customTag = ref('')
const form = reactive({ name:'',phone:'',wechat:'',id_card:'',company:'',remark:'' })
function toggleTag(t) { const i = selectedTags.value.indexOf(t); i>=0 ? selectedTags.value.splice(i,1) : selectedTags.value.push(t) }
function addCustomTag() { const t = customTag.value.trim(); if(t && !selectedTags.value.includes(t)) selectedTags.value.push(t); customTag.value = '' }
async function handleSubmit() {
  if(!form.name) { error.value='请填写客户姓名'; return }
  submitting.value = true; error.value = ''
  try { const res = await api.post('/clients', { ...form, tags: JSON.stringify(selectedTags.value) }); router.push(`/clients/${res.data.data.id}`) }
  catch (e) { error.value = e.response?.data?.detail || '添加失败' } finally { submitting.value = false }
}
</script>
