<template>
  <div>
    <div class="page-header">
      <div><h1 class="page-title">日历日程</h1></div>
      <button @click="showAddModal = true" class="btn btn-accent btn-sm">+ 添加日程</button>
    </div>

    <!-- 月份切换 -->
    <div class="filter-bar">
      <button @click="prevMonth" class="btn btn-ghost btn-sm">◀</button>
      <span style="font-family:'Noto Serif SC',serif;font-size:18px;font-weight:600;color:var(--navy-900)">{{ currentYear }}年{{ currentMonth }}月</span>
      <button @click="nextMonth" class="btn btn-ghost btn-sm">▶</button>
      <button @click="goToday" class="btn btn-outline btn-sm" style="margin-left:12px">今天</button>
    </div>

    <!-- 日历网格 -->
    <div class="calendar-grid">
      <div class="calendar-header" v-for="d in ['一','二','三','四','五','六','日']" :key="d">{{ d }}</div>
      <div v-for="(day, i) in calendarDays" :key="i"
        class="calendar-cell" :class="{ 'other-month': !day.isCurrentMonth, 'today': day.isToday }"
        @click="day.isCurrentMonth && selectDate(day.date)">
        <div class="calendar-day">{{ day.day }}</div>
        <div v-for="ev in day.events" :key="ev.id"
          @click.stop="editEvent(ev)"
          class="calendar-event"
          :class="eventColor(ev.event_type)"
          :title="ev.notes">
          {{ ev.event_type }} {{ ev.notes || ev.location }}
        </div>
      </div>
    </div>

    <!-- 日程列表 -->
    <div v-if="selectedDate" class="card mt-6">
      <div class="card-header">
        <span class="card-title">{{ selectedDate }} 日程</span>
        <button @click="showAddModal=true; newEvent.event_date=selectedDate" class="btn btn-ghost btn-sm">+ 添加</button>
      </div>
      <div class="card-body">
        <div v-if="!selectedEvents.length" style="text-align:center;padding:32px;color:var(--text-muted)">当天无日程</div>
        <div v-for="ev in selectedEvents" :key="ev.id" class="file-item" style="align-items:flex-start">
          <span class="badge" :class="eventBadge(ev.event_type)" style="flex-shrink:0;margin-top:2px">{{ ev.event_type }}</span>
          <div class="file-info">
            <div class="file-name">{{ ev.notes || '无备注' }}</div>
            <div class="file-meta">{{ ev.location }} · {{ formatTime(ev.event_date) }}</div>
          </div>
          <div style="display:flex;gap:8px;flex-shrink:0">
            <button @click="toggleDone(ev)" class="btn btn-ghost btn-sm" :style="{color:ev.is_done?'var(--success)':'var(--text-muted)'}">{{ ev.is_done?'✓已完成':'标记完成' }}</button>
            <button @click="deleteEvent(ev.id)" class="btn btn-ghost btn-sm" style="color:var(--error)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal=false">
      <div class="modal">
        <div class="modal-header"><span class="modal-title">{{ editingId ? '编辑日程' : '添加日程' }}</span><button @click="showAddModal=false" class="modal-close">✕</button></div>
        <div class="modal-body">
          <div class="form-group"><label class="form-label">类型</label>
            <select v-model="newEvent.event_type" class="form-select">
              <option>开庭</option><option>举证</option><option>立案</option><option>上诉截止</option><option>待办</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">日期时间</label><input v-model="newEvent.event_date" type="datetime-local" class="form-input" /></div>
          <div class="form-group"><label class="form-label">地点</label><input v-model="newEvent.location" type="text" placeholder="如 海淀法院第3法庭" class="form-input" /></div>
          <div class="form-group"><label class="form-label">备注</label><textarea v-model="newEvent.notes" rows="3" placeholder="日程备注" class="form-textarea"></textarea></div>
        </div>
        <div class="modal-footer">
          <button @click="showAddModal=false" class="btn btn-outline">取消</button>
          <button @click="saveEvent" class="btn btn-accent">{{ editingId ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const selectedDate = ref('')
const events = ref([])
const showAddModal = ref(false)
const editingId = ref(null)
const newEvent = reactive({ event_type:'待办', event_date:'', location:'', notes:'' })

onMounted(() => fetchEvents())

async function fetchEvents() {
  const month = `${currentYear.value}-${String(currentMonth.value).padStart(2,'0')}`
  try { const r = await api.get('/schedules', { params: { month } }); events.value = r.data.data } catch{}
}

const calendarDays = computed(() => {
  const first = new Date(currentYear.value, currentMonth.value - 1, 1)
  const last = new Date(currentYear.value, currentMonth.value, 0)
  const startDay = (first.getDay() + 6) % 7
  const today = new Date().toISOString().slice(0, 10)
  const days = []
  // 上月填充
  const prevLast = new Date(currentYear.value, currentMonth.value - 1, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    const d = new Date(currentYear.value, currentMonth.value - 2, prevLast - i)
    const ds = d.toISOString().slice(0, 10)
    days.push({ day: prevLast - i, date: ds, isCurrentMonth: false, isToday: ds === today, events: eventsForDate(ds) })
  }
  // 当月
  for (let i = 1; i <= last.getDate(); i++) {
    const d = new Date(currentYear.value, currentMonth.value - 1, i)
    const ds = d.toISOString().slice(0, 10)
    days.push({ day: i, date: ds, isCurrentMonth: true, isToday: ds === today, events: eventsForDate(ds) })
  }
  // 下月填充
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const d = new Date(currentYear.value, currentMonth.value, i)
    const ds = d.toISOString().slice(0, 10)
    days.push({ day: i, date: ds, isCurrentMonth: false, isToday: ds === today, events: eventsForDate(ds) })
  }
  return days
})

function eventsForDate(date) {
  return events.value.filter(e => e.event_date?.slice(0, 10) === date)
}

const selectedEvents = computed(() => eventsForDate(selectedDate.value))

function prevMonth() { if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- } else { currentMonth.value-- }; fetchEvents() }
function nextMonth() { if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ } else { currentMonth.value++ }; fetchEvents() }
function goToday() { const n = new Date(); currentYear.value = n.getFullYear(); currentMonth.value = n.getMonth()+1; selectedDate.value = n.toISOString().slice(0,10); fetchEvents() }
function selectDate(date) { selectedDate.value = date }
function editEvent(ev) { editingId.value = ev.id; newEvent.event_type = ev.event_type; newEvent.event_date = ev.event_date; newEvent.location = ev.location; newEvent.notes = ev.notes; showAddModal.value = true }

async function saveEvent() {
  try {
    if (editingId.value) { await api.put(`/schedules/${editingId.value}`, newEvent) }
    else { await api.post('/schedules', newEvent) }
    showAddModal.value = false; editingId.value = null
    Object.assign(newEvent, { event_type:'待办', event_date:'', location:'', notes:'' })
    await fetchEvents()
  } catch(e) { alert('操作失败') }
}

async function toggleDone(ev) { try { await api.put(`/schedules/${ev.id}`, { is_done: !ev.is_done }); await fetchEvents() } catch{} }
async function deleteEvent(id) { if(!confirm('确定删除？')) return; try { await api.delete(`/schedules/${id}`); await fetchEvents() } catch{} }

function eventColor(t) { const m={开庭:'error',举证:'warning',立案:'info','上诉截止':'error',待办:'neutral'}; return m[t]||'neutral' }
function eventBadge(t) { const m={开庭:'badge badge-error',举证:'badge badge-warning',立案:'badge badge-info','上诉截止':'badge badge-error',待办:'badge badge-neutral'}; return m[t]||'badge badge-neutral' }
function formatTime(d) { return d ? new Date(d).toLocaleString('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'}) : '' }
</script>
