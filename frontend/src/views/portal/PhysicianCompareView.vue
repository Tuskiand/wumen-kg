<script setup lang="ts">
import type { ECharts } from 'echarts';
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import TcmEmpty from '@/components/tcm/TcmEmpty.vue';
import TcmPageShell from '@/components/tcm/TcmPageShell.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import {
  analyzePhysicianCompare,
  comparePhysicianNodes,
  comparePhysicianPaths,
  comparePhysicianSubgraphs,
  downloadPhysicianCompareReport,
  downloadPhysicianSubgraphExport,
  getAiConfig,
  testAiConnection,
  updateAiConfig,
} from '@/api';
import {
  axisStyle,
  chartFontFamily,
  chartPalette,
  heatStyle as buildAncientHeatStyle,
  initAncientTcmChart,
  tcmChartColors,
  tooltipStyle,
  withAncientChartBase,
} from '@/styles/echarts-theme';
import type {
  CompareNode,
  PhysicianNodeCompareResponse,
  PhysicianPathChain,
  PhysicianPathCompareResponse,
  PhysicianPathProfile,
  PhysicianNodeProfile,
  PhysicianNodeRwrResult,
  PhysicianSimilarityPair,
  PhysicianSubgraphCompareResponse,
  PhysicianSubgraphProfile,
  RankedGraphNode,
} from '@/types';

type TabKey = 'nodes' | 'paths' | 'subgraphs';
type MetricKey = 'jaccard' | 'overlap' | 'cosine';
type MatrixCategoryKey = 'overall' | 'patterns' | 'causes' | 'mechanisms';
type NodeCategoryKey = 'patterns' | 'causes' | 'mechanisms';
type NodeSimilaritySource = 'explicit' | 'fastrp';

const text = {
  title: '医家比较',
  subtitle: '节点、辨证路径、核心子图三层一起比较，只保留需求说明书里的算法。',
  diseasePlaceholder: '病名',
  action: '开始比较',
};

const tabLabels: Record<TabKey, string> = {
  nodes: '节点比较',
  paths: '辨证路径比较',
  subgraphs: '子图比较',
};

const categoryLabels: Record<MatrixCategoryKey, string> = {
  overall: '总体',
  patterns: '证型',
  causes: '病因',
  mechanisms: '病机',
};

const metricLabels: Record<MetricKey, string> = {
  jaccard: 'Jaccard',
  overlap: 'Overlap',
  cosine: 'Cosine',
};

const categoryMeta: Record<NodeCategoryKey, { label: string; className: string }> = {
  patterns: { label: '证型', className: 'pattern' },
  causes: { label: '病因', className: 'cause' },
  mechanisms: { label: '病机', className: 'mechanism' },
};

const filters = reactive({ disease: '中风' });
const loading = ref(false);
const nodeResult = ref<PhysicianNodeCompareResponse | null>(null);
const pathResult = ref<PhysicianPathCompareResponse | null>(null);
const subgraphResult = ref<PhysicianSubgraphCompareResponse | null>(null);
const exportingSubgraphs = ref(false);
const exportingReport = ref(false);
const activeTab = ref<TabKey>('nodes');
const activeMetric = ref<MetricKey>('jaccard');
const activeMatrixCategory = ref<MatrixCategoryKey>('overall');
const activeNodeSimilaritySource = ref<NodeSimilaritySource>('explicit');
const nodeCategories: NodeCategoryKey[] = ['patterns', 'causes', 'mechanisms'];
const matrixCategories: MatrixCategoryKey[] = ['overall', 'patterns', 'causes', 'mechanisms'];
const nodeSimilaritySourceLabels: Record<NodeSimilaritySource, string> = {
  explicit: '显性节点',
  fastrp: 'FastRP',
};
const aiAnalysis = ref('');
const aiModel = ref('');
const aiLoading = ref(false);
const aiConfigVisible = ref(false);
const aiConfigForm = reactive({
  apiKey: '',
  baseUrl: 'https://api.deepseek.com/v1',
  model: 'deepseek-chat',
});
const aiConfigSaving = ref(false);
const aiHasKey = ref(false);
const aiTesting = ref(false);
const aiTestResult = ref('');
const timingState = reactive({
  totalMs: 0,
  nodeMs: 0,
  pathMs: 0,
  subgraphMs: 0,
  reportTotalMs: 0,
  reportFigureMs: 0,
  reportWordMs: 0,
});
const nodeRadarRef = ref<HTMLDivElement | null>(null);
const nodeScatterRef = ref<HTMLDivElement | null>(null);
const pathScatterRef = ref<HTMLDivElement | null>(null);
const subgraphScatterRef = ref<HTMLDivElement | null>(null);
const chartInstances: Partial<Record<'nodeRadar' | 'nodeScatter' | 'pathScatter' | 'subgraphScatter', ECharts>> = {};

const doctorNames = computed(() => nodeResult.value?.doctors.map((doctor) => doctor.name) ?? []);
const currentNodeSimilarityGroup = computed(() => {
  if (!nodeResult.value) return null;
  return activeNodeSimilaritySource.value === 'fastrp' ? nodeResult.value.fastrpSimilarity : nodeResult.value.similarity;
});
const currentMatrixPairs = computed<PhysicianSimilarityPair[]>(() => {
  return currentNodeSimilarityGroup.value?.[activeMatrixCategory.value] ?? [];
});
const currentSharedNodes = computed(() => nodeResult.value?.sharedNodes ?? null);
const rwrResults = computed(() => nodeResult.value?.rwr ?? []);
const pathDoctorNames = computed(() => pathResult.value?.doctors.map((doctor) => doctor.name) ?? []);
const subgraphDoctorNames = computed(() => subgraphResult.value?.doctors.map((doctor) => doctor.name) ?? []);
const pathCompletenessRows = computed(() => {
  return pathResult.value?.doctorProfiles.map((item) => ({
    doctor: item.doctor.name,
    completeCount: item.completeness.completeCount,
    partialCount: item.completeness.partialCount,
    singleCount: item.completeness.singleCount,
    completeRatio: item.completeness.completeRatio,
    pathCoverage: item.completeness.pathCoverage,
  })) ?? [];
});
const nodeFeatureEmbeddingRows = computed(() => {
  return nodeResult.value?.doctorFeatureEmbeddings.map((item) => ({
    doctor: item.doctor.name,
    patternDimension: item.patterns.length,
    causeDimension: item.causes.length,
    mechanismDimension: item.mechanisms.length,
    overallDimension: item.overall.length,
  })) ?? [];
});
const pathEmbeddingRows = computed(() => {
  return pathResult.value?.embeddings.map((item) => ({
    doctor: item.doctor.name,
    dimension: item.vector.length,
    preview: vectorPreview(item.vector),
  })) ?? [];
});
const subgraphEmbeddingRows = computed(() => {
  return subgraphResult.value?.embeddings.map((item) => ({
    doctor: item.doctor.name,
    graph2vecDimension: item.graph2vecVector.length,
    graph2vecPreview: vectorPreview(item.graph2vecVector),
  })) ?? [];
});

