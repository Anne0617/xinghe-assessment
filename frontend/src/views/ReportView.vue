<template>
  <div>
    <div class="page-header">
      <h2>评估报告</h2>
    </div>
    <div class="search-bar">
      <select v-model="filterRisk" @change="loadResults">
        <option value="">全部风险等级</option>
        <option value="low">低风险</option>
        <option value="medium">中风险</option>
        <option value="high">高风险</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>员工</th>
            <th>任务</th>
            <th>总分</th>
            <th>得分率</th>
            <th>风险等级</th>
            <th>岗位适配度</th>
            <th>评估时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in results" :key="r.id">
            <td><strong>{{ r.employee_name || '-' }}</strong></td>
            <td>{{ r.task_name || '-' }}</td>
            <td>{{ r.total_score }} / {{ r.max_score }}</td>
            <td>{{ r.score_percent }}%</td>
            <td><span class="tag" :class="'tag-' + r.risk_level">{{ riskLabel(r.risk_level) }}</span></td>
            <td>{{ r.fit_score ?? '-' }}</td>
            <td>{{ r.generated_at?.slice(0,10) }}</td>
          </tr>
          <tr v-if="results.length === 0">
            <td colspan="7">
              <div class="empty-state"><i class="fas fa-file-alt"></i><p>暂无评估报告</p></div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page <= 1" @click="page = page - 1; loadResults()">上一页</button>
        <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="page = p; loadResults()">{{ p }}</button>
        <button :disabled="page >= totalPages" @click="page = page + 1; loadResults()">下一页</button>
        <span>共 {{ total }} 条</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const filterRisk = ref('')
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)
const results = ref([])

function riskLabel(s) {
  return { low: '低风险', medium: '中风险', high: '高风险' }[s] || s
}

async function loadResults() {
  try {
    const params = { page: page.value }
    if (filterRisk.value) params.risk = filterRisk.value
    const r = await api.get('/results/', { params })
    results.value = r.data.results || r.data
    total.value = r.data.count || results.value.length
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch (e) { console.error(e) }
}

onMounted(loadResults)
</script>
