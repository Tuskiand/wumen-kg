<script setup lang="ts">
import { reactive, ref } from 'vue';
import GraphCanvas from '@/components/GraphCanvas.vue';
import { queryPath } from '@/api';
import TcmEmpty from '@/components/tcm/TcmEmpty.vue';
import TcmPageShell from '@/components/tcm/TcmPageShell.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import type { GraphSnapshot } from '@/types';

const text = {
  title: '路径查询',
  subtitle: '查看两个实体之间的语义链路，并可限定来源医案。',
  sourcePlaceholder: '起点实体名称',
  targetPlaceholder: '终点实体名称',
  sourceCasePlaceholder: '可选：来源医案',
  action: '查询路径',
  summary: '输入起点和终点后，展示图谱路径。',
};
const form = reactive({
  sourceName: '中风',
  targetName: '痰阻清窍',
  sourceCase: '',
});

const summary = ref(text.summary);
const graphData = ref<GraphSnapshot>({ nodes: [], edges: [] });

async function runQuery() {
  const result = await queryPath(form.sourceName, form.targetName, form.sourceCase);
  graphData.value = { nodes: result.nodes, edges: result.edges };
  summary.value = result.description;
}
</script>

<template>
  <TcmPageShell :title="text.title" :subtitle="text.subtitle" icon="path">
    <TcmPanel title="查询条件" icon="path">
      <div class="toolbar">
        <el-input v-model="form.sourceName" :placeholder="text.sourcePlaceholder" style="max-width: 220px" />
        <el-input v-model="form.targetName" :placeholder="text.targetPlaceholder" style="max-width: 220px" />
        <el-input v-model="form.sourceCase" :placeholder="text.sourceCasePlaceholder" style="max-width: 240px" clearable />
        <el-button type="primary" @click="runQuery">{{ text.action }}</el-button>
      </div>
      <el-alert :title="summary" type="info" :closable="false" style="margin-top: 20px" />
    </TcmPanel>

    <TcmPanel title="路径图谱" icon="graph" class="spaced" :decorated="false">
      <TcmEmpty v-if="!graphData.nodes.length" text="当前条件下暂无路径结果" />
      <GraphCanvas v-else :data="graphData" :height="480" />
    </TcmPanel>
  </TcmPageShell>
</template>
