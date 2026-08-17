from urllib.parse import quote

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.security import get_current_user
from app.schemas.graph import (
    EntityDetailResponse,
    GraphSnapshot,
    PathQueryRequest,
    PathQueryResponse,
    PhysicianPathCompareResponse,
    PhysicianNodeCompareResponse,
    PhysicianSubgraphCompareResponse,
    SearchResponse,
)
from app.services.graph_service import GraphService


class SchemaResponse(BaseModel):
    entity_types: list[str]
    relation_types: list[str]


router = APIRouter(prefix="/graph", tags=["graph"], dependencies=[Depends(get_current_user)])


def get_graph_service(settings: Settings = Depends(get_settings)) -> GraphService:
    return GraphService(settings)


@router.get("/schema", response_model=SchemaResponse)
def get_schema(service: GraphService = Depends(get_graph_service)) -> SchemaResponse:
    entity_types, relation_types = service.get_schema()
    return SchemaResponse(entity_types=entity_types, relation_types=relation_types)


@router.get("/search", response_model=SearchResponse)
def search_graph(
    q: str = Query(default=""),
    entity_type: str = Query(default=""),
    source: str = Query(default=""),
    source_case: str = Query(default=""),
    type: str = Query(default=""),
    service: GraphService = Depends(get_graph_service),
) -> SearchResponse:
    final_type = entity_type or type
    return service.search(q, final_type, source, source_case)


@router.get("/snapshot", response_model=GraphSnapshot)
def get_snapshot(
    source: str = Query(default=""),
    source_case: str = Query(default=""),
    entity_type: str = Query(default=""),
    name: str = Query(default=""),
    service: GraphService = Depends(get_graph_service),
) -> GraphSnapshot:
    return service.snapshot(source, source_case, entity_type, name)


@router.get("/entity/{entity_id}", response_model=EntityDetailResponse)
def get_entity(entity_id: str, service: GraphService = Depends(get_graph_service)) -> EntityDetailResponse:
    return service.entity_detail(entity_id)


@router.get("/entity/{entity_id}/neighbors", response_model=EntityDetailResponse)
def get_neighbors(entity_id: str, service: GraphService = Depends(get_graph_service)) -> EntityDetailResponse:
    return service.entity_detail(entity_id)


@router.post("/path/query", response_model=PathQueryResponse)
def query_path(payload: PathQueryRequest, service: GraphService = Depends(get_graph_service)) -> PathQueryResponse:
    return service.path_query(
        payload.source_name, payload.target_name, payload.max_depth, payload.source_case,
        payload.max_paths, payload.min_length, payload.node_types,
    )


@router.get("/compare/nodes", response_model=PhysicianNodeCompareResponse)
def compare_nodes(
    disease: str = Query(default="中风"),
    service: GraphService = Depends(get_graph_service),
) -> PhysicianNodeCompareResponse:
    return service.compare_physician_nodes(disease)


@router.get("/compare/paths", response_model=PhysicianPathCompareResponse)
def compare_paths(
    disease: str = Query(default="中风"),
    service: GraphService = Depends(get_graph_service),
) -> PhysicianPathCompareResponse:
    return service.compare_physician_paths(disease)


@router.get("/compare/subgraphs", response_model=PhysicianSubgraphCompareResponse)
def compare_subgraphs(
    disease: str = Query(default="中风"),
    service: GraphService = Depends(get_graph_service),
) -> PhysicianSubgraphCompareResponse:
    return service.compare_physician_subgraphs(disease)


@router.get("/compare/subgraphs/export")
def export_subgraphs(
    disease: str = Query(default="中风"),
    service: GraphService = Depends(get_graph_service),
) -> Response:
    filename, payload = service.export_physician_subgraphs(disease)
    quoted = quote(filename)
    return Response(
        content=payload,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={quoted}; filename*=UTF-8''{quoted}",
        },
    )


@router.get("/compare/report/export")
def export_report(
    disease: str = Query(default="中风"),
    service: GraphService = Depends(get_graph_service),
) -> Response:
    filename, payload, timings = service.export_physician_compare_report(disease)
    quoted = quote(filename)
    return Response(
        content=payload,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={quoted}; filename*=UTF-8''{quoted}",
            "X-Report-Total-Ms": str(timings.get("total_ms", 0)),
            "X-Report-Figure-Ms": str(timings.get("figure_ms", 0)),
            "X-Report-Word-Ms": str(timings.get("word_ms", 0)),
        },
    )
