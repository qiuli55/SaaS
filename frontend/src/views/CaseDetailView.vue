<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.push('/cases')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-800">{{ caseInfo.plaintiff }}{{ caseInfo.case_type }}</h1>
      </div>
      <div class="flex items-center space-x-3">
        <router-link :to="`/cases/${caseId}/documents/new`" class="btn-primary text-sm">
          + 生成文书
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>
    <template v-else>
      <!-- 案件信息卡片 -->
      <div class="card mb-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold text-gray-800">案件信息</h2>
          <span :class="statusClass(caseInfo.status)">{{ caseInfo.status }}</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div><span class="text-gray-400">编号</span><p class="font-medium">{{ caseInfo.case_no }}</p></div>
          <div><span class="text-gray-400">原告</span><p class="font-medium">{{ caseInfo.plaintiff }}</p></div>
          <div><span class="text-gray-400">被告</span><p class="font-medium">{{ caseInfo.defendant }}</p></div>
          <div><span class="text-gray-400">标的额</span><p class="font-medium">¥{{ formatMoney(caseInfo.subject_amount) }}</p></div>
          <div><span class="text-gray-400">委托日期</span><p class="font-medium">{{ formatDate(caseInfo.commission_date) }}</p></div>
          <div><span class="text-gray-400">创建时间</span><p class="font-medium">{{ formatDate(caseInfo.created_at) }}</p></div>
        </div>
        <div v-if="caseInfo.description" class="mt-3 pt-3 border-t border-gray-100">
          <span class="text-sm text-gray-400">补充描述</span>
          <p class="text-sm text-gray-600 mt-1">{{ caseInfo.description }}</p>
        </div>
      </div>

      <!-- Tab 区域 -->
      <div class="flex border-b border-gray-200 mb-6 space-x-6">
        <button
          @click="activeTab = 'documents'"
          class="pb-3 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === 'documents' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          文书 ({{ documents.length }})
        </button>
        <button
          @click="activeTab = 'files'"
          class="pb-3 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === 'files' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          文件 ({{ files.length }})
        </button>
      </div>

      <!-- 文书列表 -->
      <div v-if="activeTab === 'documents'">
        <div v-if="documents.length === 0" class="card text-center py-12">
          <p class="text-gray-500 mb-4">还没有生成文书</p>
          <router-link :to="`/cases/${caseId}/documents/new`" class="btn-primary">生成第一份文书</router-link>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="card hover:shadow-md transition-shadow cursor-pointer"
            @click="$router.push(`/documents/${doc.id}`)"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-gray-800">
                  {{ doc.doc_type }}
                  <span class="text-xs text-gray-400 ml-2">V{{ doc.version }}</span>
                </h3>
                <div class="text-sm text-gray-500 mt-1">
                  {{ formatDate(doc.created_at) }}
                  <span v-if="doc.verified_articles && doc.verified_articles.length > 0" class="ml-2 text-green-600">
                    ✅ 法条已校验
                  </span>
                </div>
              </div>
              <span :class="doc.status === '已完成' ? 'badge-green' : 'badge-gray'">
                {{ doc.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件列表 -->
      <div v-if="activeTab === 'files'">
        <div class="card mb-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-800">上传文件</h3>
          </div>
          <div class="flex items-center space-x-3">
            <input
              ref="fileInput"
              type="file"
              multiple
              class="hidden"
              @change="handleFileSelect"
            />
            <button @click="$refs.fileInput.click()" class="btn-secondary text-sm">
              + 选择文件
            </button>
            <span v-if="selectedFiles.length" class="text-sm text-gray-500">
              已选择 {{ selectedFiles.length }} 个文件
            </span>
            <button
              v-if="selectedFiles.length"
              @click="uploadFiles"
              class="btn-primary text-sm"
              :disabled="uploading"
            >
              {{ uploading ? '上传中...' : '确认上传' }}
            </button>
          </div>
          <div v-if="uploadError" class="mt-2 text-sm text-red-600">{{ uploadError }}</div>
        </div>

        <div v-if="files.length === 0 && !selectedFiles.length" class="card text-center py-12">
          <p class="text-gray-500">还没有上传文件</p>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="f in files"
            :key="f.id"
            class="card flex items-center justify-between"
          >
            <div class="flex items-center space-x-3 min-w-0">
              <span class="text-xl">{{ fileIcon(f.file_name) }}</span>
              <div class="min-w-0">
                <div class="font-medium text-gray-800 truncate">{{ f.file_name }}</div>
                <div class="text-xs text-gray-400">
                  {{ formatSize(f.file_size) }} · {{ formatDate(f.created_at) }}
                  <span class="ml-2" :class="fileTypeClass(f.file_type)">
                    {{ fileTypeLabel(f.file_type) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-2 shrink-0">
              <button @click="previewFile(f.id)" class="text-sm text-primary-600 hover:text-primary-700">预览</button>
              <button @click="downloadFile(f.id, f.file_name)" class="text-sm text-primary-600 hover:text-primary-700">下载</button>
              <button @click="deleteFile(f.id)" class="text-sm text-red-500 hover:text-red-700">删除</button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const caseId = route.params.id

const caseInfo = ref({})
const documents = ref([])
const files = ref([])
const loading = ref(true)
const activeTab = ref('documents')
const selectedFiles = ref([])
const uploading = ref(false)
const uploadError = ref('')
const fileInput = ref(null)

onMounted(async () => {
  try {
    const [caseRes, docRes, fileRes] = await Promise.all([
      api.get(`/cases/${caseId}`),
      api.get(`/cases/${caseId}/documents`),
      api.get(`/cases/${caseId}/files`),
    ])
    caseInfo.value = caseRes.data
    documents.value = docRes.data.data || []
    files.value = fileRes.data.data || []
  } catch (err) {
    console.error('加载案件详情失败', err)
  } finally {
    loading.value = false
  }
})

function handleFileSelect(e) {
  selectedFiles.value = Array.from(e.target.files)
  uploadError.value = ''
}

async function uploadFiles() {
  if (!selectedFiles.value.length) return
  uploading.value = true
  uploadError.value = ''
  try {
    const formData = new FormData()
    selectedFiles.value.forEach((f) => formData.append('files', f))
    await api.post(`/cases/${caseId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    selectedFiles.value = []
    // 刷新文件列表
    const res = await api.get(`/cases/${caseId}/files`)
    files.value = res.data.data || []
    // 更新案件文件计数
    caseInfo.value.file_count = files.value.length
  } catch (err) {
    uploadError.value = err.response?.data?.detail || '上传失败'
  } finally {
    uploading.value = false
  }
}

function previewFile(fileId) {
  window.open(`/api/files/${fileId}/preview`, '_blank')
}

function downloadFile(fileId, fileName) {
  const a = document.createElement('a')
  a.href = `/api/files/${fileId}/download`
  a.download = fileName
  a.click()
}

async function deleteFile(fileId) {
  if (!confirm('确定要删除这个文件吗？')) return
  try {
    await api.delete(`/files/${fileId}`)
    files.value = files.value.filter((f) => f.id !== fileId)
    caseInfo.value.file_count = files.value.length
  } catch (err) {
    alert('删除失败')
  }
}

function statusClass(status) {
  const map = { '进行中': 'badge-blue', '已结案': 'badge-green', '待立案': 'badge-yellow' }
  return map[status] || 'badge-gray'
}

function fileTypeClass(type) {
  const map = { evidence: 'badge-blue', judgment: 'badge-yellow', entrustment: 'badge-green' }
  return map[type] || 'badge-gray'
}

function fileTypeLabel(type) {
  const map = { evidence: '证据', judgment: '判决书', entrustment: '委托书', other: '其他' }
  return map[type] || '其他'
}

function fileIcon(name) {
  const ext = name?.split('.').pop()?.toLowerCase()
  const map = { pdf: '📄', doc: '📄', docx: '📄', xls: '📊', xlsx: '📊', jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️' }
  return map[ext] || '📎'
}

function formatDate(d) {
  return d ? d.slice(0, 10) : '未填写'
}

function formatMoney(v) {
  return Number(v || 0).toLocaleString('zh-CN')
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return size.toFixed(1) + ' ' + units[i]
}
</script>
