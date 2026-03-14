<!--
  文件名: Dashboard.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 仪表盘，数据质量概览与快捷入口
-->
<template>
  <div class="page-container">
    <PageHeader title="仪表盘" subtitle="数据质量概览与快捷入口" />

    <section class="stats-grid">
      <div
        v-for="s in statItems"
        :key="s.key"
        class="stat-card"
        @click="s.path && $router.push(s.path)"
      >
        <span class="stat-value">{{ s.value }}</span>
        <span class="stat-label">{{ s.label }}</span>
      </div>
    </section>

    <section class="dashboard-grid">
      <div class="m3-card chart-card">
        <h3 class="m3-card-header">质量概览</h3>
        <div v-if="recentScore" class="score-entry">
          <span class="score-label">总体质量得分：</span>
          <span class="score-value">{{ recentScore.rate }} 分</span>
          <span class="grade-tag" :class="`grade-${recentScore.grade}`">{{ recentScore.grade }}</span>
          <el-button link type="primary" size="small" @click="$router.push((latestReportTaskId ? `/reports/${latestReportTaskId}` : null) || (recentTasks.length ? `/reports/${recentTasks[0].id}` : '/reports'))">
            查看报告与各样板得分
          </el-button>
        </div>
        <QualityChart
          v-if="recentSummary"
          :passed="recentSummary.passed"
          :failed="recentSummary.failed"
          title="最近一次评估"
        />
        <el-empty v-else description="暂无评估数据" :image-size="80" />
      </div>
      <div class="m3-card">
        <h3 class="m3-card-header">最近任务</h3>
        <el-table :data="recentTasks" stripe max-height="220">
          <el-table-column prop="name" label="任务" show-overflow-tooltip min-width="140" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
                {{ row.status === 'completed' ? '完成' : row.status === 'failed' ? '失败' : '运行中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="$router.push(`/reports/${row.id}`)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>

    <section class="quick-actions">
      <h3 class="section-title">快捷入口</h3>
      <div class="action-cards">
        <div class="action-card" @click="$router.push('/datasources')">
          <Connection class="action-icon" />
          <div class="action-text">
            <span class="action-title">数据源管理</span>
            <span class="action-desc">配置 CSV、Excel 等数据源</span>
          </div>
        </div>
        <div class="action-card" @click="$router.push('/rules')">
          <List class="action-icon" />
          <div class="action-text">
            <span class="action-title">规则管理</span>
            <span class="action-desc">定义数据质量规则集</span>
          </div>
        </div>
        <div class="action-card" @click="$router.push('/tasks')">
          <VideoPlay class="action-icon" />
          <div class="action-text">
            <span class="action-title">执行评估</span>
            <span class="action-desc">推荐组合快速测试，或自定义数据源与规则集</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/client'
import QualityChart from '../components/QualityChart.vue'
import PageHeader from '../components/PageHeader.vue'
import { Connection, List, VideoPlay } from '@element-plus/icons-vue'

const stats = ref({ datasources: 0, rulesets: 0, tasks: 0, completed: 0 })
const recentTasks = ref<{ id: string; name: string; status: string }[]>([])
const recentSummary = ref<{ passed: number; failed: number } | null>(null)
const recentScore = ref<{ rate: number; grade: string; sampleScores?: { name: string; score: number }[] } | null>(null)
const latestReportTaskId = ref<string | null>(null)

const statItems = computed(() => [
  { key: 'ds', value: stats.value.datasources, label: '数据源', path: '/datasources' },
  { key: 'rs', value: stats.value.rulesets, label: '规则集', path: '/rules' },
  { key: 'tasks', value: stats.value.tasks, label: '任务总数', path: '/tasks' },
  { key: 'done', value: stats.value.completed, label: '已完成', path: '/reports' },
  ...(recentScore.value ? [{ key: 'score', value: `${recentScore.value.rate}`, label: '最近质量得分', path: latestReportTaskId.value ? `/reports/${latestReportTaskId.value}` : '/reports' }] : []),
])

onMounted(async () => {
  try {
    const [ds, rs, ts] = await Promise.all([
      api.getDatasources(),
      api.getRuleSets(),
      api.getTasks(),
    ])
    stats.value = {
      datasources: ds.data.length,
      rulesets: rs.data.length,
      tasks: ts.data.length,
      completed: ts.data.filter((t) => t.status === 'completed').length,
    }
    recentTasks.value = ts.data.slice(0, 5)
    if (ts.data.length) {
      const latest = ts.data.find((t) => t.status === 'completed') || ts.data[0]
      const { data } = await api.getTask(latest.id)
      if (data.result?.summary) {
        recentSummary.value = data.result.summary
      }
      latestReportTaskId.value = latest.id
      try {
        const cnRes = await api.getReportCn(latest.id)
        const r = cnRes.data as { quality_rate?: number; quality_grade?: string; sample_scores?: { name: string; score: number }[] }
        if (r.quality_rate != null) {
          recentScore.value = {
            rate: r.quality_rate,
            grade: r.quality_grade || '',
            sampleScores: r.sample_scores,
          }
        }
      } catch {
        const s = data.result?.summary
        if (s?.total) {
          const rate = Math.round((s.passed / s.total) * 1000) / 10
          const grade = rate >= 95 ? '优' : rate >= 80 ? '良' : rate >= 60 ? '中' : '差'
          recentScore.value = { rate, grade }
        }
      }
    }
  } catch {
    /* ignore */
  }
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--md-spacing-md);
  margin-bottom: var(--md-spacing-xl);
}

.stat-card {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-sys-shape-corner-medium);
  padding: var(--md-spacing-lg);
  box-shadow: var(--md-sys-elevation-1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.stat-card:hover {
  box-shadow: var(--md-sys-elevation-2);
  transform: translateY(-2px);
}

.stat-value {
  font: 500 2rem/2.5rem 'Noto Sans SC', 'Roboto', sans-serif;
  color: var(--md-sys-color-primary);
  display: block;
}

.stat-label {
  font: var(--md-typescale-body-medium);
  color: #6b7280;
  margin-top: var(--md-spacing-xs);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--md-spacing-lg);
  margin-bottom: var(--md-spacing-xl);
}

.chart-card {
  min-height: 280px;
}
.score-entry {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
}
.score-label { color: #666; }
.score-value { font-weight: 600; font-size: 1.1rem; color: var(--md-sys-color-primary); }
.grade-tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.grade-优 { background: #e8f5e9; color: #2e7d32; }
.grade-良 { background: #e3f2fd; color: #1976d2; }
.grade-中 { background: #fff3e0; color: #ed6c02; }
.grade-差 { background: #ffebee; color: #c62828; }

.quick-actions {
  margin-top: var(--md-spacing-lg);
}

.section-title {
  font: var(--md-typescale-title-large);
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--md-spacing-md) 0;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--md-spacing-md);
}

.action-card {
  display: flex;
  align-items: center;
  gap: var(--md-spacing-md);
  padding: var(--md-spacing-lg);
  background: var(--md-sys-color-surface);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: var(--md-sys-elevation-1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-card:hover {
  box-shadow: var(--md-sys-elevation-2);
  background: var(--md-sys-color-primary-container);
}

.action-icon {
  width: 40px;
  height: 40px;
  color: var(--md-sys-color-primary);
}

.action-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.action-title {
  font: var(--md-typescale-title-medium);
  font-weight: 600;
  color: #111827;
}

.action-desc {
  font: var(--md-typescale-body-medium);
  color: #6b7280;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .action-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
