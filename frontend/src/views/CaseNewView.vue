<template>
  <div>
    <div class="page-header"><h1 class="page-title">新建案件</h1></div>
    <div class="card" style="max-width:700px">
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-row">
            <div class="form-group"><label class="form-label">案由 <span style="color:var(--error)">*</span></label>
              <select v-model="form.case_type" class="form-select" required><option value="">请选择</option><option>买卖合同纠纷</option><option>民间借贷纠纷</option><option>离婚纠纷</option><option>劳动仲裁</option><option>侵权责任纠纷</option><option>建设工程合同纠纷</option><option>租赁合同纠纷</option><option>交通事故责任纠纷</option><option>其他</option></select></div>
            <div class="form-group"><label class="form-label">状态</label><select v-model="form.status" class="form-select"><option value="进行中">进行中</option><option value="待立案">待立案</option><option value="已结案">已结案</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">原告 <span style="color:var(--error)">*</span></label><input v-model="form.plaintiff" type="text" placeholder="姓名或公司名称" class="form-input" required /></div>
            <div class="form-group"><label class="form-label">被告 <span style="color:var(--error)">*</span></label><input v-model="form.defendant" type="text" placeholder="姓名或公司名称" class="form-input" required /></div>
          </div>

          <details style="margin-bottom:12px"><summary style="font-size:13px;color:var(--navy-700);font-weight:500;cursor:pointer">原告详细信息（选填）</summary>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px;padding:12px;background:#fff7ed;border-radius:8px;border:1px solid #fed7aa">
              <div class="form-group"><label class="form-label" style="font-size:12px">性别</label><select v-model="pInfo.gender" class="form-select"><option value="">请选择</option><option>男</option><option>女</option></select></div>
              <div class="form-group"><label class="form-label" style="font-size:12px">出生日期</label><input v-model="pInfo.birth" type="text" placeholder="如 1985年3月15日" class="form-input" /></div>
              <div class="form-group"><label class="form-label" style="font-size:12px">民族</label><input v-model="pInfo.ethnicity" type="text" placeholder="汉族" class="form-input" /></div>
              <div class="form-group" style="grid-column:span 2"><label class="form-label" style="font-size:12px">身份证号</label><input v-model="pInfo.id_card" type="text" placeholder="身份证号码" class="form-input" /></div>
              <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="pInfo.phone" type="text" placeholder="手机号" class="form-input" /></div>
              <div class="form-group" style="grid-column:span 3"><label class="form-label" style="font-size:12px">住址</label><input v-model="pInfo.address" type="text" placeholder="详细住址" class="form-input" /></div>
            </div>
          </details>

          <details style="margin-bottom:12px"><summary style="font-size:13px;color:var(--navy-700);font-weight:500;cursor:pointer">被告详细信息（选填）</summary>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:8px;padding:12px;background:var(--surface-alt);border-radius:8px">
              <div class="form-group"><label class="form-label" style="font-size:12px">法定代表人</label><input v-model="dInfo.legal_rep" type="text" placeholder="法人代表" class="form-input" /></div>
              <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="dInfo.phone" type="text" placeholder="联系电话" class="form-input" /></div>
              <div class="form-group" style="grid-column:span 2"><label class="form-label" style="font-size:12px">住所地</label><input v-model="dInfo.address" type="text" placeholder="被告地址" class="form-input" /></div>
            </div>
          </details>

          <div class="form-group"><label class="form-label">管辖法院</label><input v-model="form.court_name" type="text" placeholder="如 XX市XX区人民法院" class="form-input" /></div>

          <div class="form-row">
            <div class="form-group"><label class="form-label">标的额（元）</label><input v-model.number="form.subject_amount" type="number" placeholder="0" class="form-input" /></div>
            <div class="form-group"><label class="form-label">委托日期</label><input v-model="form.commission_date" type="date" class="form-input" /></div>
          </div>
          <div class="form-group"><label class="form-label">补充描述</label><textarea v-model="form.description" rows="4" placeholder="案件背景、关键事实等" class="form-textarea"></textarea></div>

          <div v-if="error" style="padding:10px;border-radius:6px;background:#fef2f2;color:var(--error);font-size:13px;margin-bottom:16px">{{ error }}</div>

          <div style="display:flex;justify-content:flex-end;gap:8px">
            <button type="button" @click="$router.back()" class="btn btn-outline">取消</button>
            <button type="submit" class="btn btn-accent" :disabled="submitting">{{ submitting?'创建中...':'创建案件' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'; import { useRouter } from 'vue-router'; import api from '../api'
const router = useRouter(); const submitting = ref(false); const error = ref('')
const form = reactive({ case_type:'',plaintiff:'',defendant:'',subject_amount:0,commission_date:'',description:'',status:'进行中',court_name:'' })
const pInfo = reactive({ gender:'',birth:'',ethnicity:'',id_card:'',phone:'',address:'' })
const dInfo = reactive({ legal_rep:'',phone:'',address:'' })
async function handleSubmit() {
  if(!form.case_type||!form.plaintiff||!form.defendant){error.value='请填写必填字段';return}
  submitting.value = true; error.value = ''
  try { const payload = { ...form, plaintiff_detail:JSON.stringify(pInfo), defendant_detail:JSON.stringify(dInfo) }; if(!payload.commission_date) delete payload.commission_date
    const r = await api.post('/cases', payload); router.push(`/cases/${r.data.id}`) }
  catch(e) { error.value = e.response?.data?.detail || '创建失败' } finally { submitting.value = false }
}
</script>
