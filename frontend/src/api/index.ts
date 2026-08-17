import type {
  AuditRecord,
  CompareNode,
  CompareNodeGroup,
  GraphEdge,
  GraphEdgeInput,
  GraphNode,
  GraphNodeInput,
  GraphSnapshot,
  ImportTask,
  LoginResult,
  NodeRankingGroup,
  PhysicianNodeCompareResponse,
  PhysicianPathCompareResponse,
  PhysicianSubgraphCompareResponse,
  SearchResult,
  User,
  UserInput,
  UserUpdateInput,
  VersionRecord,
} from '@/types';
import { demoDownload, demoRequest } from './mock';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '/api/v1';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';
const TOKEN_KEY = 'auth-token';

interface LoginResponse {
  token: string;
  id: number;
  username: string;
  expires_in: number;
  role: 'admin' | 'user';
}

interface UserResponse {
  id: number;
  username: string;
  role: 'admin' | 'user';
  is_active: boolean;
}

interface GraphNodeResponse {
  id: string;
  name: string;
  label: string;
  type: string;
  summary?: string;
  source?: string;
  source_cases?: string[];
  source_batches?: string[];
}

interface GraphEdgeResponse {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  source_cases?: string[];
  source_batches?: string[];
}

interface SearchResponseRaw {
  total: number;
  items: GraphNodeResponse[];
}

interface GraphSnapshotResponse {
  nodes: GraphNodeResponse[];
  edges: GraphEdgeResponse[];
}

interface EntityDetailResponse {
  entity: GraphNodeResponse;
  relations: GraphEdgeResponse[];
  neighbors: GraphNodeResponse[];
}

interface PathQueryResponse {
  paths: unknown[];
  total_paths: number;
  source_name: string;
  target_name: string;
  description: string;
}

interface RankedGraphNodeResponse {
  id: string;
  name: string;
  type: string;
  score: number;
  count: number;
}

interface NodeRankingGroupResponse {
  patterns: RankedGraphNodeResponse[];
  causes: RankedGraphNodeResponse[];
  mechanisms: RankedGraphNodeResponse[];
}

interface CompareNodeResponse {
  id: string;
  name: string;
  label: string;
  type: string;
}

interface CompareNodeGroupResponse {
  patterns: CompareNodeResponse[];
  causes: CompareNodeResponse[];
  mechanisms: CompareNodeResponse[];
}

interface PhysicianSimilarityPairResponse {
  left_doctor: string;
  right_doctor: string;
  jaccard: number;
  overlap: number;
  cosine: number;
}

interface PhysicianSimilarityGroupResponse {
  patterns: PhysicianSimilarityPairResponse[];
  causes: PhysicianSimilarityPairResponse[];
  mechanisms: PhysicianSimilarityPairResponse[];
  overall: PhysicianSimilarityPairResponse[];
}

interface SharedCompareNodeResponse {
  node: CompareNodeResponse;
  doctors: string[];
}

interface SharedCompareNodeGroupResponse {
  patterns: SharedCompareNodeResponse[];
  causes: SharedCompareNodeResponse[];
  mechanisms: SharedCompareNodeResponse[];
}

interface PhysicianNodeProfileResponse {
  doctor: GraphNodeResponse;
  all: CompareNodeGroupResponse;
  shared: CompareNodeGroupResponse;
  unique: CompareNodeGroupResponse;
}

interface PhysicianNodeRwrResultResponse {
  doctor: GraphNodeResponse;
  restart_probability: number;
  rankings: NodeRankingGroupResponse;
}

interface PhysicianEmbeddingScatterPointResponse {
  id: string;
  label: string;
  group: string;
  x: number;
  y: number;
}

interface PhysicianCategoryScoresResponse {
  patterns: number;
  causes: number;
  mechanisms: number;
  overall: number;
}

interface PhysicianDoctorScoreResponse {
  doctor: GraphNodeResponse;
  scores: PhysicianCategoryScoresResponse;
}

interface PhysicianFeatureEmbeddingResponse {
  doctor: GraphNodeResponse;
  patterns: number[];
  causes: number[];
  mechanisms: number[];
  overall: number[];
}

interface PhysicianFeatureSimilarityCandidateResponse {
  category: string;
  left_doctor: string;
  left_feature_name: string;
  right_doctor: string;
  right_feature_name: string;
  similarity: number;
}

