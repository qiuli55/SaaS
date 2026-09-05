<template>
  <div>
    <div class="detail-head">
      <div>
        <div class="no">V{{ doc.version }}</div>
        <div class="nm">{{ doc.doc_type }}</div>
        <div class="detail-meta">
          <span>关联案件 <b>{{ doc.case_name || '—' }}</b></span>
          <span>生成时间 <b>{{ formatDate(doc.created_at) }}</b></span>
        </div>
      </div>
      <div style="display:flex;gap:8px;align-items:flex-end">
        <button @click="copyContent" class="btn btn-outline btn-sm">{{ copied?'已复制':'复制文本' }}</button>
        <button @click="downloadWord" class="btn btn-gold btn-sm">Word</button>
        <button @click="downloadPdf" class="btn btn-gold btn-sm">PDF</button>
      </div>
    </div>

    <!-- 版本切换 -->
    <div v-if="versions.length>1" class="filter-bar">
      <div class="tabs">
        <button v-for="v in versions" :key="v.id" @click="switchVersion(v.id)" class="tab" :class="{ active: v.id===currentDocId }">
          V{{ v.version }} ({{ formatDate(v.created_at) }})
        </button>
      </div>
    </div>

    <div v-if="loading" class="empty">加载中...</div>
    <template v-else>
      <div class="card"><div class="card-body"><div class="doc-preview">{{ doc.final_content }}</div></div></div>

      <div v-if="doc.verified_articles?.length" class="card" style="margin-top:20px"><div class="card-body">
        <div style="background:var(--ok-bg);border:1px solid #cfe7d3;border-radius:10px;padding:14px 18px">
          <div style="font-weight:600;color:var(--ok);margin-bottom:8px">法条引用校验</div>
          <div v-for="a in doc.verified_articles" :key="a.law+a.article" style="display:flex;align-items:center;gap:8px;font-size:13px;padding:3px 0">
            <span>{{ a.verified?'✅':'⚠️' }}</span><span class="mono" style="color:var(--ok)">{{ a.law }}{{ a.article }}</span><span style="color:var(--muted)">— {{ a.verified?'存在':'需人工核实' }}</span>
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

<style scoped>
.doc-preview{
  font-family:var(--serif); line-height:1.9; font-size:14px; color:var(--text);
  white-space:pre-wrap; word-break:break-word; min-height:400px;
}
</style>
