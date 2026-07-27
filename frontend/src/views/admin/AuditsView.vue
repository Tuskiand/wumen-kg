<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getAuditRecords } from '@/api';
import type { AuditRecord } from '@/types';

const text = {
  title: '审计日志',
  subtitle: '记录导入、编辑、发布、回滚等关键动作，为生产环境接入真实日志接口预留结构。',
  actor: '操作人',
  action: '操作类型',
  target: '对象',
  createdAt: '时间',
  result: '结果',
};
const rows = ref<AuditRecord[]>([]);

onMounted(async () => {
  rows.value = await getAuditRecords();
});
</script>

<template>
  <section class="glass-panel section-card">
    <h1 class="page-title">{{ text.title }}</h1>
    <p class="page-subtitle">{{ text.subtitle }}</p>
    <el-table :data="rows" style="margin-top: 20px">
      <el-table-column prop="actor" :label="text.actor" width="120" />
      <el-table-column prop="action" :label="text.action" width="140" />
      <el-table-column prop="target" :label="text.target" min-width="180" />
      <el-table-column prop="createdAt" :label="text.createdAt" width="180" />
      <el-table-column prop="result" :label="text.result" width="120" />
    </el-table>
  </section>
</template>
