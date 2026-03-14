<template>
  <div class="page-container">
    <PageHeader title="数据源管理" subtitle="配置 CSV、Excel、PostgreSQL、MySQL 等数据源">
      <template #extra>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          新增数据源
        </el-button>
      </template>
    </PageHeader>

    <div class="m3-card filter-bar" style="margin-bottom:16px">
      <el-select v-model="filterScenario" placeholder="业务场景筛选" clearable style="width:160px" @change="load">
        <el-option label="金融信贷" value="金融信贷" />
        <el-option label="政务人口" value="政务人口" />
        <el-option label="电商订单" value="电商订单" />
        <el-option label="人力资源" value="人力资源" />
        <el-option label="演示示例" value="演示示例" />
      </el-select>
    </div>
    <div class="m3-card">
      <el-table :data="list" stripe>
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="business_scenario" label="业务场景" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.business_scenario" size="small" type="info">{{ row.business_scenario }}</el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="source_type" label="类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.source_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="路径/连接" min-width="200">
          <template #default="{ row }">{{ configSummary(row) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="testConn(row)">测试</el-button>
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="doDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑数据源' : '新增数据源'" width="540">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="数据源名称" />
        </el-form-item>
        <el-form-item label="业务场景">
          <el-select v-model="form.business_scenario" placeholder="可选" clearable style="width:100%">
            <el-option label="金融信贷" value="金融信贷" />
            <el-option label="政务人口" value="政务人口" />
            <el-option label="电商订单" value="电商订单" />
            <el-option label="人力资源" value="人力资源" />
            <el-option label="演示示例" value="演示示例" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.source_type" style="width: 100%" @change="onSourceTypeChange">
            <el-option label="CSV" value="csv" />
            <el-option label="Excel" value="excel" />
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="MySQL" value="mysql" />
          </el-select>
        </el-form-item>

        <template v-if="isFileSource">
          <el-form-item label="路径">
            <el-input v-model="form.config.path" placeholder="如 good_data.csv（相对 backend/data）" />
          </el-form-item>
          <el-form-item v-if="form.source_type === 'excel'" label="Sheet">
            <el-input v-model="form.config.sheet" placeholder="0 或 sheet 名称" />
          </el-form-item>
        </template>

        <template v-if="isDbSource">
          <el-form-item label="主机">
            <el-input v-model="form.config.host" placeholder="localhost" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input v-model.number="form.config.port" :placeholder="form.source_type === 'mysql' ? '3306' : '5432'" />
          </el-form-item>
          <el-form-item label="数据库">
            <el-input v-model="form.config.database" placeholder="数据库名" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="form.config.user" placeholder="用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.config.password" type="password" placeholder="密码" show-password autocomplete="new-password" />
          </el-form-item>
          <el-form-item label="表名/SQL">
            <el-input v-model="form.config.table" placeholder="表名，或留空使用自定义 SQL" />
          </el-form-item>
          <el-form-item v-if="!form.config.table" label="查询 SQL">
            <el-input v-model="form.config.query" type="textarea" :rows="2" placeholder="SELECT * FROM your_table" />
          </el-form-item>
        </template>
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
import { api, type Datasource } from '../api/client'
import PageHeader from '../components/PageHeader.vue'

const list = ref<Datasource[]>([])
const filterScenario = ref('')
const dialogVisible = ref(false)
const saving = ref(false)
const editing = ref(false)

const form = reactive({
  id: '',
  name: '',
  source_type: 'csv',
  business_scenario: '',
  config: {
    path: '',
    sheet: 0,
    host: '',
    port: 5432,
    database: '',
    user: '',
    password: '',
    table: '',
    query: '',
  } as Record<string, unknown>,
})

const isFileSource = computed(() => ['csv', 'excel'].includes(form.source_type))
const isDbSource = computed(() => ['postgresql', 'mysql'].includes(form.source_type))

onMounted(load)

async function load() {
  const params = filterScenario.value ? { business_scenario: filterScenario.value } : undefined
  const { data } = await api.getDatasources(params)
  list.value = data
}

function openDialog(row?: Datasource) {
  editing.value = !!row
  form.id = row?.id ?? ''
  form.name = row?.name ?? ''
  form.source_type = row?.source_type ?? 'csv'
  const c = row?.config ? { ...row.config } : {}
  form.business_scenario = row?.business_scenario ?? ''
  form.config = {
    path: c.path ?? '',
    sheet: c.sheet ?? 0,
    host: c.host ?? '',
    port: c.port ?? (row?.source_type === 'mysql' ? 3306 : 5432),
    database: c.database ?? '',
    user: c.user ?? '',
    password: c.password ?? '',
    table: c.table ?? '',
    query: c.query ?? '',
  }
  dialogVisible.value = true
}

function onSourceTypeChange() {
  if (form.source_type === 'mysql') {
    form.config.port = 3306
  } else if (form.source_type === 'postgresql') {
    form.config.port = 5432
  }
}

function typeLabel(t: string): string {
  const map: Record<string, string> = {
    csv: 'CSV',
    excel: 'Excel',
    postgresql: 'PostgreSQL',
    mysql: 'MySQL',
  }
  return map[t] ?? t.toUpperCase()
}

function configSummary(row: Datasource): string {
  const c = row.config || {}
  if (row.source_type === 'csv' || row.source_type === 'excel') {
    return (c.path as string) || '-'
  }
  if (row.source_type === 'postgresql' || row.source_type === 'mysql') {
    const h = c.host || 'localhost'
    const db = c.database || ''
    const tbl = c.table || (c.query ? '(SQL)' : '')
    return `${h}/${db}${tbl ? ':' + tbl : ''}`
  }
  return JSON.stringify(c)
}

async function save() {
  if (!form.name) {
    ElMessage.warning('请填写名称')
    return
  }
  if (isFileSource.value && !form.config.path) {
    ElMessage.warning('请填写路径')
    return
  }
  if (isDbSource.value) {
    if (!form.config.host || !form.config.database || !form.config.user) {
      ElMessage.warning('请填写主机、数据库和用户名')
      return
    }
    if (!form.config.table && !form.config.query) {
      ElMessage.warning('请填写表名或查询 SQL')
      return
    }
  }
  saving.value = true
  try {
    if (editing.value) {
      await api.updateDatasource(form.id, {
        name: form.name,
        source_type: form.source_type,
        config: form.config,
        business_scenario: form.business_scenario || undefined,
      })
      ElMessage.success('更新成功')
    } else {
      await api.createDatasource({
        name: form.name,
        source_type: form.source_type,
        config: form.config,
        business_scenario: form.business_scenario || undefined,
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

async function testConn(row: Datasource) {
  try {
    const { data } = await api.testDatasource(row.id)
    ElMessage.success(data.ok ? data.message : '测试失败')
  } catch {
    ElMessage.error('连接失败')
  }
}

async function doDelete(row: Datasource) {
  await ElMessageBox.confirm('确定删除该数据源？', '确认')
  await api.deleteDatasource(row.id)
  ElMessage.success('已删除')
  load()
}
</script>
