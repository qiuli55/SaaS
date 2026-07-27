<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.push('/cases')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <h1 class="text-2xl font-bold text-gray-800">批量生成文书</h1>
    </div>

    <!-- 选择文书类型 -->
    <div class="card mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">选择文书类型</h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button v-for="dt in docTypes" :key="dt" @click="form.doc_type = dt"
          class="p-3 rounded-lg border-2 text-center font-medium transition-all"
          :class="form.doc_type === dt ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-200 text-gray-600 hover:border-gray-300 bg-white'">
          {{ dt }}
        </button>
      </div>
    </div>

    <!-- 公共信息 -->
    <div v-if="form.doc_type" class="card mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">公共信息（所有文书共用）</h2>
      <div class="space-y-4">
        <div>
          <label class="form-label">管辖法院</label>
          <input v-model="form.court_name" type="text" placeholder="如 XX市XX区人民法院" class="input-field" />
        </div>
        <div>
          <label class="form-label">诉讼请求（共享模板）</label>
          <textarea v-model="form.claims" rows="3" placeholder="例如：&#10;1. 请求被告支付欠款及利息&#10;2. 请求被告承担本案诉讼费用" class="input-field"></textarea>
        </div>
        <div>
          <label class="form-label">案件事实（共享模板，可用 {原告} {被告} {金额} 作为占位符）</label>
          <textarea v-model="form.facts" rows="4"
            placeholder="例如：{原告}与{被告}于2025年签订借款合同，约定借款{金额}元，到期后{被告}未还款。经多次催告无果，特提起诉讼。"
            class="input-field"></textarea>
        </div>
      </div>
    </div>

    <!-- 条目列表 -->
    <div v-if="form.doc_type" class="card mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">生成条目 ({{ entries.length }})</h2>
        <button @click="addEntry" class="btn-primary text-sm">+ 添加一行</button>
      </div>

      <div v-if="entries.length === 0" class="text-center py-6 text-gray-400">
        点击「添加一行」开始添加当事人信息
      </div>

      <div v-else class="space-y-2">
        <div v-for="(e, i) in entries" :key="i" class="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
          <span class="text-xs text-gray-400 pt-2 w-6 shrink-0">{{ i + 1 }}</span>
          <input v-model="e.plaintiff_name" type="text" placeholder="原告姓名" class="input-field text-sm flex-1" />
          <input v-model="e.defendant_name" type="text" placeholder="被告姓名" class="input-field text-sm flex-1" />
          <input v-model.number="e.amount" type="number" placeholder="标的额" class="input-field text-sm w-28 shrink-0" />
          <button @click="entries.splice(i, 1)" class="text-red-400 hover:text-red-600 px-2 py-2 shrink-0">✕</button>
        </div>
      </div>

      <!-- 快速粘贴 -->
      <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
        <details>
          <summary class="text-sm text-blue-700 cursor-pointer font-medium">📋 快速粘贴（每行一条：原告 被告 金额，用空格或Tab分隔）</summary>
          <textarea v-model="pasteText" rows="6" placeholder="张三 李四 200000&#10;王五 赵六 150000&#10;..." class="input-field text-sm mt-2"></textarea>
          <button @click="parsePaste" class="btn-secondary text-sm mt-2">解析并添加</button>
        </details>
      </div>
    </div>

    <!-- 生成按钮 -->
    <div v-if="form.doc_type && entries.length > 0" class="text-center mb-6">
      <button @click="startBatch" class="btn-primary text-lg px-8 py-3" :disabled="generating">
        {{ generating ? `🤖 正在生成 ${progress.current}/${progress.total}...` : `🤖 批量生成 ${entries.length} 份${form.doc_type}` }}
      </button>
      <div v-if="generateError" class="mt-3 text-sm text-red-600">{{ generateError }}</div>
    </div>

    <!-- 结果 -->
    <div v-if="results.length > 0" class="card">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">
        生成结果（{{ results.filter(r => r.success).length }}/{{ results.length }} 成功）
      </h2>
      <div class="space-y-2 max-h-[500px] overflow-y-auto">
        <div v-for="r in results" :key="r.index"
          class="flex items-center justify-between p-3 rounded-lg"
          :class="r.success ? 'bg-green-50' : 'bg-red-50'">
          <div class="min-w-0">
            <div class="font-medium text-sm">
              {{ r.success ? '✅' : '❌' }}
              {{ r.plaintiff }} vs {{ r.defendant }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ r.success ? '生成成功' : r.error }}
            </div>
          </div>
          <div v-if="r.success" class="flex space-x-2 shrink-0 ml-4">
            <button @click="viewDoc(r.document_id)" class="text-xs text-primary-600 hover:text-primary-700 font-medium">查看</button>
            <button @click="downloadWord(r.document_id)" class="text-xs text-primary-600 hover:text-primary-700 font-medium">Word</button>
            <button @click="downloadPdf(r.document_id)" class="text-xs text-primary-600 hover:text-primary-700 font-medium">PDF</button>
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

const form = reactive({
  doc_type: '',
  claims: '',
  facts: '',
  court_name: '',
})

const entries = ref([])
const pasteText = ref('')
const generating = ref(false)
const generateError = ref('')
const results = ref([])
const progress = reactive({ current: 0, total: 0 })

function addEntry() {
  entries.value.push({ plaintiff_name: '', defendant_name: '', amount: 0 })
}

function parsePaste() {
  const lines = pasteText.value.trim().split('\n').filter(l => l.trim())
  for (const line of lines) {
    const parts = line.trim().split(/[\t ]+/)
    if (parts.length >= 2) {
      entries.value.push({
        plaintiff_name: parts[0],
        defendant_name: parts[1],
        amount: parts.length >= 3 ? parseFloat(parts[2]) || 0 : 0,
      })
    }
  }
  pasteText.value = ''
}

function replaceTemplate(template, entry) {
  return template
    .replace(/{原告}/g, entry.plaintiff_name)
    .replace(/{被告}/g, entry.defendant_name)
    .replace(/{金额}/g, String(entry.amount || ''))
}

async function startBatch() {
  generateError.value = ''
  generating.value = true
  results.value = []

  try {
    const payload = {
      doc_type: form.doc_type,
      claims: form.claims,
      facts: form.facts,
      court_name: form.court_name,
      entries: entries.value.map(e => ({
        plaintiff_name: e.plaintiff_name,
        defendant_name: e.defendant_name,
        amount: e.amount,
        custom_facts: replaceTemplate(form.facts, e),
      })),
    }

    progress.total = payload.entries.length
    progress.current = 0

    const res = await api.post('/documents/generate-batch', payload)
    results.value = res.data.data.results
    progress.current = progress.total
  } catch (err) {
    generateError.value = err.response?.data?.detail || '批量生成失败'
  } finally {
    generating.value = false
  }
}

function viewDoc(docId) {
  router.push(`/documents/${docId}`)
}

function downloadWord(docId) {
  window.open(`/api/documents/${docId}/download/docx`, '_blank')
}

function downloadPdf(docId) {
  window.open(`/api/documents/${docId}/download/pdf`, '_blank')
}
</script>
