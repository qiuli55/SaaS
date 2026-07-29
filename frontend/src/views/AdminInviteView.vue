<template>
  <div class="page">
    <div class="page-header">
      <h1>邀请码管理</h1>
      <p class="subtitle">生成和管理用户注册用的邀请码</p>
    </div>

    <!-- 生成区 -->
    <div class="card" style="margin-bottom: 24px">
      <h3 style="margin-bottom: 12px">生成邀请码</h3>
      <div style="display:flex; gap:12px; align-items:center">
        <input v-model.number="genCount" type="number" min="1" max="50" style="width:80px;padding:8px 12px;border:1px solid var(--border);border-radius:6px" />
        <span style="color:var(--text-muted);font-size:13px">个</span>
        <button class="btn btn-accent" @click="generate" :disabled="generating">{{ generating ? '生成中...' : '生成' }}</button>
      </div>
    </div>

    <!-- 已生成列表 -->
    <div class="card" v-if="codes.length > 0">
      <h3 style="margin-bottom: 16px">邀请码列表（{{ codes.length }}）</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <div v-for="c in codes" :key="c.id" class="code-card" :class="{ used: c.is_used, copying: copyingId === c.id }">
          <template v-if="showFull[c.id]">
            <div class="code-text">{{ c.code }}</div>
            <div class="code-meta">{{ formatTime(c.created_at) }} 生成</div>
            <div v-if="c.is_used" class="code-used">已使用 · {{ c.used_by_phone }} · {{ formatTime(c.used_at) }}</div>
            <div v-else class="code-new">未使用</div>
          </template>
          <template v-else>
            <div class="code-masked">{{ c.code.slice(0, 6) }}······</div>
            <div class="code-meta">{{ c.is_used ? '已使用' : '可用' }}</div>
          </template>
          <div class="code-actions">
            <button class="btn-sm" @click="toggleShow(c.id)" :title="showFull[c.id] ? '隐藏' : '查看'">
              {{ showFull[c.id] ? '👁' : '👁‍🗨' }}
            </button>
            <button v-if="!c.is_used" class="btn-sm" @click="copyCode(c)" :disabled="copyingId === c.id">
              {{ copyingId === c.id ? '已复制' : '📋' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="card">
      <p style="text-align:center;color:var(--text-muted);padding:40px 0">还没有邀请码，先生成一些吧</p>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const genCount = ref(5)
const generating = ref(false)
const loading = ref(true)
const error = ref('')
const codes = ref([])
const showFull = reactive({})
const copyingId = ref(null)

async function loadCodes() {
  loading.value = true
  try {
    const r = await api.get('/invite/list')
    codes.value = r.data
  } catch(e) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

async function generate() {
  generating.value = true
  try {
    await api.post('/invite/generate', { count: genCount.value })
    await loadCodes()
  } catch(e) {
    error.value = e.response?.data?.detail || '生成失败'
  } finally {
    generating.value = false
  }
}

function toggleShow(id) {
  showFull[id] = !showFull[id]
}

async function copyCode(c) {
  copyingId.value = c.id
  try {
    await navigator.clipboard.writeText(c.code)
  } catch(e) {
    // fallback - just show the code
    showFull[c.id] = true
  }
  setTimeout(() => { copyingId.value = null }, 1500)
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', { month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' })
}

onMounted(loadCodes)
</script>

<style scoped>
.page { padding: 24px; max-width: 900px; margin: 0 auto }
.page-header { margin-bottom: 24px }
.page-header h1 { font-size: 22px; font-weight: 700 }
.subtitle { color: var(--text-muted); font-size: 13px; margin-top: 4px }
.card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 20px }
.code-card { position: relative; border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; width: 200px; background: var(--bg) }
.code-card.copying { border-color: var(--accent) }
.code-card.used { opacity: .55 }
.code-text { font-family: monospace; font-size: 15px; letter-spacing: 1px; margin-bottom: 4px; color: var(--accent); font-weight: 600 }
.code-masked { font-family: monospace; font-size: 14px; letter-spacing: 2px; color: var(--text-muted); margin-bottom: 4px }
.code-meta { font-size: 11px; color: var(--text-muted) }
.code-used { font-size: 11px; color: var(--text-muted); margin-top: 2px }
.code-new { font-size: 11px; color: var(--success); margin-top: 2px }
.code-actions { position: absolute; top: 8px; right: 8px; display: flex; gap: 4px }
.btn-sm { background: none; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; padding: 2px 6px; font-size: 14px }
.btn-sm:hover { background: var(--hover) }
.btn-sm:disabled { opacity: .5; cursor: default }
.error-msg { padding: 10px; margin-top: 12px; background: #fef2f2; color: var(--error); border-radius: 6px; font-size: 13px }
</style>
