<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { executeImport, getImportTasks, validateImport } from '@/api';
import { SOURCE_OPTIONS } from '@/constants/sourceOptions';
import type { ImportTask } from '@/types';
import type { UploadFile, UploadFiles } from 'element-plus';

const text = {
  title: '导入任务',
  subtitle: '上传单个三列表 CSV，校验通过后使用 LOAD CSV 追加导入 Neo4j。',
  upload: '选择三列表 CSV',
  formatHint: '文件表头必须严格为 `subject,relation,object`，实体值格式必须为 `名称(类型)`。',
  source: '来源',
  sourceCase: '来源医案',
  schema: 'Schema',
  sourcePlaceholder: '请选择来源卷册',
  sourceCasePlaceholder: '例如：中风、中寒',
  schemaPlaceholder: '可选，例如：tcm；不填则允许任意实体和关系',
  validate: '开始校验',
  execute: '执行导入',
  taskId: '任务 ID',
  name: '任务名称',
  status: '状态',
  createdAt: '创建时间',
  summary: '摘要',
  stats: '融合统计',
};
const sourceOptions = SOURCE_OPTIONS;
const tasks = ref<ImportTask[]>([]);
const selectedFile = ref<File | null>(null);
const validating = ref(false);
const executing = ref(false);
const lastValidatedTaskId = ref('');
const form = reactive({
  source: '',
  sourceCase: '',
  schema: '',
});

async function loadData() {
  tasks.value = await getImportTasks();
}

function handleChange(_: UploadFile, fileList: UploadFiles) {
  const latest = [...fileList].reverse().find((item) => item.raw);
  selectedFile.value = latest?.raw ? (latest.raw as File) : null;
}

async function runValidate() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择 CSV 文件');
    return;
  }
  if (!form.source.trim() || !form.sourceCase.trim()) {
    ElMessage.warning('请填写来源和来源医案');
    return;
  }
  validating.value = true;
  try {
    const task = await validateImport(selectedFile.value, form.source, form.sourceCase, form.schema);
    lastValidatedTaskId.value = task.id;
    ElMessage.success('导入校验已完成，可以继续执行追加导入');
    await loadData();
  } finally {
    validating.value = false;
  }
}

async function runExecute() {
  if (!lastValidatedTaskId.value) {
    ElMessage.warning('请先执行校验');
    return;
  }
  executing.value = true;
  try {
    await executeImport(lastValidatedTaskId.value);
    ElMessage.success('追加导入执行完成');
    await loadData();
  } finally {
    executing.value = false;
  }
}

function buildStats(task: ImportTask) {
  if (task.createdNodes === undefined) {
    return '-';
  }
  return `新增节点 ${task.createdNodes} / 重复节点 ${task.mergedNodes ?? 0} / 新增关系 ${task.createdRelations ?? 0} / 重复关系 ${task.deduplicatedRelations ?? 0}`;
}

onMounted(async () => {
  await loadData();
});
</script>

<template>
  <section>
    <div class="glass-panel section-card">
      <h1 class="page-title">{{ text.title }}</h1>
      <p class="page-subtitle">{{ text.subtitle }}</p>
      <p class="page-subtitle">{{ text.formatHint }}</p>
      <div class="toolbar">
        <el-upload action="#" :auto-upload="false" :limit="1" accept=".csv,text/csv" :on-change="handleChange" :show-file-list="true">
          <el-button type="primary">{{ text.upload }}</el-button>
        </el-upload>
        <el-select v-model="form.source" :placeholder="text.sourcePlaceholder" clearable style="width: 200px">
          <el-option v-for="item in sourceOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-input v-model="form.sourceCase" :placeholder="text.sourceCasePlaceholder" style="max-width: 220px" clearable />
        <el-input v-model="form.schema" :placeholder="text.schemaPlaceholder" style="max-width: 320px" clearable />
        <el-button type="success" plain :loading="validating" @click="runValidate">{{ text.validate }}</el-button>
        <el-button type="warning" plain :loading="executing" @click="runExecute">{{ text.execute }}</el-button>
      </div>
    </div>

    <div class="glass-panel section-card" style="margin-top: 20px">
      <el-table :data="tasks">
        <el-table-column prop="id" :label="text.taskId" min-width="180" />
        <el-table-column prop="name" :label="text.name" min-width="180" />
        <el-table-column prop="status" :label="text.status" width="120" />
        <el-table-column prop="source" :label="text.source" min-width="180" />
        <el-table-column prop="sourceCase" :label="text.sourceCase" min-width="180" />
        <el-table-column prop="schema" :label="text.schema" width="120" />
        <el-table-column prop="createdAt" :label="text.createdAt" width="180" />
        <el-table-column prop="summary" :label="text.summary" min-width="240" />
        <el-table-column :label="text.stats" min-width="300">
          <template #default="{ row }">
            {{ buildStats(row) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </section>
</template>
