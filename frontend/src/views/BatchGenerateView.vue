<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">批量生成文书</h1>
    </div>

    <!-- 选择文书类型 -->
    <div class="card mb-6">
      <div class="card-header">
        <span class="card-title">步骤 1：选择文书类型</span>
      </div>
      <div class="card-body">
        <div class="doc-type-grid">
          <div v-for="dt in docTypes" :key="dt" @click="form.doc_type = dt"
            class="doc-type-card" :class="{ selected: form.doc_type === dt }">
            <div class="doc-type-card-label">{{ dt }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 公共信息 -->
    <div v-if="form.doc_type" class="card mb-6">
      <div class="card-header">
        <span class="card-title">步骤 2：公共信息（所有文书共用）</span>
      </div>
      <div class="card-body">
        <div class="form-group">
          <label class="form-label">管辖法院</label>
          <input v-model="form.court_name" type="text" placeholder="如 XX市XX区人民法院" class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label">诉讼请求（共享模板）</label>
          <textarea v-model="form.claims" rows="3" placeholder="1. 请求被告支付欠款及利息\n2. 请求被告承担本案诉讼费用" class="form-textarea"></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">案件事实（可用 {原告} {被告} {金额} 占位符）</label>
          <textarea v-model="form.facts" rows="4" :placeholder="`{原告}与{被告}于2025年签订借款合同，约定借款{金额}元，到期后{被告}未还款。`" class="form-textarea"></textarea>
        </div>
      </div>
    </div>

    <!-- 条目列表 -->
    <div v-if="form.doc_type" class="card mb-6">
      <div class="card-header">
        <span class="card-title">步骤 3：添加生成条目 ({{ entries.length }})</span>
        <button @click="addEntry" class="btn btn-accent btn-sm">+ 添加一行</button>
      </div>
      <div class="card-body">
        <div v-if="entries.length === 0" style="text-align:center;padding:40px;color:var(--text-muted)">
          点击右上角「添加一行」开始填写当事人信息
        </div>

        <div v-else class="space-y-2">
          <div v-for="(e, i) in entries" :key="i" style="display:flex;align-items:center;gap:8px">
            <span style="color:var(--text-muted);font-size:13px;width:24px;text-align:center;flex-shrink:0">{{ i + 1 }}</span>
            <input v-model="e.plaintiff_name" type="text" placeholder="原告" class="form-input" style="flex:1;height:36px" />
            <input v-model="e.defendant_name" type="text" placeholder="被告" class="form-input" style="flex:1;height:36px" />
            <input v-model.number="e.amount" type="number" placeholder="标的额" class="form-input" style="width:120px;height:36px;flex-shrink:0" />
            <button @click="entries.splice(i, 1)" class="btn btn-ghost btn-sm" style="color:var(--error);flex-shrink:0">删除</button>
          </div>
        </div>

        <!-- 快速粘贴 -->
        <details style="margin-top:16px">
          <summary style="font-size:13px;color:var(--accent);cursor:pointer;font-weight:500">📋 快速粘贴（每行一条：原告 被告 金额，空格或Tab分隔）</summary>
          <textarea v-model="pasteText" rows="6" placeholder="张三 李四 200000\n王五 赵六 150000" class="form-textarea" style="margin-top:8px;min-height:100px"></textarea>
          <button @click="parsePaste" class="btn btn-outline btn-sm" style="margin-top:8px">解析并添加</button>
        </details>
      </div>
    </div>

    <!-- 生成按钮 -->
    <div v-if="form.doc_type && entries.length > 0" style="text-align:center;margin-bottom:24px">
      <button @click="startBatch" class="btn btn-accent btn-lg" :disabled="generating" style="font-size:16px">
        {{ generating ? `正在生成 ${progress.current}/${progress.total}...` : `批量生成 ${entries.length} 份${form.doc_type}` }}
      </button>
      <div v-if="generateError" style="margin-top:12px;font-size:13px;color:var(--error)">{{ generateError }}</div>
    </div>

    <!-- 结果 -->
    <div v-if="results.length > 0" class="card">
      <div class="card-header">
        <span class="card-title">生成结果（{{ results.filter(r => r.success).length }}/{{ results.length }} 成功）</span>
      </div>
      <div class="card-body" style="max-height:400px;overflow-y:auto">
        <div v-for="r in results" :key="r.index" class="file-item">
          <div class="file-info">
            <div class="file-name">{{ r.success ? '✅' : '❌' }} {{ r.plaintiff }} vs {{ r.defendant }}</div>
            <div class="file-meta">{{ r.success ? '生成成功' : '失败: ' + r.error }}</div>
          </div>
          <div v-if="r.success" style="display:flex;gap:8px;flex-shrink:0">
            <button @click="viewDoc(r.document_id)" class="btn btn-ghost btn-sm">查看</button>
            <button @click="downloadWord(r.document_id)" class="btn btn-ghost btn-sm">Word</button>
            <button @click="downloadPdf(r.document_id)" class="btn btn-ghost btn-sm">PDF</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

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
function downloadWord(id) { window.open(`/api/documents/${id}/download/docx`, '_blank') }
function downloadPdf(id) { window.open(`/api/documents/${id}/download/pdf`, '_blank') }
</script>
