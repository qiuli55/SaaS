<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">案件管理</div>
        <div class="page-sub">共 {{ total }} 个案件</div>
      </div>
      <div class="page-actions">
        <router-link to="/cases/new" class="btn btn-primary">+ 新建案件</router-link>
      </div>
    </div>

    <div class="filter-bar">
      <div class="tabs">
        <button @click="statusFilter=''; fetchCases()" class="tab" :class="{ active: !statusFilter }">全部</button>
        <button @click="statusFilter='进行中'; fetchCases()" class="tab" :class="{ active: statusFilter==='进行中' }">进行中</button>
        <button @click="statusFilter='待立案'; fetchCases()" class="tab" :class="{ active: statusFilter==='待立案' }">待立案</button>
        <button @click="statusFilter='已结案'; fetchCases()" class="tab" :class="{ active: statusFilter==='已结案' }">已结案</button>
      </div>
      <label class="search">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="8" cy="8" r="5"/><path d="M12 12l4 4"/></svg>
        <input v-model="keyword" @input="searchDebounced" type="text" placeholder="搜索案由、当事人…" />
      </label>
    </div>

    <div v-if="loading" class="empty">加载中...</div>

    <div v-else-if="cases.length === 0" class="empty">
      <div class="ico">📭</div>
      <div class="t">暂无案件</div>
      <router-link to="/cases/new" class="btn btn-gold" style="margin-top:14px">创建第一个案件</router-link>
    </div>

    <div v-else class="table-wrap">
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
          <tr v-for="c in cases" :key="c.id" style="cursor:pointer" @click="$router.push(`/cases/${c.id}`)">
            <td><span class="mono" style="color:var(--ink);font-weight:600">{{ c.case_no }}</span></td>
            <td style="font-weight:500">{{ c.case_type }}</td>
            <td style="color:var(--muted)">{{ c.plaintiff }} <span style="color:var(--line-strong)">vs</span> {{ c.defendant }}</td>
            <td class="mono" style="font-weight:500">{{ c.subject_amount ? '¥' + formatMoney(c.subject_amount) : '—' }}</td>
            <td style="font-size:13px;color:var(--muted)">{{ formatDate(c.commission_date) }}</td>
            <td><span class="badge" :class="statusBadge(c.status)">{{ c.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > pageSize" class="pager">
      <button @click="page--;fetchCases()" :disabled="page<=1" class="btn btn-outline btn-sm">上一页</button>
      <span class="p-info">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
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
  const m = { '进行中':'b-info', '已结案':'b-success', '待立案':'b-warning' }
  return m[s] || 'b-neutral'
}

function formatDate(d) { return d ? d.slice(0,10) : '' }
function formatMoney(v) { return Number(v||0).toLocaleString('zh-CN') }
</script>
