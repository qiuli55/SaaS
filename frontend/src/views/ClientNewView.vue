<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.back()" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <h1 class="text-2xl font-bold text-gray-800">添加客户</h1>
    </div>

    <div class="card max-w-3xl">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">姓名 <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" placeholder="客户姓名" class="input-field" required />
          </div>
          <div>
            <label class="form-label">手机号</label>
            <input v-model="form.phone" type="text" placeholder="手机号码" class="input-field" />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">微信</label>
            <input v-model="form.wechat" type="text" placeholder="微信号" class="input-field" />
          </div>
          <div>
            <label class="form-label">身份证号</label>
            <input v-model="form.id_card" type="text" placeholder="身份证号码" class="input-field" />
          </div>
        </div>

        <div>
          <label class="form-label">所在公司</label>
          <input v-model="form.company" type="text" placeholder="公司名称" class="input-field" />
        </div>

        <div>
          <label class="form-label">标签</label>
          <div class="flex flex-wrap gap-2 mb-2">
            <button type="button" v-for="t in presetTags" :key="t" @click="toggleTag(t)" class="px-2 py-1 text-xs rounded-full border transition-colors" :class="selectedTags.includes(t) ? 'bg-primary-100 border-primary-400 text-primary-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'">{{ t }}</button>
          </div>
          <input v-model="customTag" @keydown.enter.prevent="addCustomTag" type="text" placeholder="输入自定义标签后回车" class="input-field text-sm" />
        </div>

        <div>
          <label class="form-label">备注</label>
          <textarea v-model="form.remark" rows="3" placeholder="客户备注信息" class="input-field"></textarea>
        </div>

        <div v-if="error" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{{ error }}</div>

        <div class="flex justify-end space-x-3 pt-2">
          <button type="button" @click="$router.back()" class="btn-secondary">取消</button>
          <button type="submit" class="btn-primary" :disabled="submitting">
            {{ submitting ? '添加中...' : '添加客户' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const submitting = ref(false)
const error = ref('')
const presetTags = ['VIP客户', '风险客户', '企业客户', '个人客户', '长期合作', '新客户']
const selectedTags = ref([])
const customTag = ref('')

const form = reactive({
  name: '',
  phone: '',
  wechat: '',
  id_card: '',
  company: '',
  remark: '',
})

function toggleTag(tag) {
  const idx = selectedTags.value.indexOf(tag)
  if (idx >= 0) selectedTags.value.splice(idx, 1)
  else selectedTags.value.push(tag)
}

function addCustomTag() {
  const t = customTag.value.trim()
  if (t && !selectedTags.value.includes(t)) {
    selectedTags.value.push(t)
  }
  customTag.value = ''
}

async function handleSubmit() {
  error.value = ''
  if (!form.name) {
    error.value = '请填写客户姓名'
    return
  }

  submitting.value = true
  try {
    const payload = { ...form, tags: JSON.stringify(selectedTags.value) }
    const res = await api.post('/clients', payload)
    router.push(`/clients/${res.data.data.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || '添加失败'
  } finally {
    submitting.value = false
  }
}
</script>
