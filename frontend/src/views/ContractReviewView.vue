<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">合同审查</h1>
    </div>

    <div class="review-layout">
      <!-- 输入区 -->
      <div class="review-input">
        <div class="review-tabs">
          <button :class="{ active: mode === 'text' }" @click="mode = 'text'">粘贴文本</button>
          <button :class="{ active: mode === 'file' }" @click="mode = 'file'">上传文件</button>
        </div>

        <div v-if="mode === 'text'">
          <textarea v-model="content" placeholder="在此粘贴合同全文或关键条款..." class="review-textarea"></textarea>
        </div>
        <div v-else class="upload-zone">
          <label class="upload-label">
            <input type="file" accept=".txt,.pdf,.docx,.doc" @change="handleFile" hidden />
            <div v-if="!fileName" class="upload-hint">
              <svg width="32" height="32" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 11v4H4v-4M9 2v9M6 7l3-3 3 3"/>
              </svg>
              <span>点击上传合同文件<br/>（支持 PDF / Word / TXT）</span>
            </div>
            <div v-else class="upload-done">{{ fileName }}</div>
          </label>
        </div>

        <div class="review-actions">
          <select v-model="reviewType" class="review-select">
            <option value="full">全面审查</option>
            <option value="clauses_only">仅关键条款</option>
            <option value="risks_only">仅风险点</option>
          </select>
          <button @click="doReview" :disabled="loading || !canSubmit" class="btn btn-primary">
            {{ loading ? '审查中...' : '开始审查' }}
          </button>
        </div>
      </div>

      <!-- 结果区 -->
      <div class="review-output">
        <div v-if="loading"><div class="spinner"><div></div></div>AI 正在分析合同...</div>
        <div v-else-if="result" class="markdown-body" v-html="renderedResult"></div>
        <div v-else class="empty-hint">
          <div style="font-size:40px;margin-bottom:12px">📋</div>
          <div>粘贴或上传合同文本，点击"开始审查"</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api'

const mode = ref('text')
const content = ref('')
const reviewType = ref('full')
const loading = ref(false)
const result = ref('')
const fileName = ref('')

const canSubmit = computed(() => mode.value === 'file' ? !!fileName.value : !!content.value.trim())
const renderedResult = computed(() => {
  return result.value
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/^- (.+)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, (m) => '<ul>' + m + '</ul>')
    .replace(/\n/g, '<br/>')
})

async function handleFile(e) {
  const file = e.target.files[0]
  if (!file) return
  fileName.value = file.name
  const reader = new FileReader()
  reader.onload = (ev) => { content.value = ev.target.result }
  reader.readAsText(file)
}

async function doReview() {
  loading.value = true
  result.value = ''
  try {
    const res = await api.post('/contract/review', { content: content.value, review_type: reviewType.value })
    result.value = res.data.result
  } catch (e) {
    result.value = '审查失败：' + (e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.review-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; min-height: 70vh }
@media (max-width: 900px) { .review-layout { grid-template-columns: 1fr } }
.review-input, .review-output {
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border-tertiary);
  border-radius: 12px;
  padding: 20px;
}
.review-tabs { display: flex; gap: 4px; margin-bottom: 12px }
.review-tabs button {
  flex: 1; padding: 8px; border: 1px solid var(--color-border-tertiary);
  border-radius: 8px; background: none; cursor: pointer; font-size: 13px;
  color: var(--text-secondary);
}
.review-tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent) }
.review-textarea {
  width: 100%; height: 340px; border: 1px solid var(--color-border-tertiary);
  border-radius: 8px; padding: 14px; font-size: 13px; line-height: 1.7;
  resize: vertical; background: var(--color-background-primary); color: var(--text-primary);
}
.upload-zone { margin-bottom: 12px }
.upload-label { cursor: pointer; display: block }
.upload-hint {
  border: 2px dashed var(--color-border-secondary); border-radius: 8px; padding: 40px;
  text-align: center; color: var(--text-tertiary); font-size: 13px; line-height: 1.8
}
.upload-done {
  padding: 16px; background: #EAF3DE; border-radius: 8px; text-align: center;
  font-size: 13px; color: #3B6D11;
}
.review-actions { display: flex; gap: 8px; margin-top: 12px }
.review-select {
  flex: 1; padding: 8px 12px; border: 1px solid var(--color-border-tertiary);
  border-radius: 8px; font-size: 13px; background: var(--color-background-primary);
  color: var(--text-primary);
}
.review-output { overflow-y: auto; line-height: 1.8 }
.spinner { display: flex; align-items: center; gap: 12px; padding: 60px 0; justify-content: center; color: var(--text-secondary); font-size: 14px }
.spinner div { width: 20px; height: 20px; border: 2px solid var(--color-border-secondary); border-top-color: var(--accent); border-radius: 50%; animation: spin .8s linear infinite }
@keyframes spin { to { transform: rotate(360deg) } }
.empty-hint { text-align: center; padding: 80px 20px; color: var(--text-tertiary); font-size: 14px }
.markdown-body :deep(h2) { font-size: 16px; margin: 16px 0 8px; color: var(--text-primary) }
.markdown-body :deep(h3) { font-size: 14px; margin: 12px 0 6px; color: var(--text-primary) }
.markdown-body :deep(li) { font-size: 13px; color: var(--text-secondary); margin: 4px 0; padding-left: 4px }
.markdown-body :deep(b) { color: var(--text-primary) }
.markdown-body :deep(ul) { padding-left: 20px }
</style>
