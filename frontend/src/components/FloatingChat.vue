<template>
  <Teleport to="body">
    <!-- 悬浮按钮 -->
    <button v-if="!open" class="float-btn" @click="openChat" title="AI 法律助手">
      <svg width="22" height="22" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 2l6 2v5c0 4-3 6-6 8-3-2-6-4-6-8V4l6-2z"/><path d="M6.5 9l2 2 3.5-4"/></svg>
    </button>

    <!-- 弹窗 -->
    <div v-if="open" class="float-panel" :style="panelStyle" @mousedown="bringToFront">
      <!-- 标题栏（可拖拽） -->
      <div class="float-bar" @mousedown.prevent="startDrag">
        <span class="float-title">🤖 AI 法律助手</span>
        <div class="float-actions">
          <button class="float-action" @click="toggleSize" :title="expanded ? '缩小' : '放大'">
            <svg v-if="expanded" width="16" height="16" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12v3h3"/><path d="M15 6V3h-3"/><path d="M13 3l-4 4"/><path d="M5 15l4-4"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9v5h5"/><path d="M15 9V4h-5"/></svg>
          </button>
          <button class="float-action" @click.stop="open = false" title="最小化">—</button>
          <button class="float-action float-close" @click.stop="open = false" title="关闭">✕</button>
        </div>
      </div>

      <!-- 消息区 -->
      <div class="float-msgs" ref="msgBox" @scroll="onScroll">
        <div v-if="messages.length === 0" class="float-welcome">
          <div class="float-welcome-text">有什么法律问题想问我？</div>
          <div class="float-hints">
            <button v-for="h in quickHints" :key="h" class="float-hint" @click="send(h)">{{ h }}</button>
          </div>
        </div>
        <div v-for="(m, i) in messages" :key="i" :class="'float-msg ' + m.role">
          <div class="float-bubble">{{ m.content }}</div>
        </div>
        <div v-if="loading" class="float-msg assistant">
          <div class="float-bubble float-typing">思考中...</div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="float-input">
        <textarea
          v-model="input"
          class="float-textarea"
          placeholder="输入问题..."
          rows="1"
          @keydown.enter.exact.prevent="send()"
          :disabled="loading"
          @input="resizeTextarea"
        ></textarea>
        <button class="float-send" @click="send()" :disabled="loading || !input.trim()">➤</button>
      </div>

      <!-- 拖拽结构 -->
      <div v-if="dragging" class="float-drag-cover" @mousemove="onDrag" @mouseup="endDrag" @mouseleave="endDrag"></div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, nextTick, watch } from 'vue'
import api from '../api'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref([])
const msgBox = ref(null)
const expanded = ref(false)
const dragging = ref(false)
const dragStart = reactive({ x: 0, y: 0 })
const panelPos = reactive({ x: 0, y: 0 })
const panelStyle = ref({})

const quickHints = ['起诉条件是什么？', '如何计算违约金？', '劳动争议仲裁流程', '离婚财产怎么分割？']

function openChat() {
  open.value = true
  // 默认位置：右下角
  panelPos.x = window.innerWidth - 420
  panelPos.y = window.innerHeight - 520
  updateStyle()
  nextTick(() => scrollToBottom())
}

function toggleSize() {
  expanded.value = !expanded.value
  updateStyle()
}

function updateStyle() {
  const w = expanded.value ? 600 : 380
  const h = expanded.value ? 520 : 480
  // 限制不超出屏幕
  const x = Math.max(0, Math.min(panelPos.x, window.innerWidth - w))
  const y = Math.max(0, Math.min(panelPos.y, window.innerHeight - h))
  panelStyle.value = {
    position: 'fixed',
    left: x + 'px',
    top: y + 'px',
    width: w + 'px',
    height: h + 'px',
    zIndex: 9999,
  }
}

function startDrag(e) {
  dragging.value = true
  dragStart.x = e.clientX - panelPos.x
  dragStart.y = e.clientY - panelPos.y
}

function onDrag(e) {
  panelPos.x = e.clientX - dragStart.x
  panelPos.y = e.clientY - dragStart.y
  updateStyle()
}

