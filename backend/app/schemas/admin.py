from pydantic import BaseModel


class ImportTask(BaseModel):
    id: str
    name: str
    created_at: str
    status: str
    summary: str
    source: str | None = None
    source_case: str | None = None
    schema: str | None = None
    created_nodes: int | None = None
    merged_nodes: int | None = None
    created_relations: int | None = None
    deduplicated_relations: int | None = None


class VersionRecord(BaseModel):
    id: str
    name: str
    created_at: str
    status: str


class AuditRecord(BaseModel):
    id: str
    actor: str
    action: str
    target: str
    created_at: str
    result: str


class DashboardStats(BaseModel):
    node_count: int
    edge_count: int
    import_success_rate: float
    last_publish_at: str


class ActionResponse(BaseModel):
    message: str
