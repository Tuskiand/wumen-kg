<script setup lang="ts">
const emptyImage = new URL('@/assets/tcm-theme/empty/empty-ink-state.png', import.meta.url).href;

withDefaults(
  defineProps<{
    text?: string;
    desc?: string;
  }>(),
  {
    text: '暂无数据',
    desc: '',
  },
);
</script>

<template>
  <div class="tcm-empty">
    <img :src="emptyImage" alt="empty" />
    <p>{{ text }}</p>
    <small v-if="desc">{{ desc }}</small>
  </div>
</template>
