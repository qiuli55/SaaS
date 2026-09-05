<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">文书列表</div>
        <div class="page-sub">共 {{ docs.length }} 份文书</div>
      </div>
    </div>

    <div class="filter-bar">
      <div class="tabs">
        <button :class="{ active: filter === '' }" @click="filter = ''" class="tab">全部</button>
        <button v-for="t in docTypes" :key="t" :class="{ active: filter === t }" @click="filter = t" class="tab">{{ t }}</button>
      </div>
    </div>

    <div v-if="loading" class="empty">加载中...</div>
    <div v-else-if="docs.length === 0" class="empty">
      <div class="ico">📄</div>
      <div class="t">暂无文书</div>
      <router-link to="/cases" class="btn btn-gold btn-sm" style="margin-top:14px">前往案件管理生成文书</router-link>
    </div>
    <div v-else class="doc-grid">
      <div v-for="d in filteredDocs" :key="d.id" class="card card-hover doc-card" @click="$router.push(`/documents/${d.id}`)">
        <div class="dh">
          <div class="c-mono">{{ (d.doc_type || '文书').slice(0,2) }}</div>
          <div class="flex-1 min-w-0"><div class="t">{{ d.doc_type }}</div><div class="m">版本 {{ d.version }}</div></div>
          <span class="badge" :class="d.status === '已完成' ? 'b-success' : 'b-neutral'">{{ d.status }}</span>
        </div>
        <div class="dm">案件：{{ d.case_name || `#${d.case_id}` }}</div>
        <div class="acts">
          <a @click.stop="$router.push(`/documents/${d.id}`)">查看</a>
          <a @click.stop="downloadDoc(d)">下载</a>
        </div>
      </div>
    </div>

    <div v-if="docs.length > 0" class="pager">
      <button v-if="hasMore" @click="loadMore" class="btn btn-outline btn-sm" :disabled="loadingMore">{{ loadingMore ? '加载中...' : '加载更多' }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { authDownload } from '../api'

const docs = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const filter = ref('')
const page = ref(1)
const hasMore = ref(false)

const docTypes = ['民事起诉状', '民事答辩状', '律师函', '代理词', '法律意见书', '上诉状', '催收函']

const filteredDocs = computed(() => filter.value ? docs.value.filter(d => d.doc_type === filter.value) : docs.value)

async function loadDocuments() {
  try {
    const res = await api.get('/documents/history', { params: { page: page.value, page_size: 20 } })
    docs.value = res.data.data.items || res.data.data || []
    hasMore.value = (res.data.data.items || res.data.data || []).length === 20
  } catch (e) { console.error(e) }
  loading.value = false
}

async function loadMore() {
  loadingMore.value = true
  page.value++
  try {
    const res = await api.get('/documents/history', { params: { page: page.value, page_size: 20 } })
    const items = res.data.data.items || res.data.data || []
    docs.value.push(...items)
    hasMore.value = items.length === 20
  } catch (e) { console.error(e) }
  loadingMore.value = false
}

function downloadDoc(d) {
  authDownload(`/documents/${d.id}/download/docx`, `文书_${d.doc_type}_V${d.version}.docx`)
}

onMounted(loadDocuments)
</script>

<style scoped>
.doc-grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:14px; }
.doc-card{ padding:16px 18px; cursor:pointer; }
.doc-card .dh{ display:flex; align-items:center; gap:12px; margin-bottom:10px; }
.doc-card .c-mono{ width:40px; height:40px; border-radius:10px; display:grid; place-items:center; font-family:var(--serif); font-weight:600; font-size:14px; color:var(--ink-700); background:var(--paper-2); border:1px solid var(--line); flex-shrink:0; }
.doc-card .t{ font-weight:600; font-size:14px; color:var(--ink-700); }
.doc-card .m{ font-size:12px; color:var(--muted); margin-top:1px; }
.doc-card .dm{ font-size:12.5px; color:var(--muted); margin-bottom:10px; }
.doc-card .acts{ display:flex; gap:14px; font-size:12.5px; }
.doc-card .acts a{ color:var(--gold-deep); cursor:pointer; font-weight:500; }
.doc-card .acts a:hover{ text-decoration:underline; }
.flex-1{ flex:1; }
.min-w-0{ min-width:0; }
</style>
