import { onMounted, ref } from 'vue';
import { getGraphSchema } from '@/api';

const entityTypes = ref<string[]>([]);
const relationTypes = ref<string[]>([]);
const loaded = ref(false);
const loading = ref(false);

export function useSchema() {
  async function load() {
    if (loaded.value || loading.value) return;
    loading.value = true;
    try {
      const result = await getGraphSchema();
      entityTypes.value = result.entityTypes;
      relationTypes.value = result.relationTypes;
      loaded.value = true;
    } finally {
      loading.value = false;
    }
  }

  onMounted(load);

  return { entityTypes, relationTypes, loaded, loading, load };
}