<template>
  <div>
    <div v-if="loading" class="empty">加载中...</div>
    <template v-else>
      <div class="detail-head">
        <div>
          <div class="no">{{ caseInfo.case_no }}</div>
          <div class="nm">{{ caseInfo.plaintiff }}{{ caseInfo.case_type }}</div>
          <div class="detail-meta">
            <span>原告 <b>{{ caseInfo.plaintiff }}</b></span>
            <span>被告 <b>{{ caseInfo.defendant }}</b></span>
            <span>标的额 <b class="mono">{{ caseInfo.subject_amount ? '¥' + formatMoney(caseInfo.subject_amount) : '—' }}</b></span>
            <span>委托日期 <b>{{ formatDate(caseInfo.commission_date) }}</b></span>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;align-items:flex-end">
          <span class="badge" :class="statusBadge(caseInfo.status)">{{ caseInfo.status }}</span>
          <div style="display:flex;gap:8px">
            <router-link :to="`/cases/${caseId}/edit`" class="btn btn-outline btn-sm">编辑</router-link>
            <router-link :to="`/cases/${caseId}/documents/new`" class="btn btn-gold btn-sm">✨ 生成文书</router-link>
          </div>
        </div>
      </div>

      <div v-if="caseInfo.description" class="card" style="margin-bottom:20px">
        <div class="card-body" style="font-size:13.5px;color:var(--muted)">
          <b style="color:var(--ink-700)">补充描述：</b>{{ caseInfo.description }}
        </div>
      </div>

      <div class="filter-bar">
        <div class="tabs">
          <button @click="activeTab='documents'" class="tab" :class="{ active: activeTab==='documents' }">文书 ({{ documents.length }})</button>
          <button @click="activeTab='files'" class="tab" :class="{ active: activeTab==='files' }">文件 ({{ files.length }})</button>
          <button @click="activeTab='analysis'" class="tab" :class="{ active: activeTab==='analysis' }">AI 分析</button>
        </div>
      </div>

      <!-- AI 分析面板 -->
      <div v-if="activeTab==='analysis'" class="analysis-panel">
        <div v-if="!analysisResult && !analyzing" class="analysis-intro">
          <p>让 AI 读取已上传的案件材料，自动生成：时间线梳理、主体关系分析、事实概述、争议焦点总结。</p>
          <button class="btn btn-gold" @click="runAnalysis" :disabled="!files.length">
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
        <div v-if="!documents.length" class="empty">
          <div class="ico">📝</div>
          <div class="t">还没有生成文书</div>
          <router-link :to="`/cases/${caseId}/documents/new`" class="btn btn-gold btn-sm" style="margin-top:14px">生成第一份文书</router-link>
        </div>
        <div class="table-wrap" v-else>
          <table class="table"><thead><tr><th>文书类型</th><th>版本</th><th>生成时间</th><th>状态</th><th style="width:110px">操作</th></tr></thead>
            <tbody><tr v-for="d in documents" :key="d.id" style="cursor:pointer" @click="$router.push(`/documents/${d.id}`)">
              <td style="font-weight:600;color:var(--ink)">{{ d.doc_type }}</td>
              <td class="mono" style="font-size:13px">V{{ d.version }}</td>
              <td style="color:var(--muted);font-size:13px">{{ formatDate(d.created_at) }}</td>
              <td><span class="badge" :class="d.status==='已完成' ? 'b-success' : 'b-neutral'">{{ d.status }}</span></td>
              <td><button @click.stop="regenerate(d)" class="btn btn-ghost btn-sm">重新生成</button></td>
            </tr></tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab==='files'">
        <div class="card" style="margin-bottom:14px"><div class="card-body">
          <div style="display:flex;gap:8px;align-items:center">
            <button @click="$refs.fileInput.click()" class="btn btn-outline btn-sm">+ 选择文件</button>
            <span v-if="selectedFiles.length" style="font-size:13px;color:var(--muted)">已选 {{ selectedFiles.length }} 个</span>
            <button v-if="selectedFiles.length" @click="uploadFiles" class="btn btn-gold btn-sm" :disabled="uploading">{{ uploading ? '上传中...' : '确认上传' }}</button>
            <input ref="fileInput" type="file" multiple hidden @change="handleFileSelect" />
          </div>
        </div></div>
        <div v-if="!files.length && !selectedFiles.length" class="empty">还没有上传文件</div>
        <div class="card" v-if="files.length">
          <div v-for="f in files" :key="f.id" class="file-item">
            <div class="file-ico">{{ fileIcon(f.file_name) }}</div>
            <div class="file-info"><div class="file-name">{{ f.file_name }}</div><div class="file-meta">{{ formatSize(f.file_size) }} · {{ formatDate(f.created_at) }} · {{ fileTypeLabel(f.file_type) }}</div></div>
            <div style="display:flex;gap:8px;flex-shrink:0">
              <button @click="previewFile(f.id)" class="btn btn-ghost btn-sm">预览</button>
              <button @click="downloadFile(f.id,f.file_name)" class="btn btn-ghost btn-sm">下载</button>
              <button @click="deleteFile(f.id)" class="btn btn-ghost btn-sm" style="color:var(--danger)">删除</button>
            </div>
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
function statusBadge(s) { const m={'进行中':'b-info','已结案':'b-success','待立案':'b-warning'}; return m[s]||'b-neutral' }
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
.file-item{ display:flex; align-items:center; gap:12px; padding:13px 20px; border-bottom:1px solid var(--line); }
.file-item:last-child{ border-bottom:none; }
.file-ico{ width:36px; height:36px; border-radius:8px; background:var(--paper-2); display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0; }
.file-info{ flex:1; min-width:0; }
.file-name{ font-weight:600; font-size:13.5px; color:var(--ink-700); }
.file-meta{ font-size:12px; color:var(--muted); margin-top:2px; }

.analysis-panel{ padding:20px; background:var(--paper-2); border-radius:var(--radius); border:1px solid var(--line); }
.analysis-intro p{ font-size:14px; color:var(--muted); margin-bottom:16px; line-height:1.7; }
.analysis-loading{ display:flex; align-items:center; gap:12px; padding:48px; justify-content:center; color:var(--muted); font-size:14px; }
.analysis-result :deep(h2){ font-family:var(--serif); font-size:16px; margin:16px 0 8px; color:var(--ink); }
.analysis-result :deep(h3){ font-size:14px; margin:12px 0 6px; color:var(--ink); }
.analysis-result :deep(li){ font-size:13px; color:var(--text); margin:4px 0; padding-left:4px; }
.analysis-result :deep(b){ color:var(--ink); }
.analysis-result :deep(ul){ padding-left:20px; }
.spinner{ display:inline-flex; }
.spinner div{ width:20px; height:20px; border:2px solid var(--line-strong); border-top-color:var(--gold); border-radius:50%; animation:spin .8s linear infinite; }
@keyframes spin{ to{ transform:rotate(360deg) } }
</style>
