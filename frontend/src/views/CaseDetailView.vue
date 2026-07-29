<template>
  <div>
    <div class="page-header">
      <div><h1 class="page-title">{{ caseInfo.plaintiff }}{{ caseInfo.case_type }}</h1></div>
      <div style="display:flex;gap:8px">
        <router-link :to="`/cases/${caseId}/edit`" class="btn btn-outline btn-sm">编辑</router-link>
        <router-link :to="`/cases/${caseId}/documents/new`" class="btn btn-accent btn-sm">+ 生成文书</router-link>
      </div>
    </div>

    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-muted)">加载中...</div>
    <template v-else>
      <div class="card mb-6">
        <div class="card-header"><span class="card-title">案件信息</span><span :class="statusBadge(caseInfo.status)">{{ caseInfo.status }}</span></div>
        <div class="card-body">
          <div class="stats-grid" style="margin-bottom:0">
            <div><div class="stat-label">编号</div><div style="font-family:'JetBrains Mono',monospace;font-weight:500;color:var(--navy-800)">{{ caseInfo.case_no }}</div></div>
            <div><div class="stat-label">原告</div><div style="font-weight:500">{{ caseInfo.plaintiff }}</div></div>
            <div><div class="stat-label">被告</div><div style="font-weight:500">{{ caseInfo.defendant }}</div></div>
            <div><div class="stat-label">标的额</div><div style="font-family:'JetBrains Mono',monospace;font-weight:500">¥{{ formatMoney(caseInfo.subject_amount) }}</div></div>
            <div><div class="stat-label">委托日期</div><div>{{ formatDate(caseInfo.commission_date) }}</div></div>
            <div><div class="stat-label">创建时间</div><div>{{ formatDate(caseInfo.created_at) }}</div></div>
          </div>
          <div v-if="caseInfo.description" style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-light)"><div class="stat-label">补充描述</div><div style="font-size:14px;color:var(--text-secondary)">{{ caseInfo.description }}</div></div>
        </div>
      </div>

      <div class="tabs-nav">
        <button @click="activeTab='documents'" class="tab-item" :class="{ active: activeTab==='documents' }">文书 ({{ documents.length }})</button>
        <button @click="activeTab='files'" class="tab-item" :class="{ active: activeTab==='files' }">文件 ({{ files.length }})</button>
        <button @click="activeTab='analysis'" class="tab-item" :class="{ active: activeTab==='analysis' }">AI 分析</button>
      </div>

      <!-- AI 分析面板 -->
      <div v-if="activeTab==='analysis'" class="analysis-panel">
        <div v-if="!analysisResult && !analyzing" class="analysis-intro">
          <p>让 AI 读取已上传的案件材料，自动生成：时间线梳理、主体关系分析、事实概述、争议焦点总结。</p>
          <button class="btn btn-accent" @click="runAnalysis" :disabled="!files.length">
            {{ files.length ? '开始智能分析' : '请先上传案件文件' }}
          </button>
        </div>
        <div v-if="analyzing" class="analysis-loading">
          <div class="spinner"><div></div></div>
          <span>AI 正在阅读案件材料并分析...</span>
        </div>
        <div v-if="analysisResult" class="analysis-result markdown-body" v-html="renderedAnalysis"></div>
        <button v-if="analysisResult" class="btn btn-outline btn-sm" style="margin-top:12px" @click="runAnalysis">重新分析</button>
      </div>

      <div v-if="activeTab==='documents'">
        <div v-if="!documents.length" style="text-align:center;padding:48px;color:var(--text-muted)">
          <div style="font-size:36px;margin-bottom:12px">📝</div><div style="margin-bottom:16px">还没有生成文书</div>
          <router-link :to="`/cases/${caseId}/documents/new`" class="btn btn-accent btn-sm">生成第一份文书</router-link>
        </div>
        <div class="table-wrapper" v-else>
          <table class="table"><thead><tr><th>文书类型</th><th>版本</th><th>生成时间</th><th>状态</th><th style="width:100px">操作</th></tr></thead>
            <tbody><tr v-for="d in documents" :key="d.id" @click="$router.push(`/documents/${d.id}`)">
              <td style="font-weight:500;color:var(--navy-800)">{{ d.doc_type }}</td>
              <td style="font-family:'JetBrains Mono',monospace;font-size:13px">V{{ d.version }}</td>
              <td style="color:var(--text-secondary);font-size:13px">{{ formatDate(d.created_at) }}</td>
              <td><span :class="d.status==='已完成'?'badge badge-success':'badge badge-neutral'">{{ d.status }}</span></td>
              <td><button @click.stop="regenerate(d)" class="btn btn-ghost btn-sm" style="color:var(--accent)">重新生成</button></td>
            </tr></tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab==='files'">
        <div class="card mb-4"><div class="card-body">
          <div style="display:flex;gap:8px;align-items:center">
            <button @click="$refs.fileInput.click()" class="btn btn-outline btn-sm">+ 选择文件</button>
            <span v-if="selectedFiles.length" style="font-size:13px;color:var(--text-secondary)">已选 {{ selectedFiles.length }} 个</span>
            <button v-if="selectedFiles.length" @click="uploadFiles" class="btn btn-accent btn-sm" :disabled="uploading">{{ uploading ? '上传中...' : '确认上传' }}</button>
            <input ref="fileInput" type="file" multiple hidden @change="handleFileSelect" />
          </div>
        </div></div>
        <div v-if="!files.length && !selectedFiles.length" style="text-align:center;padding:48px;color:var(--text-muted)">还没有上传文件</div>
        <div v-for="f in files" :key="f.id" class="file-item">
          <div style="width:36px;height:36px;border-radius:6px;background:var(--navy-50);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0">{{ fileIcon(f.file_name) }}</div>
          <div class="file-info"><div class="file-name">{{ f.file_name }}</div><div class="file-meta">{{ formatSize(f.file_size) }} · {{ formatDate(f.created_at) }} · {{ fileTypeLabel(f.file_type) }}</div></div>
          <div style="display:flex;gap:8px;flex-shrink:0">
            <button @click="previewFile(f.id)" class="btn btn-ghost btn-sm">预览</button>
            <button @click="downloadFile(f.id,f.file_name)" class="btn btn-ghost btn-sm">下载</button>
            <button @click="deleteFile(f.id)" class="btn btn-ghost btn-sm" style="color:var(--error)">删除</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; import { useRoute, useRouter } from 'vue-router'; import api, { authDownload } from '../api'