interface PhysicianNodeCompareSummaryResponse {
  primary_similarity_metric: string;
  primary_embedding_metric: string;
  shared_node_count: number;
  pairwise_comparison_count: number;
  primary_restart_probability: number;
  message: string;
}

interface PhysicianNodeCompareResponseRaw {
  disease: string;
  doctor_count: number;
  doctors: GraphNodeResponse[];
  similarity: PhysicianSimilarityGroupResponse;
  fastrp_similarity: PhysicianSimilarityGroupResponse;
  shared_nodes: SharedCompareNodeGroupResponse;
  doctor_profiles: PhysicianNodeProfileResponse[];
  rwr: PhysicianNodeRwrResultResponse[];
  doctor_feature_embeddings: PhysicianFeatureEmbeddingResponse[];
  similarity_overview: PhysicianDoctorScoreResponse[];
  feature_similarity_candidates: PhysicianFeatureSimilarityCandidateResponse[];
  embedding_points: PhysicianEmbeddingScatterPointResponse[];
  summary: PhysicianNodeCompareSummaryResponse;
}

interface PhysicianPathChainResponse {
  path_type: string;
  path_category: string;
  signature: string;
  text: string;
  cause?: CompareNodeResponse;
  mechanism?: CompareNodeResponse;
  pattern?: CompareNodeResponse;
}

interface SharedPhysicianPathResponse {
  path: PhysicianPathChainResponse;
  doctors: string[];
}

interface PhysicianPathCompletenessResponse {
  complete_count: number;
  partial_count: number;
  single_count: number;
  total_count: number;
  complete_ratio: number;
  path_coverage: number;
}

interface PhysicianPathProfileResponse {
  doctor: GraphNodeResponse;
  complete_paths: PhysicianPathChainResponse[];
  partial_paths: PhysicianPathChainResponse[];
  single_paths: PhysicianPathChainResponse[];
  unique_paths: PhysicianPathChainResponse[];
  completeness: PhysicianPathCompletenessResponse;
}

interface PhysicianPathSimilarityPairResponse {
  left_doctor: string;
  right_doctor: string;
  shared_path_count: number;
  union_path_count: number;
  path_jaccard: number;
  metapath2vec_cosine: number;
}

interface PhysicianPathEmbeddingProfileResponse {
  doctor: GraphNodeResponse;
  vector: number[];
}

interface PhysicianPathCompareSummaryResponse {
  shared_path_count: number;
  pairwise_comparison_count: number;
  primary_similarity_metric: string;
  embedding_metric: string;
  message: string;
}

interface PhysicianPathCompareResponseRaw {
  disease: string;
  doctor_count: number;
  doctors: GraphNodeResponse[];
  shared_paths: SharedPhysicianPathResponse[];
  doctor_profiles: PhysicianPathProfileResponse[];
  similarity_pairs: PhysicianPathSimilarityPairResponse[];
  embeddings: PhysicianPathEmbeddingProfileResponse[];
  embedding_points: PhysicianEmbeddingScatterPointResponse[];
  summary: PhysicianPathCompareSummaryResponse;
}

interface PhysicianSubgraphEdgeResponse {
  signature: string;
  relation_type: string;
  text: string;
  source_name: string;
  source_type: string;
  target_name: string;
  target_type: string;
}

interface SharedPhysicianSubgraphEdgeResponse {
  edge: PhysicianSubgraphEdgeResponse;
  doctors: string[];
}

interface PhysicianSubgraphRelationStatResponse {
  relation_type: string;
  count: number;
  ratio: number;
}

interface PhysicianSubgraphAuditNodeResponse {
  id: string;
  name: string;
  label: string;
  type: string;
  inclusion_reason: string;
}

interface PhysicianSubgraphAuditEdgeResponse {
  relation_type: string;
  text: string;
  source_name: string;
  source_type: string;
  target_name: string;
  target_type: string;
}

interface PhysicianSubgraphProfileResponse {
  doctor: GraphNodeResponse;
  node_count: number;
  edge_count: number;
  nodes: CompareNodeGroupResponse;
  unique_nodes: CompareNodeGroupResponse;
  edges: PhysicianSubgraphEdgeResponse[];
  unique_edges: PhysicianSubgraphEdgeResponse[];
  relation_distribution: PhysicianSubgraphRelationStatResponse[];
  audit_nodes: PhysicianSubgraphAuditNodeResponse[];
  audit_edges: PhysicianSubgraphAuditEdgeResponse[];
}

