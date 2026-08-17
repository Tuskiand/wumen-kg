<script setup lang="ts">
import { reactive, ref, computed } from 'vue';
import GraphCanvas from '@/components/GraphCanvas.vue';
import { queryPath } from '@/api';
import TcmEmpty from '@/components/tcm/TcmEmpty.vue';
import TcmPageShell from '@/components/tcm/TcmPageShell.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import type { GraphSnapshot, QueryPathItem } from '@/types';

const ENTITY_TYPE_LABELS: Record<string, string> = {
  A医家: '医家', B病名: '病名', C证型: '证型', D病因: '病因', E病机: '病机',
};

const text = {
  title: '路径查询',
  subtitle: '查看两个实体之间的所有语义链路，按路径长度排序。',
  action: '查询路径',
};
const form = reactive({
  sourceName: '中风',
  targetName: '风邪',
  sourceCase: '',
  maxDepth: 4,
  maxPaths: 10,
  minLength: 1,
  nodeTypes: [] as string[],
});
const loading = ref(false);
const description = ref('');
const paths = ref<QueryPathItem[]>([]);
const totalPaths = ref(0);
const selectedPath = ref<QueryPathItem | null>(null);
const selectedPathIndex = ref(-1);
const graphData = computed<GraphSnapshot>(() => {
  if (!selectedPath.value) return { nodes: [], edges: [] };
  return { nodes: selectedPath.value.nodes, edges: selectedPath.value.edges };
});
const nodeTypeOptions = ['A医家', 'B病名', 'C证型', 'D病因', 'E病机'];

async function runQuery() {
  loading.value = true;
  try {
    const result = await queryPath(
      form.sourceName, form.targetName, form.sourceCase,
      form.maxDepth, form.maxPaths, form.minLength, form.nodeTypes,
    );
    paths.value = result.paths;
    totalPaths.value = result.totalPaths;
    description.value = result.description;
    selectedPath.value = result.paths.length > 0 ? result.paths[0] : null;
    selectedPathIndex.value = result.paths.length > 0 ? 0 : -1;
  } finally {
    loading.value = false;
  }
}

function selectPath(index: number) {
  selectedPathIndex.value = index;
  selectedPath.value = paths.value[index];
}

function typeLabel(nodeType: string) {
  return ENTITY_TYPE_LABELS[nodeType] || nodeType;
}

function typeSequenceLabel(types: string[]) {
  return types.map((t) => typeLabel(t)).join(' -> ');
}
</script>

