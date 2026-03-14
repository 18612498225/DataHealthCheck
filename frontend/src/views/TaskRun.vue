<!--
  文件名: TaskRun.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 执行评估任务，推荐组合与自定义配置
-->
<template>
  <div class="page-container">
    <PageHeader title="执行评估" subtitle="选择一个或多个数据源和规则集，生成整体数据质量评估报告" />

    <div class="presets m3-card" v-if="presets.length">
      <h3 class="m3-card-header">推荐组合</h3>
      <div class="preset-btns">
        <el-button
          v-for="p in presets"
          :key="p.label"
          :type="isSelected(p) ? 'primary' : 'default'"
          @click="applyPreset(p)"
        >
          {{ p.label }}
        </el-button>
      </div>
    </div>

    <div class="task-layout">
      <div class="m3-card task-form-card">
        <h3 class="m3-card-header">新建任务</h3>
        <el-form :model="form" label-width="100px" class="task-form">
          <el-form-item label="任务名称">
            <el-input v-model="form.name" placeholder="例如：入湖前校验" />
          </el-form-item>
          <el-form-item label="数据源">
            <el-select v-model="form.datasource_ids" placeholder="可多选，生成整体评估报告" style="width: 100%" filterable multiple collapse-tags collapse-tags-tooltip>
              <el-option
                v-for="d in datasources"
                :key="d.id"
                :label="d.name"
                :value="d.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.datasource_ids.length <= 1" label="规则集">
            <el-select v-model="form.rule_set_id" placeholder="选择规则集" style="width: 100%" filterable>
              <el-option v-for="r in ruleSets" :key="r.id" :label="r.name" :value="r.id" />
            </el-select>
          </el-form-item>
          <template v-else>
            <el-form-item label="每表规则">
              <div class="ds-rule-table">
                <el-table :data="dsRuleRows" size="small" max-height="200">
                  <el-table-column prop="dsName" label="数据源" width="140" />
                  <el-table-column label="规则集">
                    <template #default="{ row }">
                      <el-select v-model="dsRuleSelections[row.datasource_id]" placeholder="选择" size="small" style="width:100%">
                        <el-option v-for="r in ruleSets" :key="r.id" :label="r.name" :value="r.id" />
                      </el-select>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-form-item>
          </template>
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="run">
              <el-icon><VideoPlay /></el-icon>
              立即执行
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <div class="m3-card task-list-card">
        <h3 class="m3-card-header">最近任务</h3>
        <el-table :data="tasks" stripe max-height="320">
          <el-table-column prop="name" label="任务" min-width="120" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
                {{ row.status === 'completed' ? '完成' : row.status === 'failed' ? '失败' : '运行中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="$router.push(`/reports/${row.id}`)">
                查看报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader.vue'

interface Ds { id: string; name: string }
interface Rs { id: string; name: string }

const router = useRouter()
const datasources = ref<Ds[]>([])
const ruleSets = ref<Rs[]>([])
const tasks = ref<{ id: string; name: string; status: string }[]>([])
const loading = ref(false)

const form = reactive({
  name: '评估任务',
  datasource_ids: [] as string[],
  rule_set_id: '',
})

const dsRuleSelections = reactive<Record<string, string>>({})

const dsRuleRows = computed(() =>
  form.datasource_ids.map((id) => ({
    datasource_id: id,
    dsName: datasources.value.find((d) => d.id === id)?.name ?? id,
    rule_set_id: dsRuleSelections[id] ?? form.rule_set_id ?? '',
  })),
)

watch(
  () => form.datasource_ids,
  (ids) => {
    ids.forEach((id) => {
      if (!(id in dsRuleSelections) && form.rule_set_id) dsRuleSelections[id] = form.rule_set_id
    })
  },
  { immediate: true },
)

const presets = computed(() => {
  const ds = datasources.value
  const rs = ruleSets.value
  const pairs: { label: string; dsMatch: (x: Ds) => boolean; rsKey: string }[] = [
    { label: '全规则通过', dsMatch: (x) => x.name.includes('all_rules_pass'), rsKey: '通用六维全覆盖' },
    { label: '良好数据', dsMatch: (x) => x.name.includes('good_data'), rsKey: '通用完整性' },
    { label: '空值检测', dsMatch: (x) => x.name.includes('nulls'), rsKey: '完整性检测' },
    { label: '重复检测', dsMatch: (x) => x.name.includes('duplicates'), rsKey: '唯一性检测' },
    { label: '员工综合', dsMatch: (x) => x.name.includes('employees'), rsKey: '人力资源数据质量' },
    { label: '日期顺序', dsMatch: (x) => x.name.includes('dates_order_sample'), rsKey: '一致性-日期顺序' },
    { label: '时效性', dsMatch: (x) => x.name.includes('timeliness_sample'), rsKey: '及时性规则集' },
    { label: '综合违规', dsMatch: (x) => x.name.includes('all_rules_violations'), rsKey: '综合违规检测' },
    { label: '日期顺序违规', dsMatch: (x) => x.name.includes('dates_order_violations'), rsKey: '一致性-日期顺序（违规' },
    { label: '时效性违规', dsMatch: (x) => x.name.includes('timeliness_violations'), rsKey: '及时性（违规' },
  ]
  return pairs
    .map((p) => {
      const d = ds.find(p.dsMatch)
      const r = rs.find((x) => x.name.includes(p.rsKey))
      if (d && r) return { label: p.label, dsId: d.id, rsId: r.id }
      return null
    })
    .filter(Boolean) as { label: string; dsId: string; rsId: string }[]
})

function isSelected(p: { dsId: string; rsId: string }) {
  if (form.datasource_ids.length !== 1 || form.datasource_ids[0] !== p.dsId) return false
  if (form.datasource_ids.length === 1) return form.rule_set_id === p.rsId
  return dsRuleRows.value.some((r) => r.datasource_id === p.dsId && r.rule_set_id === p.rsId)
}

function applyPreset(p: { label: string; dsId: string; rsId: string }) {
  form.datasource_ids = [p.dsId]
  form.rule_set_id = p.rsId
  form.name = `评估-${p.label}`
}

onMounted(async () => {
  const [ds, rs, ts] = await Promise.all([
    api.getDatasources(),
    api.getRuleSets(),
    api.getTasks(),
  ])
  datasources.value = ds.data
  ruleSets.value = rs.data
  tasks.value = ts.data
  if (ds.data.length && rs.data.length) {
    form.datasource_ids = [ds.data[0].id]
    form.rule_set_id = rs.data[0].id
    const allPass = presets.value.find((x) => x.label === '全规则通过')
    if (allPass) {
      form.datasource_ids = [allPass.dsId]
      form.rule_set_id = allPass.rsId
      form.name = '评估-全规则通过'
    }
  }
})

async function run() {
  if (!form.name || !form.datasource_ids?.length) {
    ElMessage.warning('请选择至少一个数据源')
    return
  }
  const useMapping = form.datasource_ids.length > 1
  if (useMapping) {
    const missing = form.datasource_ids.filter((id) => !dsRuleSelections[id])
    if (missing.length) {
      ElMessage.warning('请为每个数据源选择规则集')
      return
    }
  } else if (!form.rule_set_id) {
    ElMessage.warning('请选择规则集')
    return
  }
  loading.value = true
  try {
    const payload = useMapping
      ? {
          name: form.name,
          datasource_rule_mappings: form.datasource_ids.map((id) => ({
            datasource_id: id,
            rule_set_id: dsRuleSelections[id],
          })),
        }
      : {
          name: form.name,
          datasource_ids: form.datasource_ids,
          rule_set_id: form.rule_set_id,
        }
    const { data } = await api.runTask(payload)
    ElMessage.success('执行完成')
    tasks.value = [{ id: data.task_id, name: form.name, status: data.status }, ...tasks.value.filter((t) => t.id !== data.task_id)]
    router.push(`/reports/${data.task_id}`)
  } catch (e: unknown) {
    ElMessage.error((e as Error).message || '执行失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.presets {
  margin-bottom: var(--md-spacing-lg);
}

.preset-btns {
  display: flex;
  flex-wrap: wrap;
  gap: var(--md-spacing-sm);
}

.task-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--md-spacing-lg);
}

.task-form-card {
  max-width: 480px;
}

.ds-rule-table {
  width: 100%;
}

.task-form :deep(.el-form-item) {
  margin-bottom: var(--md-spacing-md);
}

@media (max-width: 900px) {
  .task-layout {
    grid-template-columns: 1fr;
  }
  .task-form-card {
    max-width: none;
  }
}
</style>
