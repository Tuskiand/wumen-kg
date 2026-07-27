<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getDashboardStats, getImportTasks } from '@/api';
import type { ImportTask } from '@/types';

const text = {
  nodeCount: '图谱节点数',
  edgeCount: '图谱关系数',
  rate: '导入成功率',
  publishAt: '最近发布时间',
  tasks: '最近导入任务',
  name: '任务名称',
  status: '状态',
  createdAt: '创建时间',
  summary: '摘要',
};
const stats = ref({
  nodeCount: 0,
  edgeCount: 0,
  importSuccessRate: 0,
  lastPublishAt: '',
});
const tasks = ref<ImportTask[]>([]);

onMounted(async () => {
  stats.value = await getDashboardStats();
  tasks.value = await getImportTasks();
});
</script>

<template>
  <section>
    <div class="stats-grid">
      <div class="glass-panel stat-card">
        <div class="stat-label">{{ text.nodeCount }}</div>
        <div class="stat-value">{{ stats.nodeCount }}</div>
      </div>
      <div class="glass-panel stat-card">
        <div class="stat-label">{{ text.edgeCount }}</div>
        <div class="stat-value">{{ stats.edgeCount }}</div>
      </div>
      <div class="glass-panel stat-card">
        <div class="stat-label">{{ text.rate }}</div>
        <div class="stat-value">{{ stats.importSuccessRate }}%</div>
      </div>
      <div class="glass-panel stat-card">
        <div class="stat-label">{{ text.publishAt }}</div>
        <div class="stat-value" style="font-size: 20px">{{ stats.lastPublishAt }}</div>
      </div>
    </div>

    <div class="glass-panel section-card" style="margin-top: 20px">
      <h2 class="section-title">{{ text.tasks }}</h2>
      <el-table :data="tasks">
        <el-table-column prop="name" :label="text.name" min-width="220" />
        <el-table-column prop="status" :label="text.status" width="140" />
        <el-table-column prop="createdAt" :label="text.createdAt" width="180" />
        <el-table-column prop="summary" :label="text.summary" min-width="280" />
      </el-table>
    </div>
  </section>
</template>
