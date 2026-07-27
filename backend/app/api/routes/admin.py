from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.security import require_admin
from app.schemas.admin import ActionResponse, AuditRecord, DashboardStats, ImportTask, VersionRecord
from app.schemas.graph import GraphEdge, GraphEdgeUpsert, GraphNode, GraphNodeUpsert
from app.services.admin_service import AdminService
from app.services.graph_service import GraphService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


class BatchDeleteRequest(BaseModel):
    ids: list[str]


def get_admin_service(settings: Settings = Depends(get_settings)) -> AdminService:
    return AdminService(settings)


def get_graph_service(settings: Settings = Depends(get_settings)) -> GraphService:
    return GraphService(settings)


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    service: AdminService = Depends(get_admin_service),
    graph_service: GraphService = Depends(get_graph_service),
) -> DashboardStats:
    return service.dashboard(graph_service.graph_totals())


@router.get("/entities", response_model=list[GraphNode])
def get_entities(service: GraphService = Depends(get_graph_service)) -> list[GraphNode]:
    return list(service.entities())


@router.post("/entities", response_model=GraphNode)
def create_entity(payload: GraphNodeUpsert, service: GraphService = Depends(get_graph_service)) -> GraphNode:
    return service.create_entity(payload)


@router.post("/entities/batch-delete", response_model=ActionResponse)
def batch_delete_entities(payload: BatchDeleteRequest, service: GraphService = Depends(get_graph_service)) -> ActionResponse:
    count = service.delete_entities(payload.ids)
    return ActionResponse(message=f"Deleted {count} entities")


@router.put("/entities/{entity_id}", response_model=GraphNode)
def update_entity(entity_id: str, payload: GraphNodeUpsert, service: GraphService = Depends(get_graph_service)) -> GraphNode:
    return service.update_entity(entity_id, payload)


@router.delete("/entities/{entity_id}", response_model=ActionResponse)
def delete_entity(entity_id: str, service: GraphService = Depends(get_graph_service)) -> ActionResponse:
    service.delete_entity(entity_id)
    return ActionResponse(message="Entity deleted")


@router.get("/relations", response_model=list[GraphEdge])
def get_relations(service: GraphService = Depends(get_graph_service)) -> list[GraphEdge]:
    return list(service.relations())


@router.post("/relations", response_model=GraphEdge)
def create_relation(payload: GraphEdgeUpsert, service: GraphService = Depends(get_graph_service)) -> GraphEdge:
    return service.create_relation(payload)


@router.post("/relations/batch-delete", response_model=ActionResponse)
def batch_delete_relations(payload: BatchDeleteRequest, service: GraphService = Depends(get_graph_service)) -> ActionResponse:
    count = service.delete_relations(payload.ids)
    return ActionResponse(message=f"Deleted {count} relations")


@router.put("/relations/{relation_id}", response_model=GraphEdge)
def update_relation(relation_id: str, payload: GraphEdgeUpsert, service: GraphService = Depends(get_graph_service)) -> GraphEdge:
    return service.update_relation(relation_id, payload)


@router.delete("/relations/{relation_id}", response_model=ActionResponse)
def delete_relation(relation_id: str, service: GraphService = Depends(get_graph_service)) -> ActionResponse:
    service.delete_relation(relation_id)
    return ActionResponse(message="Relation deleted")


@router.get("/imports", response_model=list[ImportTask])
def get_imports(service: AdminService = Depends(get_admin_service)) -> list[ImportTask]:
    return service.import_tasks()


@router.post("/imports/validate", response_model=ImportTask)
async def validate_import(
    files: list[UploadFile] = File(default=[]),
    source: str = Form(default=""),
    source_case: str = Form(default=""),
    schema: str = Form(default=""),
    service: AdminService = Depends(get_admin_service),
) -> ImportTask:
    return await service.validate_import(files, source, source_case, schema or None)


@router.post("/imports/{task_id}/execute", response_model=ImportTask)
def execute_import(
    task_id: str,
    admin_service: AdminService = Depends(get_admin_service),
    graph_service: GraphService = Depends(get_graph_service),
) -> ImportTask:
    return admin_service.execute_import(task_id, graph_service.import_standardized_csv)


@router.get("/versions", response_model=list[VersionRecord])
def get_versions(service: AdminService = Depends(get_admin_service)) -> list[VersionRecord]:
    return service.versions()


@router.get("/audits", response_model=list[AuditRecord])
def get_audits(service: AdminService = Depends(get_admin_service)) -> list[AuditRecord]:
    return service.audits()