const route = useRoute(); const router = useRouter(); const caseId = route.params.id
const caseInfo = ref({}); const documents = ref([]); const files = ref([]); const loading = ref(true); const activeTab = ref('documents'); const error = ref('')
const selectedFiles = ref([]); const uploading = ref(false)
const analyzing = ref(false); const analysisResult = ref('')

onMounted(async () => {
  try { const [a,b,c] = await Promise.all([api.get(`/cases/${caseId}`), api.get(`/cases/${caseId}/documents`), api.get(`/cases/${caseId}/files`)])
    caseInfo.value = a.data; documents.value = b.data.data||[]; files.value = c.data.data||[] } catch(e) { error.value = e?.response?.data?.detail || '加载案件详情失败' } finally { loading.value = false }
})

function handleFileSelect(e) { selectedFiles.value = Array.from(e.target.files) }
async function uploadFiles() {
  uploading.value = true; const fd = new FormData(); selectedFiles.value.forEach(f => fd.append('files',f))
  try { await api.post(`/cases/${caseId}/files`, fd, { headers:{'Content-Type':'multipart/form-data'} }); selectedFiles.value = []
    const r = await api.get(`/cases/${caseId}/files`); files.value = r.data.data||[] } catch(e) { alert('上传失败：' + (e?.response?.data?.detail || e.message)) } finally { uploading.value = false }
}
function previewFile(id) {
  const token = localStorage.getItem('token')
  const url = `/api/files/${id}/preview?token=${encodeURIComponent(token || '')}`
  window.open(url, '_blank')
}
function downloadFile(id, name) { authDownload(`/files/${id}/download`, name) }
async function deleteFile(id) { if(!confirm('确定删除？')) return; try { await api.delete(`/files/${id}`); files.value = files.value.filter(f => f.id!==id) } catch(e) { alert('删除失败：' + (e?.response?.data?.detail || e.message)) } }
function statusBadge(s) { const m={'进行中':'badge badge-info','已结案':'badge badge-success','待立案':'badge badge-warning'}; return m[s]||'badge badge-neutral' }
function regenerate(doc) { router.push(`/cases/${caseId}/documents/new?doc_type=${encodeURIComponent(doc.doc_type)}`) }
function fileIcon(n) { const e=n?.split('.').pop()?.toLowerCase(); const m={pdf:'📄',doc:'📄',docx:'📄',xls:'📊',xlsx:'📊',png:'🖼️',jpg:'🖼️',jpeg:'🖼️'}; return m[e]||'📎' }
function fileTypeLabel(t) { const m={evidence:'证据',judgment:'判决书',entrustment:'委托书',other:'其他'}; return m[t]||'其他' }
function formatDate(d) { return d?.slice(0,10)||'' }

const renderedAnalysis = computed(() => {
  return analysisResult.value
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/^- (.+)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, m => '<ul>' + m + '</ul>')
    .replace(/\n/g, '<br/>')
})

async function runAnalysis() {
  analyzing.value = true; analysisResult.value = ''
  try {
    const res = await api.post(`/contract/cases/${caseId}/analyze`)
    analysisResult.value = res.data.result
  } catch (e) {
    analysisResult.value = '分析失败：' + (e.response?.data?.detail || e.message)
  } finally { analyzing.value = false }
}
function formatMoney(v) { return Number(v||0).toLocaleString('zh-CN') }
function formatSize(b) { if(!b) return '0B'; const u=['B','KB','MB','GB']; let i=0,s=b; while(s>=1024&&i<u.length-1){s/=1024;i++}; return s.toFixed(1)+' '+u[i] }
</script>

<style scoped>
.analysis-panel { padding: 20px; background: var(--color-background-secondary); border-radius: 12px; border: 1px solid var(--color-border-tertiary) }
.analysis-intro p { font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.7 }
.analysis-loading { display: flex; align-items: center; gap: 12px; padding: 48px; justify-content: center; color: var(--text-secondary); font-size: 14px }
.analysis-result :deep(h2) { font-size: 16px; margin: 16px 0 8px; color: var(--text-primary) }
.analysis-result :deep(h3) { font-size: 14px; margin: 12px 0 6px; color: var(--text-primary) }
.analysis-result :deep(li) { font-size: 13px; color: var(--text-secondary); margin: 4px 0; padding-left: 4px }
.analysis-result :deep(b) { color: var(--text-primary) }
.analysis-result :deep(ul) { padding-left: 20px }
.spinner { display: inline-flex }
.spinner div { width: 20px; height: 20px; border: 2px solid var(--color-border-secondary); border-top-color: var(--accent); border-radius: 50%; animation: spin .8s linear infinite }
@keyframes spin { to { transform: rotate(360deg) } }
</style>
