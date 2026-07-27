import { reactive } from 'vue';

export interface GraphCanvasSessionSettings {
  density: number;
}

const graphCanvasSessionSettings = reactive<GraphCanvasSessionSettings>({
  density: 50,
});

export function useGraphCanvasSettings() {
  return graphCanvasSessionSettings;
}
