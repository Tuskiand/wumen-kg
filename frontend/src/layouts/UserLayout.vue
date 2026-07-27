<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { logout } from '@/api';
import { authState, clearSession } from '@/auth';
import TcmIcon from '@/components/tcm/TcmIcon.vue';

const router = useRouter();
const logoSeal = new URL('@/assets/tcm-theme/brand/logo-seal-wumen.png', import.meta.url).href;
const text = {
  brandTitle: '吴门医案知识图谱',
  goAdmin: '管理端',
  logout: '退出登录',
};

const menuItems = computed(() => {
  const items = [
    { label: '图谱概览', index: '/portal/home', icon: 'dashboard' },
    { label: '知识检索', index: '/portal/search', icon: 'search' },
    { label: '图谱探索', index: '/portal/graph', icon: 'graph' },
    { label: '路径查询', index: '/portal/path', icon: 'path' },
    { label: '医家比较', index: '/portal/physician-compare', icon: 'compare' },
  ];
  if (authState.user?.role === 'admin') {
    items.push({ label: text.goAdmin, index: '/admin/dashboard', icon: 'settings' });
  }
  return items;
});

const activeMenu = computed(() => {
  return router.currentRoute.value.path;
});

async function handleLogout() {
  try {
    await logout();
  } catch {
    // ignore network errors on logout
  } finally {
    clearSession();
    ElMessage.success('已退出登录');
    await router.push('/login');
  }
}
</script>

<template>
  <el-container class="portal-layout">
    <el-aside width="240px" class="portal-aside">
      <div class="portal-brand">
        <img class="portal-logo" :src="logoSeal" alt="吴门医派" />
        <div>
          <div class="brand-title">{{ text.brandTitle }}</div>
        </div>
      </div>
      <el-menu :default-active="activeMenu" router class="portal-menu">
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          <span class="menu-item-content">
            <TcmIcon :name="item.icon" :size="35" />
            {{ item.label }}
          </span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="portal-body">
      <el-header class="portal-header">
        <div>
          <div class="brand-title">吴门医案知识图谱</div>
          <div class="brand-subtitle">图谱概览 · 知识检索 · 图谱探索 · 路径查询 · 医家比较</div>
        </div>
        <div class="user-actions">
          <el-tag effect="plain" type="info">{{ authState.user?.username }}</el-tag>
          <el-button type="primary" plain size="small" @click="handleLogout">{{ text.logout }}</el-button>
        </div>
      </el-header>
      <el-main class="page-shell">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.portal-layout {
  position: relative;
  isolation: isolate;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background-color: var(--tcm-bg);
  background-image:
    linear-gradient(rgba(251, 248, 241, 0.88), rgba(251, 248, 241, 0.88)),
    url("@/assets/tcm-theme/backgrounds/bg-paper.png");
  background-repeat: repeat;
  background-size: auto, 420px 420px;
}

.portal-layout::after {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 2;
  height: 220px;
  pointer-events: none;
  content: "";
  background-image: url("@/assets/tcm-theme/decorations/deco-ink-mountain-bottom.png");
  background-repeat: no-repeat;
  background-position: center bottom;
  background-size: 100% auto;
  opacity: 0.22;
  mask-image: linear-gradient(to bottom, transparent 0, rgba(0, 0, 0, 0.18) 24%, #000 58%);
  -webkit-mask-image: linear-gradient(to bottom, transparent 0, rgba(0, 0, 0, 0.18) 24%, #000 58%);
}

.portal-aside {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  height: 100vh;
  padding: 22px 16px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 252, 245, 0.96), rgba(247, 242, 234, 0.92)),
    url("@/assets/tcm-theme/backgrounds/bg-paper.png") center / 420px auto repeat;
  border-right: 1px solid var(--tcm-border);
  box-shadow: 6px 0 24px rgba(94, 73, 49, 0.06);
}

.portal-body {
  position: relative;
  z-index: 1;
  height: 100vh;
  overflow: hidden;
}

.portal-brand {
  display: grid;
  justify-items: center;
  gap: 8px;
  padding: 4px 6px 18px;
  text-align: center;
  border-bottom: 1px solid rgba(139, 110, 74, 0.16);
}

.portal-logo {
  width: 54px;
  height: 54px;
  object-fit: contain;
}

.portal-brand .brand-title {
  font-size: 20px;
  line-height: 1.2;
  white-space: nowrap;
}

.portal-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 0 24px;
  height: 88px;
  backdrop-filter: blur(20px);
  background: rgba(251, 247, 239, 0.9);
  border-bottom: 1px solid var(--color-border);
  overflow: hidden;
}

.portal-header::after {
  position: absolute;
  top: 6px;
  right: 28px;
  z-index: 0;
  width: 260px;
  height: 76px;
  pointer-events: none;
  content: "";
  background-image: url("@/assets/tcm-theme/decorations/deco-cloud-pattern.png");
  background-repeat: no-repeat;
  background-position: right center;
  background-size: contain;
  opacity: 0.24;
}

.portal-header > * {
  position: relative;
  z-index: 1;
}

.brand-title {
  color: var(--color-primary-dark);
  font-family: "Noto Serif SC", "Songti SC", "SimSun", "Microsoft YaHei", serif;
  font-size: 22px;
  font-weight: 700;
}

.brand-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-sub);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.portal-menu {
  flex: 1;
  border-bottom: none;
  background: transparent;
}

.portal-menu :deep(.el-menu-item) {
  height: 50px;
  margin-bottom: 8px;
  color: var(--color-primary-dark);
  border-radius: var(--radius-md);
}

.portal-menu :deep(.el-menu-item.is-active) {
  color: #fff;
  background: var(--color-primary);
  border-bottom: none;
}

.portal-menu :deep(.el-menu-item.is-active .tcm-icon img) {
  filter: brightness(0) invert(1) sepia(0.15) saturate(0.8);
  opacity: 0.94;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-item-content {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.page-shell {
  height: calc(100vh - 88px);
  padding-bottom: 220px;
  overflow-y: auto;
  background-color: var(--tcm-bg);
  background-image:
    linear-gradient(rgba(251, 248, 241, 0.9), rgba(251, 248, 241, 0.9)),
    url("@/assets/tcm-theme/backgrounds/bg-paper.png");
  background-repeat: repeat;
  background-size: auto, 420px 420px;
}

@media (max-width: 960px) {
  .portal-aside {
    display: none;
  }

  .portal-header {
    height: auto;
    padding: 16px;
    flex-direction: column;
    align-items: flex-start;
  }

  .portal-header::after {
    width: 180px;
    opacity: 0.16;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
