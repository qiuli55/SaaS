<template>
  <div>
    <div class="page-header"><h1 class="page-title">历史记录</h1></div>
    <div class="filter-bar"><input v-model="keyword" @input="searchDebounced" type="text" placeholder="搜索文书类型、案由..." class="form-input" style="width:300px;height:36px" /></div>
    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-muted)">加载中...</div>
    <div v-else-if="!items.length" style="text-align:center;padding:64px;color:var(--text-muted)"><div style="font-size:36px;margin-bottom:12px">📜</div>暂无生成记录</div>
    <div v-else class="table-wrapper">
      <table class="table">
        <thead><tr><th>文书类型</th><th>版本</th><th>关联案件</th><th>生成时间</th><th>状态</th></tr></thead>
        <tbody><tr v-for="item in items" :key="item.id" @click="$router.push(`/documents/${item.id}`)">
          <td style="font-weight:500;color:var(--navy-800)">{{ item.doc_type }}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:13px">V{{ item.version }}</td>
          <td style="color:var(--text-secondary)">{{ item.case_name||'--' }}</td>
          <td style="color:var(--text-secondary);font-size:13px">{{ formatDate(item.created_at) }}</td>
          <td><span :class="item.status==='已完成'?'badge badge-success':'badge badge-neutral'">{{ item.status }}</span></td>
        </tr></tbody>
      </table>
    </div>
    <div v-if="total>pageSize" style="display:flex;justify-content:center;margin-top:20px;gap:8px">
      <button @click="page--;fetchHistory()" :disabled="page<=1" class="btn btn-outline btn-sm">上一页</button>
      <span style="padding:6px 16px;font-size:13px;color:var(--text-muted)">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
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
