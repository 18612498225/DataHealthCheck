<!--
  文件名: RuleSetList.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 规则集管理，增删改查、JSON 规则编辑
-->
<template>
  <div class="page-container">
    <PageHeader title="规则集管理" subtitle="按行业标准定义数据质量检查规则">
      <template #extra>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          新增规则集
        </el-button>
      </template>
    </PageHeader>

    <div class="m3-card filter-bar">
      <el-select v-model="filterIndustry" placeholder="行业筛选" clearable style="width: 140px" @change="load">
        <el-option v-for="i in industries" :key="i" :label="i" :value="i" />
      </el-select>
    </div>

    <div class="m3-card">
      <el-table :data="list" stripe>
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="industry" label="行业" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.industry" size="small" type="info">{{ row.industry }}</el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="质量维度" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="d in (row.quality_dimensions || [])" :key="d" size="small" style="margin: 1px 2px 1px 0">
              {{ dimLabel(d) }}
            </el-tag>
            <span v-if="!row.quality_dimensions?.length" class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column label="规则数" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.rules?.length ?? 0 }} 条</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="规则类型" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="t in ruleTypes(row)" :key="t" size="small" type="info" style="margin: 1px 2px 1px 0">
              {{ t }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="doDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑规则集' : '新增规则集'" width="720">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="规则集名称" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="form.industry" placeholder="可选" clearable style="width: 100%">
            <el-option label="通用" value="通用" />
            <el-option label="金融" value="金融" />
            <el-option label="政务" value="政务" />
            <el-option label="人力资源" value="人力资源" />
          </el-select>
        </el-form-item>
        <el-form-item label="引用标准">
          <el-input v-model="form.standard_ref" placeholder="如 GB/T 36344-2018, DAMA-DMBOK" />
        </el-form-item>
        <el-form-item label="质量维度">
          <el-select v-model="form.quality_dimensions" multiple placeholder="可选" style="width: 100%">
            <el-option label="完整性" value="completeness" />
            <el-option label="唯一性" value="uniqueness" />
            <el-option label="有效性" value="validity" />
            <el-option label="准确性" value="accuracy" />
            <el-option label="一致性" value="consistency" />
            <el-option label="及时性" value="timeliness" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="规则集说明" />
        </el-form-item>
        <el-form-item label="规则 (JSON)">
          <el-input
            v-model="rulesJson"
            type="textarea"
            :rows="12"
            placeholder='[{"type":"completeness","column":"name"},{"type":"uniqueness","column":"id"}]'
            style="font-family: 'Consolas', 'Monaco', monospace; font-size: 13px"
          />
          <div class="hint">规则数组，每项包含 type、column 等字段，参考示例格式</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api, type RuleSet } from '../api/client'
import PageHeader from '../components/PageHeader.vue'

const list = ref<RuleSet[]>([])
const filterIndustry = ref('')
const industries = ['通用', '金融', '政务', '人力资源']
const dialogVisible = ref(false)
const saving = ref(false)
const editing = ref(false)

const form = reactive({
  id: '',
  name: '',
  description: '',
  rules: [] as Record<string, unknown>[],
  industry: '',
  quality_dimensions: [] as string[],
  standard_ref: '',
})

const rulesJson = computed({
  get: () => JSON.stringify(form.rules, null, 2),
  set: (v) => {
    try {
      form.rules = JSON.parse(v || '[]')
    } catch {
      /* keep previous */
    }
  },
})

onMounted(load)

async function load() {
  const params = filterIndustry.value ? { industry: filterIndustry.value } : undefined
  const { data } = await api.getRuleSets(params)
  list.value = data
}

function openDialog(row?: RuleSet) {
  editing.value = !!row
  form.id = row?.id ?? ''
  form.name = row?.name ?? ''
  form.description = row?.description ?? ''
  form.rules = row?.rules ? JSON.parse(JSON.stringify(row.rules)) : []
  form.industry = row?.industry ?? ''
  form.quality_dimensions = row?.quality_dimensions ? [...row.quality_dimensions] : []
  form.standard_ref = row?.standard_ref ?? ''
  dialogVisible.value = true
}

async function save() {
  if (!form.name) {
    ElMessage.warning('请填写名称')
    return
  }
  try {
    JSON.parse(rulesJson.value)
  } catch {
    ElMessage.warning('规则 JSON 格式错误')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await api.updateRuleSet(form.id, {
        name: form.name,
        description: form.description,
        rules: form.rules,
        industry: form.industry || undefined,
        quality_dimensions: form.quality_dimensions.length ? form.quality_dimensions : undefined,
        standard_ref: form.standard_ref || undefined,
      })
      ElMessage.success('更新成功')
    } else {
      await api.createRuleSet({
        name: form.name,
        description: form.description,
        rules: form.rules,
        industry: form.industry || undefined,
        quality_dimensions: form.quality_dimensions.length ? form.quality_dimensions : undefined,
        standard_ref: form.standard_ref || undefined,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    load()
  } catch (e: unknown) {
    ElMessage.error((e as Error).message || '保存失败')
  } finally {
    saving.value = false
  }
}

function dimLabel(d: string): string {
  const map: Record<string, string> = {
    completeness: '完整性',
    uniqueness: '唯一性',
    validity: '有效性',
    accuracy: '准确性',
    consistency: '一致性',
    timeliness: '及时性',
  }
  return map[d] || d
}

function ruleTypes(row: RuleSet): string[] {
  const rules = row.rules || []
  const typeNames: Record<string, string> = {
    completeness: '完整性',
    uniqueness: '唯一性',
    data_type: '数据类型',
    accuracy_range_check: '范围',
    validity_regex_match_check: '正则',
    consistency_date_order_check: '日期顺序',
    timeliness_fixed_range_check: '时效性',
  }
  const types = [...new Set((rules as { type?: string }[]).map((r) => r.type).filter(Boolean))]
  return types.map((t) => typeNames[t as string] || t)
}

async function doDelete(row: RuleSet) {
  await ElMessageBox.confirm('确定删除该规则集？', '确认')
  await api.deleteRuleSet(row.id)
  ElMessage.success('已删除')
  load()
}
</script>

<style scoped>
.filter-bar {
  margin-bottom: var(--md-spacing-md);
}
.muted {
  color: #9ca3af;
}
.hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 6px;
}
</style>
