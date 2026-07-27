import type {
  AuditRecord,
  GraphEdge,
  GraphNode,
  GraphSnapshot,
  ImportTask,
  SearchResult,
  VersionRecord,
} from '@/types';

const nodes: GraphNode[] = [
  { id: 'doctor-001', name: '薛雪', label: 'A医家', type: 'A医家', summary: '吴门医家，擅长内风与痰证辨治。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'disease-001', name: '中风', label: 'B病名', type: 'B病名', summary: '以猝然昏仆、口眼㖞斜、半身不遂为主要表现。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'pattern-001', name: '风痰闭阻证', label: 'C证型', type: 'C证型', summary: '风痰闭阻经络，清窍不利。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'cause-001', name: '风痰上扰', label: 'D病因', type: 'D病因', summary: '外风引动痰浊，上蒙清窍。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'mechanism-001', name: '痰阻清窍', label: 'E病机', type: 'E病机', summary: '痰浊闭阻清窍，经络不畅。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
];

const edges: GraphEdge[] = [
  { id: 'e1', source: 'doctor-001', target: 'disease-001', type: 'A医家-B病名', label: 'A医家-B病名', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e2', source: 'doctor-001', target: 'pattern-001', type: 'A医家-C证型', label: 'A医家-C证型', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e3', source: 'doctor-001', target: 'cause-001', type: 'A医家-D病因', label: 'A医家-D病因', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e4', source: 'doctor-001', target: 'mechanism-001', type: 'A医家-E病机', label: 'A医家-E病机', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e5', source: 'disease-001', target: 'pattern-001', type: 'B病名-C证型', label: 'B病名-C证型', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e6', source: 'disease-001', target: 'cause-001', type: 'B病名-D病因', label: 'B病名-D病因', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e7', source: 'disease-001', target: 'mechanism-001', type: 'B病名-E病机', label: 'B病名-E病机', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e8', source: 'cause-001', target: 'mechanism-001', type: 'D病因-E病机', label: 'D病因-E病机', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
  { id: 'e9', source: 'pattern-001', target: 'mechanism-001', type: 'C证型-E病机', label: 'C证型-E病机', sourceCases: ['中风'], sourceBatches: ['吴门医案·卷一'] },
];

const imports: ImportTask[] = [
  { id: 'import-20260309-01', name: '第一批图谱导入', createdAt: '2026-03-09 09:30', status: 'completed', summary: '来源医案 中风，新增节点 5 个，新增关系 9 条。', source: '吴门医案·卷一', sourceCase: '中风', createdNodes: 5, mergedNodes: 0, createdRelations: 9, deduplicatedRelations: 0 },
];

const versions: VersionRecord[] = [
  { id: 'v1.0.0', name: '一期基线数据', createdAt: '2026-03-09 10:00', status: 'published' },
  { id: 'v1.1.0-rc1', name: '字段映射修订', createdAt: '2026-03-09 11:15', status: 'draft' },
];

const audits: AuditRecord[] = [
  { id: 'audit-01', actor: 'admin', action: '导入发布', target: 'v1.0.0', createdAt: '2026-03-09 10:05', result: '成功' },
  { id: 'audit-02', actor: 'editor', action: '编辑节点', target: 'disease-001', createdAt: '2026-03-09 10:36', result: '成功' },
];

function sleep<T>(payload: T, delay = 320): Promise<T> {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(payload), delay);
  });
}

export function login(username: string, password: string) {
  return sleep({
    token: 'mock-jwt-token',
    id: 1,
    username,
    expiresIn: 7200,
    role: username === 'admin' && password ? 'admin' : 'user',
  });
}

export function getDashboardStats() {
  return sleep({
    nodeCount: nodes.length,
    edgeCount: edges.length,
    importSuccessRate: 98.4,
    lastPublishAt: '2026-03-09 10:05',
  });
}

export function searchGraph(query = '', entityType = '', source = '', sourceCase = ''): Promise<SearchResult> {
  const filtered = nodes.filter((item) => {
    const textMatch = query ? item.name.includes(query) || item.summary?.includes(query) : true;
    const typeMatch = entityType ? item.type === entityType : true;
    const sourceMatch = source ? item.source === source : true;
    const sourceCaseMatch = sourceCase ? item.sourceCases.includes(sourceCase) : true;
    return textMatch && typeMatch && sourceMatch && sourceCaseMatch;
  });
  return sleep({ total: filtered.length, items: filtered });
}

export function getGraphSnapshot(source = '', sourceCase = '', entityType = ''): Promise<GraphSnapshot> {
  const filteredNodes = nodes.filter((item) => (!source || item.source === source) && (!sourceCase || item.sourceCases.includes(sourceCase)) && (!entityType || item.type === entityType));
  const nodeIds = new Set(filteredNodes.map((item) => item.id));
  const filteredEdges = edges.filter((item) => nodeIds.has(item.source) && nodeIds.has(item.target) && (!sourceCase || item.sourceCases.includes(sourceCase)));
  return sleep({ nodes: filteredNodes, edges: filteredEdges });
}

export function getEntityDetail(id: string) {
  const node = nodes.find((item) => item.id === id) ?? nodes[0];
  const relatedEdges = edges.filter((item) => item.source === node.id || item.target === node.id);
  const relatedIds = new Set(relatedEdges.flatMap((item) => [item.source, item.target]));
  const relatedNodes = nodes.filter((item) => relatedIds.has(item.id) && item.id !== node.id);
  return sleep({ entity: node, relations: relatedEdges, neighbors: relatedNodes });
}

export function queryPath(sourceName: string, targetName: string, sourceCase = '') {
  const source = nodes.find((item) => item.name === sourceName && (!sourceCase || item.sourceCases.includes(sourceCase)));
  const target = nodes.find((item) => item.name === targetName && (!sourceCase || item.sourceCases.includes(sourceCase)));
  const pathEdges = source && target
    ? edges.filter((item) => (
      (item.source === source.id && item.target === target.id)
      || (item.source === target.id && item.target === source.id)
    ) && (!sourceCase || item.sourceCases.includes(sourceCase)))
    : [];
  const pathNodeIds = new Set(pathEdges.flatMap((item) => [item.source, item.target]));
  const pathNodes = nodes.filter((item) => pathNodeIds.has(item.id));
  return sleep({
    nodes: pathNodes,
    edges: pathEdges,
    description: pathEdges.length ? `找到 ${pathEdges.length} 条路径关系。` : '未找到符合筛选条件的路径。',
  });
}

export function getEntities() {
  return sleep(nodes);
}

export function getRelations() {
  return sleep(edges);
}

export function getImportTasks() {
  return sleep(imports);
}

export function getVersionRecords() {
  return sleep(versions);
}

export function getAuditRecords() {
  return sleep(audits);
}

