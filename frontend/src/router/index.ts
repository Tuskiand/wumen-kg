import { createRouter, createWebHistory } from 'vue-router';

import { authState, ensureAuthLoaded } from '@/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/portal/home' },
    { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guestOnly: true } },
    { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { guestOnly: true } },
    {
      path: '/portal',
      component: () => import('@/layouts/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: 'home', component: () => import('@/views/portal/HomeView.vue') },
        { path: 'search', component: () => import('@/views/portal/SearchView.vue') },
        { path: 'graph', component: () => import('@/views/portal/GraphView.vue') },
        { path: 'entity/:id', component: () => import('@/views/portal/EntityDetailView.vue') },
        { path: 'path', component: () => import('@/views/portal/PathQueryView.vue') },
        { path: 'physician-compare', component: () => import('@/views/portal/PhysicianCompareView.vue') },
      ],
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, adminOnly: true },
      children: [
        { path: 'dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'graph', component: () => import('@/views/portal/GraphView.vue') },
        { path: 'path', component: () => import('@/views/portal/PathQueryView.vue') },
        { path: 'physician-compare', component: () => import('@/views/portal/PhysicianCompareView.vue') },
        { path: 'entities', component: () => import('@/views/admin/EntitiesView.vue') },
        { path: 'relations', component: () => import('@/views/admin/RelationsView.vue') },
        { path: 'imports', component: () => import('@/views/admin/ImportsView.vue') },
        { path: 'versions', component: () => import('@/views/admin/VersionsView.vue') },
        { path: 'audits', component: () => import('@/views/admin/AuditsView.vue') },
        { path: 'users', component: () => import('@/views/admin/UsersView.vue') },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  await ensureAuthLoaded();

  const requiresAuth = to.matched.some((record) => Boolean(record.meta.requiresAuth));
  const adminOnly = to.matched.some((record) => Boolean(record.meta.adminOnly));
  const guestOnly = to.matched.some((record) => Boolean(record.meta.guestOnly));
  const user = authState.user;

  if (guestOnly && user) {
    return user.role === 'admin' ? '/admin/dashboard' : '/portal/home';
  }

  if (requiresAuth && !user) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    };
  }

  if (adminOnly && user?.role !== 'admin') {
    return '/portal/home';
  }

  return true;
});

export default router;
