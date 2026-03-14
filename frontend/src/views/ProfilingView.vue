<!--
  文件名: ProfilingView.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 数据剖析，列级统计与规则推荐
-->
<template>
  <div class="page-container">
    <PageHeader title="数据剖析" subtitle="对数据源进行列级统计与规则推荐" />

    <div class="m3-card profiling-form">
      <el-form inline :model="profForm" class="prof-form-inline">
        <el-form-item label="数据源">
          <el-select v-model="profForm.datasourceId" placeholder="选择数据源" style="width: 240px">
            <el-option v-for="d in datasources" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="采样数">
          <el-input-number v-model="profForm.sampleSize" :min="100" :max="1000000" :step="1000" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="run">
            <el-icon><TrendCharts /></el-icon>
            执行剖析
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <template v-if="result">
      <div class="m3-card profiling-overview">
        <h3 class="m3-card-header">概览</h3>
        <p class="overview-text">总行数: <strong>{{ result.row_count }}</strong>，列数: <strong>{{ result.columns?.length ?? 0 }}</strong></p>
      </div>
      <div class="m3-card profiling-table-card">
        <h3 class="m3-card-header">列级统计</h3>
        <el-table :data="result.columns" stripe>
          <el-table-column prop="name" label="列名" width="140" />
          <el-table-column prop="dtype" label="类型" width="100" />
          <el-table-column prop="non_null_count" label="非空数" width="100" />
          <el-table-column prop="null_count" label="空值数" width="100" />
          <el-table-column prop="unique_count" label="唯一值数" width="110" />
          <el-table-column label="建议规则" min-width="180">
            <template #default="{ row }">
              <el-tag v-for="r in (row.suggested_rules || [])" :key="r" size="small" style="margin: 2px 4px 2px 0">
                {{ r }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="范围" min-width="160">
            <template #default="{ row }">
              <span v-if="row.min != null">min: {{ row.min }}, max: {{ row.max }}</span>
              <span v-else-if="row.min_date"> {{ row.min_date }} ~ {{ row.max_date }}</span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>
    <el-empty v-else-if="!loading" description="选择数据源并执行剖析" :image-size="100" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts } from '@element-plus/icons-vue'
import { api, type ProfilingResult } from '../api/client'
import PageHeader from '../components/PageHeader.vue'

const datasources = ref<{ id: string; name: string }[]>([])
const profForm = reactive({ datasourceId: '', sampleSize: 10000 })
const loading = ref(false)
const result = ref<ProfilingResult | null>(null)

onMounted(async () => {
  const { data } = await api.getDatasources()
  datasources.value = data
  if (data.length) profForm.datasourceId = data[0].id
})

async function run() {
  if (!profForm.datasourceId) {
    ElMessage.warning('请选择数据源')
    return
  }
  loading.value = true
  result.value = null
  try {
    const { data } = await api.runProfiling(profForm.datasourceId, profForm.sampleSize)
    result.value = data
    ElMessage.success('剖析完成')
  } catch {
    ElMessage.error('剖析失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profiling-form {
  margin-bottom: var(--md-spacing-lg);
}

.prof-form-inline :deep(.el-form-item) {
  margin-right: var(--md-spacing-lg);
}

.profiling-overview {
  margin-bottom: var(--md-spacing-lg);
}

.overview-text {
  margin: 0;
  font: var(--md-typescale-body-large);
  color: #374151;
}

.overview-text strong {
  color: var(--md-sys-color-primary);
}

.text-muted {
  color: #9ca3af;
}

.profiling-table-card {
  margin-bottom: var(--md-spacing-lg);
}
</style>
