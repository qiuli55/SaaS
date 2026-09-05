<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">新建客户</div>
        <div class="page-sub">录入客户基础信息，关联案件将自动归集</div>
      </div>
    </div>

    <div class="two-col">
      <div class="card">
        <div class="card-head"><span class="card-title">客户信息</span><span class="form-hint">🔒 仅您可见</span></div>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-grid">
              <div class="form-group"><label class="form-label">姓名 / 公司名称 <span class="req">*</span></label><input v-model="form.name" type="text" placeholder="客户名称" class="form-input" required /></div>
              <div class="form-group"><label class="form-label">手机号</label><input v-model="form.phone" type="text" placeholder="手机号码" class="form-input" /></div>
              <div class="form-group"><label class="form-label">微信</label><input v-model="form.wechat" type="text" placeholder="微信号" class="form-input" /></div>
              <div class="form-group"><label class="form-label">身份证号</label><input v-model="form.id_card" type="text" placeholder="身份证号码" class="form-input" /></div>
              <div class="form-group col-span"><label class="form-label">所在公司</label><input v-model="form.company" type="text" placeholder="公司名称" class="form-input" /></div>
              <div class="form-group col-span">
                <label class="form-label">标签</label>
                <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">
                  <button type="button" v-for="t in presetTags" :key="t" @click="toggleTag(t)" class="doc-type-card"
                    :class="{ selected: selectedTags.includes(t) }"
                    style="padding:6px 12px;font-size:12px;border-radius:999px">{{ t }}</button>
                </div>
                <input v-model="customTag" @keydown.enter.prevent="addCustomTag" type="text" placeholder="输入自定义标签回车" class="form-input" />
              </div>
              <div class="form-group col-span"><label class="form-label">备注</label><textarea v-model="form.remark" rows="3" placeholder="客户背景、特殊要求…" class="form-textarea"></textarea></div>
            </div>
            <div v-if="error" class="auth-error">{{ error }}</div>
            <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px">
              <button type="button" @click="$router.back()" class="btn btn-outline">取消</button>
              <button type="submit" class="btn btn-gold" :disabled="submitting">{{ submitting ? '添加中...' : '保存客户' }}</button>
            </div>
          </form>
        </div>
      </div>

      <aside class="aside-panel">
        <div class="card">
          <div class="card-head"><span class="card-title">客户管理提示</span></div>
          <div class="card-body">
            <ul class="tips">
              <li>客户信息<b>仅您可见</b>，安全隔离</li>
              <li>关联案件将自动归集到该客户</li>
              <li>企业客户建议补全<b>统一社会信用代码</b></li>
              <li>标签用于快速筛选与群发</li>
            </ul>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><span class="card-title">快捷操作</span></div>
          <div class="card-body">
            <div class="mini-row"><router-link class="sec-more" to="/clients">查看通讯录 ›</router-link></div>
            <div class="mini-row"><router-link class="sec-more" to="/cases/new">新建关联案件 ›</router-link></div>
          </div>
        </div>
      </aside>
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