async function runAnalysis() {
  loading.value = true;
  const totalStart = performance.now();
  try {
    const nodePromise = timedCall(() => comparePhysicianNodes(filters.disease));
    const pathPromise = timedCall(() => comparePhysicianPaths(filters.disease));
    const subgraphPromise = timedCall(() => comparePhysicianSubgraphs(filters.disease));
    const [nodePayload, pathPayload, subgraphPayload] = await Promise.all([nodePromise, pathPromise, subgraphPromise]);
    nodeResult.value = nodePayload.result;
    pathResult.value = pathPayload.result;
    subgraphResult.value = subgraphPayload.result;
    timingState.nodeMs = nodePayload.elapsedMs;
    timingState.pathMs = pathPayload.elapsedMs;
    timingState.subgraphMs = subgraphPayload.elapsedMs;
    timingState.totalMs = Math.round(performance.now() - totalStart);
    activeTab.value = 'nodes';
    aiAnalysis.value = '';
    aiModel.value = '';
  } finally {
    loading.value = false;
  }
}

async function runAiAnalysis() {
  aiLoading.value = true;
  try {
    const doctors = (nodeResult.value?.doctors ?? []).map((d) => d.name);
    const result = await analyzePhysicianCompare(filters.disease, doctors);
    aiAnalysis.value = result.analysis;
    aiModel.value = result.model;
  } finally {
    aiLoading.value = false;
  }
}

async function openAiConfig() {
  try {
    const config = await getAiConfig();
    aiConfigForm.baseUrl = config.baseUrl;
    aiConfigForm.model = config.model;
    aiHasKey.value = config.hasKey;
  } catch {
    // 默认值
  }
  aiConfigForm.apiKey = '';
  aiConfigVisible.value = true;
}

async function saveAiConfig() {
  aiConfigSaving.value = true;
  try {
    const result = await updateAiConfig({
      api_key: aiConfigForm.apiKey,
      base_url: aiConfigForm.baseUrl,
      model: aiConfigForm.model,
    });
    aiHasKey.value = result.hasKey;
    aiConfigForm.apiKey = '';
    ElMessage.success('AI 配置已保存');
    aiConfigVisible.value = false;
  } finally {
    aiConfigSaving.value = false;
  }
}