interface PhysicianSubgraphSimilarityPairResponse {
  left_doctor: string;
  right_doctor: string;
  node_jaccard: number;
  edge_jaccard: number;
  subgraph_jaccard: number;
  graph2vec_cosine: number;
}

interface PhysicianSubgraphEmbeddingProfileResponse {
  doctor: GraphNodeResponse;
  graph2vec_vector: number[];
}

interface PhysicianSubgraphCompareSummaryResponse {
  primary_similarity_metric: string;
  shared_node_count: number;
  shared_edge_count: number;
  pairwise_comparison_count: number;
  vector_similarity_metrics: string[];
  message: string;
}

interface PhysicianSubgraphCompareResponseRaw {
  disease: string;
  doctor_count: number;
  doctors: GraphNodeResponse[];
  similarity_pairs: PhysicianSubgraphSimilarityPairResponse[];
  shared_nodes: SharedCompareNodeGroupResponse;
  shared_edges: SharedPhysicianSubgraphEdgeResponse[];
  doctor_profiles: PhysicianSubgraphProfileResponse[];
  embeddings: PhysicianSubgraphEmbeddingProfileResponse[];
  embedding_points: PhysicianEmbeddingScatterPointResponse[];
  summary: PhysicianSubgraphCompareSummaryResponse;
}

interface DashboardStatsResponse {
  node_count: number;
  edge_count: number;
  import_success_rate: number;
  last_publish_at: string;
}

interface ImportTaskResponse {
  id: string;
  name: string;
  created_at: string;
  status: 'pending' | 'validating' | 'completed' | 'failed';
  summary: string;
  source?: string;
  source_case?: string;
  schema?: string;
  created_nodes?: number;
  merged_nodes?: number;
  created_relations?: number;
  deduplicated_relations?: number;
}

interface VersionRecordResponse {
  id: string;
  name: string;
  created_at: string;
  status: 'draft' | 'published' | 'archived';
}

interface AuditRecordResponse {
  id: string;
  actor: string;
  action: string;
  target: string;
  created_at: string;
  result: string;
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY) ?? '';
}

function mapUser(item: UserResponse): User {
  return {
    id: item.id,
    username: item.username,
    role: item.role,
    isActive: item.is_active,
  };
}

function mapNode(item: GraphNodeResponse): GraphNode {
  return {
    id: item.id,
    name: item.name,
    label: item.label,
    type: item.type,
    summary: item.summary,
    source: item.source,
    sourceCases: item.source_cases ?? [],
    sourceBatches: item.source_batches ?? [],
  };
}

