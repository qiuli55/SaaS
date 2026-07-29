<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">协作团队</h1>
      <button @click="showCreate = true" class="btn btn-accent btn-sm">创建团队</button>
    </div>

    <div v-if="loading" style="text-align:center;padding:64px;color:var(--text-tertiary)">加载中...</div>

    <div v-else-if="!teams.length" class="empty-state">
      <div style="font-size:48px;margin-bottom:16px">👥</div>
      <div style="font-size:15px;color:var(--text-primary);margin-bottom:8px">还没有团队</div>
      <div style="font-size:13px;color:var(--text-tertiary);margin-bottom:20px">创建团队后可以邀请其他律师协作处理案件</div>
    </div>

    <div v-else class="team-grid">
      <router-link v-for="t in teams" :key="t.id" :to="`/teams/${t.id}`" class="team-card">
        <div class="tc-header">
          <div class="tc-name">{{ t.name }}</div>
          <span class="tc-badge" :class="t.my_role === 'owner' ? 'badge-accent' : 'badge-neutral'">
            {{ t.my_role === 'owner' ? '创建者' : '成员' }}
          </span>
        </div>
        <div class="tc-desc" v-if="t.description">{{ t.description }}</div>
        <div class="tc-meta">
          <span>{{ t.members.length }} 位成员</span>
          <span>{{ t.case_count }} 个案件</span>
        </div>
        <div class="tc-avatars">
          <span v-for="m in t.members.slice(0,5)" :key="m.id" :title="m.name" class="avat">{{ (m.name||'?')[0] }}</span>
        </div>
      </router-link>
    </div>

    <!-- 创建弹窗 -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate=false">
      <div class="modal">
        <h3 class="modal-title">创建团队</h3>
        <input v-model="newName" placeholder="团队名称" class="input" />
        <textarea v-model="newDesc" placeholder="团队描述（选填）" class="input" rows="3" style="margin-top:8px"></textarea>
        <div class="modal-actions">
          <button @click="showCreate=false" class="btn btn-ghost btn-sm">取消</button>
          <button @click="doCreate" :disabled="!newName.trim()" class="btn btn-accent btn-sm">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const teams = ref([]); const loading = ref(true)
const showCreate = ref(false); const newName = ref(''); const newDesc = ref('')

onMounted(async () => {
  try { const r = await api.get('/teams'); teams.value = r.data } catch(e) { console.error(e) }
  finally { loading.value = false }
})

async function doCreate() {
  try {
    const r = await api.post('/teams', { name: newName.value, description: newDesc.value })
    showCreate.value = false; newName.value = ''; newDesc.value = ''
    router.push(`/teams/${r.data.id}`)
  } catch(e) { alert('创建失败') }
}
</script>

<style scoped>
.team-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px }
.team-card {
  background: var(--color-background-secondary); border: 1px solid var(--color-border-tertiary);
  border-radius: 12px; padding: 20px; text-decoration: none; color: inherit;
  transition: border-color .2s
}
.team-card:hover { border-color: var(--accent) }
.tc-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px }
.tc-name { font-size: 15px; font-weight: 500; color: var(--text-primary) }
.tc-badge { font-size: 11px; padding: 2px 8px; border-radius: 4px }
.badge-accent { background: var(--accent); color: #fff }
.badge-neutral { background: var(--navy-100); color: var(--navy-700) }
.tc-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5 }
.tc-meta { display: flex; gap: 16px; font-size: 12px; color: var(--text-tertiary); margin-bottom: 12px }
.tc-avatars { display: flex; gap: 4px }
.avat {
  width: 28px; height: 28px; border-radius: 50%; background: var(--navy-100);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 500; color: var(--navy-700)
}
.empty-state { text-align: center; padding: 80px 20px }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.3); display: flex; align-items: center; justify-content: center; z-index: 100 }
.modal { background: var(--color-background-primary); border-radius: 12px; padding: 24px; width: 380px; max-width: 90vw }
.modal-title { font-size: 16px; font-weight: 500; margin-bottom: 16px }
.input { width: 100%; padding: 10px 12px; border: 1px solid var(--color-border-tertiary); border-radius: 8px; font-size: 14px; background: var(--color-background-secondary); color: var(--text-primary) }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px }
</style>