<template>
  <TcmPageShell :title="text.title" :subtitle="text.subtitle" icon="path">
    <TcmPanel title="查询条件" icon="search">
      <div class="toolbar">
        <el-input v-model="form.sourceName" placeholder="起点实体" style="max-width: 180px" />
        <el-input v-model="form.targetName" placeholder="终点实体" style="max-width: 180px" />
        <el-input v-model="form.sourceCase" placeholder="来源医案" style="max-width: 180px" clearable />
        <el-input-number v-model="form.maxDepth" :min="1" :max="8" :step="1" size="small" style="width: 100px" title="路径最大深度" />
        <el-input-number v-model="form.maxPaths" :min="1" :max="50" :step="5" size="small" style="width: 100px" title="最大返回路径数" />
        <el-select v-model="form.nodeTypes" multiple placeholder="中间节点类型" style="max-width: 200px" clearable>
          <el-option v-for="opt in nodeTypeOptions" :key="opt" :label="typeLabel(opt)" :value="opt" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="runQuery">{{ text.action }}</el-button>
      </div>
    </TcmPanel>

    <div v-if="description" class="glass-panel section-card compare-section" style="margin-top: 16px; padding: 12px 20px;">
      <div class="flex-row" style="gap: 12px; flex-wrap: wrap;">
        <el-tag type="info" effect="plain">{{ description }}</el-tag>
        <el-tag v-if="totalPaths" type="success" effect="plain">起点：{{ form.sourceName }}</el-tag>
        <el-tag v-if="totalPaths" type="warning" effect="plain">终点：{{ form.targetName }}</el-tag>
        <el-tag v-if="totalPaths" type="primary" effect="plain">深度 {{ form.maxDepth }}</el-tag>
        <el-tag v-if="form.nodeTypes.length" type="info" effect="plain">中间节点：{{ form.nodeTypes.map(typeLabel).join('、') }}</el-tag>
      </div>
    </div>

    <template v-if="paths.length">
      <div class="path-layout">
        <div class="path-list-panel">
          <TcmPanel title="路径列表" icon="path" :decorated="false">
            <div class="path-list-header">
              <span class="path-list-stat">共 {{ totalPaths }} 条路径，按长度升序</span>
            </div>
            <div class="path-list">
              <div
                v-for="(item, idx) in paths"
                :key="idx"
                class="path-card"
                :class="{ 'is-selected': selectedPathIndex === idx }"
                @click="selectPath(idx)"
              >
                <div class="path-card-head">
                  <span class="path-card-badge">#{{ idx + 1 }}</span>
                  <span class="path-card-length">长度 {{ item.length }}</span>
                  <span class="path-card-nodes">{{ item.nodes.length }} 节点</span>
                </div>
                <div class="path-card-types">{{ typeSequenceLabel(item.typeSequence) }}</div>
                <div class="path-card-names">{{ item.nameSequence.join(' -> ') }}</div>
              </div>
            </div>
          </TcmPanel>
        </div>

        <div class="path-detail-panel">
          <TcmPanel title="路径图谱" icon="graph" :decorated="false">
            <GraphCanvas :data="graphData" :height="360" />
          </TcmPanel>

          <TcmPanel v-if="selectedPath" title="节点详情" icon="entity" :decorated="false" class="spaced">
            <el-table :data="selectedPath.nodes" size="small" border max-height="320">
              <el-table-column prop="name" label="名称" min-width="120" />
              <el-table-column label="类型" width="80">
                <template #default="{ row }">{{ typeLabel(row.type) }}</template>
              </el-table-column>
              <el-table-column prop="source" label="来源" min-width="140" />
              <el-table-column label="来源医案" min-width="140">
                <template #default="{ row }">
                  <span v-if="row.sourceCases?.length">{{ row.sourceCases.join('、') }}</span>
                  <span v-else class="empty-text">-</span>
                </template>
              </el-table-column>
              <el-table-column label="来源批次" min-width="120">
                <template #default="{ row }">
                  <span v-if="row.sourceBatches?.length">{{ row.sourceBatches[0] }}</span>
                  <span v-else class="empty-text">-</span>
                </template>
              </el-table-column>
            </el-table>
          </TcmPanel>
        </div>
      </div>
    </template>

    <TcmPanel v-else-if="!loading" title="路径图谱" icon="graph" class="spaced" :decorated="false">
      <TcmEmpty text="点击「查询路径」开始探索实体间的语义链路" />
    </TcmPanel>
  </TcmPageShell>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.path-layout {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  align-items: flex-start;
}
.path-list-panel {
  flex: 0 0 360px;
  min-width: 0;
}
.path-detail-panel {
  flex: 1;
  min-width: 0;
}
.path-list-header {
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--tcm-text-secondary);
}
.path-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
}
.path-card {
  background: var(--tcm-card);
  border: 1px solid var(--tcm-border);
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.path-card:hover {
  border-color: var(--tcm-accent);
  box-shadow: 0 2px 8px rgba(139, 110, 74, 0.12);
}
.path-card.is-selected {
  border-color: var(--tcm-accent);
  background: rgba(139, 110, 74, 0.06);
  box-shadow: 0 0 0 2px rgba(139, 110, 74, 0.15);
}
.path-card-head {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}
.path-card-badge {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  background: var(--tcm-accent);
  border-radius: 6px;
  padding: 0 7px;
  line-height: 18px;
}
.path-card-length {
  font-size: 12px;
  font-weight: 600;
  color: var(--tcm-text-primary);
}
.path-card-nodes {
  font-size: 11px;
  color: var(--tcm-text-secondary);
}
.path-card-types {
  font-size: 12px;
  color: var(--tcm-text-secondary);
  margin-bottom: 2px;
}
.path-card-names {
  font-size: 13px;
  color: var(--tcm-text-primary);
  word-break: break-all;
}
.spaced {
  margin-top: 16px;
}
.flex-row {
  display: flex;
  align-items: center;
}
.empty-text {
  color: var(--tcm-text-secondary);
  font-size: 12px;
}
</style>