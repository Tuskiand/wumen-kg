<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

import { createUser, deleteUser, getUsers, updateUser } from '@/api';
import { authState } from '@/auth';
import type { User, UserInput, UserUpdateInput } from '@/types';

const text = {
  title: '用户管理',
  subtitle: '管理管理员与普通用户账号，控制角色与启用状态。',
  create: '新增用户',
  username: '用户名',
  password: '密码',
  role: '角色',
  status: '状态',
  action: '操作',
  enabled: '启用',
  disabled: '停用',
  admin: '管理员',
  user: '普通用户',
  edit: '编辑',
  remove: '删除',
  dialogCreate: '新增用户',
  dialogEdit: '编辑用户',
  save: '保存',
  passwordHint: '编辑时留空则不修改密码',
};

const rows = ref<User[]>([]);
const visible = ref(false);
const saving = ref(false);
const editingId = ref<number | null>(null);
const form = reactive({
  username: '',
  password: '',
  role: 'user' as 'admin' | 'user',
  isActive: true,
});

function resetForm() {
  form.username = '';
  form.password = '';
  form.role = 'user';
  form.isActive = true;
  editingId.value = null;
}

async function loadData() {
  rows.value = await getUsers();
}

function openCreate() {
  resetForm();
  visible.value = true;
}

function openEdit(row: User) {
  editingId.value = row.id;
  form.username = row.username;
  form.password = '';
  form.role = row.role;
  form.isActive = row.isActive;
  visible.value = true;
}

async function submit() {
  saving.value = true;
  try {
    if (editingId.value !== null) {
      const payload: UserUpdateInput = {
        username: form.username,
        role: form.role,
        isActive: form.isActive,
      };
      if (form.password.trim()) {
        payload.password = form.password;
      }
      await updateUser(editingId.value, payload);
      ElMessage.success('用户已更新');
    } else {
      const payload: UserInput = {
        username: form.username,
        password: form.password,
        role: form.role,
        isActive: form.isActive,
      };
      await createUser(payload);
      ElMessage.success('用户已新增');
    }
    visible.value = false;
    await loadData();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败');
  } finally {
    saving.value = false;
  }
}

async function remove(row: User) {
  try {
    await ElMessageBox.confirm(`确认删除用户 ${row.username} 吗？`, '删除确认', { type: 'warning' });
    await deleteUser(row.id);
    ElMessage.success('用户已删除');
    await loadData();
  } catch (error) {
    if (error === 'cancel') {
      return;
    }
    ElMessage.error(error instanceof Error ? error.message : '删除失败');
  }
}

onMounted(async () => {
  await loadData();
});
</script>

<template>
  <section class="glass-panel section-card">
    <h1 class="page-title">{{ text.title }}</h1>
    <p class="page-subtitle">{{ text.subtitle }}</p>
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">{{ text.create }}</el-button>
    </div>
    <el-table :data="rows" style="margin-top: 20px">
      <el-table-column prop="id" label="ID" width="100" />
      <el-table-column prop="username" :label="text.username" min-width="180" />
      <el-table-column :label="text.role" width="140">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
            {{ row.role === 'admin' ? text.admin : text.user }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="text.status" width="140">
        <template #default="{ row }">
          <el-tag :type="row.isActive ? 'success' : 'info'">
            {{ row.isActive ? text.enabled : text.disabled }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="text.action" width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">{{ text.edit }}</el-button>
          <el-button link type="danger" :disabled="row.id === authState.user?.id" @click="remove(row)">{{ text.remove }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editingId !== null ? text.dialogEdit : text.dialogCreate" width="520px">
      <el-form label-position="top">
        <el-form-item :label="text.username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item :label="text.password">
          <el-input v-model="form.password" type="password" show-password />
          <div v-if="editingId !== null" class="field-hint">{{ text.passwordHint }}</div>
        </el-form-item>
        <el-form-item :label="text.role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option :label="text.admin" value="admin" />
            <el-option :label="text.user" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item :label="text.status">
          <el-switch v-model="form.isActive" :active-text="text.enabled" :inactive-text="text.disabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ text.save }}</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.toolbar {
  display: flex;
  justify-content: flex-end;
}

.field-hint {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 12px;
}
</style>
