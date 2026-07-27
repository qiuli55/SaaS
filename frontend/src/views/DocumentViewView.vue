<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.back()" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-800">
          {{ doc.doc_type }}
          <span class="text-sm text-gray-400 font-normal ml-2">V{{ doc.version }}</span>
        </h1>
        <p class="text-sm text-gray-500">{{ doc.case_name }} · {{ formatDate(doc.created_at) }}</p>
      </div>
      <div class="flex space-x-2">
        <button @click="copyContent" class="btn-secondary text-sm">{{ copied ? '已复制' : '复制文本' }}</button>
        <button @click="downloadWord" class="btn-primary text-sm">下载 Word</button>
        <button @click="downloadPdf" class="btn-primary text-sm">下载 PDF</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

    <template v-else>
      <!-- 文书正文 -->
      <div class="card">
        <div class="bg-gray-50 rounded-lg p-8 document-content min-h-[400px]">
          {{ doc.final_content }}
        </div>
      </div>

      <!-- 法条校验 -->
      <div v-if="doc.verified_articles && doc.verified_articles.length > 0" class="card mt-4">
        <h3 class="font-semibold text-gray-800 mb-3">法条引用校验</h3>
        <ul class="space-y-1 text-sm">
          <li v-for="a in doc.verified_articles" :key="a.law + a.article" class="flex items-start space-x-2">
            <span>{{ a.verified ? '✅' : '⚠️' }}</span>
            <span>
              {{ a.law }}{{ a.article }}
              <span class="text-gray-500">— {{ a.verified ? '存在' : '未在法条库中找到' }}</span>
            </span>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const docId = route.params.id
const doc = ref({})
const loading = ref(true)
const copied = ref(false)

onMounted(async () => {
  try {
    const res = await api.get(`/documents/${docId}`)
    doc.value = res.data.data
  } catch (err) {
    console.error('加载文书失败', err)
  } finally {
    loading.value = false
  }
})

function copyContent() {
  if (doc.value?.final_content) {
    navigator.clipboard.writeText(doc.value.final_content)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  }
}

function downloadWord() {
  window.open(`/api/documents/${docId}/download/docx`, '_blank')
}

function downloadPdf() {
  window.open(`/api/documents/${docId}/download/pdf`, '_blank')
}

function formatDate(d) {
  return d ? d.slice(0, 10) : ''
}
</script>
