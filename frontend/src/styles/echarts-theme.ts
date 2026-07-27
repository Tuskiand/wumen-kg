import type { ECharts } from 'echarts';

export const ANCIENT_TCM_THEME_NAME = 'ancient-tcm';

export const tcmChartColors = {
  bgPage: '#FBF8F1',
  bgSoft: '#FFFCF5',
  bgMuted: '#F7F2EA',
  textMain: '#2F2A24',
  textSecondary: '#8A7B6A',
  border: '#E8DCC8',
  borderStrong: '#CDBB9F',
  primary: '#8B5E34',
  primaryDark: '#5C3A21',
  secondary: '#2E6B57',
  accent: '#B86E4A',
  danger: '#A33A2A',
  warning: '#D9A45F',
  info: '#5C7C7A',
  defaultEntity: '#8C7B6B',
};

export const entityColors: Record<string, string> = {
  A医家: '#8B5E34',
  B病名: '#B86E4A',
  C证型: '#2E6B57',
  D病因: '#D9A45F',
  E病机: '#5C7C7A',
};

export const chartPalette = [
  '#8B5E34',
  '#2E6B57',
  '#B86E4A',
  '#D9A45F',
  '#5C7C7A',
  '#A33A2A',
  '#8C7B6B',
];

export const chartFontFamily = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif';

export function getEntityColor(type: string) {
  return entityColors[type] ?? tcmChartColors.defaultEntity;
}

export function heatStyle(score: number) {
  const value = Math.max(0, Math.min(1, score));
  const alpha = 0.16 + value * 0.74;
  return {
    background: `rgba(139, 94, 52, ${alpha})`,
    color: value >= 0.48 ? '#fffaf3' : tcmChartColors.textMain,
  };
}

export const tooltipStyle = {
  backgroundColor: tcmChartColors.bgSoft,
  borderColor: tcmChartColors.border,
  borderWidth: 1,
  textStyle: {
    color: tcmChartColors.textMain,
    fontFamily: chartFontFamily,
  },
};

export const axisStyle = {
  axisLine: { lineStyle: { color: tcmChartColors.borderStrong } },
  axisTick: { lineStyle: { color: tcmChartColors.border } },
  axisLabel: { color: tcmChartColors.textSecondary, fontFamily: chartFontFamily },
  splitLine: { lineStyle: { color: '#E4D7C3' } },
  nameTextStyle: { color: tcmChartColors.primaryDark, fontFamily: chartFontFamily },
};

export const graphLineStyle = {
  color: tcmChartColors.borderStrong,
  opacity: 0.55,
  width: 1,
  curveness: 0.12,
};

let themeRegistered = false;

export function registerAncientTcmTheme(echarts: typeof import('echarts')) {
  if (themeRegistered) {
    return;
  }

  echarts.registerTheme(ANCIENT_TCM_THEME_NAME, {
    color: chartPalette,
    backgroundColor: 'transparent',
    textStyle: {
      color: tcmChartColors.textMain,
      fontFamily: chartFontFamily,
    },
    title: {
      textStyle: {
        color: tcmChartColors.primaryDark,
        fontFamily: chartFontFamily,
      },
    },
    legend: {
      textStyle: {
        color: tcmChartColors.textSecondary,
        fontFamily: chartFontFamily,
      },
    },
    tooltip: tooltipStyle,
    radar: {
      axisName: {
        color: tcmChartColors.primaryDark,
        fontFamily: chartFontFamily,
      },
      splitLine: {
        lineStyle: {
          color: tcmChartColors.border,
        },
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(251, 247, 239, 0.72)', 'rgba(239, 230, 214, 0.46)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: tcmChartColors.border,
        },
      },
    },
  });
  themeRegistered = true;
}

export function initAncientTcmChart(echarts: typeof import('echarts'), el: HTMLElement): ECharts {
  registerAncientTcmTheme(echarts);
  return echarts.init(el, ANCIENT_TCM_THEME_NAME);
}

export function withAncientChartBase(option: Record<string, unknown>): Record<string, unknown> {
  return {
    color: chartPalette,
    backgroundColor: 'transparent',
    textStyle: {
      color: tcmChartColors.textMain,
      fontFamily: chartFontFamily,
    },
    tooltip: tooltipStyle,
    ...option,
  };
}
