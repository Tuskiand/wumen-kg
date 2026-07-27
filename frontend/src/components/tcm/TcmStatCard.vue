<script setup lang="ts">
import TcmIcon from './TcmIcon.vue';

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

defineProps<{
  icon: TcmIconName;
  title: string;
  value: string | number;
  desc?: string;
}>();
</script>

<template>
  <article class="tcm-stat-card">
    <div class="tcm-stat-icon">
      <TcmIcon :name="icon" :size="30" />
    </div>
    <div>
      <div class="stat-label">{{ title }}</div>
      <div class="stat-value">{{ value }}</div>
      <div v-if="desc" class="tcm-stat-note">{{ desc }}</div>
    </div>
  </article>
</template>
