<template>
  <div>
    <div class="page-header"><div><h1 class="page-title">生成文书</h1></div></div>

    <div class="card mb-6"><div class="card-header"><span class="card-title">步骤 1：选择文书类型</span></div>
      <div class="card-body"><div class="doc-type-grid">
        <div v-for="dt in docTypes" :key="dt" @click="form.doc_type=dt" class="doc-type-card" :class="{selected:form.doc_type===dt}"><div class="doc-type-card-label">{{ dt }}</div></div>
      </div></div>
    </div>

    <div v-if="form.doc_type" class="card mb-6"><div class="card-header"><span class="card-title">步骤 2：填写当事人信息和案件详情</span></div>
      <div class="card-body">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:12px;background:var(--navy-50);border-radius:8px;margin-bottom:20px;font-size:13px">
          <div><span style="color:var(--text-muted)">原告：</span><strong>{{ caseInfo.plaintiff }}</strong></div>
          <div><span style="color:var(--text-muted)">被告：</span><strong>{{ caseInfo.defendant }}</strong></div>
          <div><span style="color:var(--text-muted)">案由：</span><strong>{{ caseInfo.case_type }}</strong></div>
          <div><span style="color:var(--text-muted)">标的额：</span><strong>¥{{ formatMoney(caseInfo.subject_amount) }}</strong></div>
        </div>

        <details style="margin-bottom:16px"><summary style="font-size:13px;color:var(--navy-700);font-weight:500;cursor:pointer">原告详细信息（选填）</summary>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px;padding:12px;background:#fff7ed;border-radius:8px;border:1px solid #fed7aa">
            <div class="form-group"><label class="form-label" style="font-size:12px">性别</label><select v-model="pInfo.gender" class="form-select"><option value="">请选择</option><option>男</option><option>女</option></select></div>
            <div class="form-group"><label class="form-label" style="font-size:12px">出生日期</label><input v-model="pInfo.birth" type="text" placeholder="如 1985年3月15日" class="form-input" /></div>
            <div class="form-group"><label class="form-label" style="font-size:12px">民族</label><input v-model="pInfo.ethnicity" type="text" placeholder="汉族" class="form-input" /></div>
            <div class="form-group" style="grid-column:span 2"><label class="form-label" style="font-size:12px">身份证号</label><input v-model="pInfo.id_card" type="text" placeholder="身份证号码" class="form-input" /></div>
            <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="pInfo.phone" type="text" placeholder="手机号" class="form-input" /></div>
            <div class="form-group" style="grid-column:span 3"><label class="form-label" style="font-size:12px">住址</label><input v-model="pInfo.address" type="text" placeholder="详细住址" class="form-input" /></div>
          </div>
        </details>

        <details style="margin-bottom:16px"><summary style="font-size:13px;color:var(--navy-700);font-weight:500;cursor:pointer">被告详细信息（选填）</summary>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:12px;padding:12px;background:var(--surface-alt);border-radius:8px">
            <div class="form-group"><label class="form-label" style="font-size:12px">法定代表人</label><input v-model="dInfo.legal_rep" type="text" placeholder="法人代表" class="form-input" /></div>
            <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="dInfo.phone" type="text" placeholder="联系电话" class="form-input" /></div>
            <div class="form-group" style="grid-column:span 2"><label class="form-label" style="font-size:12px">住所地</label><input v-model="dInfo.address" type="text" placeholder="被告地址" class="form-input" /></div>
          </div>
        </details>

        <div class="form-group"><label class="form-label">管辖法院</label><input v-model="form.court_name" type="text" placeholder="如 XX市XX区人民法院" class="form-input" /></div>
        <div class="form-group"><label class="form-label">诉讼请求</label><textarea v-model="form.claims" rows="4" placeholder="1. 请求被告支付货款20万元\n2. 请求被告承担本案诉讼费用" class="form-textarea"></textarea></div>
        <div class="form-group"><label class="form-label">案件事实描述</label><textarea v-model="form.facts" rows="6" :placeholder="`详细描述案件经过。例如：\n2026年1月15日，${caseInfo.plaintiff}与${caseInfo.defendant}签订购销合同...`" class="form-textarea"></textarea></div>
      </div>
    </div>

    <div v-if="form.doc_type" style="text-align:center;margin-bottom:24px">
      <button @click="generateDocument" class="btn btn-accent btn-lg" :disabled="generating" style="font-size:16px">{{ generating ? 'AI 正在生成中...' : '生成' + form.doc_type + '草稿' }}</button>
      <div v-if="generateError" style="margin-top:12px;font-size:13px;color:var(--error)">{{ generateError }}</div>
    </div>

    <div v-if="result" class="card">
      <div class="card-header"><span class="card-title">生成结果</span>
        <div style="display:flex;gap:8px">
          <button @click="copyContent" class="btn btn-outline btn-sm">{{ copied?'已复制':'复制文本' }}</button>
          <button @click="downloadWord(result.id)" class="btn btn-accent btn-sm">Word</button>
          <button @click="downloadPdf(result.id)" class="btn btn-accent btn-sm">PDF</button>
        </div>
      </div>
      <div class="card-body"><div class="doc-preview">{{ result.final_content }}</div></div>
      <div v-if="result.verified_articles?.length" class="card-body" style="padding-top:0">
        <div style="background:#ecfdf5;border:1px solid #d1fae5;border-radius:8px;padding:16px 20px">
          <div style="font-weight:600;color:var(--success);margin-bottom:8px">法条引用校验</div>
          <div v-for="a in result.verified_articles" :key="a.law+a.article" style="display:flex;align-items:center;gap:8px;font-size:13px;padding:4px 0">
            <span>{{ a.verified?'✅':'⚠️' }}</span><span style="font-family:'JetBrains Mono',monospace;color:var(--success)">{{ a.law }}{{ a.article }}</span><span style="color:var(--text-secondary)">— {{ a.verified?'存在':'需人工核实' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'; import { useRoute } from 'vue-router'; import api, { authDownload } from '../api'
const route = useRoute(); const caseId = route.params.id
const docTypes = ['民事起诉状','民事答辩状','律师函','代理词','法律意见书','上诉状','再审申请书','催收函']
const caseInfo = ref({}); const generating = ref(false); const generateError = ref(''); const result = ref(null); const copied = ref(false)
const form = reactive({ doc_type:'', claims:'', facts:'', court_name:'' })
const pInfo = reactive({ gender:'',birth:'',ethnicity:'',id_card:'',phone:'',address:'' })
const dInfo = reactive({ legal_rep:'',phone:'',address:'' })

onMounted(async () => {
  // 从URL参数预选文书类型（重新生成场景）
  if (route.query.doc_type) form.doc_type = route.query.doc_type

  try { const r = await api.get(`/cases/${caseId}`); caseInfo.value = r.data
    if(r.data.plaintiff_detail) try { Object.assign(pInfo, JSON.parse(r.data.plaintiff_detail)) } catch(e) { console.error('解析原告详情失败', e) }
    if(r.data.defendant_detail) try { Object.assign(dInfo, JSON.parse(r.data.defendant_detail)) } catch(e) { console.error('解析被告详情失败', e) }
    if(r.data.court_name) form.court_name = r.data.court_name
  } catch(e) { generateError.value = e?.response?.data?.detail || '加载案件信息失败' }
})

async function generateDocument() {
  generateError.value = ''; generating.value = true; result.value = null
  try { const r = await api.post('/documents/generate', { case_id:Number(caseId), doc_type:form.doc_type, claims:form.claims, facts:form.facts, plaintiff_info:JSON.stringify(pInfo), defendant_info:JSON.stringify(dInfo), court_name:form.court_name })
    result.value = r.data.data } catch(e) { generateError.value = e.response?.data?.detail||'生成失败' } finally { generating.value = false }
}
function copyContent() { if(result.value?.final_content) { navigator.clipboard.writeText(result.value.final_content); copied.value = true; setTimeout(()=>copied.value=false, 2000) } }
function downloadWord(id) { authDownload(`/documents/${id}/download/docx`, `${form.doc_type}.docx`) }
function downloadPdf(id) { authDownload(`/documents/${id}/download/pdf`, `${form.doc_type}.pdf`) }
function formatMoney(v) { return Number(v||0).toLocaleString('zh-CN') }
</script>
