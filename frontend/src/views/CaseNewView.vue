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

        <!-- 原告详细信息 -->
        <div class="p-3 bg-orange-50 rounded-lg border border-orange-100">
          <details>
            <summary class="text-sm text-orange-700 cursor-pointer font-medium">原告详细信息（选填，生成文书时会自动填入）</summary>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3">
              <div><label class="text-xs text-gray-500">性别</label><select v-model="pInfo.gender" class="input-field text-sm"><option value="">请选择</option><option>男</option><option>女</option></select></div>
              <div><label class="text-xs text-gray-500">出生日期</label><input v-model="pInfo.birth" type="text" placeholder="如 1985年3月15日" class="input-field text-sm" /></div>
              <div><label class="text-xs text-gray-500">民族</label><input v-model="pInfo.ethnicity" type="text" placeholder="如 汉族" class="input-field text-sm" /></div>
              <div class="sm:col-span-2"><label class="text-xs text-gray-500">身份证号</label><input v-model="pInfo.id_card" type="text" placeholder="身份证号码" class="input-field text-sm" /></div>
              <div><label class="text-xs text-gray-500">电话</label><input v-model="pInfo.phone" type="text" placeholder="手机号" class="input-field text-sm" /></div>
              <div class="sm:col-span-3"><label class="text-xs text-gray-500">住址</label><input v-model="pInfo.address" type="text" placeholder="详细住址" class="input-field text-sm" /></div>
            </div>
          </details>
        </div>

        <!-- 被告详细信息 -->
        <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
          <details>
            <summary class="text-sm text-gray-600 cursor-pointer font-medium">被告详细信息（选填）</summary>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3">
              <div><label class="text-xs text-gray-500">法定代表人</label><input v-model="dInfo.legal_rep" type="text" placeholder="法人代表" class="input-field text-sm" /></div>
              <div><label class="text-xs text-gray-500">电话</label><input v-model="dInfo.phone" type="text" placeholder="联系电话" class="input-field text-sm" /></div>
              <div class="sm:col-span-2"><label class="text-xs text-gray-500">住所地</label><input v-model="dInfo.address" type="text" placeholder="被告地址" class="input-field text-sm" /></div>
            </div>
          </details>
        </div>

        <div>
          <label class="form-label">管辖法院</label>
          <input v-model="form.court_name" type="text" placeholder="如 XX市XX区人民法院" class="input-field" />
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
  court_name: '',
})

const pInfo = reactive({ gender: '', birth: '', ethnicity: '', id_card: '', phone: '', address: '' })
const dInfo = reactive({ legal_rep: '', phone: '', address: '' })

async function handleSubmit() {
  error.value = ''
  if (!form.case_type || !form.plaintiff || !form.defendant) {
    error.value = '请填写必填字段'
    return
  }

  submitting.value = true
  try {
    const payload = { ...form, plaintiff_detail: JSON.stringify(pInfo), defendant_detail: JSON.stringify(dInfo) }
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
