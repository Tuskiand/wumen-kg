<script setup lang="ts">
type TcmIconName =
  | 'graph'
  | 'search'
  | 'entity'
  | 'relation'
  | 'path'
  | 'compare'
  | 'dashboard'
  | 'import'
  | 'users'
  | 'settings'
  | 'classics'
  | 'analytics';

const props = withDefaults(
  defineProps<{
    name: TcmIconName | string;
    size?: number | string;
  }>(),
  {
    size: 24,
  },
);

const iconMap: Record<TcmIconName, string> = {
  graph: new URL('@/assets/tcm-theme/icons/01-graph.svg', import.meta.url).href,
  search: new URL('@/assets/tcm-theme/icons/02-search.svg', import.meta.url).href,
  entity: new URL('@/assets/tcm-theme/icons/03-entity.svg', import.meta.url).href,
  relation: new URL('@/assets/tcm-theme/icons/04-relation.svg', import.meta.url).href,
  path: new URL('@/assets/tcm-theme/icons/05-path.svg', import.meta.url).href,
  compare: new URL('@/assets/tcm-theme/icons/06-compare.svg', import.meta.url).href,
  dashboard: new URL('@/assets/tcm-theme/icons/07-dashboard.svg', import.meta.url).href,
  import: new URL('@/assets/tcm-theme/icons/08-import.svg', import.meta.url).href,
  users: new URL('@/assets/tcm-theme/icons/09-users.svg', import.meta.url).href,
  settings: new URL('@/assets/tcm-theme/icons/10-settings.svg', import.meta.url).href,
  classics: new URL('@/assets/tcm-theme/icons/11-classics.svg', import.meta.url).href,
  analytics: new URL('@/assets/tcm-theme/icons/12-analytics.svg', import.meta.url).href,
};

function sizeValue(value: number | string) {
  return typeof value === 'number' ? `${value}px` : value;
}

function iconSrc(name: string) {
  return iconMap[name as TcmIconName] ?? iconMap.graph;
}
</script>

<template>
  <span class="tcm-icon" :style="{ '--tcm-icon-size': sizeValue(props.size) }">
    <img :src="iconSrc(props.name)" :alt="props.name" />
  </span>
</template>

<style scoped>
.tcm-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  width: var(--tcm-icon-size, 24px);
  height: var(--tcm-icon-size, 24px);
  vertical-align: middle;
}

.tcm-icon img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
