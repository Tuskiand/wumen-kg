<script setup lang="ts">
import type { ECharts } from 'echarts';
import { computed, onBeforeUnmount, onMounted, reactive, ref, type CSSProperties, watch } from 'vue';
import { useGraphCanvasSettings } from '@/composables/useGraphCanvasSettings';
import {
  chartFontFamily,
  getEntityColor,
  graphLineStyle,
  initAncientTcmChart,
  tcmChartColors,
  tooltipStyle,
} from '@/styles/echarts-theme';
import type { GraphSnapshot } from '@/types';

type GraphViewCenter = [number | string, number | string];

const DEFAULT_DENSITY = 50;
const DEFAULT_ZOOM = 1;
const MIN_ZOOM = 0.2;
const MAX_ZOOM = 2.2;
const ZOOM_STEP = 0.12;
const DEFAULT_CENTER: GraphViewCenter = ['50%', '50%'];
const ANIMATION_EASING_UPDATE = 'quinticInOut' as const;

const props = withDefaults(
  defineProps<{
    data: GraphSnapshot;
    height?: number | string;
    showControls?: boolean;
  }>(),
  {
    height: 460,
    showControls: true,
  },
);

const graphShell = ref<HTMLDivElement | null>(null);
const container = ref<HTMLDivElement | null>(null);
const sessionSettings = useGraphCanvasSettings();
const viewState = reactive({
  zoom: DEFAULT_ZOOM,
  center: [...DEFAULT_CENTER] as GraphViewCenter,
});
const isFullscreen = ref(false);
let chartInstance: ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;
let resizeFrame = 0;

const density = computed({
  get: () => sessionSettings.density,
  set: (value: number) => {
    sessionSettings.density = clamp(value, 0, 100);
  },
});

const zoomPercent = computed(() => `${Math.round(viewState.zoom * 100)}%`);
const fullscreenLabel = computed(() => (isFullscreen.value ? '退出全屏' : '铺满全屏'));
const canvasStyle = computed<CSSProperties>(() => {
  if (isFullscreen.value) {
    return {};
  }

  return {
    height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  };
});

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function lerp(start: number, end: number, progress: number) {
  return start + (end - start) * progress;
}

function getForceLayoutSettings() {
  const progress = density.value / 100;
  return {
    edgeLength: [
      Math.round(lerp(260, 110, progress)),
      Math.round(lerp(340, 160, progress)),
    ],
    repulsion: Math.round(lerp(1250, 550, progress)),
    gravity: Number(lerp(0.04, 0.12, progress).toFixed(3)),
    friction: 0.08,
  };
}

function normalizeCenter(center: unknown): GraphViewCenter {
  if (Array.isArray(center) && center.length >= 2) {
    return [center[0] as number | string, center[1] as number | string];
  }
  return [...DEFAULT_CENTER];
}

function normalizeZoom(value: unknown) {
  const zoom = Number(value);
  if (!Number.isFinite(zoom)) {
    return DEFAULT_ZOOM;
  }
  return clamp(Number(zoom.toFixed(2)), MIN_ZOOM, MAX_ZOOM);
}

function resetViewState() {
  viewState.zoom = DEFAULT_ZOOM;
  viewState.center = [...DEFAULT_CENTER];
}

function syncViewStateFromChart() {
  if (!chartInstance) {
    return;
  }

  const option = chartInstance.getOption() as { series?: Array<{ zoom?: unknown; center?: unknown }> };
  const currentSeries = option.series?.[0];
  viewState.zoom = normalizeZoom(currentSeries?.zoom);
  viewState.center = normalizeCenter(currentSeries?.center);
}

function buildOption() {
  const forceLayout = getForceLayoutSettings();
  return {
    backgroundColor: tcmChartColors.bgPage,
    tooltip: {
      ...tooltipStyle,
      trigger: 'item',
      formatter(params: { dataType?: string; data?: Record<string, unknown> }) {
        if (params.dataType === 'edge') {
          return `${params.data?.label ?? params.data?.type ?? '关系'}`;
        }
        return [
          `<strong>${params.data?.name ?? ''}</strong>`,
          `类型：${params.data?.type ?? '-'}`,
          params.data?.summary ? `摘要：${params.data.summary}` : '',
        ].filter(Boolean).join('<br/>');
      },
    },
    animationDuration: 300,
    animationEasingUpdate: ANIMATION_EASING_UPDATE,
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: 'move',
        draggable: true,
        focusNodeAdjacency: true,
        center: [...viewState.center],
        zoom: viewState.zoom,
        scaleLimit: {
          min: MIN_ZOOM,
          max: MAX_ZOOM,
        },
        force: forceLayout,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          color: tcmChartColors.textMain,
          fontSize: 12,
          fontFamily: chartFontFamily,
        },
        emphasis: {
          scale: true,
          lineStyle: {
            width: 2,
          },
          label: {
            show: true,
          },
        },
        lineStyle: {
          ...graphLineStyle,
          width: 1.2,
          opacity: 0.68,
        },
        edgeLabel: {
          show: true,
          formatter: (params: { data?: Record<string, unknown> }) => String(params.data?.label ?? params.data?.type ?? ''),
          color: tcmChartColors.primaryDark,
          fontSize: 11,
          fontFamily: chartFontFamily,
          backgroundColor: 'rgba(255, 252, 245, 0.78)',
          padding: [2, 4],
          borderRadius: 4,
        },
        data: props.data.nodes.map((node) => ({
          id: node.id,
          name: node.name,
          type: node.type,
          summary: node.summary,
          symbolSize: 38,
          draggable: true,
          itemStyle: {
            color: getEntityColor(node.type),
            borderColor: '#FFFCF5',
            borderWidth: 2,
            shadowBlur: 12,
            shadowColor: 'rgba(92, 58, 33, 0.18)',
          },
        })),
        links: props.data.edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          label: edge.label ?? edge.type,
        })),
      },
    ],
  };
}

