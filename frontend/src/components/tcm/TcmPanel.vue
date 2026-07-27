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
    title?: string;
    subtitle?: string;
    icon?: TcmIconName;
    decorated?: boolean;
    bamboo?: boolean;
    cloud?: boolean;
  }>(),
  {
    title: '',
    subtitle: '',
    decorated: true,
    bamboo: false,
    cloud: false,
  },
);
</script>

<template>
  <section class="tcm-panel" :class="{ 'is-decorated': decorated, 'has-bamboo': decorated && bamboo, 'has-cloud': decorated && cloud }">
    <header v-if="title || subtitle || icon" class="tcm-panel-head">
      <div v-if="icon" class="tcm-panel-icon">
        <TcmIcon :name="icon" :size="26" />
      </div>
      <div>
        <h2 v-if="title" class="section-title tcm-panel-title">{{ title }}</h2>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
      </div>
    </header>
    <div class="tcm-card-content">
      <slot />
    </div>
  </section>
</template>
