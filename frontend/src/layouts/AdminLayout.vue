<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { logout } from '@/api';
import { authState, clearSession } from '@/auth';
import TcmIcon from '@/components/tcm/TcmIcon.vue';

const router = useRouter();
const logoSeal = new URL('@/assets/tcm-theme/brand/logo-seal-wumen.png', import.meta.url).href;
const menuItems = [
  { label: '控制台', index: '/admin/dashboard', icon: 'dashboard' },
  { label: '图谱探索', index: '/admin/graph', icon: 'graph' },
  { label: '路径查询', index: '/admin/path', icon: 'path' },
  { label: '医家比较', index: '/admin/physician-compare', icon: 'compare' },
  { label: '节点管理', index: '/admin/entities', icon: 'entity' },
  { label: '关系管理', index: '/admin/relations', icon: 'relation' },
  { label: '导入任务', index: '/admin/imports', icon: 'import' },
  { label: '用户管理', index: '/admin/users', icon: 'users' },
  { label: '版本管理', index: '/admin/versions', icon: 'classics' },
  { label: '审计日志', index: '/admin/audits', icon: 'analytics' },
];

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
  <el-container class="admin-layout">
    <el-aside width="240px" class="admin-aside">
      <div class="admin-brand">
        <img class="admin-logo" :src="logoSeal" alt="吴门医派" />
        <div>
          <div class="admin-brand-title">图谱管理台</div>
        </div>
      </div>
      <el-menu :default-active="$route.path" router class="admin-menu">
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          <span class="menu-item-content">
            <TcmIcon :name="item.icon" :size="35" />
            {{ item.label }}
          </span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="admin-body">
      <el-header class="admin-header">
        <div>
          <div class="admin-header-title">知识图谱管理系统</div>
          <div class="admin-header-subtitle">支持 CSV 导入、用户权限管理与图谱维护</div>
        </div>
        <div class="admin-header-links">
          <el-tag effect="plain" type="info">{{ authState.user?.username }}</el-tag>
          <el-button class="header-link-button" text tag="router-link" to="/portal/home">用户端首页</el-button>
          <el-button type="primary" plain @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="page-shell">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-layout {
  position: relative;
  isolation: isolate;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
}

.admin-layout::after {
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

.admin-aside {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  height: 100vh;
  padding: 22px 16px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(251, 247, 239, 0.96), rgba(239, 230, 214, 0.94)),
    url("@/assets/tcm-theme/backgrounds/bg-paper.png") center / 420px auto repeat;
  color: var(--color-text-main);
  border-right: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.admin-brand {
  display: grid;
  justify-items: center;
  gap: 8px;
  padding: 4px 6px 18px;
  text-align: center;
  border-bottom: 1px solid rgba(139, 110, 74, 0.16);
}

.admin-logo {
  width: 54px;
  height: 54px;
  object-fit: contain;
}

.admin-brand-title {
  color: var(--color-primary-dark);
  font-family: "Noto Serif SC", "Songti SC", "SimSun", "Microsoft YaHei", serif;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.admin-menu {
  flex: 1;
  border-right: none;
  background: transparent;
}

.admin-menu :deep(.el-menu) {
  border-right: none;
  background: transparent;
}

.admin-menu :deep(.el-menu-item) {
  height: 50px;
  margin-bottom: 8px;
  border-radius: var(--radius-md);
  color: var(--color-primary-dark);
  font-weight: 600;
}

.menu-item-content {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.admin-menu :deep(.el-menu-item:hover) {
  color: var(--color-primary-dark);
  background: rgba(139, 94, 52, 0.12);
}

.admin-menu :deep(.el-menu-item.is-active) {
  color: #fff;
  background: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.admin-menu :deep(.el-menu-item.is-active .tcm-icon img) {
  filter: brightness(0) invert(1) sepia(0.15) saturate(0.8);
  opacity: 0.94;
}

.admin-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  height: 88px;
  padding: 0 24px;
  background: rgba(251, 247, 239, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--color-border);
  overflow: hidden;
}

.admin-header::after {
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

.admin-header > * {
  position: relative;
  z-index: 1;
}

.admin-header-title {
  color: var(--color-primary-dark);
  font-family: "Noto Serif SC", "Songti SC", "SimSun", "Microsoft YaHei", serif;
  font-size: 20px;
  font-weight: 700;
}

.admin-header-subtitle {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 13px;
}

.admin-header-links {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-body {
  position: relative;
  z-index: 1;
  height: 100vh;
  overflow: hidden;
}

.page-shell {
  height: calc(100vh - 88px);
  padding-bottom: 220px;
  overflow-y: auto;
}

@media (max-width: 960px) {
  .admin-aside {
    display: none;
  }

  .admin-header {
    padding: 16px;
    height: auto;
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-header::after {
    width: 180px;
    opacity: 0.16;
  }

  .admin-header-links {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
