<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">客户通讯录</div>
        <div class="page-sub"><span style="font-size:12px;color:var(--gold-deep);background:rgba(47,107,213,.1);padding:2px 8px;border-radius:4px">🔒 数据仅您可见</span></div>
      </div>
      <div class="page-actions">
        <button @click="exportExcel" class="btn btn-outline btn-sm">导出 Excel</button>
        <label class="btn btn-outline btn-sm" style="cursor:pointer;margin:0">
          <input type="file" accept=".xlsx,.xls" hidden @change="importExcel" />
          导入 Excel
        </label>
        <router-link to="/clients/new" class="btn btn-primary btn-sm">+ 添加客户</router-link>
      </div>
    </div>

    <div class="filter-bar">
      <label class="search">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="8" cy="8" r="5"/><path d="M12 12l4 4"/></svg>
        <input v-model="keyword" @input="searchDebounced" type="text" placeholder="搜索客户姓名、电话或公司…" />
      </label>
    </div>

    <div v-if="loading" class="empty">加载中...</div>

    <div v-else-if="clients.length === 0" class="empty">
      <div class="ico">👥</div>
      <div class="t">暂无客户</div>
      <router-link to="/clients/new" class="btn btn-gold" style="margin-top:14px">添加第一个客户</router-link>
    </div>

    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>客户</th><th>联系方式</th><th>标签</th><th>关联案件</th><th style="width:90px">操作</th></tr></thead>
        <tbody>
          <tr v-for="c in clients" :key="c.id" style="cursor:pointer" @click="$router.push(`/clients/${c.id}`)">
            <td style="font-weight:600;color:var(--ink)">{{ c.name || '未填写' }}</td>
            <td style="color:var(--muted)">📱 {{ c.phone || '—' }}<span v-if="c.company" style="margin-left:8px">{{ c.company }}</span></td>
            <td>
              <span v-if="!c.tags" style="color:var(--muted)">—</span>
              <span v-else style="display:flex;gap:4px;flex-wrap:wrap"><span v-for="t in parseTags(c.tags)" :key="t" class="badge b-info" style="font-size:10.5px">{{ t }}</span></span>
            </td>
            <td class="mono">{{ c.case_count }} 案</td>
            <td><button @click.stop="$router.push(`/clients/${c.id}`)" class="btn btn-ghost btn-sm">查看</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > pageSize" class="pager">
      <button @click="page--; fetchClients()" :disabled="page<=1" class="btn btn-outline btn-sm">上一页</button>
      <span class="p-info">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
      <button @click="page++; fetchClients()" :disabled="page*pageSize>=total" class="btn btn-outline btn-sm">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { authDownload } from '../api'

const clients = ref([]); const loading = ref(true); const keyword = ref(''); const page = ref(1); const pageSize = 20; const total = ref(0); let timer = null

onMounted(() => fetchClients())
function searchDebounced() { clearTimeout(timer); timer = setTimeout(() => { page.value = 1; fetchClients() }, 400) }
async function fetchClients() {
  loading.value = true
  try { const res = await api.get('/clients', { params: { keyword: keyword.value||undefined, page: page.value, page_size: pageSize } })
    clients.value = res.data.data.items; total.value = res.data.data.total || 0 }
  catch (e) { console.error('加载客户列表失败', e) } finally { loading.value = false }
}
function parseTags(t) { try { return JSON.parse(t) } catch { return t ? t.split(',') : [] } }

async function exportExcel() {
  try { authDownload('/clients/export', '客户通讯录.xlsx') }
  catch(e) { alert('导出失败') }
}

async function importExcel(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!confirm(`确认从「${file.name}」导入客户？`)) { e.target.value = ''; return }
  const fd = new FormData()
  fd.append('file', file)
  try {
    const r = await api.post('/clients/import', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    alert(`导入完成：新增 ${r.data.data.created} 条，跳过 ${r.data.data.skipped} 条（重复）`)
    fetchClients()
  } catch(e) {
    alert('导入失败：' + (e.response?.data?.detail || e.message))
  }
  e.target.value = ''
}
</script>
