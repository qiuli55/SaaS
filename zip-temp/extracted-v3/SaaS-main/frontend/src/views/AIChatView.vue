<template>
  <div>
    <div class="zone-title"><span class="bar"></span><h2>AI 法律助手</h2></div>

    <div class="card" style="display:flex;flex-direction:column;height:calc(100vh - 200px);min-height:500px">
      <!-- 消息区 -->
      <div class="chat-messages" ref="msgBox">
        <div v-if="messages.length === 0" class="chat-welcome">
          <div class="chat-welcome-icon">⚖️</div>
          <div class="chat-welcome-title">AI 法律助手</div>
          <div class="chat-welcome-desc">我是您的 AI 律师助手，可以帮您解答法律问题、分析案情、提供诉讼建议。</div>
          <div class="chat-welcome-hints">
            <button v-for="h in hints" :key="h" class="chat-hint" @click="send(h)">{{ h }}</button>
          </div>
        </div>
        <div v-for="(m, i) in messages" :key="i" :class="'chat-msg ' + m.role">
          <div class="chat-avatar">{{ m.role === 'user' ? '我' : 'AI' }}</div>
          <div class="chat-bubble">{{ m.content }}</div>
        </div>
        <div v-if="loading" class="chat-msg assistant">
          <div class="chat-avatar">AI</div>
          <div class="chat-bubble chat-loading">思考中<span class="dots"></span></div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-area">
        <textarea
          v-model="input"
          class="chat-textarea"
          placeholder="输入您想咨询的法律问题…"
          rows="2"
          @keydown.enter.exact.prevent="send()"
          :disabled="loading"
        ></textarea>
        <button class="btn btn-accent" @click="send()" :disabled="loading || !input.trim()">
          <svg width="16" height="16" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 2l14 7L2 16l6-7z"/></svg>
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import api from '../api'

const input = ref('')
const loading = ref(false)
const messages = ref([])
const msgBox = ref(null)

const hints = [
  '民事诉讼的起诉条件是什么？',
  '合同纠纷中如何计算违约金？',
  '劳动争议仲裁的流程是怎样的？',
]

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
    messages.value.push({ role: 'assistant', content: '抱歉，连接 AI 服务失败，请稍后重试。' })
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
</script>

<style scoped>
.chat-messages {
  flex: 1; overflow-y: auto; padding: 24px;
  display: flex; flex-direction: column; gap: 20px;
}
.chat-welcome { text-align: center; padding: 60px 20px 30px; }
.chat-welcome-icon { font-size: 48px; margin-bottom: 16px; }
.chat-welcome-title { font-family: 'Noto Serif SC', serif; font-size: 22px; font-weight: 600; color: var(--navy-900); margin-bottom: 12px; }
.chat-welcome-desc { font-size: 14px; color: var(--text-secondary); max-width: 480px; margin: 0 auto 24px; line-height: 1.7; }
.chat-welcome-hints { display: flex; flex-direction: column; gap: 8px; max-width: 380px; margin: 0 auto; }
.chat-hint {
  width: 100%; text-align: left; padding: 12px 16px; border: 1px solid var(--border); border-radius: 8px;
  background: #fff; cursor: pointer; font-size: 13px; color: var(--text-secondary); transition: .15s;
  font-family: inherit;
}
.chat-hint:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
.chat-msg { display: flex; gap: 10px; align-items: flex-start; }
.chat-msg.user { flex-direction: row-reverse; }
.chat-avatar {
  width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center;
  justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; color: #fff;
}
.chat-msg.user .chat-avatar { background: var(--accent); }
.chat-msg.assistant .chat-avatar { background: var(--navy-600); }
.chat-bubble {
  max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 14px;
  line-height: 1.7; white-space: pre-wrap; word-break: break-word;
}
.chat-msg.user .chat-bubble { background: var(--accent-light); color: var(--text-primary); border-bottom-right-radius: 4px; }
.chat-msg.assistant .chat-bubble { background: var(--surface-alt); color: var(--text-primary); border-bottom-left-radius: 4px; }
.chat-loading { color: var(--text-muted); font-style: italic; }
.dots::after { content: ''; animation: dots 1.5s steps(4) infinite; }
@keyframes dots { 0% { content: ''; } 25% { content: '.'; } 50% { content: '..'; } 75% { content: '...'; } }
.chat-input-area {
  padding: 16px 24px; border-top: 1px solid var(--border-light);
  display: flex; gap: 12px; align-items: flex-end; background: var(--surface-alt);
  border-radius: 0 0 12px 12px;
}
.chat-textarea {
  flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px;
  font-size: 14px; font-family: inherit; resize: none; line-height: 1.5;
  outline: none; transition: border-color .15s;
}
.chat-textarea:focus { border-color: var(--accent); }
</style>
