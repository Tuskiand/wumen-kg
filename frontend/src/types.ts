export interface GraphNode {
  id: string;
  name: string;
  label: string;
  type: string;
  summary?: string;
  source?: string;
  sourceCases: string[];
  sourceBatches: string[];
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  sourceCases: string[];
  sourceBatches: string[];
}

export interface GraphSnapshot {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface RankedGraphNode {
  id: string;
  name: string;
  type: string;
  score: number;
  count: number;
}

export interface NodeRankingGroup {
  patterns: RankedGraphNode[];
  causes: RankedGraphNode[];
  mechanisms: RankedGraphNode[];
}

export interface CompareNode {
  id: string;
  name: string;
  label: string;
  type: string;
}

export interface CompareNodeGroup {
  patterns: CompareNode[];
  causes: CompareNode[];
  mechanisms: CompareNode[];
}

export interface PhysicianSimilarityPair {
  leftDoctor: string;
  rightDoctor: string;
  jaccard: number;
  overlap: number;
  cosine: number;
}

export interface PhysicianSimilarityGroup {
  patterns: PhysicianSimilarityPair[];
  causes: PhysicianSimilarityPair[];
  mechanisms: PhysicianSimilarityPair[];
  overall: PhysicianSimilarityPair[];
}

export interface SharedCompareNode {
  node: CompareNode;
  doctors: string[];
}

export interface SharedCompareNodeGroup {
  patterns: SharedCompareNode[];
  causes: SharedCompareNode[];
  mechanisms: SharedCompareNode[];
}

export interface PhysicianEmbeddingScatterPoint {
  id: string;
  label: string;
  group: string;
  x: number;
  y: number;
}

export interface PhysicianCategoryScores {
  patterns: number;
  causes: number;
  mechanisms: number;
  overall: number;
}

export interface PhysicianDoctorScore {
  doctor: GraphNode;
  scores: PhysicianCategoryScores;
}

export interface PhysicianFeatureEmbedding {
  doctor: GraphNode;
  patterns: number[];
  causes: number[];
  mechanisms: number[];
  overall: number[];
}

export interface PhysicianFeatureSimilarityCandidate {
  category: string;
  leftDoctor: string;
  leftFeatureName: string;
  rightDoctor: string;
  rightFeatureName: string;
  similarity: number;
}

export interface PhysicianNodeProfile {
  doctor: GraphNode;
  all: CompareNodeGroup;
  shared: CompareNodeGroup;
  unique: CompareNodeGroup;
}

export interface PhysicianNodeRwrResult {
  doctor: GraphNode;
  restartProbability: number;
  rankings: NodeRankingGroup;
}

export interface PhysicianNodeCompareSummary {
  primarySimilarityMetric: string;
  primaryEmbeddingMetric: string;
  sharedNodeCount: number;
  pairwiseComparisonCount: number;
  primaryRestartProbability: number;
  message: string;
}

export interface PhysicianNodeCompareResponse {
  disease: string;
  doctorCount: number;
  doctors: GraphNode[];
  similarity: PhysicianSimilarityGroup;
  fastrpSimilarity: PhysicianSimilarityGroup;
  sharedNodes: SharedCompareNodeGroup;
  doctorProfiles: PhysicianNodeProfile[];
  rwr: PhysicianNodeRwrResult[];
  doctorFeatureEmbeddings: PhysicianFeatureEmbedding[];
  similarityOverview: PhysicianDoctorScore[];
  featureSimilarityCandidates: PhysicianFeatureSimilarityCandidate[];
  embeddingPoints: PhysicianEmbeddingScatterPoint[];
  summary: PhysicianNodeCompareSummary;
}

export interface PhysicianPathChain {
  pathType: string;
  pathCategory: string;
  signature: string;
  text: string;
  cause?: CompareNode;
  mechanism?: CompareNode;
  pattern?: CompareNode;
}

export interface SharedPhysicianPath {
  path: PhysicianPathChain;
  doctors: string[];
}

export interface PhysicianPathCompleteness {
  completeCount: number;
  partialCount: number;
  singleCount: number;
  totalCount: number;
  completeRatio: number;
  pathCoverage: number;
}

export interface PhysicianPathProfile {
  doctor: GraphNode;
  completePaths: PhysicianPathChain[];
  partialPaths: PhysicianPathChain[];
  singlePaths: PhysicianPathChain[];
  uniquePaths: PhysicianPathChain[];
  completeness: PhysicianPathCompleteness;
}

export interface PhysicianPathSimilarityPair {
  leftDoctor: string;
  rightDoctor: string;
  sharedPathCount: number;
  unionPathCount: number;
  pathJaccard: number;
  metapath2vecCosine: number;
}

export interface PhysicianPathEmbeddingProfile {
  doctor: GraphNode;
  vector: number[];
}

export interface PhysicianPathCompareSummary {
  sharedPathCount: number;
  pairwiseComparisonCount: number;
  primarySimilarityMetric: string;
  embeddingMetric: string;
  message: string;
}

export interface PhysicianPathCompareResponse {
  disease: string;
  doctorCount: number;
  doctors: GraphNode[];
  sharedPaths: SharedPhysicianPath[];
  doctorProfiles: PhysicianPathProfile[];
  similarityPairs: PhysicianPathSimilarityPair[];
  embeddings: PhysicianPathEmbeddingProfile[];
  embeddingPoints: PhysicianEmbeddingScatterPoint[];
  summary: PhysicianPathCompareSummary;
}

export interface PhysicianSubgraphEdge {
  signature: string;
  relationType: string;
  text: string;
  sourceName: string;
  sourceType: string;
  targetName: string;
  targetType: string;
}

export interface SharedPhysicianSubgraphEdge {
  edge: PhysicianSubgraphEdge;
  doctors: string[];
}

export interface PhysicianSubgraphRelationStat {
  relationType: string;
  count: number;
  ratio: number;
}

export interface PhysicianSubgraphAuditNode {
  id: string;
  name: string;
  label: string;
  type: string;
  inclusionReason: string;
}

export interface PhysicianSubgraphAuditEdge {
  relationType: string;
  text: string;
  sourceName: string;
  sourceType: string;
  targetName: string;
  targetType: string;
}

export interface PhysicianSubgraphProfile {
  doctor: GraphNode;
  nodeCount: number;
  edgeCount: number;
  nodes: CompareNodeGroup;
  uniqueNodes: CompareNodeGroup;
  edges: PhysicianSubgraphEdge[];
  uniqueEdges: PhysicianSubgraphEdge[];
  relationDistribution: PhysicianSubgraphRelationStat[];
  auditNodes: PhysicianSubgraphAuditNode[];
  auditEdges: PhysicianSubgraphAuditEdge[];
}

export interface PhysicianSubgraphSimilarityPair {
  leftDoctor: string;
  rightDoctor: string;
  nodeJaccard: number;
  edgeJaccard: number;
  subgraphJaccard: number;
  graph2vecCosine: number;
}

export interface PhysicianSubgraphEmbeddingProfile {
  doctor: GraphNode;
  graph2vecVector: number[];
}

export interface PhysicianSubgraphCompareSummary {
  primarySimilarityMetric: string;
  sharedNodeCount: number;
  sharedEdgeCount: number;
  pairwiseComparisonCount: number;
  vectorSimilarityMetrics: string[];
  message: string;
}

export interface PhysicianSubgraphCompareResponse {
  disease: string;
  doctorCount: number;
  doctors: GraphNode[];
  similarityPairs: PhysicianSubgraphSimilarityPair[];
  sharedNodes: SharedCompareNodeGroup;
  sharedEdges: SharedPhysicianSubgraphEdge[];
  doctorProfiles: PhysicianSubgraphProfile[];
  embeddings: PhysicianSubgraphEmbeddingProfile[];
  embeddingPoints: PhysicianEmbeddingScatterPoint[];
  summary: PhysicianSubgraphCompareSummary;
}

export interface SearchResult {
  total: number;
  items: GraphNode[];
}

export interface ImportTask {
  id: string;
  name: string;
  createdAt: string;
  status: 'pending' | 'validating' | 'completed' | 'failed';
  summary: string;
  source?: string;
  sourceCase?: string;
  schema?: string;
  createdNodes?: number;
  mergedNodes?: number;
  createdRelations?: number;
  deduplicatedRelations?: number;
}

export interface AuditRecord {
  id: string;
  actor: string;
  action: string;
  target: string;
  createdAt: string;
  result: string;
}

export interface VersionRecord {
  id: string;
  name: string;
  createdAt: string;
  status: 'draft' | 'published' | 'archived';
}

export interface User {
  id: number;
  username: string;
  role: 'admin' | 'user';
  isActive: boolean;
}

export interface LoginResult {
  token: string;
  id: number;
  username: string;
  expiresIn: number;
  role: 'admin' | 'user';
}

export type GraphNodeInput = GraphNode;
export type GraphEdgeInput = GraphEdge;

export interface UserInput {
  username: string;
  password: string;
  role: 'admin' | 'user';
  isActive: boolean;
}

export interface UserUpdateInput {
  username?: string;
  password?: string;
  role?: 'admin' | 'user';
  isActive?: boolean;
}
