from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    name: str
    label: str
    type: str
    summary: str | None = None
    source: str | None = None
    source_cases: list[str] = Field(default_factory=list)
    source_batches: list[str] = Field(default_factory=list)


class GraphNodeUpsert(BaseModel):
    id: str
    name: str
    label: str
    type: str
    summary: str | None = None
    source: str | None = None
    source_cases: list[str] = Field(default_factory=list)
    source_batches: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    label: str | None = None
    source_cases: list[str] = Field(default_factory=list)
    source_batches: list[str] = Field(default_factory=list)


class GraphEdgeUpsert(BaseModel):
    id: str
    source: str
    target: str
    type: str
    label: str | None = None
    source_cases: list[str] = Field(default_factory=list)
    source_batches: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    total: int
    items: list[GraphNode]


class GraphSnapshot(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class EntityDetailResponse(BaseModel):
    entity: GraphNode
    relations: list[GraphEdge]
    neighbors: list[GraphNode]


class PathQueryRequest(BaseModel):
    source_name: str
    target_name: str
    max_depth: int = Field(default=4, ge=1, le=8)
    source_case: str = ''


class PathQueryResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    description: str


class RankedGraphNode(BaseModel):
    id: str
    name: str
    type: str
    score: float
    count: int = 0


class NodeRankingGroup(BaseModel):
    patterns: list[RankedGraphNode] = Field(default_factory=list)
    causes: list[RankedGraphNode] = Field(default_factory=list)
    mechanisms: list[RankedGraphNode] = Field(default_factory=list)


class CompareNode(BaseModel):
    id: str
    name: str
    label: str
    type: str


class CompareNodeGroup(BaseModel):
    patterns: list[CompareNode] = Field(default_factory=list)
    causes: list[CompareNode] = Field(default_factory=list)
    mechanisms: list[CompareNode] = Field(default_factory=list)


class PhysicianSimilarityPair(BaseModel):
    left_doctor: str
    right_doctor: str
    jaccard: float
    overlap: float
    cosine: float


class PhysicianSimilarityGroup(BaseModel):
    patterns: list[PhysicianSimilarityPair] = Field(default_factory=list)
    causes: list[PhysicianSimilarityPair] = Field(default_factory=list)
    mechanisms: list[PhysicianSimilarityPair] = Field(default_factory=list)
    overall: list[PhysicianSimilarityPair] = Field(default_factory=list)


class SharedCompareNode(BaseModel):
    node: CompareNode
    doctors: list[str] = Field(default_factory=list)


class SharedCompareNodeGroup(BaseModel):
    patterns: list[SharedCompareNode] = Field(default_factory=list)
    causes: list[SharedCompareNode] = Field(default_factory=list)
    mechanisms: list[SharedCompareNode] = Field(default_factory=list)


class PhysicianEmbeddingScatterPoint(BaseModel):
    id: str
    label: str
    group: str
    x: float
    y: float


class PhysicianCategoryScores(BaseModel):
    patterns: float = 0.0
    causes: float = 0.0
    mechanisms: float = 0.0
    overall: float = 0.0


class PhysicianDoctorScore(BaseModel):
    doctor: GraphNode
    scores: PhysicianCategoryScores


class PhysicianFeatureEmbedding(BaseModel):
    doctor: GraphNode
    patterns: list[float] = Field(default_factory=list)
    causes: list[float] = Field(default_factory=list)
    mechanisms: list[float] = Field(default_factory=list)
    overall: list[float] = Field(default_factory=list)


class PhysicianFeatureSimilarityCandidate(BaseModel):
    category: str
    left_doctor: str
    left_feature_name: str
    right_doctor: str
    right_feature_name: str
    similarity: float


class PhysicianNodeProfile(BaseModel):
    doctor: GraphNode
    all: CompareNodeGroup
    shared: CompareNodeGroup
    unique: CompareNodeGroup


class PhysicianNodeRwrResult(BaseModel):
    doctor: GraphNode
    restart_probability: float
    rankings: NodeRankingGroup


class PhysicianNodeCompareSummary(BaseModel):
    primary_similarity_metric: str
    primary_embedding_metric: str
    shared_node_count: int
    pairwise_comparison_count: int
    primary_restart_probability: float
    message: str


class PhysicianNodeCompareResponse(BaseModel):
    disease: str
    doctor_count: int
    doctors: list[GraphNode] = Field(default_factory=list)
    similarity: PhysicianSimilarityGroup
    fastrp_similarity: PhysicianSimilarityGroup
    shared_nodes: SharedCompareNodeGroup
    doctor_profiles: list[PhysicianNodeProfile] = Field(default_factory=list)
    rwr: list[PhysicianNodeRwrResult] = Field(default_factory=list)
    doctor_feature_embeddings: list[PhysicianFeatureEmbedding] = Field(default_factory=list)
    similarity_overview: list[PhysicianDoctorScore] = Field(default_factory=list)
    feature_similarity_candidates: list[PhysicianFeatureSimilarityCandidate] = Field(default_factory=list)
    embedding_points: list[PhysicianEmbeddingScatterPoint] = Field(default_factory=list)
    summary: PhysicianNodeCompareSummary


class PhysicianPathChain(BaseModel):
    path_type: str
    path_category: str
    signature: str
    text: str
    cause: CompareNode | None = None
    mechanism: CompareNode | None = None
    pattern: CompareNode | None = None


class SharedPhysicianPath(BaseModel):
    path: PhysicianPathChain
    doctors: list[str] = Field(default_factory=list)


class PhysicianPathCompleteness(BaseModel):
    complete_count: int
    partial_count: int
    single_count: int
    total_count: int
    complete_ratio: float
    path_coverage: float = 0.0


class PhysicianPathProfile(BaseModel):
    doctor: GraphNode
    complete_paths: list[PhysicianPathChain] = Field(default_factory=list)
    partial_paths: list[PhysicianPathChain] = Field(default_factory=list)
    single_paths: list[PhysicianPathChain] = Field(default_factory=list)
    unique_paths: list[PhysicianPathChain] = Field(default_factory=list)
    completeness: PhysicianPathCompleteness


class PhysicianPathSimilarityPair(BaseModel):
    left_doctor: str
    right_doctor: str
    shared_path_count: int
    union_path_count: int
    path_jaccard: float
    metapath2vec_cosine: float


class PhysicianPathEmbeddingProfile(BaseModel):
    doctor: GraphNode
    vector: list[float] = Field(default_factory=list)


class PhysicianPathCompareSummary(BaseModel):
    shared_path_count: int
    pairwise_comparison_count: int
    primary_similarity_metric: str
    embedding_metric: str
    message: str


class PhysicianPathCompareResponse(BaseModel):
    disease: str
    doctor_count: int
    doctors: list[GraphNode] = Field(default_factory=list)
    shared_paths: list[SharedPhysicianPath] = Field(default_factory=list)
    doctor_profiles: list[PhysicianPathProfile] = Field(default_factory=list)
    similarity_pairs: list[PhysicianPathSimilarityPair] = Field(default_factory=list)
    embeddings: list[PhysicianPathEmbeddingProfile] = Field(default_factory=list)
    embedding_points: list[PhysicianEmbeddingScatterPoint] = Field(default_factory=list)
    summary: PhysicianPathCompareSummary


class PhysicianSubgraphEdge(BaseModel):
    signature: str
    relation_type: str
    text: str
    source_name: str
    source_type: str
    target_name: str
    target_type: str


class SharedPhysicianSubgraphEdge(BaseModel):
    edge: PhysicianSubgraphEdge
    doctors: list[str] = Field(default_factory=list)


class PhysicianSubgraphRelationStat(BaseModel):
    relation_type: str
    count: int
    ratio: float


class PhysicianSubgraphAuditNode(BaseModel):
    id: str
    name: str
    label: str
    type: str
    inclusion_reason: str


class PhysicianSubgraphAuditEdge(BaseModel):
    relation_type: str
    text: str
    source_name: str
    source_type: str
    target_name: str
    target_type: str


class PhysicianSubgraphProfile(BaseModel):
    doctor: GraphNode
    node_count: int
    edge_count: int
    nodes: CompareNodeGroup
    unique_nodes: CompareNodeGroup
    edges: list[PhysicianSubgraphEdge] = Field(default_factory=list)
    unique_edges: list[PhysicianSubgraphEdge] = Field(default_factory=list)
    relation_distribution: list[PhysicianSubgraphRelationStat] = Field(default_factory=list)
    audit_nodes: list[PhysicianSubgraphAuditNode] = Field(default_factory=list)
    audit_edges: list[PhysicianSubgraphAuditEdge] = Field(default_factory=list)


class PhysicianSubgraphSimilarityPair(BaseModel):
    left_doctor: str
    right_doctor: str
    node_jaccard: float
    edge_jaccard: float
    subgraph_jaccard: float
    graph2vec_cosine: float


class PhysicianSubgraphEmbeddingProfile(BaseModel):
    doctor: GraphNode
    graph2vec_vector: list[float] = Field(default_factory=list)


class PhysicianSubgraphCompareSummary(BaseModel):
    primary_similarity_metric: str
    shared_node_count: int
    shared_edge_count: int
    pairwise_comparison_count: int
    vector_similarity_metrics: list[str] = Field(default_factory=list)
    message: str


class PhysicianSubgraphCompareResponse(BaseModel):
    disease: str
    doctor_count: int
    doctors: list[GraphNode] = Field(default_factory=list)
    similarity_pairs: list[PhysicianSubgraphSimilarityPair] = Field(default_factory=list)
    shared_nodes: SharedCompareNodeGroup
    shared_edges: list[SharedPhysicianSubgraphEdge] = Field(default_factory=list)
    doctor_profiles: list[PhysicianSubgraphProfile] = Field(default_factory=list)
    embeddings: list[PhysicianSubgraphEmbeddingProfile] = Field(default_factory=list)
    embedding_points: list[PhysicianEmbeddingScatterPoint] = Field(default_factory=list)
    summary: PhysicianSubgraphCompareSummary
