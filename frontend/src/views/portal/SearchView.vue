<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import { searchGraph } from '@/api';
import TcmEmpty from '@/components/tcm/TcmEmpty.vue';
import TcmPageShell from '@/components/tcm/TcmPageShell.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import { ENTITY_TYPES } from '@/constants/entityTypes';
import { SOURCE_OPTIONS } from '@/constants/sourceOptions';
import type { GraphNode } from '@/types';

const text = {
  title: '知识检索',
  subtitle: '按实体名称快速定位图谱节点，并支持按来源、来源医案与实体类型筛选。',
  queryPlaceholder: '搜索医家、病名、证型、病机、脉象、舌象、治法、方剂、药物等实体',
  typePlaceholder: '实体类型',
  sourcePlaceholder: '来源',
  sourceCasePlaceholder: '来源医案，例如：中风、中寒',
  search: '执行检索',
  detail: '查看详情',
  name: '名称',
  type: '类型',
  source: '来源',
  cases: '来源医案',
  summary: '摘要',
  action: '操作',
};
const entityTypes = ENTITY_TYPES;
const sourceOptions = SOURCE_OPTIONS;
const filters = reactive({
  query: '',
  type: '',
  source: '',
  sourceCase: '',
});
const loading = ref(false);
const rows = ref<GraphNode[]>([]);

async function loadData() {
  loading.value = true;
  try {
    const result = await searchGraph(filters.query, filters.type, filters.source, filters.sourceCase);
    rows.value = result.items;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadData();
});
</script>

<template>
  <TcmPageShell :title="text.title" :subtitle="text.subtitle" icon="search">
    <TcmPanel title="检索条件" icon="search">
      <div class="toolbar">
        <el-input v-model="filters.query" :placeholder="text.queryPlaceholder" style="max-width: 300px" clearable />
        <el-select v-model="filters.type" :placeholder="text.typePlaceholder" clearable filterable style="width: 220px">
          <el-option v-for="item in entityTypes" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="filters.source" :placeholder="text.sourcePlaceholder" clearable style="width: 200px">
          <el-option v-for="item in sourceOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-input v-model="filters.sourceCase" :placeholder="text.sourceCasePlaceholder" style="max-width: 220px" clearable />
        <el-button type="primary" @click="loadData">{{ text.search }}</el-button>
      </div>
    </TcmPanel>

    <TcmPanel class="spaced" title="检索结果" icon="entity">
      <TcmEmpty v-if="!loading && !rows.length" text="当前筛选条件下暂无搜索结果" />
      <el-table v-else :data="rows" v-loading="loading">
        <el-table-column prop="name" :label="text.name" min-width="160" />
        <el-table-column prop="type" :label="text.type" width="180" />
        <el-table-column prop="source" :label="text.source" min-width="160" />
        <el-table-column :label="text.cases" min-width="220">
          <template #default="{ row }">
            <el-tag v-for="item in row.sourceCases" :key="item" style="margin-right: 6px; margin-bottom: 6px">{{ item }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="summary" :label="text.summary" min-width="280" />
        <el-table-column :label="text.action" width="120">
          <template #default="{ row }">
            <el-button link type="primary" tag="router-link" :to="`/portal/entity/${row.id}`">{{ text.detail }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </TcmPanel>
  </TcmPageShell>
</template>
