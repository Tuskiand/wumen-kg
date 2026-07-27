import { reactive } from 'vue';

import { getCurrentUser } from '@/api';
import type { User } from '@/types';

const TOKEN_KEY = 'auth-token';
const USER_KEY = 'auth-user';

export const authState = reactive<{
  loaded: boolean;
  token: string;
  user: User | null;
}>({
  loaded: false,
  token: localStorage.getItem(TOKEN_KEY) ?? '',
  user: readStoredUser(),
});

let loadingPromise: Promise<void> | null = null;

function readStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function setSession(token: string, user: User) {
  authState.token = token;
  authState.user = user;
  authState.loaded = true;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  authState.token = '';
  authState.user = null;
  authState.loaded = true;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function ensureAuthLoaded() {
  if (authState.loaded) {
    return;
  }
  if (!authState.token) {
    clearSession();
    return;
  }
  if (loadingPromise) {
    return loadingPromise;
  }
  loadingPromise = (async () => {
    try {
      const user = await getCurrentUser();
      setSession(authState.token, user);
    } catch {
      clearSession();
    } finally {
      loadingPromise = null;
    }
  })();
  return loadingPromise;
}
