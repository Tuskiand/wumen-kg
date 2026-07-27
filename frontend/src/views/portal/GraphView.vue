<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import GraphCanvas from '@/components/GraphCanvas.vue';
import { getGraphSnapshot } from '@/api';
import TcmEmpty from '@/components/tcm/TcmEmpty.vue';
import TcmPageShell from '@/components/tcm/TcmPageShell.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import { ENTITY_TYPES } from '@/constants/entityTypes';
import { SOURCE_OPTIONS } from '@/constants/sourceOptions';
import type { GraphSnapshot } from '@/types';

const text = {
  title: '图谱探索',
  subtitle: '在总图上按来源、来源医案与实体类型筛选知识图谱。',
  nodeCount: '节点',
  edgeCount: '关系',
  ability: '支持拖拽 / 缩放 / 关系标注',
  sourcePlaceholder: '来源',
  sourceCasePlaceholder: '来源医案，例如：中风、中寒',
  typePlaceholder: '实体类型',
  filter: '应用筛选',
};
const graphData = ref<GraphSnapshot>({ nodes: [], edges: [] });
const entityTypes = ENTITY_TYPES;
const sourceOptions = SOURCE_OPTIONS;
const loading = ref(false);
const filters = reactive({
  source: '',
  sourceCase: '',
  entityType: '',
});

async function loadData() {
  loading.value = true;
  try {
    graphData.value = await getGraphSnapshot(filters.source, filters.sourceCase, filters.entityType);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadData();
});
</script>

<template>
  <TcmPageShell :title="text.title" :subtitle="text.subtitle" icon="graph">
    <TcmPanel title="筛选条件" icon="search">
      <div class="toolbar">
        <el-select v-model="filters.source" :placeholder="text.sourcePlaceholder" clearable style="width: 200px">
          <el-option v-for="item in sourceOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-input v-model="filters.sourceCase" :placeholder="text.sourceCasePlaceholder" style="max-width: 220px" clearable />
        <el-select v-model="filters.entityType" :placeholder="text.typePlaceholder" clearable filterable style="width: 220px">
          <el-option v-for="item in entityTypes" :key="item" :label="item" :value="item" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadData">{{ text.filter }}</el-button>
        <el-tag type="primary">{{ text.nodeCount }} {{ graphData.nodes.length }}</el-tag>
        <el-tag type="success">{{ text.edgeCount }} {{ graphData.edges.length }}</el-tag>
        <el-tag>{{ text.ability }}</el-tag>
      </div>
    </TcmPanel>

    <TcmPanel title="图谱画布" icon="graph" class="spaced" :decorated="false">
      <div class="graph-stage">
        <TcmEmpty v-if="!loading && !graphData.nodes.length" text="当前筛选条件下暂无图谱数据" />
        <GraphCanvas
          v-else
          :data="graphData"
          height="clamp(320px, min(68vh, calc(100vw - 120px)), 760px)"
        />
      </div>
    </TcmPanel>
  </TcmPageShell>
</template>

<style scoped>
.graph-stage {
  width: 100%;
  margin-top: 20px;
}

@media (max-width: 960px) {
  .graph-stage {
    margin-top: 16px;
  }
}
</style>
