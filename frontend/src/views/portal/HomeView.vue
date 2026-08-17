<script setup lang="ts">
import { useSchema } from '@/composables/useSchema';
import { SOURCE_OPTIONS } from '@/constants/sourceOptions';
import TcmIcon from '@/components/tcm/TcmIcon.vue';
import TcmPanel from '@/components/tcm/TcmPanel.vue';
import TcmStatCard from '@/components/tcm/TcmStatCard.vue';

const { entityTypes } = useSchema();
const sourceOptions = SOURCE_OPTIONS;
const quickEntries = [
  { title: '知识检索', icon: 'search', to: '/portal/search' },
  { title: '图谱探索', icon: 'graph', to: '/portal/graph' },
  { title: '路径查询', icon: 'path', to: '/portal/path' },
  { title: '医家比较', icon: 'compare', to: '/portal/physician-compare' },
] as const;
</script>

<template>
  <section class="home-overview-page">
    <section class="home-hero">
      <div class="home-hero-copy">
        <TcmIcon name="dashboard" :size="54" />
        <div>
          <h1>图谱概览</h1>
          <p>吴门医案知识图谱的实体类型、医案来源和常用分析入口。</p>
        </div>
      </div>
    </section>

    <div class="stats-grid">
      <TcmStatCard icon="entity" title="实体类型" :value="entityTypes.length" desc="覆盖医家、病名、证型等类型" />
      <TcmStatCard icon="classics" title="医案来源" :value="sourceOptions.length" desc="按卷册和来源医案筛选" />
      <TcmStatCard icon="graph" title="图谱功能" :value="3" desc="探索、路径、实体详情联动查看" />
      <TcmStatCard icon="analytics" title="快捷入口" :value="quickEntries.length" desc="图谱、路径、比较一键进入" />
    </div>

    <TcmPanel title="快捷入口" subtitle="常用功能集中进入，概览和检索分开显示。" icon="graph" class="spaced" cloud bamboo>
      <div class="quick-entry-grid">
        <router-link v-for="item in quickEntries" :key="item.title" :to="item.to" class="quick-entry-card">
          <TcmIcon :name="item.icon" :size="58" />
          <span>{{ item.title }}</span>
        </router-link>
      </div>
    </TcmPanel>
  </section>
</template>

<style scoped>
.home-overview-page {
  position: relative;
}

.home-hero {
  display: flex;
  align-items: center;
  min-height: 230px;
  margin-bottom: 18px;
  padding: 28px;
  overflow: hidden;
  background-image:
    linear-gradient(90deg, rgba(251, 248, 241, 0.3), rgba(251, 248, 241, 0.8)),
    url("@/assets/tcm-theme/backgrounds/bg-ink-mountain-banner.png");
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  border: 1px solid var(--tcm-border);
  border-radius: 24px;
}

.home-hero-copy {
  display: flex;
  gap: 18px;
  align-items: center;
  width: min(620px, 100%);
  padding: 22px 24px;
  background: rgba(255, 252, 245, 0.74);
  border: 1px solid rgba(232, 220, 200, 0.82);
  border-radius: 18px;
}

.home-hero h1 {
  margin: 0;
  color: var(--tcm-primary-dark);
  font-size: 32px;
}

.home-hero p {
  margin: 10px 0 0;
  color: var(--tcm-muted);
  font-size: 15px;
}

@media (max-width: 720px) {
  .home-hero {
    padding: 18px;
  }

  .home-hero-copy {
    align-items: flex-start;
    padding: 18px;
  }

  .home-hero h1 {
    font-size: 26px;
  }
}
</style>
