<template>
  <div class="page-container">
    <PageHeader title="评估报告" subtitle="查看数据质量评估结果" />

    <div class="report-toolbar m3-card">
      <el-select
        v-model="selectedTaskId"
        placeholder="选择任务查看报告"
        clearable
        style="width: 320px"
        size="large"
        @change="onTaskChange"
      >
        <el-option v-for="t in tasks" :key="t.id" :label="t.name" :value="t.id" />
      </el-select>
      <div v-if="report" class="toolbar-actions">
        <el-button @click="download('html')"><el-icon><Download /></el-icon>下载 HTML</el-button>
        <el-button @click="download('json')"><el-icon><Download /></el-icon>下载 JSON</el-button>
        <el-button @click="download('pdf')"><el-icon><Download /></el-icon>下载 PDF</el-button>
      </div>
    </div>

    <template v-if="report">
      <!-- 一、执行摘要：总评分 + 等级 -->
      <div class="m3-card report-score-card">
        <h3 class="m3-card-header">一、执行摘要</h3>
        <div class="score-row">
          <div ref="gaugeRef" class="gauge-chart" />
          <div class="score-info">
            <div class="total-score">
              <span class="score-value">{{ report.quality_rate ?? reportSummaryRate }}<small>分</small></span>
              <span class="grade-tag" :class="gradeClass">{{ report.quality_grade ?? reportSummaryGrade }}</span>
            </div>
            <p class="score-desc">
              总检查项 {{ report.summary?.total ?? 0 }} 项，通过
              <span class="status-passed">{{ report.summary?.passed ?? 0 }}</span> 项，失败
              <span class="status-failed">{{ report.summary?.failed ?? 0 }}</span> 项。
            </p>
          </div>
        </div>
      </div>

      <!-- 二、各样板得分 -->
      <div v-if="report.sample_scores?.length" class="m3-card report-samples">
        <h3 class="m3-card-header">二、参与评估的数据样板及得分</h3>
        <div class="samples-layout">
          <div ref="barChartRef" class="bar-chart" />
          <el-table :data="report.sample_scores" stripe class="sample-table">
            <el-table-column prop="name" label="数据样板" min-width="180" />
            <el-table-column prop="score" label="得分" width="100" align="center">
              <template #default="{ row }">
                <span :class="row.score >= 95 ? 'score-优' : row.score >= 80 ? 'score-良' : row.score >= 60 ? 'score-中' : 'score-差'">
                  {{ row.score }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="grade" label="等级" width="80" align="center" />
            <el-table-column prop="passed" label="通过" width="80" align="center">
              <template #default="{ row }"><span class="status-passed">{{ row.passed }}</span></template>
            </el-table-column>
            <el-table-column prop="failed" label="失败" width="80" align="center">
              <template #default="{ row }"><span class="status-failed">{{ row.failed }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 六维雷达图 -->
      <div v-if="indicatorRadarData.length" class="m3-card report-radar">
        <h3 class="m3-card-header">三、六维指标分析</h3>
        <div ref="radarRef" class="radar-chart" />
      </div>

      <!-- 明细 -->
      <div class="m3-card report-details">
        <h3 class="m3-card-header">四、检查明细</h3>
        <el-table :data="report.details || []" stripe>
          <el-table-column v-if="hasMultipleSources" prop="datasource" label="数据源" width="160" />
          <el-table-column prop="rule_type" label="规则类型" width="200" />
          <el-table-column prop="column" label="列" width="140">
            <template #default="{ row }">{{ row.column || `${row.column_a || ''} / ${row.column_b || ''}` }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'passed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
                {{ row.status === 'passed' ? '通过' : row.status === 'failed' ? '失败' : row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="消息" min-width="200" />
        </el-table>
      </div>
    </template>
    <el-empty v-else-if="!loading" description="请选择任务或先执行评估" :image-size="120" />
    <div v-else class="loading-wrap">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader.vue'

const route = useRoute()
const loading = ref(false)
const tasks = ref<{ id: string; name: string }[]>([])
const report = ref<{
  summary?: { total: number; passed: number; failed: number; by_datasource?: Record<string, { total: number; passed: number; failed: number }> }
  details?: Record<string, unknown>[]
  quality_grade?: string
  quality_rate?: number
  sample_scores?: { name: string; score: number; grade: string; passed: number; failed: number }[]
  indicators?: Record<string, { total: number; passed: number; failed: number }>
  datasource_names?: Record<string, string>
} | null>(null)

const gaugeRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const radarRef = ref<HTMLElement>()
let gaugeChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null

const reportSummaryRate = computed(() => {
  const s = report.value?.summary
  if (!s?.total) return 0
  return Math.round((s.passed / s.total) * 1000) / 10
})
const reportSummaryGrade = computed(() => {
  const rate = reportSummaryRate.value / 100
  if (rate >= 0.95) return '优'
  if (rate >= 0.8) return '良'
  if (rate >= 0.6) return '中'
  return '差'
})
const gradeClass = computed(() => {
  const g = report.value?.quality_grade ?? reportSummaryGrade.value
  return `grade-${g}`
})

const indicatorRadarData = computed(() => {
  const ind = report.value?.indicators
  if (!ind || !Object.keys(ind).length) return []
  return Object.entries(ind).map(([name, s]) => ({
    name,
    value: s.total ? Math.round((s.passed / s.total) * 1000) / 10 : 0,
  }))
})

function toLegacyReport(raw: { summary?: { total?: number; passed?: number; failed?: number; by_datasource?: Record<string, { total: number; passed: number; failed: number }> }; details?: unknown[]; datasource_names?: Record<string, string> }) {
  const s = raw.summary || {}
  const total = s.total ?? 0
  const passed = s.passed ?? 0
  const rate = total ? (passed / total) * 100 : 0
  const grade = rate >= 95 ? '优' : rate >= 80 ? '良' : rate >= 60 ? '中' : '差'
  const names = raw.datasource_names || {}
  const byDs = s.by_datasource || {}
  const sample_scores = Object.entries(byDs).map(([id, st]) => ({
    datasource_id: id,
    name: names[id] || id,
    total: st.total,
    passed: st.passed,
    failed: st.failed,
    score: st.total ? Math.round((st.passed / st.total) * 1000) / 10 : 0,
    grade: st.total ? (st.passed / st.total >= 0.95 ? '优' : st.passed / st.total >= 0.8 ? '良' : st.passed / st.total >= 0.6 ? '中' : '差') : '差',
  }))
  return {
    ...raw,
    quality_rate: Math.round(rate * 10) / 10,
    quality_grade: grade,
    sample_scores,
    indicators: {} as Record<string, { total: number; passed: number; failed: number }>,
    details: raw.details || [],
  }
}

const hasMultipleSources = computed(
  () => report.value?.summary?.by_datasource && Object.keys(report.value.summary.by_datasource).length > 1
)

const routeTaskId = computed(() => route.params.taskId as string)
const selectedTaskId = ref('')
const taskId = computed(() => selectedTaskId.value || routeTaskId.value || '')

async function loadTasks() {
  const { data } = await api.getTasks()
  tasks.value = data
  if (routeTaskId.value && !selectedTaskId.value) selectedTaskId.value = routeTaskId.value
  if (!selectedTaskId.value && data.length) selectedTaskId.value = data[0].id
}

async function load() {
  if (!taskId.value) {
    report.value = null
    return
  }
  loading.value = true
  try {
    const { data } = await api.getReportCn(taskId.value)
    report.value = data
    await nextTick()
    renderCharts()
  } catch (e: unknown) {
    const err = e as { response?: { status?: number } }
    if (err.response?.status === 400 || err.response?.status === 404) {
      try {
        const { data } = await api.getReport(taskId.value)
        report.value = toLegacyReport(data)
        await nextTick()
        renderCharts()
      } catch {
        report.value = null
      }
    } else {
      report.value = null
    }
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  const r = report.value
  if (!r) return
  const rate = r.quality_rate ?? reportSummaryRate.value
  if (gaugeRef.value) {
    if (gaugeChart) gaugeChart.dispose()
    gaugeChart = echarts.init(gaugeRef.value)
    gaugeChart.setOption({
      series: [{
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        splitNumber: 5,
        itemStyle: { color: rate >= 95 ? '#2e7d32' : rate >= 80 ? '#1976d2' : rate >= 60 ? '#ed6c02' : '#c62828' },
        progress: { show: true, width: 12 },
        pointer: { show: false },
        axisLine: { lineStyle: { width: 12 } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        title: { show: false },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, 0],
          formatter: '{value}',
          fontSize: 28,
          fontWeight: 600,
          color: '#333',
        },
        data: [{ value: rate }],
      }],
    })
  }
  if (r.sample_scores?.length && barChartRef.value) {
    if (barChart) barChart.dispose()
    barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: r.sample_scores.map((s) => s.name), axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', min: 0, max: 100, name: '得分' },
      series: [{ type: 'bar', data: r.sample_scores.map((s) => s.score), itemStyle: {
        color: (params: { data: number }) =>
          params.data >= 95 ? '#2e7d32' : params.data >= 80 ? '#1976d2' : params.data >= 60 ? '#ed6c02' : '#c62828',
      } }],
    })
  }
  if (indicatorRadarData.value.length && radarRef.value) {
    if (radarChart) radarChart.dispose()
    radarChart = echarts.init(radarRef.value)
    const indData = indicatorRadarData.value
    radarChart.setOption({
      tooltip: {},
      radar: {
        indicator: indData.map((d) => ({ name: d.name, max: 100 })),
      },
      series: [{
        type: 'radar',
        data: [{ value: indData.map((d) => d.value), name: '六维得分' }],
        areaStyle: { opacity: 0.3 },
      }],
    })
  }
}

function onTaskChange() {
  if (selectedTaskId.value) {
    history.replaceState(null, '', `/reports/${selectedTaskId.value}`)
  }
  load()
}

async function download(format: 'html' | 'json' | 'pdf') {
  if (!taskId.value || !report.value) return
  try {
    const { data } = await api.downloadReport(taskId.value, format)
    const url = URL.createObjectURL(data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report-${taskId.value}.${format}`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch {
    ElMessage.error('下载失败')
  }
}

onMounted(async () => {
  await loadTasks()
  if (routeTaskId.value) selectedTaskId.value = routeTaskId.value
  load()
})
watch(taskId, load)
</script>

<style scoped>
.report-toolbar {
  display: flex;
  align-items: center;
  gap: var(--md-spacing-md);
  margin-bottom: var(--md-spacing-lg);
}

.toolbar-actions {
  display: flex;
  gap: var(--md-spacing-sm);
}

.report-score-card { margin-bottom: var(--md-spacing-lg); }
.score-row { display: flex; align-items: center; gap: var(--md-spacing-xl); flex-wrap: wrap; }
.gauge-chart { width: 180px; height: 180px; flex-shrink: 0; }
.score-info { flex: 1; min-width: 200px; }
.total-score { display: flex; align-items: baseline; gap: var(--md-spacing-md); margin-bottom: 8px; }
.score-value { font-size: 2.5rem; font-weight: 700; color: var(--md-sys-color-primary); }
.score-value small { font-size: 1rem; font-weight: 400; margin-left: 2px; }
.grade-tag { padding: 4px 12px; border-radius: 4px; font-weight: 600; }
.grade-优 { background: #e8f5e9; color: #2e7d32; }
.grade-良 { background: #e3f2fd; color: #1976d2; }
.grade-中 { background: #fff3e0; color: #ed6c02; }
.grade-差 { background: #ffebee; color: #c62828; }
.score-desc { color: #666; margin: 0; }
.report-samples { margin-bottom: var(--md-spacing-lg); }
.samples-layout { display: flex; flex-wrap: wrap; gap: var(--md-spacing-lg); }
.bar-chart { width: 100%; min-width: 300px; height: 240px; }
.sample-table { flex: 1; min-width: 320px; }
.score-优 { color: #2e7d32; font-weight: 600; }
.score-良 { color: #1976d2; font-weight: 600; }
.score-中 { color: #ed6c02; font-weight: 600; }
.score-差 { color: #c62828; font-weight: 600; }
.report-radar { margin-bottom: var(--md-spacing-lg); }
.radar-chart { width: 100%; height: 320px; }

.report-details {
  margin-bottom: var(--md-spacing-lg);
}

.status-passed {
  color: var(--md-sys-color-success);
  font-weight: 600;
}

.status-failed {
  color: var(--md-sys-color-error);
  font-weight: 600;
}

.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 48px;
  color: #6b7280;
}
</style>
