<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.push(`/cases/${caseId}`)" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <h1 class="text-2xl font-bold text-gray-800">生成文书</h1>
    </div>

    <!-- 步骤1: 选择文书类型 -->
    <div class="card mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">步骤 1：选择文书类型</h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button
          v-for="dt in docTypes"
          :key="dt"
          @click="form.doc_type = dt"
          class="p-3 rounded-lg border-2 text-center font-medium transition-all"
          :class="form.doc_type === dt
            ? 'border-primary-500 bg-primary-50 text-primary-700'
            : 'border-gray-200 text-gray-600 hover:border-gray-300 bg-white'"
        >
          {{ dt }}
        </button>
      </div>
    </div>

    <!-- 步骤2: 填写信息 -->
    <div class="card mb-6" v-if="form.doc_type">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">步骤 2：确认案件信息并填写补充内容</h2>

      <div class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3 bg-gray-50 rounded-lg text-sm">
          <div><span class="text-gray-400">原告：</span>{{ caseInfo.plaintiff }} <span class="text-green-600 ml-1">✓</span></div>
          <div><span class="text-gray-400">被告：</span>{{ caseInfo.defendant }} <span class="text-green-600 ml-1">✓</span></div>
          <div><span class="text-gray-400">案由：</span>{{ caseInfo.case_type }} <span class="text-green-600 ml-1">✓</span></div>
          <div><span class="text-gray-400">标的额：</span>¥{{ formatMoney(caseInfo.subject_amount) }} <span class="text-green-600 ml-1">✓</span></div>
        </div>

        <div>
          <label class="form-label">诉讼请求（建议填写）</label>
          <textarea
            v-model="form.claims"
            rows="4"
            placeholder="例如：&#10;1. 请求被告支付货款20万元&#10;2. 请求被告承担本案诉讼费用"
            class="input-field"
          ></textarea>
        </div>

        <div>
          <label class="form-label">案件事实描述（越详细 AI 生成越准确）</label>
          <textarea
            v-model="form.facts"
            rows="6"
            :placeholder="'例如：' + caseInfo.plaintiff + '与' + caseInfo.defendant + '于2026年1月签订购销合同...'"
            class="input-field"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- 生成按钮 -->
    <div v-if="form.doc_type" class="text-center mb-6">
      <button
        @click="generateDocument"
        class="btn-primary text-lg px-8 py-3"
        :disabled="generating"
      >
        {{ generating ? '🤖 AI 正在生成中...' : '🤖 生成' + form.doc_type + '草稿' }}
      </button>
      <div v-if="generateError" class="mt-3 text-sm text-red-600">{{ generateError }}</div>
    </div>

    <!-- 生成结果 -->
    <div v-if="result" class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">生成结果</h2>
        <div class="flex space-x-2">
          <button @click="copyContent" class="btn-secondary text-sm">{{ copied ? '已复制' : '复制文本' }}</button>
          <button @click="downloadWord(result.id)" class="btn-primary text-sm">下载 Word</button>
          <button @click="downloadPdf(result.id)" class="btn-primary text-sm">下载 PDF</button>
        </div>
      </div>

      <div class="bg-gray-50 rounded-lg p-6 document-content max-h-[600px] overflow-y-auto">
        {{ result.final_content }}
      </div>

      <!-- 法条校验结果 -->
      <div v-if="result.verified_articles && result.verified_articles.length > 0" class="mt-4 p-4 bg-green-50 rounded-lg">
        <h3 class="font-semibold text-green-800 mb-2">✅ 法条引用校验：</h3>
        <ul class="space-y-1 text-sm">
          <li v-for="a in result.verified_articles" :key="a.law + a.article" class="flex items-start space-x-2">
            <span>{{ a.verified ? '✅' : '⚠️' }}</span>
            <span>
              {{ a.law }}{{ a.article }}
              <span class="text-gray-500">— {{ a.verified ? '存在' : '未在法条库中找到，请人工核实' }}</span>
            </span>
          </li>
        </ul>
      </div>

      <div class="mt-4 flex justify-center">
        <button @click="regenerate" class="btn-secondary" :disabled="generating">
          重新生成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const caseId = route.params.id

const docTypes = ['民事起诉状', '民事答辩状', '律师函', '代理词', '法律意见书', '上诉状', '再审申请书', '催收函']

const caseInfo = ref({})
const generating = ref(false)
const generateError = ref('')
const result = ref(null)
const copied = ref(false)

const form = reactive({
  doc_type: '',
  claims: '',
  facts: '',
})

onMounted(async () => {
  try {
    const res = await api.get(`/cases/${caseId}`)
    caseInfo.value = res.data
  } catch (err) {
    console.error('加载案件信息失败', err)
  }
})

async function generateDocument() {
  generateError.value = ''
  generating.value = true
  result.value = null
  try {
    const res = await api.post('/documents/generate', {
      case_id: Number(caseId),
      doc_type: form.doc_type,
      claims: form.claims,
      facts: form.facts,
    })
    result.value = res.data.data
  } catch (err) {
    generateError.value = err.response?.data?.detail || '生成失败，请检查 API Key 配置后重试'
  } finally {
    generating.value = false
  }
}

async function regenerate() {
  await generateDocument()
}

function copyContent() {
  if (result.value?.final_content) {
    navigator.clipboard.writeText(result.value.final_content)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  }
}

function downloadWord(docId) {
  window.open(`/api/documents/${docId}/download/docx`, '_blank')
}

function formatMoney(v) {
  return Number(v || 0).toLocaleString('zh-CN')
}
</script>
