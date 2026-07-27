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

withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    icon?: TcmIconName;
    showInkBottom?: boolean;
  }>(),
  {
    subtitle: '',
    showInkBottom: true,
  },
);
</script>

<template>
  <section class="tcm-page-shell" :class="{ 'has-ink-bottom': showInkBottom }">
    <header class="tcm-page-head">
      <div v-if="icon" class="tcm-page-icon">
        <TcmIcon :name="icon" :size="34" />
      </div>
      <div>
        <h1 class="page-title tcm-page-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
      </div>
    </header>
    <div class="tcm-page-content">
      <slot />
    </div>
  </section>
</template>
