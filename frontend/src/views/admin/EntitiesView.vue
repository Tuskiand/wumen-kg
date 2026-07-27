<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { bulkDeleteEntities, createEntity, deleteEntity, getEntities, updateEntity } from '@/api';
import { ENTITY_TYPES } from '@/constants/entityTypes';
import { SOURCE_OPTIONS } from '@/constants/sourceOptions';
import type { GraphNode } from '@/types';

const text = {
  title: '节点管理',
  subtitle: '支持新增、编辑、删除节点，并可按来源和来源医案筛选。',
  create: '新增节点',
  batchRemove: '批量删除',
  selected: '已选',
  sourceFilter: '来源',
  sourceCaseFilter: '来源医案，例如：中风、中寒',
  reset: '重置',
  id: 'ID',
  name: '名称',
  type: '类型',
  source: '来源',
  action: '操作',
  edit: '编辑',
  remove: '删除',
  dialogCreate: '新增节点',
  dialogEdit: '编辑节点',
  summary: '摘要',
  label: '标签',
  save: '保存',
};
const sourceOptions = SOURCE_OPTIONS;
const entityTypes = ENTITY_TYPES;
const allRows = ref<GraphNode[]>([]);
const selectedRows = ref<GraphNode[]>([]);
const visible = ref(false);
const saving = ref(false);
const batchDeleting = ref(false);
const editingId = ref('');
const filters = reactive({
  source: '',
  sourceCase: '',
});
const form = reactive<GraphNode>({
  id: '',
  name: '',
  label: '',
  type: '',
  summary: '',
  source: '',
  sourceCases: [],
  sourceBatches: [],
});

const rows = computed(() => allRows.value.filter((item) => {
  const sourceMatch = !filters.source || item.source === filters.source;
  const sourceCaseMatch = !filters.sourceCase || item.sourceCases.some((entry) => entry.includes(filters.sourceCase));
  return sourceMatch && sourceCaseMatch;
}));

function resetForm() {
  form.id = '';
  form.name = '';
  form.label = '';
  form.type = '';
  form.summary = '';
  form.source = '';
  form.sourceCases = [];
  form.sourceBatches = [];
  editingId.value = '';
}

async function loadData() {
  allRows.value = await getEntities();
  selectedRows.value = [];
}

function openCreate() {
  resetForm();
  visible.value = true;
}

function openEdit(row: GraphNode) {
  editingId.value = row.id;
  Object.assign(form, row);
  visible.value = true;
}

function handleSelectionChange(selection: GraphNode[]) {
  selectedRows.value = selection;
}

function resetFilters() {
  filters.source = '';
  filters.sourceCase = '';
}

async function submit() {
  saving.value = true;
  try {
    const payload = { ...form };
    if (!payload.sourceBatches.length && payload.source) {
      payload.sourceBatches = [payload.source];
    }
    if (editingId.value) {
      await updateEntity(editingId.value, payload);
      ElMessage.success('节点已更新');
    } else {
      await createEntity(payload);
      ElMessage.success('节点已新增');
    }
    visible.value = false;
    await loadData();
  } finally {
    saving.value = false;
  }
}

async function remove(row: GraphNode) {
  await ElMessageBox.confirm(`确认删除节点 ${row.name} 吗？`, '删除确认', { type: 'warning' });
  await deleteEntity(row.id);
  ElMessage.success('节点已删除');
  await loadData();
}

async function removeSelected() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先选择要删除的节点');
    return;
  }
  await ElMessageBox.confirm(`确认批量删除 ${selectedRows.value.length} 个节点吗？`, '批量删除确认', { type: 'warning' });
  batchDeleting.value = true;
  try {
    await bulkDeleteEntities(selectedRows.value.map((item) => item.id));
    ElMessage.success('节点已批量删除');
    await loadData();
  } finally {
    batchDeleting.value = false;
  }
}

onMounted(async () => {
  await loadData();
});
</script>

<template>
  <section class="glass-panel section-card">
    <h1 class="page-title">{{ text.title }}</h1>
    <p class="page-subtitle">{{ text.subtitle }}</p>
    <div class="toolbar">
      <el-select v-model="filters.source" :placeholder="text.sourceFilter" clearable style="width: 200px">
        <el-option v-for="item in sourceOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-input v-model="filters.sourceCase" :placeholder="text.sourceCaseFilter" style="max-width: 220px" clearable />
      <el-button @click="resetFilters">{{ text.reset }}</el-button>
      <el-button type="primary" @click="openCreate">{{ text.create }}</el-button>
      <el-button type="danger" plain :disabled="!selectedRows.length" :loading="batchDeleting" @click="removeSelected">
        {{ text.batchRemove }}（{{ text.selected }} {{ selectedRows.length }}）
      </el-button>
    </div>
    <el-table :data="rows" style="margin-top: 20px" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="48" />
      <el-table-column prop="id" :label="text.id" min-width="180" />
      <el-table-column prop="name" :label="text.name" min-width="160" />
      <el-table-column prop="type" :label="text.type" width="180" />
      <el-table-column prop="source" :label="text.source" min-width="180" />
      <el-table-column :label="text.action" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">{{ text.edit }}</el-button>
          <el-button link type="danger" @click="remove(row)">{{ text.remove }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editingId ? text.dialogEdit : text.dialogCreate" width="520px">
      <el-form label-position="top">
        <el-form-item :label="text.id">
          <el-input v-model="form.id" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item :label="text.name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item :label="text.label">
          <el-input v-model="form.label" />
        </el-form-item>
        <el-form-item :label="text.type">
          <el-select v-model="form.type" filterable style="width: 100%">
            <el-option v-for="item in entityTypes" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="text.source">
          <el-select v-model="form.source" filterable style="width: 100%">
            <el-option v-for="item in sourceOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="text.summary">
          <el-input v-model="form.summary" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ text.save }}</el-button>
      </template>
    </el-dialog>
  </section>
</template>
