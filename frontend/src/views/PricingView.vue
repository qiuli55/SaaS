<template>
  <div class="pricing-page">
    <div class="pricing-head">
      <h1>选择适合你的套餐</h1>
      <p>AI 法务助手按用量灵活升级，随时可取消</p>
      <div class="period-toggle">
        <button :class="{ on: period === 'monthly' }" @click="period = 'monthly'">按月</button>
        <button :class="{ on: period === 'yearly' }" @click="period = 'yearly'">
          按年<span class="save">省 17%</span>
        </button>
      </div>
    </div>

    <div v-if="message" :class="['banner', message.type]">{{ message.text }}</div>

    <div v-if="loading" class="pricing-loading">加载中…</div>

    <div v-else class="plan-grid">
      <div
        v-for="p in plans"
        :key="p.code"
        class="plan-card"
        :class="{ featured: p.code === 'pro' }"
      >
        <div v-if="p.code === 'pro'" class="ribbon">推荐</div>
        <div class="plan-name">{{ p.name }}</div>
        <div class="plan-price">
          <span class="amount">¥{{ priceOf(p) }}</span>
          <span class="unit">/ {{ period === 'monthly' ? '月' : '年' }}</span>
        </div>
        <div class="plan-limit">
          {{ p.daily_limit == null ? 'AI 调用不限量' : '每日 ' + p.daily_limit + ' 次 AI 调用' }}
        </div>
        <ul class="plan-features">
          <li v-for="f in p.features" :key="f"><span class="check">✓</span>{{ f }}</li>
        </ul>
        <button
          v-if="p.code !== 'free'"
          class="buy-btn"
          :disabled="paying"
          @click="buy(p)"
        >
          {{ paying && buyingCode === p.code ? '开通中…' : '立即开通' }}
        </button>
        <div v-else class="free-badge">当前免费套餐</div>
      </div>
    </div>

    <p class="pricing-tip">
      演示环境为<strong>模拟支付</strong>：点击「立即开通」即视为支付成功并立即开通，不产生真实扣款。后续可接入微信支付 / 支付宝。
    </p>

    <!-- 页面内确认弹窗（不依赖原生 confirm，嵌入预览浏览器也能用） -->
    <div v-if="confirmPlan" class="modal-mask" @click.self="closeConfirm">
      <div class="modal">
        <h3>确认开通「{{ confirmPlan.name }}」</h3>
        <p class="modal-text">
          {{ period === 'monthly' ? '按月' : '按年' }} ¥{{ priceOf(confirmPlan) }}<br />
          演示环境为模拟支付，点击即视为支付成功，<strong>不产生真实扣款</strong>。
        </p>
        <div class="modal-actions">
          <button class="btn-ghost" @click="closeConfirm" :disabled="paying">再想想</button>
          <button class="btn-primary" @click="confirmBuy" :disabled="paying">
            {{ paying ? '开通中…' : '确认开通' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// PricingView.vue —— 套餐购买页：展示套餐与按月/按年价格，下单走模拟支付，
// 支付成功后跳转会员中心。依赖后端 /api/billing/* 接口。
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const plans = ref([])
const period = ref('monthly')
const loading = ref(false)
const paying = ref(false)
const buyingCode = ref('')
const confirmPlan = ref(null)   // 当前待确认开通的套餐
const message = ref(null)       // 页面内提示条 { type: 'success'|'error', text }

// 按当前计费周期取价格
function priceOf(p) {
  return period.value === 'yearly' ? p.price_yearly : p.price_monthly
}

// 拉取套餐列表
async function load() {
  loading.value = true
  try {
    const r = await api.get('/billing/plans')
    plans.value = r.data.plans || []
  } catch (e) {
    message.value = { type: 'error', text: '加载失败：' + (e.response?.data?.detail || e.message) }
  } finally {
    loading.value = false
  }
}

// 点击「立即开通」→ 打开页面内确认弹窗（不再用原生 confirm）
function buy(p) {
  confirmPlan.value = p
}

function closeConfirm() {
  if (paying.value) return
  confirmPlan.value = null
}

// 弹窗内「确认开通」→ 下单 + 模拟支付
async function confirmBuy() {
  const p = confirmPlan.value
  if (!p) return
  paying.value = true
  buyingCode.value = p.code
  try {
    const o = await api.post('/billing/orders', { plan_code: p.code, period: period.value })
    const orderNo = o.data.order_no
    const pay = await api.post(`/billing/orders/${orderNo}/pay`)
    message.value = { type: 'success', text: pay.data.message || '开通成功' }
    confirmPlan.value = null
    router.push('/member')
  } catch (e) {
    message.value = { type: 'error', text: '开通失败：' + (e.response?.data?.detail || e.message) }
    confirmPlan.value = null
  } finally {
    paying.value = false
    buyingCode.value = ''
  }
}

onMounted(load)
</script>

<style scoped>
.pricing-page { max-width: 980px; margin: 0 auto; padding: 28px 16px 40px }
.pricing-head { text-align: center; margin-bottom: 28px }
.pricing-head h1 { font-size: 26px; font-weight: 600; color: var(--text-primary); margin: 0 }
.pricing-head p { color: var(--text-tertiary); margin: 8px 0 0 }
.period-toggle {
  display: inline-flex; gap: 4px; margin-top: 18px;
  background: var(--color-background-secondary); border-radius: 999px; padding: 4px;
}
.period-toggle button {
  border: none; background: none; cursor: pointer; padding: 7px 18px; border-radius: 999px;
  font-size: 14px; color: var(--text-secondary); display: inline-flex; align-items: center; gap: 6px;
}
.period-toggle button.on { background: var(--navy-600, #1f3a5f); color: #fff }
.period-toggle .save {
  font-size: 11px; background: rgba(255,255,255,.25); padding: 1px 6px; border-radius: 999px;
}
.period-toggle button:not(.on) .save { background: var(--color-background-danger, #fde8e8); color: var(--color-text-danger, #c0392b) }
.pricing-loading { text-align: center; color: var(--text-tertiary); padding: 40px }
.banner { max-width: 720px; margin: 0 auto 18px; padding: 11px 16px; border-radius: 10px; font-size: 14px; line-height: 1.5 }
.banner.success { background: #e7f6ec; color: #1f7a3d; border: 1px solid #b7e2c5 }
.banner.error { background: #fdecec; color: #c0392b; border: 1px solid #f3c4c4 }
.plan-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px }
.plan-card {
  position: relative; background: var(--color-background-secondary);
  border: 1px solid var(--color-border-tertiary); border-radius: 16px; padding: 24px 22px;
  display: flex; flex-direction: column;
}
.plan-card.featured { border-color: var(--navy-600, #1f3a5f); box-shadow: 0 8px 24px rgba(31,58,95,.12) }
.ribbon {
  position: absolute; top: -10px; right: 18px; background: var(--navy-600, #1f3a5f); color: #fff;
  font-size: 12px; padding: 2px 10px; border-radius: 999px;
}
.plan-name { font-size: 17px; font-weight: 600; color: var(--text-primary) }
.plan-price { margin: 10px 0 4px }
.plan-price .amount { font-size: 30px; font-weight: 700; color: var(--text-primary) }
.plan-price .unit { font-size: 13px; color: var(--text-tertiary); margin-left: 4px }
.plan-limit { font-size: 13px; color: var(--accent, #3B6D11); font-weight: 500; margin-bottom: 14px }
.plan-features { list-style: none; padding: 0; margin: 0 0 18px; flex: 1 }
.plan-features li { font-size: 13.5px; color: var(--text-secondary); padding: 6px 0; display: flex; gap: 8px; align-items: flex-start }
.plan-features .check { color: var(--accent, #3B6D11); font-weight: 700 }
.buy-btn {
  width: 100%; padding: 11px; border: none; border-radius: 10px; cursor: pointer;
  background: var(--navy-600, #1f3a5f); color: #fff; font-size: 15px; font-weight: 500;
}
.buy-btn:disabled { opacity: .6; cursor: default }
.free-badge {
  width: 100%; text-align: center; padding: 11px; border-radius: 10px; font-size: 14px;
  background: var(--color-background-primary); color: var(--text-tertiary); border: 1px solid var(--color-border-tertiary);
}
.pricing-tip { text-align: center; font-size: 12.5px; color: var(--text-tertiary); margin-top: 24px; line-height: 1.6 }
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
