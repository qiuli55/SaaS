<template>
  <div>
    <div class="chat-shell">
      <!-- 消息区 -->
      <div class="chat-msgs" ref="msgBox">
        <div v-if="messages.length === 0" class="chat-welcome">
          <div class="ico">⚖️</div>
          <div class="wt">Lexi</div>
          <div class="wd">我是您的 Lexi 智能助理，可以帮您解答法律问题、分析案情、提供诉讼建议。</div>
          <div class="chat-hints">
            <button v-for="h in hints" :key="h" class="chat-hint" @click="send(h)">{{ h }}</button>
          </div>
        </div>
        <div v-for="(m, i) in messages" :key="i" :class="'chat-msg ' + m.role">
          <div class="chat-ava">{{ m.role === 'user' ? '我' : 'AI' }}</div>
          <div class="chat-bubble">{{ m.content }}</div>
        </div>
        <div v-if="loading" class="chat-msg assistant">
          <div class="chat-ava">AI</div>
          <div class="chat-bubble chat-typing">思考中<span class="dots"></span></div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input">
        <textarea
          v-model="input"
          placeholder="输入您想咨询的法律问题…（Enter 发送）"
          rows="2"
          @keydown.enter.exact.prevent="send()"
          :disabled="loading"
        ></textarea>
        <button class="btn btn-gold" @click="send()" :disabled="loading || !input.trim()">
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
.dots::after { content: ''; animation: dots 1.5s steps(4) infinite; }
@keyframes dots { 0% { content: ''; } 25% { content: '.'; } 50% { content: '..'; } 75% { content: '...'; } }
</style>
