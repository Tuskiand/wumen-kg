<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getVersionRecords } from '@/api';
import type { VersionRecord } from '@/types';

const text = {
  title: '版本管理',
  subtitle: '用于导入批次的发布与回滚，保持图谱数据可追溯。',
  publish: '发布版本',
  rollback: '回滚到已发布版本',
  id: '版本号',
  name: '版本名称',
  createdAt: '创建时间',
  status: '状态',
};
const rows = ref<VersionRecord[]>([]);

onMounted(async () => {
  rows.value = await getVersionRecords();
});
</script>

<template>
  <section class="glass-panel section-card">
    <h1 class="page-title">{{ text.title }}</h1>
    <p class="page-subtitle">{{ text.subtitle }}</p>
    <div class="toolbar">
      <el-button type="primary">{{ text.publish }}</el-button>
      <el-button type="warning" plain>{{ text.rollback }}</el-button>
    </div>
    <el-table :data="rows" style="margin-top: 20px">
      <el-table-column prop="id" :label="text.id" width="160" />
      <el-table-column prop="name" :label="text.name" min-width="200" />
      <el-table-column prop="createdAt" :label="text.createdAt" width="180" />
      <el-table-column prop="status" :label="text.status" width="140" />
    </el-table>
  </section>
</template>
