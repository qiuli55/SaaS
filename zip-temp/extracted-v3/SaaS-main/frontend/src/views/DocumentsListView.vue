<template>
  <div>
    <div class="zone-title"><span class="bar"></span><h2>文书管理</h2></div>

    <div class="seg">
      <button :class="{ on: filter === '' }" @click="filter = ''">全部</button>
      <button v-for="t in docTypes" :key="t" :class="{ on: filter === t }" @click="filter = t">{{ t }}</button>
    </div>

    <div v-if="loading" style="text-align:center;padding:48px;color:var(--text-muted)">加载中...</div>
    <div v-else-if="docs.length === 0" style="text-align:center;padding:64px;color:var(--text-muted)">
      <div style="font-size:48px;margin-bottom:16px">📄</div>
      <div style="font-size:15px;margin-bottom:12px">暂无文书</div>
      <router-link to="/cases" class="btn btn-accent btn-sm">前往案件管理生成文书</router-link>
    </div>
    <div v-else class="doc-grid">
      <div v-for="d in filteredDocs" :key="d.id" class="doc-card" @click="$router.push(`/documents/${d.id}`)">
        <div class="dh">
          <div class="case-ic">{{ (d.doc_type || '文书').slice(0,2) }}</div>
          <div class="flex-1"><div class="t">{{ d.doc_type }}</div><div class="m">版本 {{ d.version }}</div></div>
          <span :class="d.status === '已完成' ? 'badge badge-success' : 'badge badge-neutral'">{{ d.status }}</span>
        </div>
        <div class="dm" style="margin-bottom:8px">案件: {{ d.case_name || `#${d.case_id}` }}</div>
        <div class="acts">
          <a @click.stop="$router.push(`/documents/${d.id}`)">查看</a>
          <a @click.stop="downloadDoc(d)">下载</a>
        </div>
      </div>
    </div>

    <div v-if="docs.length > 0" style="text-align:center;margin-top:20px">
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
