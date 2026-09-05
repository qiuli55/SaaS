<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">新建案件</div>
        <div class="page-sub">填写案件基础信息，保存后可一键生成文书</div>
      </div>
    </div>

    <div class="two-col">
      <div class="card">
        <div class="card-head"><span class="card-title">案件信息</span><span class="form-hint">带 <span style="color:var(--danger)">*</span> 为必填</span></div>
        <div class="card-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">案由 <span class="req">*</span></label>
                <select v-model="form.case_type" class="form-select" required><option value="">请选择</option><option>买卖合同纠纷</option><option>民间借贷纠纷</option><option>离婚纠纷</option><option>劳动仲裁</option><option>侵权责任纠纷</option><option>建设工程合同纠纷</option><option>租赁合同纠纷</option><option>交通事故责任纠纷</option><option>其他</option></select>
              </div>
              <div class="form-group">
                <label class="form-label">案件状态</label>
                <select v-model="form.status" class="form-select"><option value="进行中">进行中</option><option value="待立案">待立案</option><option value="已结案">已结案</option></select>
              </div>
              <div class="form-group">
                <label class="form-label">原告 <span class="req">*</span></label>
                <input v-model="form.plaintiff" type="text" placeholder="姓名或公司名称" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">被告 <span class="req">*</span></label>
                <input v-model="form.defendant" type="text" placeholder="姓名或公司名称" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">标的额（元）</label>
                <input v-model.number="form.subject_amount" type="number" placeholder="如 320000" class="form-input mono" />
              </div>
              <div class="form-group">
                <label class="form-label">委托日期</label>
                <input v-model="form.commission_date" type="date" class="form-input" />
              </div>
              <div class="form-group col-span">
                <label class="form-label">管辖法院</label>
                <input v-model="form.court_name" type="text" placeholder="如 苏州市吴中区人民法院" class="form-input" />
              </div>

              <details class="col-span" style="margin-bottom:2px">
                <summary style="font-size:13px;color:var(--ink-500);font-weight:500;cursor:pointer">原告详细信息（选填）</summary>
                <div class="form-grid" style="margin-top:10px;padding:14px;background:var(--paper-2);border-radius:10px;border:1px solid var(--line)">
                  <div class="form-group"><label class="form-label" style="font-size:12px">性别</label><select v-model="pInfo.gender" class="form-select"><option value="">请选择</option><option>男</option><option>女</option></select></div>
                  <div class="form-group"><label class="form-label" style="font-size:12px">出生日期</label><input v-model="pInfo.birth" type="text" placeholder="如 1985年3月15日" class="form-input" /></div>
                  <div class="form-group"><label class="form-label" style="font-size:12px">民族</label><input v-model="pInfo.ethnicity" type="text" placeholder="汉族" class="form-input" /></div>
                  <div class="form-group col-span"><label class="form-label" style="font-size:12px">身份证号</label><input v-model="pInfo.id_card" type="text" placeholder="身份证号码" class="form-input" /></div>
                  <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="pInfo.phone" type="text" placeholder="手机号" class="form-input" /></div>
                  <div class="form-group col-span"><label class="form-label" style="font-size:12px">住址</label><input v-model="pInfo.address" type="text" placeholder="详细住址" class="form-input" /></div>
                </div>
              </details>

              <details class="col-span" style="margin-bottom:2px">
                <summary style="font-size:13px;color:var(--ink-500);font-weight:500;cursor:pointer">被告详细信息（选填）</summary>
                <div class="form-grid" style="margin-top:10px;padding:14px;background:var(--paper-2);border-radius:10px;border:1px solid var(--line)">
                  <div class="form-group"><label class="form-label" style="font-size:12px">法定代表人</label><input v-model="dInfo.legal_rep" type="text" placeholder="法人代表" class="form-input" /></div>
                  <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="dInfo.phone" type="text" placeholder="联系电话" class="form-input" /></div>
                  <div class="form-group col-span"><label class="form-label" style="font-size:12px">住所地</label><input v-model="dInfo.address" type="text" placeholder="被告地址" class="form-input" /></div>
                </div>
              </details>

              <div class="form-group col-span">
                <label class="form-label">补充描述</label>
                <textarea v-model="form.description" rows="3" placeholder="案件背景、关键事实等" class="form-textarea"></textarea>
              </div>
            </div>

            <div v-if="error" class="auth-error">{{ error }}</div>
            <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px">
              <button type="button" @click="$router.back()" class="btn btn-outline">取消</button>
              <button type="submit" class="btn btn-gold" :disabled="submitting">{{ submitting ? '创建中...' : '保存案件' }}</button>
            </div>
          </form>
        </div>
      </div>

      <aside class="aside-panel">
        <div class="card">
          <div class="card-head"><span class="card-title">填写指南</span></div>
          <div class="card-body">
            <ul class="tips">
              <li><b>案由 / 原告 / 被告</b> 为必填项</li>
              <li>标的额仅填数字，单位默认「元」</li>
              <li>保存后可一键跳转到<b>生成文书</b></li>
              <li>「待立案」状态暂不计入进度表</li>
            </ul>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><span class="card-title">状态说明</span></div>
          <div class="card-body">
            <div class="mini-row"><span class="badge b-info">进行中</span><span class="m">已受理</span></div>
            <div class="mini-row"><span class="badge b-warning">待立案</span><span class="m">尚未提交</span></div>
            <div class="mini-row"><span class="badge b-success">已结案</span><span class="m">已归档</span></div>
          </div>
        </div>
      </aside>
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
