<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { login } from '@/api';
import { setSession } from '@/auth';

const router = useRouter();
const route = useRoute();
const logoSeal = new URL('@/assets/tcm-theme/brand/logo-seal-wumen.png', import.meta.url).href;
const text = {
  title: '知识图谱管理系统',
  subtitle: '基于《吴门医案》的图谱浏览、检索与治理平台。',
  username: '用户名',
  password: '密码',
  usernamePlaceholder: '请输入用户名',
  passwordPlaceholder: '请输入密码',
  submit: '登录系统',
  success: '登录成功',
  register: '注册普通用户',
};
const form = reactive({
  username: '',
  password: '',
});
const loading = ref(false);

function resolveTarget(role: 'admin' | 'user') {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '';
  if (redirect) {
    if (role === 'admin' || !redirect.startsWith('/admin')) {
      return redirect;
    }
  }
  return role === 'admin' ? '/admin/dashboard' : '/portal/home';
}

async function submit() {
  loading.value = true;
  try {
    const result = await login(form.username, form.password);
    setSession(result.token, {
      id: result.id,
      username: result.username,
      role: result.role,
      isActive: true,
    });
    ElMessage.success(text.success);
    await router.push(resolveTarget(result.role));
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '登录失败');
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card glass-panel">
      <div class="login-heading">
        <img class="login-brand-logo tcm-seal-logo is-login" :src="logoSeal" alt="吴门医派" />
        <div class="login-kicker">WuMen Medical Graph</div>
        <h1>{{ text.title }}</h1>
        <p>{{ text.subtitle }}</p>
      </div>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item :label="text.username">
          <el-input v-model="form.username" :placeholder="text.usernamePlaceholder" />
        </el-form-item>
        <el-form-item :label="text.password">
          <el-input v-model="form.password" type="password" show-password :placeholder="text.passwordPlaceholder" />
        </el-form-item>
        <el-button type="primary" class="full-width" :loading="loading" @click="submit">
          {{ text.submit }}
        </el-button>
        <el-button class="full-width" style="margin-top: 12px" tag="router-link" to="/register">
          {{ text.register }}
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  background-image:
    linear-gradient(rgba(251, 248, 241, 0.42), rgba(251, 248, 241, 0.66)),
    url("@/assets/tcm-theme/backgrounds/bg-ink-mountain-banner.png");
  background-repeat: no-repeat;
  background-position: center bottom;
  background-size: cover;
  place-items: center;
}

.login-card {
  width: min(460px, 100%);
  padding: 40px;
  border-radius: 24px;
}

.login-heading {
  position: relative;
  z-index: 1;
  text-align: center;
}

.login-kicker {
  color: var(--brand);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1 {
  margin: 10px 0 8px;
  font-size: 28px;
}

p {
  margin: 0 0 24px;
  color: var(--text-sub);
  font-size: 15px;
}

@media (max-width: 960px) {
  .login-card {
    padding: 32px 24px;
  }
}
</style>