async function testConnection() {
  aiTesting.value = true;
  aiTestResult.value = '';
  try {
    const key = aiConfigForm.apiKey || (aiHasKey.value ? '已保存的 Key' : '');
    if (!key) {
      ElMessage.warning('请先输入 API Key');
      return;
    }
    const result = await testAiConnection({
      api_key: aiConfigForm.apiKey,
      base_url: aiConfigForm.baseUrl,
      model: aiConfigForm.model,
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

async function exportSubgraphs() {
  const disease = filters.disease.trim();
  if (!disease) {
    ElMessage.warning('请输入病名');
    return;
  }
  exportingSubgraphs.value = true;
  try {
    await downloadPhysicianSubgraphExport(disease);
    ElMessage.success('子图导出完成');
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '子图导出失败');
  } finally {
    exportingSubgraphs.value = false;
  }
}

async function exportReport() {
  const disease = filters.disease.trim();
  if (!disease) {
    ElMessage.warning('请输入病名');
    return;
  }
  exportingReport.value = true;
  const exportStart = performance.now();
  try {
    const result = await downloadPhysicianCompareReport(disease);
    timingState.reportFigureMs = result.figureMs;
    timingState.reportWordMs = result.wordMs;
    timingState.reportTotalMs = result.totalMs || Math.round(performance.now() - exportStart);
    ElMessage.success('论文包导出完成');
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '论文包导出失败');
  } finally {
    exportingReport.value = false;
  }
}

function pairScore(leftDoctor: string, rightDoctor: string) {
  if (leftDoctor === rightDoctor) return 1;
  const pair = currentMatrixPairs.value.find((item) => {
    return (
      (item.leftDoctor === leftDoctor && item.rightDoctor === rightDoctor) ||
      (item.leftDoctor === rightDoctor && item.rightDoctor === leftDoctor)
    );
  });
  if (!pair) return 0;
  return pair[activeMetric.value];
}

function heatStyle(score: number) {
  return buildAncientHeatStyle(score);
}

function categoryNodes(group: Record<NodeCategoryKey, CompareNode[]>, category: NodeCategoryKey) {
  return group[category] ?? [];
}

function topNames(items: RankedGraphNode[], limit = 5) {
  return items.length ? items.slice(0, limit).map((item) => item.name).join('、') : '暂无';
}

function doctorRwr(doctorName: string): PhysicianNodeRwrResult | undefined {
  return rwrResults.value.find((item) => item.doctor.name === doctorName);
}

function doctorProfile(doctorName: string): PhysicianNodeProfile | undefined {
  return nodeResult.value?.doctorProfiles.find((item) => item.doctor.name === doctorName);
}

function pathProfile(doctorName: string): PhysicianPathProfile | undefined {
  return pathResult.value?.doctorProfiles.find((item) => item.doctor.name === doctorName);
}

function subgraphProfile(doctorName: string): PhysicianSubgraphProfile | undefined {
  return subgraphResult.value?.doctorProfiles.find((item) => item.doctor.name === doctorName);
}

function pathTypeLabel(pathType: string) {
  const labels: Record<string, string> = {
    'D-E-C': '完整链',
    'D-E': '病因-病机',
    'E-C': '病机-证型',
    'D-C': '病因-证型',
    D: '病因单点',
    E: '病机单点',
    C: '证型单点',
  };
  return labels[pathType] ?? pathType;
}

function pathRows(paths: PhysicianPathChain[]) {
  return paths.map((item) => ({
    pathType: pathTypeLabel(item.pathType),
    text: item.text,
  }));
}

function ratioText(value: number) {
  return `${(value * 100).toFixed(0)}%`;
}

function vectorPreview(values: number[], limit = 6) {
  if (!values.length) return '暂无';
  return values.slice(0, limit).map((item) => item.toFixed(3)).join(', ');
}

function formatDuration(ms: number) {
  if (!ms) return '0 ms';
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(2)} s`;
}

async function timedCall<T>(runner: () => Promise<T>) {
  const startedAt = performance.now();
  const result = await runner();
  return {
    result,
    elapsedMs: Math.round(performance.now() - startedAt),
  };
}

function disposeChart(key: keyof typeof chartInstances) {
  chartInstances[key]?.dispose();
  delete chartInstances[key];
}

async function renderChart(key: keyof typeof chartInstances, container: HTMLDivElement | null, option: Record<string, unknown>) {
  if (!container) return;
  const echarts = await import('echarts');
  const instance = chartInstances[key] ?? initAncientTcmChart(echarts, container);
  chartInstances[key] = instance;
  instance.resize();
  instance.setOption(option as never, true);
}

function scatterOption(title: string, points: { label: string; group: string; x: number; y: number }[]) {
  const groups = Array.from(new Set(points.map((item) => item.group)));
  return withAncientChartBase({
    title: {
      text: title,
      left: 'center',
      textStyle: {
        color: tcmChartColors.primaryDark,
        fontFamily: chartFontFamily,
        fontSize: 14,
        fontWeight: 700,
      },
    },
    tooltip: {
      ...tooltipStyle,
      trigger: 'item',
      formatter: (params: { seriesName: string; data: [number, number, string] }) =>
        `${params.data[2]}<br/>${params.seriesName}<br/>x=${params.data[0].toFixed(3)}, y=${params.data[1].toFixed(3)}`,
    },
    legend: {
      bottom: 0,
      textStyle: {
        color: tcmChartColors.textSecondary,
        fontFamily: chartFontFamily,
      },
    },
    grid: { left: 16, right: 16, top: 48, bottom: 48, containLabel: true },
    xAxis: { ...axisStyle, name: 'PCA-1', nameLocation: 'middle', nameGap: 26 },
    yAxis: { ...axisStyle, name: 'PCA-2', nameLocation: 'middle', nameGap: 40 },
    series: groups.map((group, index) => ({
      name: group,
      type: 'scatter',
      symbolSize: 14,
      itemStyle: { color: chartPalette[index % chartPalette.length] },
      label: {
        show: true,
        position: 'top',
        formatter: (params: { data: [number, number, string] }) => params.data[2],
        color: tcmChartColors.primaryDark,
        fontFamily: chartFontFamily,
        fontSize: 11,
      },
      data: points.filter((item) => item.group === group).map((item) => [item.x, item.y, item.label]),
    })),
  });
}

function radarOption() {
  const rows = nodeResult.value?.similarityOverview ?? [];
  const indicators = [
    { name: '证型', max: 1 },
    { name: '病因', max: 1 },
    { name: '病机', max: 1 },
    { name: '总体', max: 1 },
  ];
  return withAncientChartBase({
    tooltip: { ...tooltipStyle, trigger: 'item' },
    legend: {
      bottom: 0,
      textStyle: {
        color: tcmChartColors.textSecondary,
        fontFamily: chartFontFamily,
      },
    },
    radar: {
      radius: '62%',
      indicator: indicators,
      axisName: {
        color: tcmChartColors.primaryDark,
        fontFamily: chartFontFamily,
      },
      splitLine: { lineStyle: { color: tcmChartColors.border } },
      axisLine: { lineStyle: { color: tcmChartColors.border } },
      splitArea: { areaStyle: { color: ['rgba(251, 247, 239, 0.72)', 'rgba(239, 230, 214, 0.42)'] } },
    },
    series: [
      {
        type: 'radar',
        areaStyle: { opacity: 0.12 },
        lineStyle: { width: 2 },
        data: rows.map((item) => ({
          name: item.doctor.name,
          value: [item.scores.patterns, item.scores.causes, item.scores.mechanisms, item.scores.overall],
        })),
      },
    ],
  });
}

async function renderCharts() {
  if (nodeResult.value?.similarityOverview.length) {
    await renderChart('nodeRadar', nodeRadarRef.value, radarOption());
  } else {
    disposeChart('nodeRadar');
  }
  if (nodeResult.value?.embeddingPoints.length) {
    await renderChart('nodeScatter', nodeScatterRef.value, scatterOption('FastRP 特征分布', nodeResult.value.embeddingPoints));
  } else {
    disposeChart('nodeScatter');
  }
  if (pathResult.value?.embeddingPoints.length) {
    await renderChart('pathScatter', pathScatterRef.value, scatterOption('Metapath2Vec 医家分布', pathResult.value.embeddingPoints));
  } else {
    disposeChart('pathScatter');
  }
  if (subgraphResult.value?.embeddingPoints.length) {
    await renderChart('subgraphScatter', subgraphScatterRef.value, scatterOption('Graph2Vec 医家分布', subgraphResult.value.embeddingPoints));
  } else {
    disposeChart('subgraphScatter');
  }
}

onMounted(runAnalysis);

watch([nodeResult, pathResult, subgraphResult], async () => {
  await nextTick();
  await renderCharts();
});

onMounted(() => {
  window.addEventListener('resize', renderCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderCharts);
  disposeChart('nodeRadar');
  disposeChart('nodeScatter');
  disposeChart('pathScatter');
  disposeChart('subgraphScatter');
});
</script>

<template>
  <TcmPageShell :title="text.title" :subtitle="text.subtitle" icon="compare">
    <TcmPanel title="分析条件" icon="analytics">
      <div class="toolbar">
        <el-input v-model="filters.disease" :placeholder="text.diseasePlaceholder" style="max-width: 220px" clearable />
        <el-button type="primary" :loading="loading" @click="runAnalysis">{{ text.action }}</el-button>
        <el-button type="success" plain :loading="exportingReport" @click="exportReport">导出论文包</el-button>
      </div>
      <div class="timing-strip">
        <el-tag type="info" effect="plain">分析总耗时：{{ formatDuration(timingState.totalMs) }}</el-tag>
        <el-tag type="primary" effect="plain">节点：{{ formatDuration(timingState.nodeMs) }}</el-tag>
        <el-tag type="success" effect="plain">路径：{{ formatDuration(timingState.pathMs) }}</el-tag>
        <el-tag type="warning" effect="plain">子图：{{ formatDuration(timingState.subgraphMs) }}</el-tag>
        <el-tag type="danger" effect="plain">论文包：{{ formatDuration(timingState.reportTotalMs) }}</el-tag>
        <el-tag v-if="timingState.reportFigureMs" type="info" effect="plain">绘图：{{ formatDuration(timingState.reportFigureMs) }}</el-tag>
        <el-tag v-if="timingState.reportWordMs" type="success" effect="plain">Word：{{ formatDuration(timingState.reportWordMs) }}</el-tag>
      </div>
    </TcmPanel>

    <el-tabs v-model="activeTab" class="compare-tabs">
      <el-tab-pane :label="tabLabels.nodes" name="nodes">
        <div v-if="nodeResult && !nodeResult.doctorCount" class="glass-panel section-card compare-section">
          <TcmEmpty text="当前病名没有可比较的医家数据" />
        </div>

        <template v-if="nodeResult && nodeResult.doctorCount">
          <div class="glass-panel section-card compare-section conclusion-panel">
            <div class="conclusion-kicker">总览</div>
            <div class="conclusion-text">{{ nodeResult.summary.message }}</div>
            <div class="conclusion-tags">
              <el-tag type="primary" effect="plain">病名：{{ nodeResult.disease }}</el-tag>
              <el-tag type="success" effect="plain">医家：{{ nodeResult.doctorCount }} 位</el-tag>
              <el-tag type="info" effect="plain">主指标：{{ nodeResult.summary.primarySimilarityMetric }}</el-tag>
              <el-tag type="success" effect="plain">嵌入：{{ nodeResult.summary.primaryEmbeddingMetric }}</el-tag>
              <el-tag type="warning" effect="plain">两两比较：{{ nodeResult.summary.pairwiseComparisonCount }}</el-tag>
              <el-tag type="warning" effect="plain">RWR：{{ nodeResult.summary.primaryRestartProbability }}</el-tag>
              <el-tag type="danger" effect="plain">共同节点：{{ nodeResult.summary.sharedNodeCount }}</el-tag>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <div class="section-head">
                <h2 class="section-title">相似度矩阵</h2>
                <div class="control-stack">
                  <el-radio-group v-model="activeNodeSimilaritySource" size="small">
                    <el-radio-button v-for="source in ['explicit', 'fastrp']" :key="source" :label="source">
                      {{ nodeSimilaritySourceLabels[source as NodeSimilaritySource] }}
                    </el-radio-button>
                  </el-radio-group>
                  <el-radio-group v-model="activeMatrixCategory" size="small">
                    <el-radio-button v-for="category in matrixCategories" :key="category" :label="category">
                      {{ categoryLabels[category] }}
                    </el-radio-button>
                  </el-radio-group>
                  <el-radio-group v-model="activeMetric" size="small">
                    <el-radio-button v-for="metric in ['jaccard', 'overlap', 'cosine']" :key="metric" :label="metric">
                      {{ metricLabels[metric as MetricKey] }}
                    </el-radio-button>
                  </el-radio-group>
                </div>
              </div>
              <div class="matrix-note">
                当前展示：{{ nodeSimilaritySourceLabels[activeNodeSimilaritySource] }}。
                颜色越深，说明两位医家越接近。
              </div>
              <div v-if="doctorNames.length >= 2" class="matrix-scroll">
                <table class="matrix-table">
                  <thead>
                    <tr>
                      <th>医家</th>
                      <th v-for="doctorName in doctorNames" :key="`head-${doctorName}`">{{ doctorName }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="rowDoctor in doctorNames" :key="`row-${rowDoctor}`">
                      <td class="doctor-name">{{ rowDoctor }}</td>
                      <td v-for="columnDoctor in doctorNames" :key="`${rowDoctor}-${columnDoctor}`">
                        <div class="heat-box" :style="heatStyle(pairScore(rowDoctor, columnDoctor))">
                          {{ pairScore(rowDoctor, columnDoctor).toFixed(3) }}
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <TcmEmpty v-else text="当前只有 1 位医家，暂时没有两两相似度矩阵" />
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">共同节点</h2>
              <div v-if="currentSharedNodes" class="shared-list">
                <div v-for="category in nodeCategories" :key="category" class="shared-block">
                  <div class="block-title compact">{{ categoryMeta[category].label }}</div>
                  <div class="chip-row">
                    <span
                      v-for="item in currentSharedNodes[category]"
                      :key="`${category}-${item.node.name}`"
                      class="node-chip"
                      :class="categoryMeta[category].className"
                    >
                      {{ item.node.name }}
                      <small>{{ item.doctors.join('、') }}</small>
                    </span>
                    <span v-if="!currentSharedNodes[category].length" class="empty-text">暂无明显共同项</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">FastRP 医家雷达图</h2>
              <div ref="nodeRadarRef" class="chart-shell"></div>
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">FastRP 特征散点</h2>
              <div ref="nodeScatterRef" class="chart-shell"></div>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">显性与 FastRP 对照</h2>
              <el-table :data="nodeResult.similarityOverview" size="small" border>
                <el-table-column prop="doctor.name" label="医家" min-width="110" />
                <el-table-column label="证型" width="88">
                  <template #default="{ row }">{{ row.scores.patterns.toFixed(3) }}</template>
                </el-table-column>
                <el-table-column label="病因" width="88">
                  <template #default="{ row }">{{ row.scores.causes.toFixed(3) }}</template>
                </el-table-column>
                <el-table-column label="病机" width="88">
                  <template #default="{ row }">{{ row.scores.mechanisms.toFixed(3) }}</template>
                </el-table-column>
                <el-table-column label="总体" width="88">
                  <template #default="{ row }">{{ row.scores.overall.toFixed(3) }}</template>
                </el-table-column>
              </el-table>
              <div class="spacer-block">
                <h3 class="mini-title">医家向量维度</h3>
                <el-table :data="nodeFeatureEmbeddingRows" size="small" border>
                  <el-table-column prop="doctor" label="医家" min-width="110" />
                  <el-table-column prop="patternDimension" label="证型维度" width="96" />
                  <el-table-column prop="causeDimension" label="病因维度" width="96" />
                  <el-table-column prop="mechanismDimension" label="病机维度" width="96" />
                  <el-table-column prop="overallDimension" label="总体维度" width="96" />
                </el-table>
              </div>
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">相似节点候选</h2>
              <el-table :data="nodeResult.featureSimilarityCandidates" size="small" border>
                <el-table-column prop="category" label="类别" width="88" />
                <el-table-column prop="leftDoctor" label="医家A" width="92" />
                <el-table-column prop="leftFeatureName" label="节点A" min-width="120" />
                <el-table-column prop="rightDoctor" label="医家B" width="92" />
                <el-table-column prop="rightFeatureName" label="节点B" min-width="120" />
                <el-table-column label="相似度" width="92">
                  <template #default="{ row }">{{ row.similarity.toFixed(3) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <div class="glass-panel section-card compare-section">
            <h2 class="section-title">医家独特点</h2>
            <div class="profile-grid">
              <div v-for="doctorName in doctorNames" :key="doctorName" class="profile-card">
                <div class="profile-head">
                  <div class="profile-name">{{ doctorName }}</div>
                  <el-tag type="success" effect="plain">节点画像</el-tag>
                </div>
                <div v-if="doctorProfile(doctorName)" class="profile-body">
                  <div v-for="category in nodeCategories" :key="`${doctorName}-${category}`" class="profile-section">
                    <div class="profile-label">{{ categoryMeta[category].label }}</div>
                    <div class="profile-subtitle">独有节点</div>
                    <div class="chip-row">
                      <span
                        v-for="node in categoryNodes(doctorProfile(doctorName)!.unique, category)"
                        :key="node.id"
                        class="node-chip"
                        :class="categoryMeta[category].className"
                      >
                        {{ node.name }}
                      </span>
                      <span v-if="!categoryNodes(doctorProfile(doctorName)!.unique, category).length" class="empty-text">暂无明显独特点</span>
                    </div>
                    <div class="profile-subtitle">全部节点</div>
                    <div class="chip-row">
                      <span
                        v-for="node in categoryNodes(doctorProfile(doctorName)!.all, category)"
                        :key="`${node.id}-all`"
                        class="plain-chip"
                      >
                        {{ node.name }}
                      </span>
                      <span v-if="!categoryNodes(doctorProfile(doctorName)!.all, category).length" class="empty-text">暂无</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="glass-panel section-card compare-section">
            <h2 class="section-title">RWR 核心节点</h2>
            <div class="profile-grid">
              <div v-for="doctorName in doctorNames" :key="`rwr-${doctorName}`" class="profile-card">
                <div class="profile-head">
                  <div class="profile-name">{{ doctorName }}</div>
                  <el-tag type="warning" effect="plain">RWR {{ doctorRwr(doctorName)?.restartProbability ?? nodeResult.summary.primaryRestartProbability }}</el-tag>
                </div>
                <template v-if="doctorRwr(doctorName)">
                  <div class="rwr-block">
                    <div class="profile-label">核心证型</div>
                    <p class="rwr-text">{{ topNames(doctorRwr(doctorName)!.rankings.patterns) }}</p>
                  </div>
                  <div class="rwr-block">
                    <div class="profile-label">核心病因</div>
                    <p class="rwr-text">{{ topNames(doctorRwr(doctorName)!.rankings.causes) }}</p>
                  </div>
                  <div class="rwr-block">
                    <div class="profile-label">核心病机</div>
                    <p class="rwr-text">{{ topNames(doctorRwr(doctorName)!.rankings.mechanisms) }}</p>
                  </div>
                </template>
                <TcmEmpty v-else text="当前没有 RWR 结果" />
              </div>
            </div>
          </div>
        </template>
      </el-tab-pane>

      <el-tab-pane :label="tabLabels.paths" name="paths">
        <div v-if="pathResult && !pathResult.doctorCount" class="glass-panel section-card compare-section">
          <TcmEmpty text="当前病名没有可比较的辨证路径数据" />
        </div>

        <template v-if="pathResult && pathResult.doctorCount">
          <div class="glass-panel section-card compare-section conclusion-panel path-panel">
            <div class="conclusion-kicker">总览</div>
            <div class="conclusion-text">{{ pathResult.summary.message }}</div>
            <div class="conclusion-tags">
              <el-tag type="primary" effect="plain">病名：{{ pathResult.disease }}</el-tag>
              <el-tag type="success" effect="plain">医家：{{ pathResult.doctorCount }} 位</el-tag>
              <el-tag type="info" effect="plain">主指标：{{ pathResult.summary.primarySimilarityMetric }}</el-tag>
              <el-tag type="success" effect="plain">嵌入：{{ pathResult.summary.embeddingMetric }}</el-tag>
              <el-tag type="warning" effect="plain">共同辨证链：{{ pathResult.summary.sharedPathCount }}</el-tag>
              <el-tag type="info" effect="plain">两两比较：{{ pathResult.summary.pairwiseComparisonCount }}</el-tag>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">两两路径相似度</h2>
              <el-table :data="pathResult.similarityPairs" size="small" border>
                <el-table-column prop="leftDoctor" label="医家A" min-width="110" />
                <el-table-column prop="rightDoctor" label="医家B" min-width="110" />
                <el-table-column prop="sharedPathCount" label="共同链数" width="96" />
                <el-table-column prop="unionPathCount" label="总链数" width="88" />
                <el-table-column label="Path Jaccard" width="110">
                  <template #default="{ row }">{{ row.pathJaccard.toFixed(3) }}</template>
                </el-table-column>
                <el-table-column label="Metapath2Vec" width="116">
                  <template #default="{ row }">{{ row.metapath2vecCosine.toFixed(3) }}</template>
                </el-table-column>
              </el-table>
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">共同辨证链</h2>
              <div class="shared-list">
                <div class="chip-row">
                  <span
                    v-for="item in pathResult.sharedPaths"
                    :key="item.path.signature"
                    class="plain-chip path-chip"
                  >
                    {{ pathTypeLabel(item.path.pathType) }}：{{ item.path.text }}
                    <small>{{ item.doctors.join('、') }}</small>
                  </span>
                  <span v-if="!pathResult.sharedPaths.length" class="empty-text">暂无明显共同辨证链</span>
                </div>
              </div>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">路径完整度统计</h2>
              <el-table :data="pathCompletenessRows" size="small" border>
                <el-table-column prop="doctor" label="医家" min-width="110" />
                <el-table-column prop="completeCount" label="完整链" width="88" />
                <el-table-column prop="partialCount" label="部分链" width="88" />
                <el-table-column prop="singleCount" label="单点链" width="88" />
                <el-table-column label="完整率" width="88">
                  <template #default="{ row }">{{ ratioText(row.completeRatio) }}</template>
                </el-table-column>
                <el-table-column label="覆盖率" width="88">
                  <template #default="{ row }">{{ ratioText(row.pathCoverage) }}</template>
                </el-table-column>
              </el-table>
              <div class="spacer-block">
                <h3 class="mini-title">路径向量预览</h3>
                <el-table :data="pathEmbeddingRows" size="small" border>
                  <el-table-column prop="doctor" label="医家" width="110" />
                  <el-table-column prop="dimension" label="维度" width="80" />
                  <el-table-column prop="preview" label="前6维" min-width="240" />
                </el-table>
              </div>
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">Metapath2Vec 散点</h2>
              <div ref="pathScatterRef" class="chart-shell"></div>
            </div>
          </div>

          <div class="glass-panel section-card compare-section">
            <h2 class="section-title">医家辨证路径画像</h2>
            <div class="profile-grid">
              <div v-for="doctorName in pathDoctorNames" :key="`path-${doctorName}`" class="profile-card">
                <div class="profile-head">
                  <div class="profile-name">{{ doctorName }}</div>
                  <el-tag type="success" effect="plain">
                    完整度 {{ (((pathProfile(doctorName)?.completeness.completeRatio ?? 0) * 100)).toFixed(0) }}%
                  </el-tag>
                  <el-tag type="info" effect="plain">
                    覆盖率 {{ (((pathProfile(doctorName)?.completeness.pathCoverage ?? 0) * 100)).toFixed(0) }}%
                  </el-tag>
                </div>
                <div v-if="pathProfile(doctorName)" class="profile-body">
                  <div class="path-stats">
                    <span class="plain-chip">完整链 {{ pathProfile(doctorName)!.completeness.completeCount }}</span>
                    <span class="plain-chip">部分链 {{ pathProfile(doctorName)!.completeness.partialCount }}</span>
                    <span class="plain-chip">单点链 {{ pathProfile(doctorName)!.completeness.singleCount }}</span>
                  </div>
                  <div class="profile-section">
                    <div class="profile-label">完整链</div>
                    <el-table :data="pathRows(pathProfile(doctorName)!.completePaths)" size="small" border>
                      <el-table-column prop="pathType" label="类型" width="96" />
                      <el-table-column prop="text" label="路径" min-width="240" />
                    </el-table>
                  </div>
                  <div class="profile-section">
                    <div class="profile-label">部分链</div>
                    <el-table :data="pathRows(pathProfile(doctorName)!.partialPaths)" size="small" border>
                      <el-table-column prop="pathType" label="类型" width="96" />
                      <el-table-column prop="text" label="路径" min-width="240" />
                    </el-table>
                  </div>
                  <div class="profile-section">
                    <div class="profile-label">独有路径</div>
                    <div class="chip-row">
                      <span
                        v-for="path in pathProfile(doctorName)!.uniquePaths"
                        :key="path.signature"
                        class="plain-chip path-chip"
                      >
                        {{ pathTypeLabel(path.pathType) }}：{{ path.text }}
                      </span>
                      <span v-if="!pathProfile(doctorName)!.uniquePaths.length" class="empty-text">暂无明显独有路径</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </el-tab-pane>

      <el-tab-pane :label="tabLabels.subgraphs" name="subgraphs">
        <div v-if="subgraphResult && !subgraphResult.doctorCount" class="glass-panel section-card compare-section">
          <TcmEmpty text="当前病名没有可比较的核心子图数据" />
        </div>

        <template v-if="subgraphResult && subgraphResult.doctorCount">
          <div class="glass-panel section-card compare-section conclusion-panel">
            <div class="conclusion-kicker">总览</div>
            <div class="conclusion-text">{{ subgraphResult.summary.message }}</div>
            <div class="conclusion-tags">
              <el-tag type="primary" effect="plain">病名：{{ subgraphResult.disease }}</el-tag>
              <el-tag type="success" effect="plain">医家：{{ subgraphResult.doctorCount }} 位</el-tag>
              <el-tag type="info" effect="plain">主指标：{{ subgraphResult.summary.primarySimilarityMetric }}</el-tag>
              <el-tag type="success" effect="plain">向量：{{ subgraphResult.summary.vectorSimilarityMetrics.join(' / ') || '暂无' }}</el-tag>
              <el-tag type="warning" effect="plain">共同节点：{{ subgraphResult.summary.sharedNodeCount }}</el-tag>
              <el-tag type="danger" effect="plain">共同边：{{ subgraphResult.summary.sharedEdgeCount }}</el-tag>
            </div>
            <div class="panel-actions">
              <el-button type="primary" plain :loading="exportingSubgraphs" @click="exportSubgraphs">导出子图包</el-button>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">两两子图相似度</h2>
              <el-table :data="subgraphResult.similarityPairs" size="small" border>
                <el-table-column prop="leftDoctor" label="医家A" min-width="110" />
                <el-table-column prop="rightDoctor" label="医家B" min-width="110" />
                <el-table-column prop="nodeJaccard" label="节点Jaccard" width="110" />
                <el-table-column prop="edgeJaccard" label="边Jaccard" width="110" />
                <el-table-column prop="subgraphJaccard" label="子图Jaccard" width="110" />
                <el-table-column prop="graph2vecCosine" label="Graph2Vec" width="110" />
              </el-table>
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">共同节点</h2>
              <div class="shared-list">
                <div v-for="category in nodeCategories" :key="`subgraph-${category}`" class="shared-block">
                  <div class="block-title compact">{{ categoryMeta[category].label }}</div>
                  <div class="chip-row">
                    <span
                      v-for="item in subgraphResult.sharedNodes[category]"
                      :key="`${category}-${item.node.name}-subgraph`"
                      class="node-chip"
                      :class="categoryMeta[category].className"
                    >
                      {{ item.node.name }}
                      <small>{{ item.doctors.join('、') }}</small>
                    </span>
                    <span v-if="!subgraphResult.sharedNodes[category].length" class="empty-text">暂无明显共同项</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="glass-panel section-card compare-section">
            <h2 class="section-title">共同边</h2>
            <div class="chip-row">
              <span
                v-for="item in subgraphResult.sharedEdges"
                :key="item.edge.signature"
                class="plain-chip path-chip"
              >
                {{ item.edge.text }}
                <small>{{ item.doctors.join('、') }}</small>
              </span>
              <span v-if="!subgraphResult.sharedEdges.length" class="empty-text">暂无明显共同边</span>
            </div>
          </div>

          <div class="summary-grid">
            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">子图向量概览</h2>
              <el-table :data="subgraphEmbeddingRows" size="small" border>
                <el-table-column prop="doctor" label="医家" width="110" />
                <el-table-column prop="graph2vecDimension" label="Graph2Vec维度" width="120" />
                <el-table-column prop="graph2vecPreview" label="Graph2Vec前6维" min-width="220" />
              </el-table>
            </div>

            <div class="glass-panel section-card compare-section">
              <h2 class="section-title">Graph2Vec 散点</h2>
              <div ref="subgraphScatterRef" class="chart-shell"></div>
            </div>
          </div>

          <div class="glass-panel section-card compare-section">
            <h2 class="section-title">医家核心子图画像</h2>
            <div class="profile-grid">
              <div v-for="doctorName in subgraphDoctorNames" :key="`subgraph-profile-${doctorName}`" class="profile-card">
                <div class="profile-head">
                  <div class="profile-name">{{ doctorName }}</div>
                  <el-tag type="success" effect="plain">
                    节点 {{ subgraphProfile(doctorName)?.nodeCount ?? 0 }} / 边 {{ subgraphProfile(doctorName)?.edgeCount ?? 0 }}
                  </el-tag>
                </div>
                <div v-if="subgraphProfile(doctorName)" class="profile-body">
                  <div class="profile-section">
                    <div class="profile-label">独有节点</div>
                    <div v-for="category in nodeCategories" :key="`${doctorName}-${category}-unique-subgraph`" class="chip-row">
                      <span
                        v-for="node in categoryNodes(subgraphProfile(doctorName)!.uniqueNodes, category)"
                        :key="`${node.id}-subgraph-unique`"
                        class="node-chip"
                        :class="categoryMeta[category].className"
                      >
                        {{ node.name }}
                      </span>
                      <span v-if="!categoryNodes(subgraphProfile(doctorName)!.uniqueNodes, category).length" class="empty-text">
                        {{ categoryMeta[category].label }}暂无独有节点
                      </span>
                    </div>
                  </div>

                  <div class="profile-section">
                    <div class="profile-label">关系分布</div>
                    <div class="chip-row">
                      <span
                        v-for="item in subgraphProfile(doctorName)!.relationDistribution"
                        :key="`${doctorName}-${item.relationType}`"
                        class="plain-chip"
                      >
                        {{ item.relationType }} {{ item.count }} 条 {{ ratioText(item.ratio) }}
                      </span>
                      <span v-if="!subgraphProfile(doctorName)!.relationDistribution.length" class="empty-text">暂无</span>
                    </div>
                  </div>

                  <div class="profile-section">
                    <div class="profile-label">独有边</div>
                    <div class="chip-row">
                      <span
                        v-for="edge in subgraphProfile(doctorName)!.uniqueEdges"
                        :key="`${doctorName}-${edge.signature}-unique-edge`"
                        class="plain-chip path-chip"
                      >
                        {{ edge.text }}
                      </span>
                      <span v-if="!subgraphProfile(doctorName)!.uniqueEdges.length" class="empty-text">暂无明显独有边</span>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
        </template>
      </el-tab-pane>
    </el-tabs>

    <div v-if="nodeResult && nodeResult.doctorCount" class="glass-panel section-card compare-section" style="margin-top: 20px;">
      <div class="section-card-header">
        <h2 class="section-title">AI 分析解读</h2>
        <div class="section-card-actions">
          <el-button text size="small" @click="openAiConfig">配置模型</el-button>
          <el-button type="warning" plain :loading="aiLoading" @click="runAiAnalysis" size="small">
            {{ aiLoading ? '分析中...' : 'AI 分析解读' }}
          </el-button>
        </div>
      </div>
      <div v-if="aiAnalysis" class="ai-analysis-content">
        <div class="ai-analysis-text">{{ aiAnalysis }}</div>
        <div v-if="aiModel" class="ai-analysis-meta">模型：{{ aiModel }}</div>
      </div>
      <div v-else class="ai-analysis-empty">
        <el-tag v-if="aiHasKey" type="info" effect="plain">点击「AI 分析解读」按钮，由大模型生成易理解的综合分析</el-tag>
        <el-tag v-else type="warning" effect="plain">尚未配置大模型，请先点击「配置模型」设置 API Key</el-tag>
      </div>
    </div>

    <el-dialog v-model="aiConfigVisible" title="AI 大模型配置" width="520px">
      <p style="font-size: 13px; color: var(--color-text-secondary); margin-bottom: 16px;">
        配置用于医家比较 AI 分析解读的大模型参数，支持 OpenAI 兼容协议。
      </p>
      <el-alert
        v-if="aiHasKey"
        type="success"
        title="已配置 API Key，可直接使用 AI 分析解读功能"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-form label-width="100px">
        <el-form-item label="API Key">
          <el-input
            v-model="aiConfigForm.apiKey"
            type="password"
            show-password
            :placeholder="aiHasKey ? '已保存（留空则保持不变）' : '请输入大模型 API Key'"
          />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="aiConfigForm.baseUrl" placeholder="https://api.deepseek.com/v1" />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="aiConfigForm.model" placeholder="deepseek-chat" />
        </el-form-item>
        <el-form-item>
          <el-button :loading="aiTesting" @click="testConnection">测试连接</el-button>
          <span v-if="aiTestResult" :class="aiTestResult.includes('成功') ? 'test-ok' : 'test-fail'" style="margin-left: 12px; font-size: 13px;">{{ aiTestResult }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="aiConfigVisible = false">取消</el-button>
        <el-button type="primary" :loading="aiConfigSaving" @click="saveAiConfig">保存</el-button>
      </template>
    </el-dialog>
  </TcmPageShell>
</template>

<style scoped>
.compare-tabs {
  margin-top: 20px;
}

.timing-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.compare-section {
  margin-top: 20px;
}

.conclusion-panel {
  background:
    linear-gradient(135deg, rgba(255, 252, 245, 0.98), rgba(247, 242, 234, 0.86));
}

.conclusion-kicker {
  color: var(--brand);
  font-size: 13px;
  font-weight: 700;
}

.conclusion-text {
  margin-top: 10px;
  font-size: 22px;
  line-height: 1.55;
  font-weight: 700;
}

.conclusion-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.panel-actions {
  margin-top: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
  gap: 20px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.section-title {
  margin: 0;
}

.control-stack {
  display: grid;
  gap: 10px;
  justify-items: end;
}

.matrix-note {
  margin-top: 10px;
  color: var(--text-sub);
  font-size: 13px;
}

.matrix-scroll {
  width: 100%;
  overflow-x: auto;
  margin-top: 14px;
  border: 1px solid var(--color-border-soft);
  border-radius: 10px;
}

.matrix-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
}

.matrix-table th,
.matrix-table td {
  padding: 10px;
  border: 1px solid var(--color-border-soft);
  text-align: center;
}

.matrix-table th {
  color: var(--color-primary-dark);
  background: var(--color-bg-muted);
  font-weight: 700;
}

.doctor-name {
  font-weight: 700;
  text-align: left !important;
}

.heat-box {
  border-radius: 8px;
  padding: 10px 6px;
  font-weight: 700;
}

.shared-list {
  display: grid;
  gap: 14px;
}

.block-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 700;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.node-chip,
.plain-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 9px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.3;
}

.node-chip {
  border: 1px solid transparent;
}

.node-chip small {
  color: var(--color-text-secondary);
}

.plain-chip {
  background: rgba(251, 247, 239, 0.86);
  border: 1px solid var(--color-border-soft);
}

.path-chip {
  align-items: flex-start;
  flex-direction: column;
}

.path-chip small {
  color: var(--color-text-secondary);
}

.pattern {
  color: var(--entity-syndrome);
  background: rgba(46, 107, 87, 0.12);
  border-color: rgba(46, 107, 87, 0.24);
}

.cause {
  color: #9a6426;
  background: rgba(217, 164, 95, 0.16);
  border-color: rgba(217, 164, 95, 0.28);
}

.mechanism {
  color: var(--entity-mechanism);
  background: rgba(92, 124, 122, 0.14);
  border-color: rgba(92, 124, 122, 0.26);
}

.empty-text {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.profile-card {
  padding: 16px;
  border: 1px solid var(--color-border-soft);
  border-radius: 10px;
  background: rgba(251, 247, 239, 0.78);
}

.profile-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.profile-name {
  font-size: 20px;
  font-weight: 700;
}

.profile-body {
  display: grid;
  gap: 14px;
  margin-top: 14px;
}

.profile-section {
  display: grid;
  gap: 8px;
}

.profile-label {
  color: var(--text-sub);
  font-size: 13px;
  font-weight: 700;
}

.profile-subtitle {
  color: var(--color-primary-dark);
  font-size: 13px;
  font-weight: 600;
}

.chart-shell {
  width: 100%;
  height: 320px;
}

.spacer-block {
  margin-top: 16px;
}

.mini-title {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 700;
}

.path-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.rwr-block {
  margin-top: 14px;
}

.rwr-text {
  margin: 6px 0 0;
  line-height: 1.7;
  color: var(--text-main);
}

@media (max-width: 960px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .section-head {
    grid-template-columns: 1fr;
    display: grid;
  }

  .control-stack {
    justify-items: start;
  }

  .conclusion-text {
    font-size: 18px;
  }
}

.section-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  gap: 12px;
}

.section-card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ai-analysis-content {
  background: rgba(251, 247, 239, 0.6);
  border: 1px solid var(--color-border-soft);
  border-radius: 12px;
  padding: 20px 24px;
}

.ai-analysis-text {
  font-size: 16px;
  line-height: 1.8;
  white-space: pre-wrap;
  color: var(--color-text-primary);
}

.ai-analysis-meta {
  margin-top: 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: right;
}

.ai-analysis-empty {
  padding: 16px 0;
}
</style>
