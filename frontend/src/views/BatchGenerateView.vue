<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">批量生成文书</div>
        <div class="page-sub">选择文书模板，填写多条当事人信息，一次性生成草稿</div>
      </div>
    </div>

    <div class="two-col">
      <div style="display:flex;flex-direction:column;gap:20px;min-width:0">
        <div class="card">
          <div class="card-head"><span class="card-title">1 · 选择文书模板</span></div>
          <div class="card-body">
            <div class="doc-type-grid">
              <div v-for="dt in docTypes" :key="dt" @click="form.doc_type = dt"
                class="doc-type-card" :class="{ selected: form.doc_type === dt }">{{ dt }}</div>
            </div>
          </div>
        </div>

        <div v-if="form.doc_type" class="card">
          <div class="card-head"><span class="card-title">2 · 公共信息（所有文书共用）</span></div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">管辖法院</label>
              <input v-model="form.court_name" type="text" placeholder="如 苏州市吴中区人民法院" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">诉讼请求（共享模板）</label>
              <textarea v-model="form.claims" rows="3" placeholder="1. 请求被告支付欠款及利息&#10;2. 请求被告承担本案诉讼费用" class="form-textarea"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">案件事实（可用 {原告} {被告} {金额} 占位符）</label>
              <textarea v-model="form.facts" rows="4" :placeholder="`{原告}与{被告}于2025年签订借款合同，约定借款{金额}元，到期后{被告}未还款。`" class="form-textarea"></textarea>
            </div>
          </div>
        </div>

        <div v-if="form.doc_type" class="card">
          <div class="card-head">
            <span class="card-title">3 · 添加生成条目 ({{ entries.length }})</span>
            <button @click="addEntry" class="btn btn-gold btn-sm">+ 添加一行</button>
          </div>
          <div class="card-body">
            <div v-if="entries.length === 0" class="empty" style="padding:32px">
              点击右上角「添加一行」开始填写当事人信息
            </div>

            <div v-else style="display:flex;flex-direction:column;gap:8px">
              <div v-for="(e, i) in entries" :key="i" style="display:flex;align-items:center;gap:8px">
                <span style="color:var(--muted);font-size:13px;width:24px;text-align:center;flex-shrink:0;font-family:var(--serif)">{{ i + 1 }}</span>
                <input v-model="e.plaintiff_name" type="text" placeholder="原告" class="form-input" style="flex:1" />
                <input v-model="e.defendant_name" type="text" placeholder="被告" class="form-input" style="flex:1" />
                <input v-model.number="e.amount" type="number" placeholder="标的额" class="form-input" style="width:120px;flex-shrink:0" />
                <button @click="entries.splice(i, 1)" class="btn btn-ghost btn-sm" style="color:var(--danger);flex-shrink:0">删除</button>
              </div>
            </div>

            <details style="margin-top:16px">
              <summary style="font-size:13px;color:var(--gold-deep);cursor:pointer;font-weight:500">📋 快速粘贴（每行一条：原告 被告 金额，空格或Tab分隔）</summary>
              <textarea v-model="pasteText" rows="6" placeholder="张三 李四 200000&#10;王五 赵六 150000" class="form-textarea" style="margin-top:8px;min-height:100px"></textarea>
              <button @click="parsePaste" class="btn btn-outline btn-sm" style="margin-top:8px">解析并添加</button>
            </details>
          </div>
        </div>

        <div v-if="form.doc_type && entries.length > 0" style="margin-top:4px">
          <button @click="startBatch" class="btn btn-gold btn-lg" :disabled="generating" style="width:100%;justify-content:center">
            {{ generating ? `正在生成 ${progress.current}/${progress.total}...` : `启动批量生成（${entries.length} 份）` }}
          </button>
          <div v-if="generateError" style="margin-top:12px;font-size:13px;color:var(--danger);text-align:center">{{ generateError }}</div>
        </div>
      </div>

      <div>
        <div class="sec-head"><span class="sec-mark">壹</span><span class="sec-title">生成进度</span></div>
        <div class="card" style="margin-bottom:20px">
          <div v-if="results.length === 0" class="empty" style="padding:40px">尚未开始生成</div>
          <div v-for="r in results" :key="r.index" style="display:flex;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid var(--line)">
            <span class="badge" :class="r.success ? 'b-success' : 'b-error'">{{ r.success ? '已完成' : '失败' }}</span>
            <div style="flex:1;min-width:0"><div style="font-weight:600;font-size:13.5px">{{ r.plaintiff }} vs {{ r.defendant }}</div><div v-if="!r.success" style="font-size:12px;color:var(--danger)">失败: {{ r.error }}</div></div>
            <div v-if="r.success" style="display:flex;gap:6px;flex-shrink:0">
              <button @click="viewDoc(r.document_id)" class="btn btn-ghost btn-sm">查看</button>
              <button @click="downloadWord(r.document_id)" class="btn btn-ghost btn-sm">Word</button>
              <button @click="downloadPdf(r.document_id)" class="btn btn-ghost btn-sm">PDF</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body" style="text-align:center;color:var(--muted);font-size:13px">
            <div style="font-family:var(--serif);font-size:30px;font-weight:700;color:var(--ink)">{{ results.filter(r => r.success).length }} / {{ progress.total || results.length }}</div>
            已完成 · {{ generating ? '生成中' : (results.length ? '已结束' : '等待启动') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api, { authDownload } from '../api'

const router = useRouter()
const docTypes = ['民事起诉状', '民事答辩状', '律师函', '催收函', '代理词', '法律意见书', '上诉状', '再审申请书']

const form = reactive({ doc_type: '', claims: '', facts: '', court_name: '' })
const entries = ref([])
const pasteText = ref('')
const generating = ref(false)
const generateError = ref('')
const results = ref([])
const progress = reactive({ current: 0, total: 0 })

function addEntry() { entries.value.push({ plaintiff_name: '', defendant_name: '', amount: 0 }) }

function parsePaste() {
  pasteText.value.trim().split('\n').filter(l => l.trim()).forEach(line => {
    const parts = line.trim().split(/[\t ]+/)
    if (parts.length >= 2) entries.value.push({ plaintiff_name: parts[0], defendant_name: parts[1], amount: parseFloat(parts[2]) || 0 })
  })
  pasteText.value = ''
}

function replaceTemplate(template, entry) {
  return template.replace(/{原告}/g, entry.plaintiff_name).replace(/{被告}/g, entry.defendant_name).replace(/{金额}/g, String(entry.amount || ''))
}

async function startBatch() {
  generateError.value = ''; generating.value = true; results.value = []
  try {
    const payload = {
      doc_type: form.doc_type, claims: form.claims, facts: form.facts, court_name: form.court_name,
      entries: entries.value.map(e => ({ plaintiff_name: e.plaintiff_name, defendant_name: e.defendant_name, amount: e.amount, custom_facts: replaceTemplate(form.facts, e) }))
    }
    progress.total = payload.entries.length; progress.current = 0
    const res = await api.post('/documents/generate-batch', payload)
    results.value = res.data.data.results; progress.current = progress.total
  } catch (err) {
    generateError.value = err.response?.data?.detail || '批量生成失败'
  } finally { generating.value = false }
}

function viewDoc(id) { router.push(`/documents/${id}`) }
function downloadWord(id) { authDownload(`/documents/${id}/download/docx`, `${form.doc_type}.docx`) }
function downloadPdf(id) { authDownload(`/documents/${id}/download/pdf`, `${form.doc_type}.pdf`) }
</script>
