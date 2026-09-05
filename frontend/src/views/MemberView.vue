<template>
  <div class="member-page">
    <div v-if="message" :class="['banner', message.type]">{{ message.text }}</div>

    <!-- 当前套餐卡片 -->
    <div class="member-card">
      <div class="member-card-head">
        <div>
          <div class="member-plan-name">{{ sub.plan?.name || '免费版' }}</div>
          <div class="member-plan-tag">
            <span v-if="sub.is_paid" class="badge paid">付费套餐</span>
            <span v-else class="badge free">免费版</span>
            <span v-if="sub.period" class="badge period">{{ sub.period === 'monthly' ? '按月' : '按年' }}</span>
          </div>
        </div>
        <div v-if="sub.is_paid" class="member-expire">
          有效期至<br /><b>{{ expireText }}</b>
        </div>
      </div>

      <div class="member-usage">
        <div class="usage-row">
          <span>今日 AI 调用</span>
          <span class="usage-val">
            {{ sub.today_usage }}<template v-if="sub.daily_limit != null"> / {{ sub.daily_limit }}</template>
            <template v-else> / 不限</template>
          </span>
        </div>
        <div class="usage-bar">
          <div
            class="usage-fill"
            :style="{ width: usagePercent + '%' }"
            :class="{ full: usagePercent >= 100 }"
          ></div>
        </div>
        <div class="usage-note">
          <template v-if="sub.daily_limit == null">不限量套餐，可尽情使用全部 AI 功能</template>
          <template v-else-if="usagePercent >= 100">今日额度已用完，明日 0 点重置</template>
          <template v-else>今日剩余 {{ sub.daily_limit - sub.today_usage }} 次</template>
        </div>
      </div>

      <div class="member-actions">
        <router-link v-if="!sub.is_paid" to="/pricing" class="btn-upgrade">升级套餐</router-link>
        <button v-else class="btn-cancel" @click="openCancel" :disabled="cancelling">取消订阅</button>
      </div>
    </div>

    <!-- 功能权益 -->
    <div class="member-section">
      <h3>套餐权益</h3>
      <ul class="feature-list">
        <li v-for="f in (sub.plan?.features || [])" :key="f"><span class="check">✓</span>{{ f }}</li>
      </ul>
    </div>

    <!-- 订单历史 -->
    <div class="member-section">
      <h3>订单记录</h3>
      <div v-if="orders.length === 0" class="empty">暂无订单</div>
      <table v-else class="order-table">
        <thead>
          <tr>
            <th>订单号</th><th>套餐</th><th>金额</th><th>周期</th><th>状态</th><th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in orders" :key="o.order_no">
            <td class="mono">{{ o.order_no }}</td>
            <td>{{ o.plan_name }}</td>
            <td>¥{{ o.amount }}</td>
            <td>{{ o.period === 'monthly' ? '按月' : '按年' }}</td>
            <td>
              <span :class="['ost', o.status]">
                {{ o.status === 'paid' ? '已支付' : o.status === 'cancelled' ? '已取消' : '待支付' }}
              </span>
            </td>
            <td class="mono">{{ (o.paid_at || o.created_at).slice(0, 10) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 取消订阅确认弹窗 -->
    <div v-if="confirmCancel" class="modal-mask" @click.self="closeCancel">
      <div class="modal">
        <h3>取消订阅</h3>
        <p class="modal-text">
          取消后，当前付费周期内仍可继续使用，<strong>到期后将自动降级为免费版</strong>（每日 50 次）。确定取消吗？
        </p>
        <div class="modal-actions">
          <button class="btn-ghost" @click="closeCancel" :disabled="cancelling">再想想</button>
          <button class="btn-primary" @click="confirmCancelSub" :disabled="cancelling">
            {{ cancelling ? '处理中…' : '确认取消' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// MemberView.vue —— 会员中心：展示当前订阅与今日用量、订单记录，
// 支持取消订阅（本周期内权益保留，到期降级免费版）。依赖后端 /api/billing/* 接口。
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const sub = ref({ plan: {}, is_paid: false, today_usage: 0, daily_limit: 50 })
const orders = ref([])
const message = ref(null)
const confirmCancel = ref(false)
const cancelling = ref(false)

const expireText = computed(() => (sub.value.end_at ? sub.value.end_at.slice(0, 10) : '—'))

const usagePercent = computed(() => {
  const limit = sub.value.daily_limit
  if (limit == null) return 0
  if (limit <= 0) return 100
  return Math.min(100, Math.round((sub.value.today_usage / limit) * 100))
})

async function load() {
  try {
    const r = await api.get('/billing/subscription/current')
    sub.value = r.data
  } catch (e) {
    message.value = { type: 'error', text: '加载订阅失败：' + (e.response?.data?.detail || e.message) }
  }
  try {
    const r = await api.get('/billing/orders')
    orders.value = r.data.orders || []
  } catch (e) {
    /* 订单加载失败不阻断 */
  }
}

function openCancel() {
  confirmCancel.value = true
}

function closeCancel() {
  if (cancelling.value) return
  confirmCancel.value = false
}

async function confirmCancelSub() {
  cancelling.value = true
  try {
    await api.post('/billing/subscription/cancel')
    message.value = { type: 'success', text: '已取消订阅，当前周期内可继续使用，到期降级为免费版' }
    confirmCancel.value = false
    load()
  } catch (e) {
    message.value = { type: 'error', text: '取消失败：' + (e.response?.data?.detail || e.message) }
    confirmCancel.value = false
  } finally {
    cancelling.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.member-page { max-width: 680px; margin: 0 auto; padding: 24px 16px 40px }
.banner { margin-bottom: 18px; padding: 11px 16px; border-radius: 10px; font-size: 14px; line-height: 1.5 }
.banner.success { background: #e7f6ec; color: #1f7a3d; border: 1px solid #b7e2c5 }
.banner.error { background: #fdecec; color: #c0392b; border: 1px solid #f3c4c4 }
.member-card {
  background: var(--color-background-secondary); border: 1px solid var(--color-border-tertiary);
  border-radius: 16px; padding: 24px;
}
.member-card-head { display: flex; justify-content: space-between; align-items: flex-start }
.member-plan-name { font-size: 22px; font-weight: 600; color: var(--text-primary) }
.member-plan-tag { margin-top: 8px; display: flex; gap: 6px }
.badge { font-size: 12px; padding: 2px 9px; border-radius: 999px }
.badge.paid { background: var(--navy-100, #e8eef5); color: var(--navy-700, #1f3a5f) }
.badge.free { background: var(--color-background-primary); color: var(--text-tertiary); border: 1px solid var(--color-border-tertiary) }
.badge.period { background: var(--color-background-primary); color: var(--text-secondary); border: 1px solid var(--color-border-tertiary) }
.member-expire { text-align: right; font-size: 12px; color: var(--text-tertiary) }
.member-expire b { font-size: 15px; color: var(--text-primary) }
.member-usage { margin: 22px 0 18px }
.usage-row { display: flex; justify-content: space-between; font-size: 14px; color: var(--text-secondary); margin-bottom: 8px }
.usage-val { font-weight: 600; color: var(--text-primary) }
.usage-bar { height: 8px; background: var(--color-background-primary); border-radius: 999px; overflow: hidden }
.usage-fill { height: 100%; background: var(--navy-600, #1f3a5f); border-radius: 999px; transition: width .3s }
.usage-fill.full { background: var(--color-text-danger, #c0392b) }
.usage-note { font-size: 12.5px; color: var(--text-tertiary); margin-top: 8px }
.member-actions { display: flex; gap: 10px }
.btn-upgrade {
  flex: 1; text-align: center; padding: 11px; border-radius: 10px; text-decoration: none;
  background: var(--navy-600, #1f3a5f); color: #fff; font-size: 15px; font-weight: 500;
}
.btn-cancel {
  flex: 1; padding: 11px; border-radius: 10px; cursor: pointer;
  background: var(--color-background-primary); color: var(--color-text-danger, #c0392b);
  border: 1px solid var(--color-border-tertiary); font-size: 14px;
}
.btn-cancel:disabled { opacity: .6; cursor: default }
.member-section { margin-top: 28px }
.member-section h3 { font-size: 15px; color: var(--text-primary); margin: 0 0 12px; font-weight: 600 }
.feature-list { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 8px }
.feature-list li { font-size: 13.5px; color: var(--text-secondary); display: flex; gap: 8px; align-items: flex-start }
.feature-list .check { color: var(--accent, #3B6D11); font-weight: 700 }
.empty { font-size: 13.5px; color: var(--text-tertiary) }
.order-table { width: 100%; border-collapse: collapse; font-size: 13px }
.order-table th { text-align: left; color: var(--text-tertiary); font-weight: 500; padding: 8px 6px; border-bottom: 1px solid var(--color-border-tertiary) }
.order-table td { padding: 9px 6px; border-bottom: 1px solid var(--color-border-tertiary); color: var(--text-secondary) }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px }
.ost { font-size: 12px; padding: 2px 8px; border-radius: 999px }
.ost.paid { background: var(--color-background-success, #e9f7ef); color: var(--color-text-success, #1e874b) }
.ost.pending { background: var(--color-background-primary); color: var(--text-tertiary) }
.ost.cancelled { background: #f2f2f2; color: var(--text-tertiary) }
/* 确认弹窗 */
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal { background: #fff; border-radius: 14px; padding: 24px 22px; width: 340px; max-width: 90vw; box-shadow: 0 12px 40px rgba(0,0,0,.25) }
.modal h3 { margin: 0 0 10px; font-size: 18px; color: var(--text-primary) }
.modal-text { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin: 0 0 18px }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end }
.btn-ghost { padding: 9px 16px; border: 1px solid var(--color-border-tertiary); background: #fff; border-radius: 9px; cursor: pointer; font-size: 14px; color: var(--text-secondary) }
.btn-primary { padding: 9px 18px; border: none; background: var(--navy-600, #1f3a5f); color: #fff; border-radius: 9px; cursor: pointer; font-size: 14px; font-weight: 500 }
.btn-primary:disabled, .btn-ghost:disabled { opacity: .6; cursor: default }
</style>
