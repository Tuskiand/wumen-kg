<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { login, register } from '@/api';
import { setSession } from '@/auth';

const router = useRouter();
const logoSeal = new URL('@/assets/tcm-theme/brand/logo-seal-wumen.png', import.meta.url).href;
const text = {
  title: '创建普通用户账号',
  subtitle: '注册成功后会自动登录并进入用户端。',
  username: '用户名',
  password: '密码',
  confirmPassword: '确认密码',
  usernamePlaceholder: '请输入用户名',
  passwordPlaceholder: '请输入密码',
  confirmPasswordPlaceholder: '请再次输入密码',
  submit: '注册并登录',
  back: '返回登录',
};
const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
});
const loading = ref(false);

async function submit() {
  if (form.password !== form.confirmPassword) {
    ElMessage.error('两次输入的密码不一致');
    return;
  }
  loading.value = true;
  try {
    await register(form.username, form.password);
    const result = await login(form.username, form.password);
    setSession(result.token, {
      id: result.id,
      username: result.username,
      role: result.role,
      isActive: true,
    });
    ElMessage.success('注册成功，已自动登录');
    await router.push('/portal/home');
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '注册失败');
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
        <el-form-item :label="text.confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password :placeholder="text.confirmPasswordPlaceholder" />
        </el-form-item>
        <el-button type="primary" class="full-width" :loading="loading" @click="submit">
          {{ text.submit }}
        </el-button>
        <el-button class="full-width" style="margin-top: 12px" tag="router-link" to="/login">
          {{ text.back }}
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
  padding: 32px;
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
  .login-page {
    padding: 20px;
  }

  .login-card {
    padding: 32px 24px;
  }
}
</style>