async function ensureChart() {
  if (!container.value) {
    return null;
  }

  if (!chartInstance) {
    const echarts = await import('echarts');
    chartInstance = initAncientTcmChart(echarts, container.value);
    chartInstance.on('graphRoam', syncViewStateFromChart);
  }

  return chartInstance;
}

async function renderGraph() {
  const chart = await ensureChart();
  if (!chart) {
    return;
  }

  chart.setOption(buildOption(), { notMerge: true, lazyUpdate: false });
  chart.resize();
  syncViewStateFromChart();
}

function updateChartView() {
  if (!chartInstance) {
    return;
  }

  chartInstance.setOption(
    {
      series: [
        {
          center: [...viewState.center],
          zoom: viewState.zoom,
        },
      ],
    },
    { lazyUpdate: false },
  );
}

function applyZoom(delta: number) {
  const nextZoom = clamp(Number((viewState.zoom + delta).toFixed(2)), MIN_ZOOM, MAX_ZOOM);
  if (nextZoom === viewState.zoom) {
    return;
  }

  viewState.zoom = nextZoom;
  updateChartView();
}

function zoomIn() {
  applyZoom(ZOOM_STEP);
}

function zoomOut() {
  applyZoom(-ZOOM_STEP);
}

function fitView() {
  resetViewState();
  updateChartView();
}

function restoreDefaults() {
  const shouldRerender = density.value !== DEFAULT_DENSITY;
  density.value = DEFAULT_DENSITY;
  resetViewState();

  if (shouldRerender) {
    void renderGraph();
    return;
  }

  updateChartView();
}

function syncFullscreenState() {
  isFullscreen.value = document.fullscreenElement === graphShell.value;
  handleResize();
}

async function toggleFullscreen() {
  if (!graphShell.value || typeof graphShell.value.requestFullscreen !== 'function') {
    return;
  }

  if (document.fullscreenElement === graphShell.value) {
    await document.exitFullscreen();
    return;
  }

  await graphShell.value.requestFullscreen();
}

function handleWheel(event: WheelEvent) {
  if (!chartInstance) {
    return;
  }

  event.preventDefault();
  applyZoom(event.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP);
}

function handleResize() {
  if (!chartInstance || resizeFrame) {
    return;
  }

  resizeFrame = window.requestAnimationFrame(() => {
    resizeFrame = 0;
    chartInstance?.resize();
  });
}

onMounted(() => {
  void renderGraph();
  window.addEventListener('resize', handleResize);
  window.visualViewport?.addEventListener('resize', handleResize);
  document.addEventListener('fullscreenchange', syncFullscreenState);

  if (container.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container.value);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  window.visualViewport?.removeEventListener('resize', handleResize);
  document.removeEventListener('fullscreenchange', syncFullscreenState);
  resizeObserver?.disconnect();
  resizeObserver = null;
  if (resizeFrame) {
    window.cancelAnimationFrame(resizeFrame);
    resizeFrame = 0;
  }
  chartInstance?.off('graphRoam', syncViewStateFromChart);
  chartInstance?.dispose();
  chartInstance = null;
});

watch(density, () => {
  if (!chartInstance) {
    return;
  }
  void renderGraph();
});

watch(
  () => props.data,
  () => {
    resetViewState();
    void renderGraph();
  },
  { deep: true },
);
</script>

<template>
  <div ref="graphShell" class="graph-shell" :class="{ 'is-fullscreen': isFullscreen }">
    <div v-if="showControls" class="graph-toolbar">
      <div class="control-group density-group">
        <span class="control-label">疏密</span>
        <span class="control-hint">更疏</span>
        <el-slider v-model="density" class="density-slider" :min="0" :max="100" :show-tooltip="false" />
        <span class="control-hint">更密</span>
      </div>
      <div class="control-group zoom-group">
        <el-button @click="zoomOut">缩小</el-button>
        <el-tag>{{ zoomPercent }}</el-tag>
        <el-button @click="zoomIn">放大</el-button>
        <el-button @click="fitView">适应视图</el-button>
        <el-button @click="toggleFullscreen">{{ fullscreenLabel }}</el-button>
        <el-button @click="restoreDefaults">恢复默认</el-button>
      </div>
    </div>
    <div class="graph-body">
      <div ref="container" class="graph-canvas" :style="canvasStyle" @wheel="handleWheel" />
    </div>
  </div>
</template>

<style scoped>
.graph-shell {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.graph-shell.is-fullscreen {
  height: 100vh;
  padding: 16px;
  background: var(--tcm-bg);
}

.graph-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: rgba(251, 247, 239, 0.92);
  box-shadow: var(--shadow-sm);
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 40px;
}

.density-group {
  flex: 1 1 360px;
  min-width: 260px;
}

.zoom-group {
  flex: 0 1 auto;
  flex-wrap: wrap;
}

.control-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-primary-dark);
}

.control-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.density-slider {
  flex: 1;
  min-width: 140px;
}

.graph-body {
  min-height: 0;
}

.graph-shell.is-fullscreen .graph-body {
  flex: 1 1 auto;
}

.graph-canvas {
  width: 100%;
  border: 1px solid var(--color-border-soft);
  border-radius: var(--radius-lg);
  background: var(--tcm-bg);
}

.graph-shell.is-fullscreen .graph-canvas {
  height: 100%;
}

@media (max-width: 960px) {
  .graph-toolbar {
    padding: 12px;
  }

  .density-group,
  .zoom-group {
    flex-basis: 100%;
  }
}
</style>
