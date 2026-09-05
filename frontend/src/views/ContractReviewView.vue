<template>
  <div>
    <div class="page-head">
      <div>
        <div class="page-title">合同审查</div>
        <div class="page-sub">粘贴或上传合同，AI 标注风险条款并给出修改建议</div>
      </div>
    </div>

    <div class="review-layout">
      <!-- 输入区 -->
      <div style="display:flex;flex-direction:column;gap:20px;min-width:0">
        <div class="card">
          <div class="card-head"><span class="card-title">1 · 输入合同</span></div>
          <div class="card-body">
            <div class="tabs" style="margin-bottom:14px">
              <button :class="{ active: mode === 'text' }" @click="mode = 'text'" class="tab">粘贴文本</button>
              <button :class="{ active: mode === 'file' }" @click="mode = 'file'" class="tab">上传文件</button>
            </div>

            <div v-if="mode === 'text'">
              <textarea v-model="content" placeholder="在此粘贴合同全文或关键条款..." class="review-textarea"></textarea>
            </div>
            <div v-else class="upload-zone">
              <label class="upload-label">
                <input type="file" accept=".txt,.pdf,.docx,.doc" @change="handleFile" hidden />
                <div v-if="!fileName" class="upload-hint">
                  <div style="font-size:34px;margin-bottom:10px">📄</div>
                  <div style="font-weight:600;color:var(--ink-700)">点击选择合同文件</div>
                  <div style="font-size:12px;margin-top:6px">支持 PDF / Word / TXT</div>
                </div>
                <div v-else class="upload-done">{{ fileName }}</div>
              </label>
            </div>

            <div class="review-actions">
              <select v-model="reviewType" class="form-select" style="flex:1">
                <option value="full">全面审查</option>
                <option value="clauses_only">仅关键条款</option>
                <option value="risks_only">仅风险点</option>
              </select>
              <button @click="doReview" :disabled="loading || !canSubmit" class="btn btn-gold">
                {{ loading ? '审查中...' : '开始审查' }}
              </button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-head"><span class="card-title">审查说明</span></div>
          <div class="card-body">
            <ul class="tips">
              <li>逐条核对 <b>十二类固定风险清单</b>，标注《民法典》依据</li>
              <li>长合同自动<b>分块审查 + 合并汇总</b>，避免后半截漏审</li>
              <li>报告末尾附<b>条款覆盖自检</b>，未覆盖条款会点名提示</li>
              <li>引用条号经<b>权威法条库核验</b>，虚构条号会被标出</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 结果区 -->
      <div style="min-width:0;display:flex;flex-direction:column">
        <div class="sec-head"><span class="sec-mark">壹</span><span class="sec-title">审查报告</span></div>
        <div class="card review-output">
          <div v-if="loading"><div class="spinner"><div></div></div>AI 正在分析合同...</div>
          <div v-else-if="result" class="markdown-body" v-html="renderedResult"></div>
          <div v-else class="empty-hint">
            <div style="font-size:40px;margin-bottom:12px">📋</div>
            <div>粘贴或上传合同文本，点击"开始审查"</div>
          </div>
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
.review-layout { display: grid; grid-template-columns: 1fr 1.1fr; gap: 20px; align-items: start; }
@media (max-width: 900px) { .review-layout { grid-template-columns: 1fr } }
.review-textarea {
  width: 100%; height: 300px; border: 1px solid var(--line-strong);
  border-radius: 10px; padding: 14px; font-size: 13px; line-height: 1.7;
  resize: vertical; background: #fff; color: var(--text); font-family: inherit; outline: none;
}
.review-textarea:focus { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(47,107,213,.15); }
.upload-zone { margin-bottom: 12px }
.upload-label { cursor: pointer; display: block }
.upload-hint {
  border: 2px dashed var(--line-strong); border-radius: 12px; padding: 40px 20px;
  text-align: center; color: var(--muted); font-size: 13px; line-height: 1.8; background: var(--paper-2);
}
.upload-done {
  padding: 16px; background: var(--paper-2); border: 1px solid var(--line-strong);
  border-radius: 10px; text-align: center; font-size: 13px; color: var(--ink-700); font-weight: 600;
}
.review-actions { display: flex; gap: 8px; margin-top: 14px }
.review-output { flex: 1; overflow-y: auto; line-height: 1.8; padding: 20px; min-height: 300px; }
.spinner { display: flex; align-items: center; gap: 12px; padding: 60px 0; justify-content: center; color: var(--muted); font-size: 14px }
.spinner div { width: 20px; height: 20px; border: 2px solid var(--line-strong); border-top-color: var(--gold); border-radius: 50%; animation: spin .8s linear infinite }
@keyframes spin { to { transform: rotate(360deg) } }
.empty-hint { text-align: center; padding: 80px 20px; color: var(--muted); font-size: 14px }
.markdown-body :deep(h2) { font-family: var(--serif); font-size: 16px; margin: 16px 0 8px; color: var(--ink) }
.markdown-body :deep(h3) { font-size: 14px; margin: 12px 0 6px; color: var(--ink) }
.markdown-body :deep(li) { font-size: 13px; color: var(--text); margin: 4px 0; padding-left: 4px }
.markdown-body :deep(b) { color: var(--ink) }
.markdown-body :deep(ul) { padding-left: 20px }
</style>
