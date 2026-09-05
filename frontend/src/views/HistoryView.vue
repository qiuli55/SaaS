<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">历史记录</div>
        <div class="page-sub">已生成文书的归档留痕，共 {{ total }} 条</div>
      </div>
    </div>

    <div class="filter-bar">
      <label class="search">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="8" cy="8" r="5"/><path d="M12 12l4 4"/></svg>
        <input v-model="keyword" @input="searchDebounced" type="text" placeholder="搜索文书类型、案由…" />
      </label>
    </div>

    <div v-if="loading" class="empty">加载中...</div>
    <div v-else-if="!items.length" class="empty"><div class="ico">📜</div><div class="t">暂无生成记录</div></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>文书类型</th><th>版本</th><th>关联案件</th><th>生成时间</th><th>状态</th></tr></thead>
        <tbody><tr v-for="item in items" :key="item.id" style="cursor:pointer" @click="$router.push(`/documents/${item.id}`)">
          <td style="font-weight:600;color:var(--ink)">{{ item.doc_type }}</td>
          <td class="mono" style="font-size:13px">V{{ item.version }}</td>
          <td style="color:var(--muted)">{{ item.case_name||'--' }}</td>
          <td style="color:var(--muted);font-size:13px">{{ formatDate(item.created_at) }}</td>
          <td><span class="badge" :class="item.status==='已完成' ? 'b-success' : 'b-neutral'">{{ item.status }}</span></td>
        </tr></tbody>
      </table>
    </div>

    <div v-if="total>pageSize" class="pager">
      <button @click="page--;fetchHistory()" :disabled="page<=1" class="btn btn-outline btn-sm">上一页</button>
      <span class="p-info">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
      <button @click="page++;fetchHistory()" :disabled="page*pageSize>=total" class="btn btn-outline btn-sm">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import api from '../api'
const items = ref([]); const loading = ref(true); const keyword = ref(''); const page = ref(1); const pageSize = 20; const total = ref(0); let timer = null
onMounted(() => fetchHistory())
function searchDebounced() { clearTimeout(timer); timer = setTimeout(()=>{page.value=1;fetchHistory()},400) }
async function fetchHistory() {
  loading.value = true
  try { const r = await api.get('/documents/history', { params: { keyword:keyword.value||undefined, page:page.value, page_size:pageSize } })
    items.value = r.data.data.items||[]; total.value = r.data.data.total||0 } catch(e) { console.error('加载历史记录失败', e) } finally { loading.value = false }
}
function formatDate(d) { return d?.slice(0,10)||'' }
</script>
