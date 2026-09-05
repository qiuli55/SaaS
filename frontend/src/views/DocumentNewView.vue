<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">生成文书</div>
        <div class="page-sub">由 AI 根据案情起草，自动校验法条引用</div>
      </div>
    </div>

    <div class="two-col">
      <!-- 左：表单与结果 -->
      <div style="display:flex;flex-direction:column;gap:20px;min-width:0">
        <div class="card">
          <div class="card-head"><span class="card-title">步骤 1 · 选择文书类型</span></div>
          <div class="card-body">
            <div class="doc-type-grid">
              <div v-for="dt in docTypes" :key="dt" @click="form.doc_type=dt" class="doc-type-card" :class="{selected:form.doc_type===dt}">{{ dt }}</div>
            </div>
          </div>
        </div>

        <div v-if="form.doc_type" class="card">
          <div class="card-head"><span class="card-title">步骤 2 · 填写当事人信息与案件详情</span></div>
          <div class="card-body">
            <div class="case-facts">
              <div>原告：<b>{{ caseInfo.plaintiff }}</b></div>
              <div>被告：<b>{{ caseInfo.defendant }}</b></div>
              <div>案由：<b>{{ caseInfo.case_type }}</b></div>
              <div>标的额：<b class="mono">{{ caseInfo.subject_amount ? '¥' + formatMoney(caseInfo.subject_amount) : '—' }}</b></div>
            </div>

            <details style="margin-bottom:16px">
              <summary style="font-size:13px;color:var(--ink-700);font-weight:600;cursor:pointer">原告详细信息（选填）</summary>
              <div class="form-grid" style="margin-top:12px;padding:14px;background:var(--paper-2);border-radius:10px">
                <div class="form-group"><label class="form-label" style="font-size:12px">性别</label><select v-model="pInfo.gender" class="form-select"><option value="">请选择</option><option>男</option><option>女</option></select></div>
                <div class="form-group"><label class="form-label" style="font-size:12px">出生日期</label><input v-model="pInfo.birth" type="text" placeholder="如 1985年3月15日" class="form-input" /></div>
                <div class="form-group"><label class="form-label" style="font-size:12px">民族</label><input v-model="pInfo.ethnicity" type="text" placeholder="汉族" class="form-input" /></div>
                <div class="form-group col-span"><label class="form-label" style="font-size:12px">身份证号</label><input v-model="pInfo.id_card" type="text" placeholder="身份证号码" class="form-input" /></div>
                <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="pInfo.phone" type="text" placeholder="手机号" class="form-input" /></div>
                <div class="form-group col-span"><label class="form-label" style="font-size:12px">住址</label><input v-model="pInfo.address" type="text" placeholder="详细住址" class="form-input" /></div>
              </div>
            </details>

            <details style="margin-bottom:16px">
              <summary style="font-size:13px;color:var(--ink-700);font-weight:600;cursor:pointer">被告详细信息（选填）</summary>
              <div class="form-grid" style="margin-top:12px;padding:14px;background:var(--paper-2);border-radius:10px">
                <div class="form-group"><label class="form-label" style="font-size:12px">法定代表人</label><input v-model="dInfo.legal_rep" type="text" placeholder="法人代表" class="form-input" /></div>
                <div class="form-group"><label class="form-label" style="font-size:12px">电话</label><input v-model="dInfo.phone" type="text" placeholder="联系电话" class="form-input" /></div>
                <div class="form-group col-span"><label class="form-label" style="font-size:12px">住所地</label><input v-model="dInfo.address" type="text" placeholder="被告地址" class="form-input" /></div>
              </div>
            </details>

            <div class="form-group"><label class="form-label">管辖法院</label><input v-model="form.court_name" type="text" placeholder="如 苏州市吴中区人民法院" class="form-input" /></div>
            <div class="form-group"><label class="form-label">诉讼请求</label><textarea v-model="form.claims" rows="3" placeholder="1. 请求被告支付货款20万元&#10;2. 请求被告承担本案诉讼费用" class="form-textarea"></textarea></div>
            <div class="form-group"><label class="form-label">案件事实描述</label><textarea v-model="form.facts" rows="5" :placeholder="`详细描述案件经过。例如：\n2026年1月15日，${caseInfo.plaintiff}与${caseInfo.defendant}签订购销合同...`" class="form-textarea"></textarea></div>

            <div style="text-align:center;margin-top:6px">
              <button @click="generateDocument" class="btn btn-gold btn-lg" :disabled="generating">{{ generating ? 'AI 正在生成中...' : '生成' + form.doc_type + '草稿' }}</button>
              <div v-if="generateError" style="margin-top:12px;font-size:13px;color:var(--danger)">{{ generateError }}</div>
            </div>
          </div>
        </div>

        <div v-if="result" class="card">
          <div class="card-head">
            <span class="card-title">生成结果</span>
            <div style="display:flex;gap:8px">
              <button @click="copyContent" class="btn btn-outline btn-sm">{{ copied?'已复制':'复制文本' }}</button>
              <button @click="downloadWord(result.id)" class="btn btn-gold btn-sm">Word</button>
              <button @click="downloadPdf(result.id)" class="btn btn-gold btn-sm">PDF</button>
            </div>
          </div>
          <div class="card-body">
            <div class="doc-preview">{{ result.final_content }}</div>
          </div>
          <div v-if="result.verified_articles?.length" class="card-body" style="padding-top:0">
            <div style="background:var(--ok-bg);border:1px solid #cfe7d3;border-radius:10px;padding:14px 18px">
              <div style="font-weight:600;color:var(--ok);margin-bottom:8px">法条引用校验</div>
              <div v-for="a in result.verified_articles" :key="a.law+a.article" style="display:flex;align-items:center;gap:8px;font-size:13px;padding:3px 0">
                <span>{{ a.verified?'✅':'⚠️' }}</span><span class="mono" style="color:var(--ok)">{{ a.law }}{{ a.article }}</span><span style="color:var(--muted)">— {{ a.verified?'存在':'需人工核实' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右：辅助面板 -->
      <aside class="aside-panel">
        <div class="card">
          <div class="card-head"><span class="card-title">写作提示</span></div>
          <div class="card-body">
            <ul class="tips">
              <li>案情描述越具体，<b>生成质量越高</b></li>
              <li>诉讼请求分条列出，便于法院审查</li>
              <li>涉及金额务必写明币种与数字</li>
              <li>生成后请人工核对<b>当事人信息</b></li>
            </ul>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><span class="card-title">常用法条</span></div>
          <div class="card-body">
            <div class="mini-row"><span class="t mono">《民法典》第617条</span><span class="m">瑕疵抗辩</span></div>
            <div class="mini-row"><span class="t mono">《民法典》第525条</span><span class="m">同时履行</span></div>
            <div class="mini-row"><span class="t mono">《民诉法》第122条</span><span class="m">起诉条件</span></div>
          </div>
        </div>
      </aside>
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

<style scoped>
.doc-preview{
  font-family:var(--serif); line-height:1.9; font-size:14px; color:var(--text);
  white-space:pre-wrap; word-break:break-word;
}
</style>