function endDrag() {
  dragging.value = false
}

function bringToFront() {
  panelStyle.value = { ...panelStyle.value, zIndex: 9999 }
}

async function send(msg) {
  const text = (msg || input.value).trim()
  if (!text || loading.value) return
  input.value = ''

  messages.value.push({ role: 'user', content: text })
  scrollToBottom()
  loading.value = true

  try {
    const history = messages.value.slice(-21, -1).map(m => ({ role: m.role, content: m.content }))
    const res = await api.post('/chat/send', { message: text, history })
    messages.value.push({ role: 'assistant', content: res.data.reply })
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '连接 AI 失败，请稍后重试。' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

function resizeTextarea(e) {
  e.target.style.height = 'auto'
  e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px'
}

function onScroll() {}
</script>

<style>
.float-btn {
  position: fixed; bottom: 28px; right: 28px; z-index: 9998;
  width: 52px; height: 52px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--navy-600));
  color: #fff; border: none; cursor: pointer;
  box-shadow: 0 4px 16px rgba(37,99,235,.35);
  display: flex; align-items: center; justify-content: center;
  transition: transform .2s, box-shadow .2s;
}
.float-btn:hover { transform: scale(1.08); box-shadow: 0 6px 24px rgba(37,99,235,.5); }

.float-panel {
  background: #fff; border-radius: 14px;
  box-shadow: 0 8px 40px rgba(15,41,66,.18), 0 2px 8px rgba(15,41,66,.08);
  display: flex; flex-direction: column; overflow: hidden;
  border: 1px solid var(--border);
}

.float-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; background: linear-gradient(135deg, var(--navy-800), var(--navy-700));
  color: #fff; cursor: move; user-select: none; flex-shrink: 0;
}
.float-title { font-size: 13px; font-weight: 600; flex: 1; }
.float-actions { display: flex; gap: 2px; }
.float-action {
  width: 28px; height: 28px; border-radius: 6px; border: none; background: rgba(255,255,255,.1);
  color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 13px; transition: .15s;
}
.float-action:hover { background: rgba(255,255,255,.2); }
.float-close:hover { background: rgba(220,38,38,.6); }

.float-msgs {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 12px;
}

.float-welcome { text-align: center; padding: 20px 0; }
.float-welcome-text { font-size: 14px; color: var(--text-secondary); margin-bottom: 14px; }
.float-hints { display: flex; flex-direction: column; gap: 6px; }
.float-hint {
  text-align: left; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px;
  background: #fff; cursor: pointer; font-size: 12px; color: var(--text-secondary); transition: .15s;
  font-family: inherit;
}
.float-hint:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }

.float-msg { display: flex; }
.float-msg.user { justify-content: flex-end; }
.float-bubble {
  max-width: 85%; padding: 8px 12px; border-radius: 10px; font-size: 13px;
  line-height: 1.6; white-space: pre-wrap; word-break: break-word;
}
.float-msg.user .float-bubble { background: var(--accent-light); color: var(--text-primary); border-bottom-right-radius: 3px; }
.float-msg.assistant .float-bubble { background: var(--surface-alt); color: var(--text-primary); border-bottom-left-radius: 3px; }
.float-typing { color: var(--text-muted); font-style: italic; }

.float-input {
  display: flex; gap: 8px; align-items: flex-end; padding: 10px 14px;
  border-top: 1px solid var(--border); background: var(--surface-alt); flex-shrink: 0;
}
.float-textarea {
  flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px;
  font-size: 13px; font-family: inherit; resize: none; line-height: 1.4;
  outline: none; transition: border-color .15s;
  max-height: 100px;
}
.float-textarea:focus { border-color: var(--accent); }
.float-send {
  width: 34px; height: 34px; border-radius: 8px; border: none; background: var(--accent);
  color: #fff; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;
  transition: .15s; flex-shrink: 0;
}
.float-send:hover { background: var(--accent-hover); }
.float-send:disabled { opacity: .4; cursor: not-allowed; }

.float-drag-cover { position: fixed; inset: 0; z-index: 99999; }
</style>
