<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { getEntityDetail } from '@/api';
import TcmEmpty from '@/components/tcm/TcmEmpty.vue';
import TcmPageShell from '@/components/tcm/TcmPageShell.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import type { GraphEdge, GraphNode } from '@/types';

const text = {
  relation: '关联关系',
  neighbor: '相邻节点',
  back: '回到图谱',
  source: '起点',
  relationType: '关系类型',
  target: '终点',
  sourceCases: '来源医案',
  sourceBatches: '导入批次',
};
const route = useRoute();
const entity = ref<GraphNode | null>(null);
const neighbors = ref<GraphNode[]>([]);
const relations = ref<GraphEdge[]>([]);
const backToGraph = computed(() => (route.path.startsWith('/admin/') ? '/admin/graph' : '/portal/graph'));

onMounted(async () => {
  const result = await getEntityDetail(String(route.params.id));
  entity.value = result.entity;
  neighbors.value = result.neighbors;
  relations.value = result.relations;
});
</script>

<template>
  <TcmPageShell
    v-if="entity"
    :title="entity.name"
    :subtitle="entity.summary || '知识图谱实体条目'"
    icon="entity"
  >
    <TcmPanel title="实体信息" icon="entity" bamboo>
      <div class="toolbar">
        <el-tag type="primary">{{ entity.type }}</el-tag>
        <el-tag>{{ entity.source }}</el-tag>
        <el-button type="primary" plain tag="router-link" :to="backToGraph">{{ text.back }}</el-button>
      </div>
      <div class="meta-block">
        <div>
          <div class="meta-title">{{ text.sourceCases }}</div>
          <el-tag v-for="item in entity.sourceCases" :key="item" style="margin-right: 8px; margin-top: 8px">{{ item }}</el-tag>
        </div>
        <div>
          <div class="meta-title">{{ text.sourceBatches }}</div>
          <el-tag v-for="item in entity.sourceBatches" :key="item" type="success" style="margin-right: 8px; margin-top: 8px">{{ item }}</el-tag>
        </div>
      </div>
    </TcmPanel>

    <div class="content-grid">
      <TcmPanel :title="text.relation" icon="relation" :decorated="false">
        <TcmEmpty v-if="!relations.length" text="暂无关联关系" />
        <el-table v-else :data="relations">
          <el-table-column prop="source" :label="text.source" />
          <el-table-column prop="type" :label="text.relationType" />
          <el-table-column prop="target" :label="text.target" />
        </el-table>
      </TcmPanel>
      <TcmPanel :title="text.neighbor" icon="graph" :decorated="false">
        <TcmEmpty v-if="!neighbors.length" text="暂无相邻节点" />
        <div v-else class="tag-row">
          <el-tag v-for="node in neighbors" :key="node.id" size="large">
            {{ node.name }}
          </el-tag>
        </div>
      </TcmPanel>
    </div>
  </TcmPageShell>
</template>

<style scoped>
.meta-block {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.meta-title {
  color: var(--text-sub);
  font-size: 13px;
}
</style>
