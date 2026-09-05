<template>
  <div>
    <div v-if="loading" class="empty">加载中...</div>
    <template v-else>
      <div class="detail-head">
        <div>
          <div class="no">客户通讯录</div>
          <div class="nm">{{ client.name || '未填写' }}</div>
          <div class="detail-meta">
            <span v-if="client.phone">电话 <b class="mono">{{ client.phone }}</b></span>
            <span v-if="client.company">公司 <b>{{ client.company }}</b></span>
            <span>关联案件 <b class="mono">{{ client.cases?.length || 0 }}</b></span>
          </div>
        </div>
        <div style="display:flex;gap:8px;align-items:flex-end">
          <button @click="confirmDelete" class="btn btn-danger btn-sm">删除</button>
          <router-link to="/cases/new" class="btn btn-gold btn-sm">+ 新建案件</router-link>
        </div>
      </div>

      <div class="two-col">
        <div>
          <div class="sec-head"><span class="sec-mark">壹</span><span class="sec-title">关联案件</span></div>
          <div v-if="!client.cases?.length" class="card">
            <div class="empty"><div class="ico">📋</div><div class="t">暂无关联案件</div></div>
          </div>
          <div v-else class="table-wrap" style="margin-bottom:20px">
            <table class="table">
              <thead><tr><th>编号</th><th>案由</th><th>当事人</th><th>标的额</th><th>状态</th></tr></thead>
              <tbody>
                <tr v-for="c in client.cases" :key="c.id" style="cursor:pointer" @click="$router.push(`/cases/${c.id}`)">
                  <td class="mono" style="font-size:13px;font-weight:600;color:var(--ink)">{{ c.case_no }}</td>
                  <td style="font-weight:500">{{ c.case_type }}</td>
                  <td style="color:var(--muted);font-size:13px">{{ c.plaintiff }} vs {{ c.defendant }}</td>
                  <td class="mono">{{ c.subject_amount ? '¥' + formatMoney(c.subject_amount) : '—' }}</td>
                  <td><span class="badge" :class="statusBadge(c.status)">{{ c.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="sec-head" v-if="client.remark"><span class="sec-mark">贰</span><span class="sec-title">备注</span></div>
          <div class="card" v-if="client.remark"><div class="card-body" style="font-size:13.5px;color:var(--muted);line-height:1.7">{{ client.remark }}</div></div>
        </div>

        <div>
          <div class="sec-head"><span class="sec-mark">叁</span><span class="sec-title">客户信息</span></div>
          <div class="card">
            <div class="card-body">
              <div v-if="parseTags(client.tags).length" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px">
                <span v-for="t in parseTags(client.tags)" :key="t" class="badge b-info">{{ t }}</span>
              </div>
              <dl class="kv">
                <dt v-if="client.phone">手机号</dt><dd v-if="client.phone" class="mono">{{ client.phone }}</dd>
                <dt v-if="client.wechat">微信</dt><dd v-if="client.wechat">{{ client.wechat }}</dd>
                <dt v-if="client.id_card">身份证</dt><dd v-if="client.id_card" class="mono" style="font-size:12.5px">{{ client.id_card }}</dd>
                <dt v-if="client.company">公司</dt><dd v-if="client.company">{{ client.company }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { useRoute, useRouter } from 'vue-router'; import api from '../api'
const route = useRoute(); const router = useRouter(); const client = ref({}); const loading = ref(true); const error = ref('')
onMounted(async () => { try { const r = await api.get(`/clients/${route.params.id}`); client.value = r.data.data } catch(e) { error.value = e?.response?.data?.detail || '加载客户信息失败' } finally { loading.value = false } })
async function confirmDelete() { if(!confirm('确定删除此客户？')) return; try { await api.delete(`/clients/${route.params.id}`); router.push('/clients') } catch(e) { alert('删除失败：' + (e?.response?.data?.detail || e.message)) } }
function parseTags(t) { try { return JSON.parse(t) } catch { return t ? t.split(',') : [] } }
function statusBadge(s) { const m = {'进行中':'b-info','已结案':'b-success','待立案':'b-warning'}; return m[s]||'b-neutral' }
function formatMoney(v) { return Number(v||0).toLocaleString('zh-CN') }
</script>
