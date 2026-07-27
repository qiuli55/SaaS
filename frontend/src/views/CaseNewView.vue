<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.back()" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <h1 class="text-2xl font-bold text-gray-800">新建案件</h1>
    </div>

    <div class="card max-w-3xl">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">案由 <span class="text-red-500">*</span></label>
            <select v-model="form.case_type" class="input-field" required>
              <option value="">请选择案由</option>
              <option>买卖合同纠纷</option>
              <option>民间借贷纠纷</option>
              <option>离婚纠纷</option>
              <option>劳动仲裁</option>
              <option>侵权责任纠纷</option>
              <option>建设工程合同纠纷</option>
              <option>租赁合同纠纷</option>
              <option>交通事故责任纠纷</option>
              <option>其他</option>
            </select>
          </div>
          <div>
            <label class="form-label">案件状态</label>
            <select v-model="form.status" class="input-field">
              <option value="进行中">进行中</option>
              <option value="待立案">待立案</option>
              <option value="已结案">已结案</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">原告/申请人 <span class="text-red-500">*</span></label>
            <input v-model="form.plaintiff" type="text" placeholder="姓名或公司名称" class="input-field" required />
          </div>
          <div>
            <label class="form-label">被告/被申请人 <span class="text-red-500">*</span></label>
            <input v-model="form.defendant" type="text" placeholder="姓名或公司名称" class="input-field" required />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">标的额（元）</label>
            <input v-model.number="form.subject_amount" type="number" placeholder="0" class="input-field" />
          </div>
          <div>
            <label class="form-label">委托日期</label>
            <input v-model="form.commission_date" type="date" class="input-field" />
          </div>
        </div>

        <div>
          <label class="form-label">案件补充描述</label>
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="案件背景、关键事实等（可选）"
            class="input-field"
          ></textarea>
        </div>

        <div v-if="error" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">
          {{ error }}
        </div>

        <div class="flex justify-end space-x-3 pt-2">
          <button type="button" @click="$router.back()" class="btn-secondary">取消</button>
          <button type="submit" class="btn-primary" :disabled="submitting">
            {{ submitting ? '创建中...' : '创建案件' }}
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

const form = reactive({
  case_type: '',
  plaintiff: '',
  defendant: '',
  subject_amount: 0,
  commission_date: '',
  description: '',
  status: '进行中',
})

async function handleSubmit() {
  error.value = ''
  if (!form.case_type || !form.plaintiff || !form.defendant) {
    error.value = '请填写必填字段'
    return
  }

  submitting.value = true
  try {
    const payload = { ...form }
    if (!payload.commission_date) delete payload.commission_date
    const res = await api.post('/cases', payload)
    router.push(`/cases/${res.data.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || '创建失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>
