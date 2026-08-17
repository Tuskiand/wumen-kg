import type {
  AuditRecord,
  GraphEdge,
  GraphNode,
  ImportTask,
  User,
  VersionRecord,
} from '@/types';

type JsonRecord = Record<string, unknown>;

const TOKEN_KEY = 'auth-token';

const nodes: GraphNode[] = [
  { id: 'doctor-xue', name: '薛雪', label: 'A医家', type: 'A医家', summary: '吴门医家，重视风痰、痰热与清窍闭阻。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'doctor-ye', name: '叶天士', label: 'A医家', type: 'A医家', summary: '善从络病、肝风和阴虚内动辨析中风。', source: '吴门医案·卷二', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'doctor-wang', name: '王孟英', label: 'A医家', type: 'A医家', summary: '强调痰热、津伤与气机郁滞的综合辨治。', source: '吴门医案·卷三', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'disease-zhongfeng', name: '中风', label: 'B病名', type: 'B病名', summary: '以猝然昏仆、口眼㖞斜、半身不遂为主要表现。', source: '吴门医案', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'pattern-fengtan', name: '风痰闭阻证', label: 'C证型', type: 'C证型', summary: '风痰闭阻经络，清窍不利。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'pattern-yinxu', name: '阴虚风动证', label: 'C证型', type: 'C证型', summary: '阴液亏虚，虚风内动，上扰清窍。', source: '吴门医案·卷二', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'pattern-tanre', name: '痰热腑实证', label: 'C证型', type: 'C证型', summary: '痰热内结，腑气不通，神明受扰。', source: '吴门医案·卷三', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'cause-fengtan', name: '风痰上扰', label: 'D病因', type: 'D病因', summary: '外风引动痰浊，上蒙清窍。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'cause-yinxu', name: '肝肾阴虚', label: 'D病因', type: 'D病因', summary: '阴虚阳亢，筋脉失养。', source: '吴门医案·卷二', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'cause-tanre', name: '痰热内蕴', label: 'D病因', type: 'D病因', summary: '痰热互结，气机壅滞。', source: '吴门医案·卷三', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'mechanism-qingqiao', name: '痰阻清窍', label: 'E病机', type: 'E病机', summary: '痰浊闭阻清窍，经络不畅。', source: '吴门医案·卷一', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'mechanism-neifeng', name: '虚风内动', label: 'E病机', type: 'E病机', summary: '阴虚不能潜阳，内风扰动。', source: '吴门医案·卷二', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
  { id: 'mechanism-fushi', name: '腑气不通', label: 'E病机', type: 'E病机', summary: '痰热腑实，升降失司。', source: '吴门医案·卷三', sourceCases: ['中风'], sourceBatches: ['演示数据'] },
];

const edges: GraphEdge[] = [
  edge('e1', 'doctor-xue', 'disease-zhongfeng', 'A医家-B病名'),
  edge('e2', 'doctor-ye', 'disease-zhongfeng', 'A医家-B病名'),
  edge('e3', 'doctor-wang', 'disease-zhongfeng', 'A医家-B病名'),
  edge('e4', 'doctor-xue', 'pattern-fengtan', 'A医家-C证型'),
  edge('e5', 'doctor-ye', 'pattern-yinxu', 'A医家-C证型'),
  edge('e6', 'doctor-wang', 'pattern-tanre', 'A医家-C证型'),
  edge('e7', 'doctor-xue', 'cause-fengtan', 'A医家-D病因'),
  edge('e8', 'doctor-ye', 'cause-yinxu', 'A医家-D病因'),
  edge('e9', 'doctor-wang', 'cause-tanre', 'A医家-D病因'),
  edge('e10', 'doctor-xue', 'mechanism-qingqiao', 'A医家-E病机'),
  edge('e11', 'doctor-ye', 'mechanism-neifeng', 'A医家-E病机'),
  edge('e12', 'doctor-wang', 'mechanism-fushi', 'A医家-E病机'),
  edge('e13', 'cause-fengtan', 'mechanism-qingqiao', 'D病因-E病机'),
  edge('e14', 'cause-yinxu', 'mechanism-neifeng', 'D病因-E病机'),
  edge('e15', 'cause-tanre', 'mechanism-fushi', 'D病因-E病机'),
  edge('e16', 'mechanism-qingqiao', 'pattern-fengtan', 'E病机-C证型'),
  edge('e17', 'mechanism-neifeng', 'pattern-yinxu', 'E病机-C证型'),
  edge('e18', 'mechanism-fushi', 'pattern-tanre', 'E病机-C证型'),
];

const imports: ImportTask[] = [
  { id: 'import-demo-01', name: '演示图谱导入', createdAt: '2026-03-09 09:30', status: 'completed', summary: '来源医案 中风，新增节点 13 个，新增关系 18 条。', source: '吴门医案', sourceCase: '中风', createdNodes: 13, mergedNodes: 0, createdRelations: 18, deduplicatedRelations: 0 },
];

const versions: VersionRecord[] = [
  { id: 'v1.0.0-demo', name: '演示基线数据', createdAt: '2026-03-09 10:00', status: 'published' },
  { id: 'v1.1.0-demo', name: '医家比较演示数据', createdAt: '2026-03-09 11:15', status: 'draft' },
];

const audits: AuditRecord[] = [
  { id: 'audit-demo-01', actor: 'admin', action: '导入发布', target: 'v1.0.0-demo', createdAt: '2026-03-09 10:05', result: '成功' },
  { id: 'audit-demo-02', actor: 'editor', action: '编辑节点', target: '风痰闭阻证', createdAt: '2026-03-09 10:36', result: '成功' },
];

const users: User[] = [
  { id: 1, username: 'admin', role: 'admin', isActive: true },
  { id: 2, username: 'demo', role: 'user', isActive: true },
];

function edge(id: string, source: string, target: string, type: string): GraphEdge {
  return { id, source, target, type, label: type, sourceCases: ['中风'], sourceBatches: ['演示数据'] };
}

function sleep<T>(payload: T, delay = 180): Promise<T> {
  return new Promise((resolve) => window.setTimeout(() => resolve(payload), delay));
}

function rawNode(item: GraphNode): JsonRecord {
  return {
    id: item.id,
    name: item.name,
    label: item.label,
    type: item.type,
    summary: item.summary,
    source: item.source,
    source_cases: item.sourceCases,
    source_batches: item.sourceBatches,
  };
}

function rawEdge(item: GraphEdge): JsonRecord {
  return {
    id: item.id,
    source: item.source,
    target: item.target,
    type: item.type,
    label: item.label,
    source_cases: item.sourceCases,
    source_batches: item.sourceBatches,
  };
}

function rawUser(item: User): JsonRecord {
  return { id: item.id, username: item.username, role: item.role, is_active: item.isActive };
}

function rawImport(item: ImportTask): JsonRecord {
  return {
    id: item.id,
    name: item.name,
    created_at: item.createdAt,
    status: item.status,
    summary: item.summary,
    source: item.source,
    source_case: item.sourceCase,
    schema: item.schema,
    created_nodes: item.createdNodes,
    merged_nodes: item.mergedNodes,
    created_relations: item.createdRelations,
    deduplicated_relations: item.deduplicatedRelations,
  };
}

function parsePath(path: string) {
  return new URL(path, window.location.origin);
}

async function readJson(init?: RequestInit): Promise<JsonRecord> {
  if (!init?.body || init.body instanceof FormData) return {};
  return JSON.parse(String(init.body)) as JsonRecord;
}

function compareNode(id: string): JsonRecord {
  const node = nodes.find((item) => item.id === id);
  if (!node) throw new Error(`Missing demo node: ${id}`);
  return { id: node.id, name: node.name, label: node.label, type: node.type };
}

const doctors = ['doctor-xue', 'doctor-ye', 'doctor-wang'].map((id) => nodes.find((item) => item.id === id)!);

const compareGroups = {
  xue: {
    patterns: [compareNode('pattern-fengtan')],
    causes: [compareNode('cause-fengtan')],
    mechanisms: [compareNode('mechanism-qingqiao')],
  },
  ye: {
    patterns: [compareNode('pattern-yinxu')],
    causes: [compareNode('cause-yinxu')],
    mechanisms: [compareNode('mechanism-neifeng')],
  },
  wang: {
    patterns: [compareNode('pattern-tanre')],
    causes: [compareNode('cause-tanre')],
    mechanisms: [compareNode('mechanism-fushi')],
  },
};

const emptyGroup = { patterns: [], causes: [], mechanisms: [] };

function similarityPair(left: string, right: string, jaccard: number, overlap: number, cosine: number) {
  return { left_doctor: left, right_doctor: right, jaccard, overlap, cosine };
}

const similarity = {
  patterns: [
    similarityPair('薛雪', '叶天士', 0.18, 0.33, 0.61),
    similarityPair('薛雪', '王孟英', 0.24, 0.42, 0.68),
    similarityPair('叶天士', '王孟英', 0.16, 0.29, 0.55),
  ],
  causes: [
    similarityPair('薛雪', '叶天士', 0.15, 0.25, 0.58),
    similarityPair('薛雪', '王孟英', 0.31, 0.45, 0.72),
    similarityPair('叶天士', '王孟英', 0.12, 0.22, 0.51),
  ],
  mechanisms: [
    similarityPair('薛雪', '叶天士', 0.2, 0.36, 0.64),
    similarityPair('薛雪', '王孟英', 0.26, 0.4, 0.69),
    similarityPair('叶天士', '王孟英', 0.14, 0.25, 0.53),
  ],
  overall: [
    similarityPair('薛雪', '叶天士', 0.19, 0.34, 0.62),
    similarityPair('薛雪', '王孟英', 0.28, 0.43, 0.7),
    similarityPair('叶天士', '王孟英', 0.15, 0.27, 0.54),
  ],
};

function nodeCompareResponse() {
  return {
    disease: '中风',
    doctor_count: doctors.length,
    doctors: doctors.map(rawNode),
    similarity,
    fastrp_similarity: similarity,
    shared_nodes: {
      patterns: [{ node: compareNode('pattern-fengtan'), doctors: ['薛雪', '王孟英'] }],
      causes: [{ node: compareNode('cause-fengtan'), doctors: ['薛雪', '王孟英'] }],
      mechanisms: [{ node: compareNode('mechanism-qingqiao'), doctors: ['薛雪', '王孟英'] }],
    },
    doctor_profiles: [
      { doctor: rawNode(doctors[0]), all: compareGroups.xue, shared: { patterns: [compareNode('pattern-fengtan')], causes: [compareNode('cause-fengtan')], mechanisms: [compareNode('mechanism-qingqiao')] }, unique: emptyGroup },
      { doctor: rawNode(doctors[1]), all: compareGroups.ye, shared: emptyGroup, unique: compareGroups.ye },
      { doctor: rawNode(doctors[2]), all: compareGroups.wang, shared: emptyGroup, unique: compareGroups.wang },
    ],
    rwr: doctors.map((doctor, index) => ({
      doctor: rawNode(doctor),
      restart_probability: 0.35,
      rankings: {
        patterns: [{ ...compareNode(['pattern-fengtan', 'pattern-yinxu', 'pattern-tanre'][index]), score: 0.82 - index * 0.08, count: 3 - index }],
        causes: [{ ...compareNode(['cause-fengtan', 'cause-yinxu', 'cause-tanre'][index]), score: 0.78 - index * 0.07, count: 3 - index }],
        mechanisms: [{ ...compareNode(['mechanism-qingqiao', 'mechanism-neifeng', 'mechanism-fushi'][index]), score: 0.74 - index * 0.06, count: 3 - index }],
      },
    })),
    doctor_feature_embeddings: doctors.map((doctor, index) => ({
      doctor: rawNode(doctor),
      patterns: [0.2 + index * 0.2, 0.4, 0.6 - index * 0.1],
      causes: [0.3, 0.5 + index * 0.1, 0.2],
      mechanisms: [0.4, 0.2 + index * 0.1, 0.7],
      overall: [0.3 + index * 0.1, 0.5, 0.6 - index * 0.05],
    })),
    similarity_overview: doctors.map((doctor, index) => ({
      doctor: rawNode(doctor),
      scores: { patterns: 0.78 - index * 0.08, causes: 0.74 - index * 0.06, mechanisms: 0.7 - index * 0.05, overall: 0.76 - index * 0.06 },
    })),
    feature_similarity_candidates: [
      { category: '证型', left_doctor: '薛雪', left_feature_name: '风痰闭阻证', right_doctor: '王孟英', right_feature_name: '痰热腑实证', similarity: 0.72 },
    ],
    embedding_points: [
      { id: 'doctor-xue', label: '薛雪', group: '医家', x: 0.1, y: 0.35 },
      { id: 'doctor-ye', label: '叶天士', group: '医家', x: 0.65, y: 0.68 },
      { id: 'doctor-wang', label: '王孟英', group: '医家', x: 0.38, y: 0.18 },
    ],
    summary: {
      primary_similarity_metric: 'Jaccard',
      primary_embedding_metric: 'FastRP Cosine',
      shared_node_count: 3,
      pairwise_comparison_count: 3,
      primary_restart_probability: 0.35,
      message: '演示数据展示三位医家在中风辨证中的节点相似度、共享节点与随机游走排序。',
    },
  };
}

function pathChain(signature: string, text: string, cause: string, mechanism: string, pattern: string) {
  return {
    path_type: '病因-病机-证型',
    path_category: 'complete',
    signature,
    text,
    cause: compareNode(cause),
    mechanism: compareNode(mechanism),
    pattern: compareNode(pattern),
  };
}

function pathCompareResponse() {
  const chains = [
    pathChain('风痰上扰>痰阻清窍>风痰闭阻证', '风痰上扰 -> 痰阻清窍 -> 风痰闭阻证', 'cause-fengtan', 'mechanism-qingqiao', 'pattern-fengtan'),
    pathChain('肝肾阴虚>虚风内动>阴虚风动证', '肝肾阴虚 -> 虚风内动 -> 阴虚风动证', 'cause-yinxu', 'mechanism-neifeng', 'pattern-yinxu'),
    pathChain('痰热内蕴>腑气不通>痰热腑实证', '痰热内蕴 -> 腑气不通 -> 痰热腑实证', 'cause-tanre', 'mechanism-fushi', 'pattern-tanre'),
  ];
  return {
    disease: '中风',
    doctor_count: doctors.length,
    doctors: doctors.map(rawNode),
    shared_paths: [{ path: chains[0], doctors: ['薛雪', '王孟英'] }],
    doctor_profiles: doctors.map((doctor, index) => ({
      doctor: rawNode(doctor),
      complete_paths: [chains[index]],
      partial_paths: [],
      single_paths: [],
      unique_paths: index === 0 ? [] : [chains[index]],
      completeness: { complete_count: 1, partial_count: 0, single_count: 0, total_count: 1, complete_ratio: 1, path_coverage: 0.66 - index * 0.08 },
    })),
    similarity_pairs: [
      { left_doctor: '薛雪', right_doctor: '叶天士', shared_path_count: 0, union_path_count: 2, path_jaccard: 0, metapath2vec_cosine: 0.48 },
      { left_doctor: '薛雪', right_doctor: '王孟英', shared_path_count: 1, union_path_count: 2, path_jaccard: 0.5, metapath2vec_cosine: 0.71 },
      { left_doctor: '叶天士', right_doctor: '王孟英', shared_path_count: 0, union_path_count: 2, path_jaccard: 0, metapath2vec_cosine: 0.44 },
    ],
    embeddings: doctors.map((doctor, index) => ({ doctor: rawNode(doctor), vector: [0.2 + index * 0.2, 0.6 - index * 0.1, 0.3 + index * 0.05] })),
    embedding_points: [
      { id: 'path-xue', label: '薛雪', group: '路径', x: 0.2, y: 0.3 },
      { id: 'path-ye', label: '叶天士', group: '路径', x: 0.72, y: 0.64 },
      { id: 'path-wang', label: '王孟英', group: '路径', x: 0.42, y: 0.24 },
    ],
    summary: {
      shared_path_count: 1,
      pairwise_comparison_count: 3,
      primary_similarity_metric: 'Path Jaccard',
      embedding_metric: 'Metapath2Vec Cosine',
      message: '演示数据展示完整辨证路径、共享路径和路径向量相似度。',
    },
  };
}

function subgraphCompareResponse() {
  const sharedEdge = {
    signature: '风痰上扰-D病因-E病机-痰阻清窍',
    relation_type: 'D病因-E病机',
    text: '风痰上扰 -> 痰阻清窍',
    source_name: '风痰上扰',
    source_type: 'D病因',
    target_name: '痰阻清窍',
    target_type: 'E病机',
  };
  return {
    disease: '中风',
    doctor_count: doctors.length,
    doctors: doctors.map(rawNode),
    similarity_pairs: [
      { left_doctor: '薛雪', right_doctor: '叶天士', node_jaccard: 0.18, edge_jaccard: 0.12, subgraph_jaccard: 0.15, graph2vec_cosine: 0.52 },
      { left_doctor: '薛雪', right_doctor: '王孟英', node_jaccard: 0.31, edge_jaccard: 0.26, subgraph_jaccard: 0.29, graph2vec_cosine: 0.73 },
      { left_doctor: '叶天士', right_doctor: '王孟英', node_jaccard: 0.16, edge_jaccard: 0.1, subgraph_jaccard: 0.13, graph2vec_cosine: 0.47 },
    ],
    shared_nodes: nodeCompareResponse().shared_nodes,
    shared_edges: [{ edge: sharedEdge, doctors: ['薛雪', '王孟英'] }],
    doctor_profiles: doctors.map((doctor, index) => ({
      doctor: rawNode(doctor),
      node_count: 4,
      edge_count: 5,
      nodes: [compareGroups.xue, compareGroups.ye, compareGroups.wang][index],
      unique_nodes: index === 0 ? emptyGroup : [compareGroups.xue, compareGroups.ye, compareGroups.wang][index],
      edges: [sharedEdge],
      unique_edges: index === 0 ? [] : [sharedEdge],
      relation_distribution: [
        { relation_type: 'A医家-C证型', count: 1, ratio: 0.33 },
        { relation_type: 'D病因-E病机', count: 1, ratio: 0.33 },
        { relation_type: 'E病机-C证型', count: 1, ratio: 0.34 },
      ],
      audit_nodes: [compareNode(['pattern-fengtan', 'pattern-yinxu', 'pattern-tanre'][index])].map((item) => ({ ...item, inclusion_reason: '核心辨证节点' })),
      audit_edges: [sharedEdge],
    })),
    embeddings: doctors.map((doctor, index) => ({ doctor: rawNode(doctor), graph2vec_vector: [0.25 + index * 0.12, 0.5 - index * 0.05, 0.4 + index * 0.08] })),
    embedding_points: [
      { id: 'subgraph-xue', label: '薛雪', group: '子图', x: 0.12, y: 0.38 },
      { id: 'subgraph-ye', label: '叶天士', group: '子图', x: 0.68, y: 0.7 },
      { id: 'subgraph-wang', label: '王孟英', group: '子图', x: 0.4, y: 0.2 },
    ],
    summary: {
      primary_similarity_metric: 'Subgraph Jaccard',
      shared_node_count: 3,
      shared_edge_count: 1,
      pairwise_comparison_count: 3,
      vector_similarity_metrics: ['Graph2Vec Cosine'],
      message: '演示数据展示医家核心子图、共享边和子图向量相似度。',
    },
  };
}

export async function demoRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const url = parsePath(path);
  const method = (init?.method ?? 'GET').toUpperCase();
  const pathname = url.pathname;

  if (pathname === '/auth/login' && method === 'POST') {
    const body = await readJson(init);
    const username = String(body.username || 'demo');
    const role = username === 'admin' ? 'admin' : 'user';
    localStorage.setItem(TOKEN_KEY, 'demo-token');
    return sleep({ token: 'demo-token', id: role === 'admin' ? 1 : 2, username, expires_in: 7200, role } as T);
  }
  if (pathname === '/auth/register' && method === 'POST') {
    const body = await readJson(init);
    const user: User = { id: users.length + 1, username: String(body.username || 'demo-user'), role: 'user', isActive: true };
    users.push(user);
    return sleep(rawUser(user) as T);
  }
  if (pathname === '/auth/me') return sleep(rawUser(users[0]) as T);
  if (pathname === '/auth/logout') {
    localStorage.removeItem(TOKEN_KEY);
    return sleep({ message: 'ok' } as T);
  }

  if (pathname === '/admin/dashboard') {
    return sleep({ node_count: nodes.length, edge_count: edges.length, import_success_rate: 100, last_publish_at: '2026-03-09 10:05' } as T);
  }
  if (pathname === '/graph/search') {
    const query = url.searchParams.get('q') ?? '';
    const entityType = url.searchParams.get('entity_type') ?? '';
    const source = url.searchParams.get('source') ?? '';
    const sourceCase = url.searchParams.get('source_case') ?? '';
    const items = nodes.filter((item) => {
      const textMatch = query ? item.name.includes(query) || item.summary?.includes(query) : true;
      const typeMatch = entityType ? item.type === entityType : true;
      const sourceMatch = source ? item.source === source : true;
      const sourceCaseMatch = sourceCase ? item.sourceCases.includes(sourceCase) : true;
      return textMatch && typeMatch && sourceMatch && sourceCaseMatch;
    });
    return sleep({ total: items.length, items: items.map(rawNode) } as T);
  }
  if (pathname === '/graph/snapshot') {
    const entityType = url.searchParams.get('entity_type') ?? '';
    const name = url.searchParams.get('name') ?? '';
    let filteredNodes = nodes.filter((item) => (!entityType || item.type === entityType));
    if (name) filteredNodes = filteredNodes.filter((item) => item.name.includes(name));
    const ids = new Set(filteredNodes.map((item) => item.id));
    return sleep({ nodes: filteredNodes.map(rawNode), edges: edges.filter((item) => ids.has(item.source) && ids.has(item.target)).map(rawEdge) } as T);
  }
  if (pathname === '/graph/schema') {
    const allTypes = [...new Set(nodes.map((n) => n.type))].sort();
    const allRelationTypes = [...new Set(edges.map((e) => e.type))].sort();
    return sleep({ entity_types: allTypes, relation_types: allRelationTypes } as T);
  }
  if (pathname === '/ai/analyze-physician-compare' && method === 'POST') {
    return sleep({ analysis: '## 整体结论\n三位医家对"中风"的辨证思路各有侧重，但均围绕风、痰、虚三大病机展开。\n\n### 节点比较\n张璐与徐灵胎在辨证节点上的 Jaccard 相似度较高，说明二者对中风病因病机的认识有较大重叠。沈颋与其他两位医家的相似度较低，提示其辨证视角更为独特。\n\n### 辨证路径\n张璐的辨证路径完整率最高，说明其辨证逻辑链条最为完整。徐灵胎的路径覆盖更广，涉及更多病因类型。\n\n### 核心子图\n从子图结构看，三位医家的辨证网络存在明显差异，张璐偏向痰火论治，徐灵胎重视内外风相煽，沈颋侧重于肝肾阴虚。', model: 'deepseek-chat' } as T);
  }
  if (pathname === '/ai/config') {
    if (method === 'GET') {
      return sleep({ base_url: 'https://api.deepseek.com/v1', model: 'deepseek-chat', has_key: true } as T);
    }
    if (method === 'PUT') {
      return sleep({ base_url: 'https://api.deepseek.com/v1', model: 'deepseek-chat', has_key: true } as T);
    }
  }
  if (pathname.startsWith('/graph/entity/')) {
    const id = decodeURIComponent(pathname.split('/').pop() ?? '');
    const entity = nodes.find((item) => item.id === id) ?? nodes[0];
    const relations = edges.filter((item) => item.source === entity.id || item.target === entity.id);
    const neighborIds = new Set(relations.flatMap((item) => [item.source, item.target]));
    return sleep({ entity: rawNode(entity), relations: relations.map(rawEdge), neighbors: nodes.filter((item) => neighborIds.has(item.id) && item.id !== entity.id).map(rawNode) } as T);
  }
  if (pathname === '/graph/path/query') {
    const body = await readJson(init);
    const source = nodes.find((item) => item.name === body.source_name);
    const target = nodes.find((item) => item.name === body.target_name);
    const pathEdges = source && target ? edges.filter((item) => (item.source === source.id && item.target === target.id) || (item.source === target.id && item.target === source.id)) : [];
    const ids = new Set(pathEdges.flatMap((item) => [item.source, item.target]));
    return sleep({ nodes: nodes.filter((item) => ids.has(item.id)).map(rawNode), edges: pathEdges.map(rawEdge), description: pathEdges.length ? `找到 ${pathEdges.length} 条路径关系。` : '未找到符合筛选条件的路径。' } as T);
  }

  if (pathname === '/graph/compare/nodes') return sleep(nodeCompareResponse() as T);
  if (pathname === '/graph/compare/paths') return sleep(pathCompareResponse() as T);
  if (pathname === '/graph/compare/subgraphs') return sleep(subgraphCompareResponse() as T);

  if (pathname === '/admin/entities' && method === 'GET') return sleep(nodes.map(rawNode) as T);
  if (pathname === '/admin/entities' && method === 'POST') {
    const body = await readJson(init);
    const node = toNode(body, `node-${Date.now()}`);
    nodes.push(node);
    return sleep(rawNode(node) as T);
  }
  if (pathname.startsWith('/admin/entities/') && method === 'PUT') {
    const id = decodeURIComponent(pathname.split('/').pop() ?? '');
    const body = await readJson(init);
    const index = nodes.findIndex((item) => item.id === id);
    const node = toNode(body, id);
    if (index >= 0) nodes[index] = node;
    return sleep(rawNode(node) as T);
  }
  if (pathname.startsWith('/admin/entities/') && method === 'DELETE') return sleep({ message: 'deleted' } as T);
  if (pathname === '/admin/entities/batch-delete') return sleep({ message: 'deleted' } as T);

  if (pathname === '/admin/relations' && method === 'GET') return sleep(edges.map(rawEdge) as T);
  if (pathname === '/admin/relations' && method === 'POST') {
    const body = await readJson(init);
    const relation = toEdge(body, `edge-${Date.now()}`);
    edges.push(relation);
    return sleep(rawEdge(relation) as T);
  }
  if (pathname.startsWith('/admin/relations/') && method === 'PUT') {
    const id = decodeURIComponent(pathname.split('/').pop() ?? '');
    const body = await readJson(init);
    const relation = toEdge(body, id);
    const index = edges.findIndex((item) => item.id === id);
    if (index >= 0) edges[index] = relation;
    return sleep(rawEdge(relation) as T);
  }
  if (pathname.startsWith('/admin/relations/') && method === 'DELETE') return sleep({ message: 'deleted' } as T);
  if (pathname === '/admin/relations/batch-delete') return sleep({ message: 'deleted' } as T);

  if (pathname === '/admin/imports' && method === 'GET') return sleep(imports.map(rawImport) as T);
  if (pathname === '/admin/imports/validate' && method === 'POST') {
    const form = init?.body instanceof FormData ? init.body : new FormData();
    const task: ImportTask = {
      id: `import-demo-${imports.length + 1}`,
      name: '演示校验任务',
      createdAt: new Date().toISOString().slice(0, 19).replace('T', ' '),
      status: 'validating',
      summary: '演示模式已完成 CSV 结构校验，不会写入数据库。',
      source: String(form.get('source') ?? '演示来源'),
      sourceCase: String(form.get('source_case') ?? '中风'),
      createdNodes: 0,
      mergedNodes: 0,
      createdRelations: 0,
      deduplicatedRelations: 0,
    };
    imports.unshift(task);
    return sleep(rawImport(task) as T);
  }
  if (pathname.startsWith('/admin/imports/') && pathname.endsWith('/execute')) {
    const parts = pathname.split('/');
    const id = parts[parts.length - 2];
    const task = imports.find((item) => item.id === id) ?? imports[0];
    task.status = 'completed';
    task.summary = '演示模式执行成功，数据仅保存在浏览器内存中。';
    task.createdNodes = 3;
    task.createdRelations = 3;
    return sleep(rawImport(task) as T);
  }

  if (pathname === '/admin/versions') return sleep(versions.map((item) => ({ id: item.id, name: item.name, created_at: item.createdAt, status: item.status })) as T);
  if (pathname === '/admin/audits') return sleep(audits.map((item) => ({ id: item.id, actor: item.actor, action: item.action, target: item.target, created_at: item.createdAt, result: item.result })) as T);
  if (pathname === '/admin/users' && method === 'GET') return sleep(users.map(rawUser) as T);
  if (pathname === '/admin/users' && method === 'POST') {
    const body = await readJson(init);
    const user: User = { id: users.length + 1, username: String(body.username || `user${users.length + 1}`), role: body.role === 'admin' ? 'admin' : 'user', isActive: body.is_active !== false };
    users.push(user);
    return sleep(rawUser(user) as T);
  }
  if (pathname.startsWith('/admin/users/') && method === 'PUT') {
    const id = Number(pathname.split('/').pop());
    const body = await readJson(init);
    const user = users.find((item) => item.id === id) ?? users[0];
    if (body.username !== undefined) user.username = String(body.username);
    if (body.role === 'admin' || body.role === 'user') user.role = body.role;
    if (body.is_active !== undefined) user.isActive = Boolean(body.is_active);
    return sleep(rawUser(user) as T);
  }
  if (pathname.startsWith('/admin/users/') && method === 'DELETE') return sleep({ message: 'deleted' } as T);

  throw new Error(`Demo API is not implemented: ${method} ${pathname}`);
}

