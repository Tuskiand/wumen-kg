from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import get_current_user
from app.db.mysql import get_db_session
from app.schemas.ai import AiAnalyzeRequest, AiAnalyzeResponse, AiConfigResponse, AiConfigTestRequest, AiConfigTestResponse, AiConfigUpdate
from app.services.ai_service import AiService
from app.services.graph_service import GraphService

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(get_current_user)])


def get_graph_service(settings: Settings = Depends(get_settings)) -> GraphService:
    return GraphService(settings)


def get_ai_service(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session),
) -> AiService:
    return AiService(settings, session)


@router.post("/analyze-physician-compare", response_model=AiAnalyzeResponse)
def analyze_physician_compare(
    payload: AiAnalyzeRequest,
    ai_service: AiService = Depends(get_ai_service),
    graph_service: GraphService = Depends(get_graph_service),
) -> AiAnalyzeResponse:
    try:
        node_result = graph_service.compare_physician_nodes(payload.disease)
        path_result = graph_service.compare_physician_paths(payload.disease)
        subgraph_result = graph_service.compare_physician_subgraphs(payload.disease)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"比较分析执行失败：{exc}") from exc

    node_summary = _build_node_summary(node_result)
    path_summary = _build_path_summary(path_result)
    subgraph_summary = _build_subgraph_summary(subgraph_result)

    analysis, model = ai_service.analyze_physician_compare(
        payload.disease,
        [d.name for d in node_result.doctors],
        node_summary,
        path_summary,
        subgraph_summary,
    )
    return AiAnalyzeResponse(analysis=analysis, model=model)


@router.get("/config", response_model=AiConfigResponse)
def get_ai_config(ai_service: AiService = Depends(get_ai_service)) -> AiConfigResponse:
    return AiConfigResponse(**ai_service.get_config_response())


@router.put("/config", response_model=AiConfigResponse)
def update_ai_config(
    payload: AiConfigUpdate,
    ai_service: AiService = Depends(get_ai_service),
) -> AiConfigResponse:
    ai_service.update_config(payload.api_key, payload.base_url, payload.model)
    return AiConfigResponse(**ai_service.get_config_response())


@router.post("/config/test", response_model=AiConfigTestResponse)
def test_ai_config(
    payload: AiConfigTestRequest,
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session),
) -> AiConfigTestResponse:
    ai_service = AiService(settings, session)
    success, message = ai_service.test_connection(payload.api_key, payload.base_url, payload.model)
    return AiConfigTestResponse(success=success, message=message)


def _build_node_summary(result) -> str:
    lines = [f"参与医家：{result.doctor_count} 位"]
    if result.summary:
        lines.append(f"主指标：{result.summary.primary_similarity_metric}")
        lines.append(f"嵌入：{result.summary.primary_embedding_metric}")
    for pair in result.similarity.overall[:3]:
        lines.append(
            f"{pair.left_doctor} vs {pair.right_doctor}："
            f"Jaccard={pair.jaccard:.3f}，"
        )
    for pair in result.fastrp_similarity.overall[:3]:
        lines.append(
            f"{pair.left_doctor} vs {pair.right_doctor}："
            f"FastRP余弦={pair.cosine:.3f}"
        )
    if result.shared_nodes:
        shared = result.shared_nodes
        lines.append(
            f"共享节点：证型 {len(shared.patterns)} 个，"
            f"病因 {len(shared.causes)} 个，"
            f"病机 {len(shared.mechanisms)} 个"
        )
    return "\n".join(lines)


def _build_path_summary(result) -> str:
    lines = [f"共同辨证链：{result.summary.shared_path_count} 条"]
    lines.append(f"主指标：{result.summary.primary_similarity_metric}")
    for pair in result.similarity_pairs[:3]:
        lines.append(
            f"{pair.left_doctor} vs {pair.right_doctor}："
            f"Path Jaccard={pair.path_jaccard:.3f}，"
            f"Metapath2Vec={pair.metapath2vec_cosine:.3f}"
        )
    for profile in result.doctor_profiles[:3]:
        lines.append(
            f"{profile.doctor.name}：完整链 {profile.completeness.complete_count} 条，"
            f"完整率 {profile.completeness.complete_ratio:.1%}"
        )
    return "\n".join(lines)


def _build_subgraph_summary(result) -> str:
    lines = [f"子图比较指标：{result.summary.primary_similarity_metric}"]
    if result.summary.vector_similarity_metrics:
        lines.append(f"向量指标：{', '.join(result.summary.vector_similarity_metrics)}")
    for pair in result.similarity_pairs[:3]:
        lines.append(
            f"{pair.left_doctor} vs {pair.right_doctor}："
            f"子图Jaccard={pair.subgraph_jaccard:.3f}，"
            f"Graph2Vec={pair.graph2vec_cosine:.3f}"
        )
    for profile in result.doctor_profiles[:3]:
        lines.append(
            f"{profile.doctor.name}：节点 {profile.node_count} 个，"
            f"关系 {profile.edge_count} 条"
        )
    return "\n".join(lines)