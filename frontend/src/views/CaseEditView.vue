<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">编辑案件</div>
        <div class="page-sub">案件编号：{{ caseInfo.case_no }}</div>
      </div>
    </div>
    <div v-if="loading" class="empty">加载中...</div>
    <div v-else class="card" style="max-width:720px">
      <div class="card-head"><span class="card-title">案件信息</span><span class="form-hint">带 <span style="color:var(--danger)">*</span> 为必填</span></div>
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">案由 <span class="req">*</span></label><select v-model="form.case_type" class="form-select" required><option value="">请选择</option><option>买卖合同纠纷</option><option>民间借贷纠纷</option><option>离婚纠纷</option><option>劳动仲裁</option><option>侵权责任纠纷</option><option>建设工程合同纠纷</option><option>租赁合同纠纷</option><option>交通事故责任纠纷</option><option>其他</option></select></div>
            <div class="form-group"><label class="form-label">状态</label><select v-model="form.status" class="form-select"><option value="进行中">进行中</option><option value="待立案">待立案</option><option value="已结案">已结案</option></select></div>
            <div class="form-group"><label class="form-label">原告 <span class="req">*</span></label><input v-model="form.plaintiff" type="text" class="form-input" required /></div>
            <div class="form-group"><label class="form-label">被告 <span class="req">*</span></label><input v-model="form.defendant" type="text" class="form-input" required /></div>
            <div class="form-group"><label class="form-label">标的额（元）</label><input v-model.number="form.subject_amount" type="number" class="form-input mono" /></div>
            <div class="form-group"><label class="form-label">委托日期</label><input v-model="form.commission_date" type="date" class="form-input" /></div>
            <div class="form-group col-span"><label class="form-label">补充描述</label><textarea v-model="form.description" rows="4" class="form-textarea"></textarea></div>
          </div>
          <div v-if="error" class="auth-error">{{ error }}</div>
          <div v-if="success" style="padding:10px 12px;border-radius:8px;background:var(--ok-bg);color:var(--ok);font-size:13px;margin-bottom:16px">{{ success }}</div>
          <div style="display:flex;justify-content:space-between">
            <button type="button" @click="confirmDelete" class="btn btn-danger btn-sm">删除</button>
            <div style="display:flex;gap:8px">
              <button type="button" @click="$router.push(`/cases/${caseId}`)" class="btn btn-outline">取消</button>
              <button type="submit" class="btn btn-gold" :disabled="submitting">{{ submitting?'保存中...':'保存修改' }}</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'; import { useRoute, useRouter } from 'vue-router'; import api from '../api'
const route = useRoute(); const router = useRouter(); const caseId = route.params.id
const caseInfo = ref({}); const loading = ref(true); const submitting = ref(false); const error = ref(''); const success = ref('')
const form = reactive({ case_type:'',plaintiff:'',defendant:'',subject_amount:0,commission_date:'',description:'',status:'' })
onMounted(async () => {
  try { const r = await api.get(`/cases/${caseId}`); caseInfo.value = r.data; Object.assign(form, { case_type:r.data.case_type,plaintiff:r.data.plaintiff,defendant:r.data.defendant,subject_amount:r.data.subject_amount,commission_date:r.data.commission_date?.slice(0,10)||'',description:r.data.description||'',status:r.data.status }) } catch(e) { error.value = e?.response?.data?.detail || '加载案件失败' } finally { loading.value = false }
})
async function handleSubmit() {
  error.value='';success.value='';submitting.value=true
  try { const p = { ...form }; if(!p.commission_date) delete p.commission_date; await api.put(`/cases/${caseId}`,p); success.value='保存成功！'; setTimeout(()=>router.push(`/cases/${caseId}`),800) }
  catch(e) { error.value = e.response?.data?.detail||'保存失败' } finally { submitting.value = false }
}
async function confirmDelete() {
  if(!confirm(`确定删除「${caseInfo.value.plaintiff}${caseInfo.value.case_type}」？此操作不可撤销。`)) return
  try { await api.delete(`/cases/${caseId}`); router.push('/cases') } catch(e) { alert('删除失败') }
}
</script>
