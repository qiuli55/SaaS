<template>
  <div>
    <div class="page-header">
      <div><h1 class="page-title">客户通讯录</h1></div>
      <router-link to="/clients/new" class="btn btn-primary">+ 添加客户</router-link>
    </div>

    <div class="filter-bar">
      <input v-model="keyword" @input="searchDebounced" type="text" placeholder="搜索客户姓名、电话或公司..." class="form-input" style="width:300px;height:36px" />
    </div>

    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-muted)">加载中...</div>

    <div v-else-if="clients.length === 0" style="text-align:center;padding:64px">
      <div style="font-size:36px;margin-bottom:12px">👥</div>
      <div style="color:var(--text-secondary);margin-bottom:20px">暂无客户</div>
      <router-link to="/clients/new" class="btn btn-accent">添加第一个客户</router-link>
    </div>

    <div v-else class="grid grid-cols-2 gap-4" style="grid-template-columns:repeat(auto-fill,minmax(360px,1fr))">
      <div v-for="c in clients" :key="c.id" class="card card-hover" style="display:flex;align-items:center;gap:16px;padding:20px;cursor:pointer" @click="$router.push(`/clients/${c.id}`)">
        <div style="width:48px;height:48px;border-radius:9999px;background:var(--navy-100);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:600;color:var(--navy-700);flex-shrink:0">{{ (c.name || '客')[0] }}</div>
        <div class="flex-1" style="min-width:0">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
            <span style="font-weight:600;color:var(--text-primary)">{{ c.name || '未填写' }}</span>
            <span v-if="c.tags" style="display:flex;gap:4px"><span v-for="t in parseTags(c.tags)" :key="t" class="badge badge-info" style="font-size:10px">{{ t }}</span></span>
          </div>
          <div style="font-size:13px;color:var(--text-secondary)">
            <span v-if="c.phone">📱 {{ c.phone }}</span>
            <span v-if="c.phone && c.company"> · </span>
            <span v-if="c.company">{{ c.company }}</span>
          </div>
        </div>
        <div style="font-size:13px;color:var(--text-muted);flex-shrink:0">{{ c.case_count }}案件</div>
      </div>
    </div>

    <div v-if="total > pageSize" style="display:flex;justify-content:center;margin-top:20px;gap:8px">
      <button @click="page--; fetchClients()" :disabled="page<=1" class="btn btn-outline btn-sm">上一页</button>
      <span style="padding:6px 16px;font-size:13px;color:var(--text-muted)">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
      <button @click="page++; fetchClients()" :disabled="page*pageSize>=total" class="btn btn-outline btn-sm">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

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
</script>
