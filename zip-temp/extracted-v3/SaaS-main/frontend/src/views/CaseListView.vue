<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">案件管理</h1>
      </div>
      <router-link to="/cases/new" class="btn btn-primary">+ 新建案件</router-link>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button @click="statusFilter=''; fetchCases()" class="filter-tab" :class="{ active: !statusFilter }">全部</button>
        <button @click="statusFilter='进行中'; fetchCases()" class="filter-tab" :class="{ active: statusFilter==='进行中' }">进行中</button>
        <button @click="statusFilter='待立案'; fetchCases()" class="filter-tab" :class="{ active: statusFilter==='待立案' }">待立案</button>
        <button @click="statusFilter='已结案'; fetchCases()" class="filter-tab" :class="{ active: statusFilter==='已结案' }">已结案</button>
      </div>
      <input v-model="keyword" @input="searchDebounced" type="text" placeholder="搜索案由、当事人..." class="form-input" style="width:240px;height:36px" />
    </div>

    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-muted)">加载中...</div>

    <div v-else-if="cases.length === 0" style="text-align:center;padding:64px">
      <div style="font-size:36px;margin-bottom:12px">📭</div>
      <div style="color:var(--text-secondary);margin-bottom:20px">暂无案件</div>
      <router-link to="/cases/new" class="btn btn-accent">创建第一个案件</router-link>
    </div>

    <div v-else class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>案件编号</th>
            <th>案由</th>
            <th>当事人</th>
            <th>标的额</th>
            <th>委托日期</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in cases" :key="c.id" @click="$router.push(`/cases/${c.id}`)">
            <td style="color:var(--navy-800);font-weight:500;font-family:'JetBrains Mono',monospace;font-size:13px">{{ c.case_no }}</td>
            <td style="font-weight:500">{{ c.case_type }}</td>
            <td style="color:var(--text-secondary);font-size:13px">{{ c.plaintiff }} vs {{ c.defendant }}</td>
            <td style="font-family:'JetBrains Mono',monospace;font-weight:500">¥{{ formatMoney(c.subject_amount) }}</td>
            <td style="font-size:13px;color:var(--text-secondary)">{{ formatDate(c.commission_date) }}</td>
            <td><span :class="statusBadge(c.status)">{{ c.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > pageSize" style="display:flex;justify-content:center;margin-top:20px;gap:8px">
      <button @click="page--;fetchCases()" :disabled="page<=1" class="btn btn-outline btn-sm">上一页</button>
      <span style="padding:6px 16px;font-size:13px;color:var(--text-muted)">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
      <button @click="page++;fetchCases()" :disabled="page*pageSize>=total" class="btn btn-outline btn-sm">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const cases = ref([])
const loading = ref(true)
const keyword = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
let timer = null

onMounted(() => fetchCases())

function searchDebounced() {
  clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetchCases() }, 400)
}

async function fetchCases() {
  loading.value = true
  try {
    const res = await api.get('/cases', {
      params: { keyword: keyword.value||undefined, status: statusFilter.value||undefined, page: page.value, page_size: pageSize }
    })
    cases.value = res.data.items
    total.value = res.data.total
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

function statusBadge(s) {
  const m = { '进行中':'badge badge-info', '已结案':'badge badge-success', '待立案':'badge badge-warning' }
  return m[s] || 'badge badge-neutral'
}

function formatDate(d) { return d ? d.slice(0,10) : '' }
function formatMoney(v) { return Number(v||0).toLocaleString('zh-CN') }
</script>
