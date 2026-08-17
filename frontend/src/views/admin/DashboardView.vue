<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { getAiConfig, getDashboardStats, getImportTasks, testAiConnection, updateAiConfig } from '@/api';
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
  aiTitle: 'AI 大模型配置',
  aiDesc: '配置用于医家比较 AI 分析解读的大模型参数，支持 OpenAI 兼容协议。',
  apiKey: 'API Key',
  baseUrl: 'Base URL',
  model: '模型名称',
  save: '保存配置',
  saved: '配置已保存',
  testing: '连接测试中...',
};
const stats = ref({
  nodeCount: 0,
  edgeCount: 0,
  importSuccessRate: 0,
  lastPublishAt: '',
});
const tasks = ref<ImportTask[]>([]);
const aiForm = reactive({
  apiKey: '',
  baseUrl: 'https://api.deepseek.com/v1',
  model: 'deepseek-chat',
});
const saving = ref(false);
const hasKey = ref(false);
const aiTesting = ref(false);
const aiTestResult = ref('');

onMounted(async () => {
  stats.value = await getDashboardStats();
  tasks.value = await getImportTasks();
  try {
    const config = await getAiConfig();
    aiForm.baseUrl = config.baseUrl;
    aiForm.model = config.model;
    hasKey.value = config.hasKey;
  } catch {
    // 默认值
  }
});

async function saveAiConfig() {
  saving.value = true;
  try {
    const result = await updateAiConfig({
      api_key: aiForm.apiKey,
      base_url: aiForm.baseUrl,
      model: aiForm.model,
    });
    hasKey.value = result.hasKey;
    aiForm.apiKey = '';
    ElMessage.success(text.saved);
  } finally {
    saving.value = false;
  }
}

async function testConnection() {
  aiTesting.value = true;
  aiTestResult.value = '';
  try {
    const key = aiForm.apiKey || (hasKey.value ? '已保存的 Key' : '');
    if (!key) {
      ElMessage.warning('请先输入 API Key');
      return;
    }
    const result = await testAiConnection({
      api_key: aiForm.apiKey,
      base_url: aiForm.baseUrl,
      model: aiForm.model,
    });
    aiTestResult.value = result.message;
    if (result.success) {
      ElMessage.success(result.message);
    } else {
      ElMessage.error(result.message);
    }
  } finally {
    aiTesting.value = false;
  }
}
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

    <div class="glass-panel section-card" style="margin-top: 20px">
      <h2 class="section-title">{{ text.aiTitle }}</h2>
      <p class="ai-desc">{{ text.aiDesc }}</p>
      <el-alert
        v-if="hasKey"
        type="success"
        title="已配置 API Key，AI 分析解读功能可用"
        :closable="false"
        style="margin: 12px 0"
      />
      <el-form label-width="110px" style="max-width: 640px">
        <el-form-item label="API Key">
          <el-input
            v-model="aiForm.apiKey"
            type="password"
            show-password
            :placeholder="hasKey ? '已保存（留空则保持不变）' : '请输入大模型 API Key'"
          />
        </el-form-item>
        <el-form-item :label="text.baseUrl">
          <el-input v-model="aiForm.baseUrl" placeholder="https://api.deepseek.com/v1" />
        </el-form-item>
        <el-form-item :label="text.model">
          <el-input v-model="aiForm.model" placeholder="deepseek-chat" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="saveAiConfig">{{ text.save }}</el-button>
          <el-button :loading="aiTesting" @click="testConnection" style="margin-left: 12px">测试连接</el-button>
          <span v-if="aiTestResult" :class="aiTestResult.includes('成功') ? 'test-ok' : 'test-fail'" style="margin-left: 12px">{{ aiTestResult }}</span>
        </el-form-item>
      </el-form>
    </div>
  </section>
</template>

<style scoped>
.ai-desc {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}
</style>