function toNode(body: JsonRecord, fallbackId: string): GraphNode {
  return {
    id: String(body.id || fallbackId),
    name: String(body.name || '未命名节点'),
    label: String(body.label || body.type || '节点'),
    type: String(body.type || body.label || '节点'),
    summary: typeof body.summary === 'string' ? body.summary : '',
    source: typeof body.source === 'string' ? body.source : '演示数据',
    sourceCases: Array.isArray(body.source_cases) ? body.source_cases.map(String) : ['中风'],
    sourceBatches: Array.isArray(body.source_batches) ? body.source_batches.map(String) : ['演示数据'],
  };
}

function toEdge(body: JsonRecord, fallbackId: string): GraphEdge {
  return {
    id: String(body.id || fallbackId),
    source: String(body.source || ''),
    target: String(body.target || ''),
    type: String(body.type || '关联'),
    label: String(body.label || body.type || '关联'),
    sourceCases: Array.isArray(body.source_cases) ? body.source_cases.map(String) : ['中风'],
    sourceBatches: Array.isArray(body.source_batches) ? body.source_batches.map(String) : ['演示数据'],
  };
}

export async function demoDownload(path: string, fallbackFilename: string): Promise<Headers> {
  const filename = fallbackFilename.endsWith('.zip') ? fallbackFilename.replace(/\.zip$/, '.txt') : fallbackFilename;
  const content = `吴门医案知识图谱演示导出\n\n路径：${path}\n说明：演示模式不连接后端数据库，导出文件由浏览器本地生成。\n`;
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
  const headers = new Headers();
  headers.set('X-Report-Total-Ms', '320');
  headers.set('X-Report-Figure-Ms', '120');
  headers.set('X-Report-Word-Ms', '200');
  return headers;
}
