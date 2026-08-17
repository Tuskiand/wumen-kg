<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { bulkDeleteRelations, createRelation, deleteRelation, getRelations, updateRelation } from '@/api';
import { useSchema } from '@/composables/useSchema';
import { SOURCE_OPTIONS } from '@/constants/sourceOptions';
import type { GraphEdge } from '@/types';

const text = {
  title: '关系管理',
  subtitle: '支持新增、编辑、删除关系，并可按来源和来源医案筛选。',
  create: '新增关系',
  batchRemove: '批量删除',
  selected: '已选',
  sourceFilter: '来源',
  sourceCaseFilter: '来源医案，例如：中风、中寒',
  reset: '重置',
  id: 'ID',
  source: '起点',
  type: '关系类型',
  target: '终点',
  label: '显示标签',
  action: '操作',
  edit: '编辑',
  remove: '删除',
  save: '保存',
};
const sourceOptions = SOURCE_OPTIONS;
const { relationTypes } = useSchema();
const allRows = ref<GraphEdge[]>([]);
const selectedRows = ref<GraphEdge[]>([]);
const visible = ref(false);
const saving = ref(false);
const batchDeleting = ref(false);
const editingId = ref('');
const filters = reactive({
  source: '',
  sourceCase: '',
});
const form = reactive<GraphEdge>({ id: '', source: '', target: '', type: '', label: '', sourceCases: [], sourceBatches: [] });

const rows = computed(() => allRows.value.filter((item) => {
  const sourceMatch = !filters.source || item.sourceBatches.some((entry) => entry === filters.source);
  const sourceCaseMatch = !filters.sourceCase || item.sourceCases.some((entry) => entry.includes(filters.sourceCase));
  return sourceMatch && sourceCaseMatch;
}));

function resetForm() {
  form.id = '';
  form.source = '';
  form.target = '';
  form.type = '';
  form.label = '';
  form.sourceCases = [];
  form.sourceBatches = [];
  editingId.value = '';
}

async function loadData() {
  allRows.value = await getRelations();
  selectedRows.value = [];
}

function openCreate() {
  resetForm();
  visible.value = true;
}

function openEdit(row: GraphEdge) {
  editingId.value = row.id;
  Object.assign(form, row);
  visible.value = true;
}

function handleSelectionChange(selection: GraphEdge[]) {
  selectedRows.value = selection;
}

function resetFilters() {
  filters.source = '';
  filters.sourceCase = '';
}

async function submit() {
  saving.value = true;
  try {
    if (editingId.value) {
      await updateRelation(editingId.value, { ...form });
      ElMessage.success('关系已更新');
    } else {
      await createRelation({ ...form });
      ElMessage.success('关系已新增');
    }
    visible.value = false;
    await loadData();
  } finally {
    saving.value = false;
  }
}

async function remove(row: GraphEdge) {
  await ElMessageBox.confirm(`确认删除关系 ${row.id} 吗？`, '删除确认', { type: 'warning' });
  await deleteRelation(row.id);
  ElMessage.success('关系已删除');
  await loadData();
}

async function removeSelected() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先选择要删除的关系');
    return;
  }
  await ElMessageBox.confirm(`确认批量删除 ${selectedRows.value.length} 条关系吗？`, '批量删除确认', { type: 'warning' });
  batchDeleting.value = true;
  try {
    await bulkDeleteRelations(selectedRows.value.map((item) => item.id));
    ElMessage.success('关系已批量删除');
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
      <el-table-column prop="id" :label="text.id" min-width="120" />
      <el-table-column prop="source" :label="text.source" min-width="160" />
      <el-table-column prop="type" :label="text.type" width="200" />
      <el-table-column prop="target" :label="text.target" min-width="160" />
      <el-table-column :label="text.action" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">{{ text.edit }}</el-button>
          <el-button link type="danger" @click="remove(row)">{{ text.remove }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editingId ? text.edit : text.create" width="520px">
      <el-form label-position="top">
        <el-form-item :label="text.id">
          <el-input v-model="form.id" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item :label="text.source">
          <el-input v-model="form.source" />
        </el-form-item>
        <el-form-item :label="text.target">
          <el-input v-model="form.target" />
        </el-form-item>
        <el-form-item :label="text.type">
          <el-select v-model="form.type" filterable style="width: 100%">
            <el-option v-for="item in relationTypes" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="text.label">
          <el-input v-model="form.label" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ text.save }}</el-button>
      </template>
    </el-dialog>
  </section>
</template>
