<template>
  <div>
    <div class="page-header">
      <div><h1 class="page-title">{{ client.name || '未填写' }}</h1></div>
      <button @click="confirmDelete" class="btn btn-danger btn-sm">删除</button>
    </div>

    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-muted)">加载中...</div>
    <template v-else>
      <div class="card mb-6">
        <div class="card-body">
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px">
            <span v-for="t in parseTags(client.tags)" :key="t" class="badge badge-info">{{ t }}</span>
          </div>
          <div class="stats-grid" style="margin-bottom:0">
            <div v-if="client.phone"><div class="stat-label">手机号</div><div style="font-weight:500;font-family:'JetBrains Mono',monospace">{{ client.phone }}</div></div>
            <div v-if="client.wechat"><div class="stat-label">微信</div><div style="font-weight:500">{{ client.wechat }}</div></div>
            <div v-if="client.id_card"><div class="stat-label">身份证</div><div style="font-weight:500;font-family:'JetBrains Mono',monospace;font-size:13px">{{ client.id_card }}</div></div>
            <div v-if="client.company"><div class="stat-label">公司</div><div style="font-weight:500">{{ client.company }}</div></div>
          </div>
          <div v-if="client.remark" style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-light)">
            <div class="stat-label">备注</div><div style="font-size:14px;color:var(--text-secondary)">{{ client.remark }}</div>
          </div>
        </div>
      </div>

      <h2 style="font-family:'Noto Serif SC',serif;font-size:20px;font-weight:600;color:var(--navy-900);margin-bottom:16px">关联案件 ({{ client.cases?.length || 0 }})</h2>

      <div v-if="!client.cases?.length" style="text-align:center;padding:48px;color:var(--text-muted)">
        <div style="font-size:36px;margin-bottom:12px">📋</div>
        <div style="margin-bottom:16px">暂无关联案件</div>
        <router-link to="/cases/new" class="btn btn-accent btn-sm">新建案件</router-link>
      </div>

      <div v-else class="table-wrapper">
        <table class="table">
          <thead><tr><th>编号</th><th>案由</th><th>当事人</th><th>标的额</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="c in client.cases" :key="c.id" @click="$router.push(`/cases/${c.id}`)">
              <td style="color:var(--navy-800);font-family:'JetBrains Mono',monospace;font-size:13px">{{ c.case_no }}</td>
              <td style="font-weight:500">{{ c.case_type }}</td>
              <td style="color:var(--text-secondary);font-size:13px">{{ c.plaintiff }} vs {{ c.defendant }}</td>
              <td style="font-family:'JetBrains Mono',monospace">¥{{ formatMoney(c.subject_amount) }}</td>
              <td><span :class="statusBadge(c.status)">{{ c.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { useRoute, useRouter } from 'vue-router'; import api from '../api'
const route = useRoute(); const router = useRouter(); const client = ref({}); const loading = ref(true)
onMounted(async () => { try { const r = await api.get(`/clients/${route.params.id}`); client.value = r.data.data } catch(e){} finally { loading.value = false } })
async function confirmDelete() { if(!confirm('确定删除此客户？')) return; try { await api.delete(`/clients/${route.params.id}`); router.push('/clients') } catch{} }
function parseTags(t) { try { return JSON.parse(t) } catch { return t ? t.split(',') : [] } }
function statusBadge(s) { const m = {'进行中':'badge badge-info','已结案':'badge badge-success','待立案':'badge badge-warning'}; return m[s]||'badge badge-neutral' }
function formatMoney(v) { return Number(v||0).toLocaleString('zh-CN') }
</script>
