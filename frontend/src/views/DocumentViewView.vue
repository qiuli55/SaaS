<template>
  <div>
    <div class="page-header">
      <div><h1 class="page-title">{{ doc.doc_type }} <span style="font-size:14px;color:var(--text-muted);font-weight:400">V{{ doc.version }}</span></h1>
        <div style="font-size:13px;color:var(--text-secondary)">{{ doc.case_name }} · {{ formatDate(doc.created_at) }}</div></div>
      <div style="display:flex;gap:8px">
        <button @click="copyContent" class="btn btn-outline btn-sm">{{ copied?'已复制':'复制文本' }}</button>
        <button @click="downloadWord" class="btn btn-accent btn-sm">Word</button>
        <button @click="downloadPdf" class="btn btn-accent btn-sm">PDF</button>
      </div>
    </div>

    <!-- 版本切换 -->
    <div v-if="versions.length>1" class="card mb-4"><div class="card-body" style="padding:12px 20px">
      <div style="display:flex;align-items:center;gap:8px;font-size:13px">
        <span style="color:var(--text-muted)">历史版本：</span>
        <button v-for="v in versions" :key="v.id" @click="switchVersion(v.id)" style="padding:4px 12px;border-radius:9999px;border:1px solid;font-size:13px;cursor:pointer;transition:all 0.15s"
          :style="v.id===currentDocId?{background:'var(--navy-100)',borderColor:'var(--navy-400)',color:'var(--navy-700)',fontWeight:500}:{background:'var(--surface-alt)',borderColor:'var(--border)',color:'var(--text-muted)'}">
          V{{ v.version }} ({{ formatDate(v.created_at) }})
        </button>
      </div>
    </div></div>

    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-muted)">加载中...</div>
    <template v-else>
      <div class="card"><div class="card-body"><div class="doc-preview" style="min-height:400px">{{ doc.final_content }}</div></div></div>

      <div v-if="doc.verified_articles?.length" class="card mt-4"><div class="card-body">
        <div style="background:#ecfdf5;border:1px solid #d1fae5;border-radius:8px;padding:16px 20px">
          <div style="font-weight:600;color:var(--success);margin-bottom:8px">法条引用校验</div>
          <div v-for="a in doc.verified_articles" :key="a.law+a.article" style="display:flex;align-items:center;gap:8px;font-size:13px;padding:4px 0">
            <span>{{ a.verified?'✅':'⚠️' }}</span><span style="font-family:'JetBrains Mono',monospace;color:var(--success)">{{ a.law }}{{ a.article }}</span><span style="color:var(--text-secondary)">— {{ a.verified?'存在':'需人工核实' }}</span>
          </div>
        </div>
      </div></div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { useRoute, useRouter } from 'vue-router'; import api, { authDownload } from '../api'
const route = useRoute(); const router = useRouter(); const docId = route.params.id
const doc = ref({}); const loading = ref(true); const copied = ref(false); const versions = ref([]); const currentDocId = ref(Number(docId))
onMounted(async () => { await loadDoc(docId); await loadVersions() })
async function loadDoc(id) { loading.value = true; currentDocId.value = Number(id); try { const r = await api.get(`/documents/${id}`); doc.value = r.data.data } catch(e) { console.error('加载文书失败', e) } finally { loading.value = false } }
async function loadVersions() { try { const r = await api.get(`/documents/${docId}/versions`); versions.value = r.data.data||[] } catch(e) { console.error('加载版本失败', e) } }
function switchVersion(id) { if(id===currentDocId.value) return; router.replace(`/documents/${id}`); loadDoc(id) }
function copyContent() { if(doc.value?.final_content){ navigator.clipboard.writeText(doc.value.final_content); copied.value = true; setTimeout(()=>copied.value=false,2000) } }
function downloadWord() { authDownload(`/documents/${currentDocId.value}/download/docx`, `${doc.value.doc_type}.docx`) }
function downloadPdf() { authDownload(`/documents/${currentDocId.value}/download/pdf`, `${doc.value.doc_type}.pdf`) }
function formatDate(d) { return d?.slice(0,10)||'' }
</script>