function mapEdge(item: GraphEdgeResponse): GraphEdge {
  return {
    id: item.id,
    source: item.source,
    target: item.target,
    type: item.type,
    label: item.label,
    sourceCases: item.source_cases ?? [],
    sourceBatches: item.source_batches ?? [],
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (DEMO_MODE) {
    return demoRequest<T>(path, init);
  }

  const headers = new Headers(init?.headers);
  const token = getToken();
  if (!(init?.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  const raw = await response.text();
  let payload: unknown = null;
  if (raw) {
    try {
      payload = JSON.parse(raw);
    } catch {
      payload = raw;
    }
  }

  if (!response.ok) {
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload
      ? String((payload as { detail: unknown }).detail)
      : typeof payload === 'string' && payload
        ? payload
        : `Request failed: ${response.status}`;
    throw new Error(detail);
  }

  return payload as T;
}

async function download(path: string, fallbackFilename: string): Promise<Headers> {
  if (DEMO_MODE) {
    return demoDownload(path, fallbackFilename);
  }

  const headers = new Headers();
  const token = getToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    const raw = await response.text();
    let detail = raw || '下载失败';
    try {
      const payload = JSON.parse(raw) as { detail?: unknown };
      detail = payload.detail ? String(payload.detail) : detail;
    } catch {
      // keep raw text
    }
    throw new Error(detail);
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const utf8Name = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
  const plainName = disposition.match(/filename="?([^";]+)"?/i)?.[1];
  const filename = decodeURIComponent(utf8Name ?? plainName ?? fallbackFilename);
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
  return response.headers;
}

function mapImportTask(item: ImportTaskResponse): ImportTask {
  return {
    id: item.id,
    name: item.name,
    createdAt: item.created_at,
    status: item.status,
    summary: item.summary,
    source: item.source,
    sourceCase: item.source_case,
    schema: item.schema,
    createdNodes: item.created_nodes,
    mergedNodes: item.merged_nodes,
    createdRelations: item.created_relations,
    deduplicatedRelations: item.deduplicated_relations,
  };
}

function mapRankingGroup(item: NodeRankingGroupResponse): NodeRankingGroup {
  return {
    patterns: item.patterns,
    causes: item.causes,
    mechanisms: item.mechanisms,
  };
}

function mapCompareNode(item: CompareNodeResponse): CompareNode {
  return {
    id: item.id,
    name: item.name,
    label: item.label,
    type: item.type,
  };
}

function mapCompareNodeGroup(item: CompareNodeGroupResponse): CompareNodeGroup {
  return {
    patterns: item.patterns.map(mapCompareNode),
    causes: item.causes.map(mapCompareNode),
    mechanisms: item.mechanisms.map(mapCompareNode),
  };
}

function mapPhysicianPathChain(item: PhysicianPathChainResponse) {
  return {
    pathType: item.path_type,
    pathCategory: item.path_category,
    signature: item.signature,
    text: item.text,
    cause: item.cause ? mapCompareNode(item.cause) : undefined,
    mechanism: item.mechanism ? mapCompareNode(item.mechanism) : undefined,
    pattern: item.pattern ? mapCompareNode(item.pattern) : undefined,
  };
}

function mapSubgraphEdge(item: PhysicianSubgraphEdgeResponse) {
  return {
    signature: item.signature,
    relationType: item.relation_type,
    text: item.text,
    sourceName: item.source_name,
    sourceType: item.source_type,
    targetName: item.target_name,
    targetType: item.target_type,
  };
}

function mapSimilarityGroup(group: PhysicianSimilarityGroupResponse) {
  return {
    patterns: group.patterns.map((item) => ({
      leftDoctor: item.left_doctor,
      rightDoctor: item.right_doctor,
      jaccard: item.jaccard,
      overlap: item.overlap,
      cosine: item.cosine,
    })),
    causes: group.causes.map((item) => ({
      leftDoctor: item.left_doctor,
      rightDoctor: item.right_doctor,
      jaccard: item.jaccard,
      overlap: item.overlap,
      cosine: item.cosine,
    })),
    mechanisms: group.mechanisms.map((item) => ({
      leftDoctor: item.left_doctor,
      rightDoctor: item.right_doctor,
      jaccard: item.jaccard,
      overlap: item.overlap,
      cosine: item.cosine,
    })),
    overall: group.overall.map((item) => ({
      leftDoctor: item.left_doctor,
      rightDoctor: item.right_doctor,
      jaccard: item.jaccard,
      overlap: item.overlap,
      cosine: item.cosine,
    })),
  };
}

function mapEmbeddingPoint(item: PhysicianEmbeddingScatterPointResponse) {
  return {
    id: item.id,
    label: item.label,
    group: item.group,
    x: item.x,
    y: item.y,
  };
}

export async function login(username: string, password: string): Promise<LoginResult> {
  const result = await request<LoginResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
  return { token: result.token, id: result.id, username: result.username, expiresIn: result.expires_in, role: result.role };
}

export async function register(username: string, password: string): Promise<User> {
  const result = await request<UserResponse>('/auth/register', { method: 'POST', body: JSON.stringify({ username, password }) });
  return mapUser(result);
}

export async function getCurrentUser(): Promise<User> {
  const result = await request<UserResponse>('/auth/me');
  return mapUser(result);
}

export async function logout() {
  await request<{ message: string }>('/auth/logout', { method: 'POST' });
}

export async function getDashboardStats() {
  const result = await request<DashboardStatsResponse>('/admin/dashboard');
  return { nodeCount: result.node_count, edgeCount: result.edge_count, importSuccessRate: result.import_success_rate, lastPublishAt: result.last_publish_at };
}

export async function searchGraph(query = '', entityType = '', source = '', sourceCase = ''): Promise<SearchResult> {
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (entityType) params.set('entity_type', entityType);
  if (source) params.set('source', source);
  if (sourceCase) params.set('source_case', sourceCase);
  const result = await request<SearchResponseRaw>(`/graph/search?${params.toString()}`);
  return { total: result.total, items: result.items.map(mapNode) };
}

export async function getGraphSnapshot(source = '', sourceCase = '', entityType = '', name = ''): Promise<GraphSnapshot> {
  const params = new URLSearchParams();
  if (source) params.set('source', source);
  if (sourceCase) params.set('source_case', sourceCase);
  if (entityType) params.set('entity_type', entityType);
  if (name) params.set('name', name);
  const query = params.toString();
  const result = await request<GraphSnapshotResponse>(`/graph/snapshot${query ? `?${query}` : ''}`);
  return {
    nodes: result.nodes.map(mapNode),
    edges: result.edges.map(mapEdge),
  };
}

export async function getGraphSchema(): Promise<{ entityTypes: string[]; relationTypes: string[] }> {
  const result = await request<{ entity_types: string[]; relation_types: string[] }>('/graph/schema');
  return { entityTypes: result.entity_types, relationTypes: result.relation_types };
}

export async function getAiConfig(): Promise<{ baseUrl: string; model: string; hasKey: boolean }> {
  const result = await request<{ base_url: string; model: string; has_key: boolean }>('/ai/config');
  return { baseUrl: result.base_url, model: result.model, hasKey: result.has_key };
}

export async function updateAiConfig(config: { api_key: string; base_url: string; model: string }): Promise<{ baseUrl: string; model: string; hasKey: boolean }> {
  const result = await request<{ base_url: string; model: string; has_key: boolean }>('/ai/config', {
    method: 'PUT',
    body: JSON.stringify(config),
  });
  return { baseUrl: result.base_url, model: result.model, hasKey: result.has_key };
}

export async function testAiConnection(config: { api_key: string; base_url: string; model: string }): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>('/ai/config/test', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

export async function getEntityDetail(id: string) {
  const result = await request<EntityDetailResponse>(`/graph/entity/${id}`);
  return {
    entity: mapNode(result.entity),
    relations: result.relations.map(mapEdge),
    neighbors: result.neighbors.map(mapNode),
  };
}

export async function queryPath(
  sourceName: string, targetName: string, sourceCase = '',
  maxDepth = 4, maxPaths = 10, minLength = 1, nodeTypes: string[] = [],
) {
  const result = await request<PathQueryResponse>('/graph/path/query', {
    method: 'POST',
    body: JSON.stringify({
      source_name: sourceName, target_name: targetName, max_depth: maxDepth,
      source_case: sourceCase, max_paths: maxPaths, min_length: minLength, node_types: nodeTypes,
    }),
  });
  return {
    paths: result.paths.map((item: any) => ({
      nodes: item.nodes.map(mapNode),
      edges: item.edges.map(mapEdge),
      length: item.length,
      typeSequence: item.type_sequence,
      nameSequence: item.name_sequence,
    })),
    totalPaths: result.total_paths,
    sourceName: result.source_name,
    targetName: result.target_name,
    description: result.description,
  };
}

export async function comparePhysicianNodes(disease = '中风'): Promise<PhysicianNodeCompareResponse> {
  const params = new URLSearchParams();
  if (disease) params.set('disease', disease);
  const result = await request<PhysicianNodeCompareResponseRaw>(`/graph/compare/nodes?${params.toString()}`);
  return {
    disease: result.disease,
    doctorCount: result.doctor_count,
    doctors: result.doctors.map(mapNode),
    similarity: mapSimilarityGroup(result.similarity),
    fastrpSimilarity: mapSimilarityGroup(result.fastrp_similarity),
    sharedNodes: {
      patterns: result.shared_nodes.patterns.map((item) => ({ node: mapCompareNode(item.node), doctors: item.doctors })),
      causes: result.shared_nodes.causes.map((item) => ({ node: mapCompareNode(item.node), doctors: item.doctors })),
      mechanisms: result.shared_nodes.mechanisms.map((item) => ({ node: mapCompareNode(item.node), doctors: item.doctors })),
    },
    doctorProfiles: result.doctor_profiles.map((item) => ({
      doctor: mapNode(item.doctor),
      all: mapCompareNodeGroup(item.all),
      shared: mapCompareNodeGroup(item.shared),
      unique: mapCompareNodeGroup(item.unique),
    })),
    rwr: result.rwr.map((item) => ({
      doctor: mapNode(item.doctor),
      restartProbability: item.restart_probability,
      rankings: mapRankingGroup(item.rankings),
    })),
    doctorFeatureEmbeddings: result.doctor_feature_embeddings.map((item) => ({
      doctor: mapNode(item.doctor),
      patterns: item.patterns,
      causes: item.causes,
      mechanisms: item.mechanisms,
      overall: item.overall,
    })),
    similarityOverview: result.similarity_overview.map((item) => ({
      doctor: mapNode(item.doctor),
      scores: {
        patterns: item.scores.patterns,
        causes: item.scores.causes,
        mechanisms: item.scores.mechanisms,
        overall: item.scores.overall,
      },
    })),
    featureSimilarityCandidates: result.feature_similarity_candidates.map((item) => ({
      category: item.category,
      leftDoctor: item.left_doctor,
      leftFeatureName: item.left_feature_name,
      rightDoctor: item.right_doctor,
      rightFeatureName: item.right_feature_name,
      similarity: item.similarity,
    })),
    embeddingPoints: result.embedding_points.map(mapEmbeddingPoint),
    summary: {
      primarySimilarityMetric: result.summary.primary_similarity_metric,
      primaryEmbeddingMetric: result.summary.primary_embedding_metric,
      sharedNodeCount: result.summary.shared_node_count,
      pairwiseComparisonCount: result.summary.pairwise_comparison_count,
      primaryRestartProbability: result.summary.primary_restart_probability,
      message: result.summary.message,
    },
  };
}

export async function comparePhysicianPaths(disease = '中风'): Promise<PhysicianPathCompareResponse> {
  const params = new URLSearchParams();
  if (disease) params.set('disease', disease);
  const result = await request<PhysicianPathCompareResponseRaw>(`/graph/compare/paths?${params.toString()}`);
  return {
    disease: result.disease,
    doctorCount: result.doctor_count,
    doctors: result.doctors.map(mapNode),
    sharedPaths: result.shared_paths.map((item) => ({
      path: mapPhysicianPathChain(item.path),
      doctors: item.doctors,
    })),
    doctorProfiles: result.doctor_profiles.map((item) => ({
      doctor: mapNode(item.doctor),
      completePaths: item.complete_paths.map(mapPhysicianPathChain),
      partialPaths: item.partial_paths.map(mapPhysicianPathChain),
      singlePaths: item.single_paths.map(mapPhysicianPathChain),
      uniquePaths: item.unique_paths.map(mapPhysicianPathChain),
      completeness: {
        completeCount: item.completeness.complete_count,
        partialCount: item.completeness.partial_count,
        singleCount: item.completeness.single_count,
        totalCount: item.completeness.total_count,
        completeRatio: item.completeness.complete_ratio,
        pathCoverage: item.completeness.path_coverage,
      },
    })),
    similarityPairs: result.similarity_pairs.map((item) => ({
      leftDoctor: item.left_doctor,
      rightDoctor: item.right_doctor,
      sharedPathCount: item.shared_path_count,
      unionPathCount: item.union_path_count,
      pathJaccard: item.path_jaccard,
      metapath2vecCosine: item.metapath2vec_cosine,
    })),
    embeddings: result.embeddings.map((item) => ({
      doctor: mapNode(item.doctor),
      vector: item.vector,
    })),
    embeddingPoints: result.embedding_points.map(mapEmbeddingPoint),
    summary: {
      sharedPathCount: result.summary.shared_path_count,
      pairwiseComparisonCount: result.summary.pairwise_comparison_count,
      primarySimilarityMetric: result.summary.primary_similarity_metric,
      embeddingMetric: result.summary.embedding_metric,
      message: result.summary.message,
    },
  };
}

export async function comparePhysicianSubgraphs(disease = '中风'): Promise<PhysicianSubgraphCompareResponse> {
  const params = new URLSearchParams();
  if (disease) params.set('disease', disease);
  const result = await request<PhysicianSubgraphCompareResponseRaw>(`/graph/compare/subgraphs?${params.toString()}`);
  return {
    disease: result.disease,
    doctorCount: result.doctor_count,
    doctors: result.doctors.map(mapNode),
    similarityPairs: result.similarity_pairs.map((item) => ({
      leftDoctor: item.left_doctor,
      rightDoctor: item.right_doctor,
      nodeJaccard: item.node_jaccard,
      edgeJaccard: item.edge_jaccard,
      subgraphJaccard: item.subgraph_jaccard,
      graph2vecCosine: item.graph2vec_cosine,
    })),
    sharedNodes: {
      patterns: result.shared_nodes.patterns.map((item) => ({ node: mapCompareNode(item.node), doctors: item.doctors })),
      causes: result.shared_nodes.causes.map((item) => ({ node: mapCompareNode(item.node), doctors: item.doctors })),
      mechanisms: result.shared_nodes.mechanisms.map((item) => ({ node: mapCompareNode(item.node), doctors: item.doctors })),
    },
    sharedEdges: result.shared_edges.map((item) => ({
      edge: mapSubgraphEdge(item.edge),
      doctors: item.doctors,
    })),
    doctorProfiles: result.doctor_profiles.map((item) => ({
      doctor: mapNode(item.doctor),
      nodeCount: item.node_count,
      edgeCount: item.edge_count,
      nodes: mapCompareNodeGroup(item.nodes),
      uniqueNodes: mapCompareNodeGroup(item.unique_nodes),
      edges: item.edges.map(mapSubgraphEdge),
      uniqueEdges: item.unique_edges.map(mapSubgraphEdge),
      relationDistribution: item.relation_distribution.map((entry) => ({
        relationType: entry.relation_type,
        count: entry.count,
        ratio: entry.ratio,
      })),
      auditNodes: item.audit_nodes.map((entry) => ({
        id: entry.id,
        name: entry.name,
        label: entry.label,
        type: entry.type,
        inclusionReason: entry.inclusion_reason,
      })),
      auditEdges: item.audit_edges.map((entry) => ({
        relationType: entry.relation_type,
        text: entry.text,
        sourceName: entry.source_name,
        sourceType: entry.source_type,
        targetName: entry.target_name,
        targetType: entry.target_type,
      })),
    })),
    embeddings: result.embeddings.map((item) => ({
      doctor: mapNode(item.doctor),
      graph2vecVector: item.graph2vec_vector,
    })),
    embeddingPoints: result.embedding_points.map(mapEmbeddingPoint),
    summary: {
      primarySimilarityMetric: result.summary.primary_similarity_metric,
      sharedNodeCount: result.summary.shared_node_count,
      sharedEdgeCount: result.summary.shared_edge_count,
      pairwiseComparisonCount: result.summary.pairwise_comparison_count,
      vectorSimilarityMetrics: result.summary.vector_similarity_metrics,
      message: result.summary.message,
    },
  };
}

export async function analyzePhysicianCompare(disease: string, doctors: string[]): Promise<{ analysis: string; model: string }> {
  const result = await request<{ analysis: string; model: string }>('/ai/analyze-physician-compare', {
    method: 'POST',
    body: JSON.stringify({ disease, doctors, node_summary: '', path_summary: '', subgraph_summary: '' }),
  });
  return result;
}

export async function downloadPhysicianSubgraphExport(disease = '中风'): Promise<void> {
  const params = new URLSearchParams();
  if (disease) params.set('disease', disease);
  await download(`/graph/compare/subgraphs/export?${params.toString()}`, `physician_subgraphs_${disease || 'export'}.zip`);
}

export async function downloadPhysicianCompareReport(disease = '中风') {
  const params = new URLSearchParams();
  if (disease) params.set('disease', disease);
  const headers = await download(`/graph/compare/report/export?${params.toString()}`, `physician_compare_report_${disease || 'export'}.zip`);
  return {
    totalMs: Number(headers.get('X-Report-Total-Ms') ?? '0'),
    figureMs: Number(headers.get('X-Report-Figure-Ms') ?? '0'),
    wordMs: Number(headers.get('X-Report-Word-Ms') ?? '0'),
  };
}

export async function getEntities() {
  const result = await request<GraphNodeResponse[]>('/admin/entities');
  return result.map(mapNode);
}

export async function createEntity(payload: GraphNodeInput) {
  const result = await request<GraphNodeResponse>('/admin/entities', {
    method: 'POST',
    body: JSON.stringify({
      id: payload.id,
      name: payload.name,
      label: payload.label,
      type: payload.type,
      summary: payload.summary,
      source: payload.source,
      source_cases: payload.sourceCases,
      source_batches: payload.sourceBatches,
    }),
  });
  return mapNode(result);
}

export async function updateEntity(entityId: string, payload: GraphNodeInput) {
  const result = await request<GraphNodeResponse>(`/admin/entities/${entityId}`, {
    method: 'PUT',
    body: JSON.stringify({
      id: payload.id,
      name: payload.name,
      label: payload.label,
      type: payload.type,
      summary: payload.summary,
      source: payload.source,
      source_cases: payload.sourceCases,
      source_batches: payload.sourceBatches,
    }),
  });
  return mapNode(result);
}

export async function deleteEntity(entityId: string) {
  return request<{ message: string }>(`/admin/entities/${entityId}`, { method: 'DELETE' });
}

export async function bulkDeleteEntities(entityIds: string[]) {
  return request<{ message: string }>('/admin/entities/batch-delete', {
    method: 'POST',
    body: JSON.stringify({ ids: entityIds }),
  });
}

export async function getRelations() {
  const result = await request<GraphEdgeResponse[]>('/admin/relations');
  return result.map(mapEdge);
}

export async function createRelation(payload: GraphEdgeInput) {
  const result = await request<GraphEdgeResponse>('/admin/relations', {
    method: 'POST',
    body: JSON.stringify({
      id: payload.id,
      source: payload.source,
      target: payload.target,
      type: payload.type,
      label: payload.label,
      source_cases: payload.sourceCases,
      source_batches: payload.sourceBatches,
    }),
  });
  return mapEdge(result);
}

export async function updateRelation(relationId: string, payload: GraphEdgeInput) {
  const result = await request<GraphEdgeResponse>(`/admin/relations/${relationId}`, {
    method: 'PUT',
    body: JSON.stringify({
      id: payload.id,
      source: payload.source,
      target: payload.target,
      type: payload.type,
      label: payload.label,
      source_cases: payload.sourceCases,
      source_batches: payload.sourceBatches,
    }),
  });
  return mapEdge(result);
}

export async function deleteRelation(relationId: string) {
  return request<{ message: string }>(`/admin/relations/${relationId}`, { method: 'DELETE' });
}

export async function bulkDeleteRelations(relationIds: string[]) {
  return request<{ message: string }>('/admin/relations/batch-delete', {
    method: 'POST',
    body: JSON.stringify({ ids: relationIds }),
  });
}

export async function getImportTasks() {
  const result = await request<ImportTaskResponse[]>('/admin/imports');
  return result.map(mapImportTask);
}

export async function validateImport(file: File, source: string, sourceCase: string, schema?: string) {
  const formData = new FormData();
  formData.append('files', file);
  formData.append('source', source);
  formData.append('source_case', sourceCase);
  if (schema?.trim()) {
    formData.append('schema', schema.trim());
  }
  const result = await request<ImportTaskResponse>('/admin/imports/validate', {
    method: 'POST',
    body: formData,
  });
  return mapImportTask(result);
}

export async function executeImport(taskId: string) {
  const result = await request<ImportTaskResponse>(`/admin/imports/${taskId}/execute`, { method: 'POST' });
  return mapImportTask(result);
}

export async function getVersionRecords(): Promise<VersionRecord[]> {
  const result = await request<VersionRecordResponse[]>('/admin/versions');
  return result.map((item) => ({ id: item.id, name: item.name, createdAt: item.created_at, status: item.status }));
}

export async function getAuditRecords(): Promise<AuditRecord[]> {
  const result = await request<AuditRecordResponse[]>('/admin/audits');
  return result.map((item) => ({ id: item.id, actor: item.actor, action: item.action, target: item.target, createdAt: item.created_at, result: item.result }));
}

export async function getUsers(): Promise<User[]> {
  const result = await request<UserResponse[]>('/admin/users');
  return result.map(mapUser);
}

export async function createUser(payload: UserInput): Promise<User> {
  const result = await request<UserResponse>('/admin/users', {
    method: 'POST',
    body: JSON.stringify({
      username: payload.username,
      password: payload.password,
      role: payload.role,
      is_active: payload.isActive,
    }),
  });
  return mapUser(result);
}

export async function updateUser(userId: number, payload: UserUpdateInput): Promise<User> {
  const body: Record<string, unknown> = {};
  if (payload.username !== undefined) body.username = payload.username;
  if (payload.password !== undefined) body.password = payload.password;
  if (payload.role !== undefined) body.role = payload.role;
  if (payload.isActive !== undefined) body.is_active = payload.isActive;
  const result = await request<UserResponse>(`/admin/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  return mapUser(result);
}

export async function deleteUser(userId: number) {
  return request<{ message: string }>(`/admin/users/${userId}`, { method: 'DELETE' });
}


