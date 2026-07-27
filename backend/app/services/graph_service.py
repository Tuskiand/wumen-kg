from __future__ import annotations

from collections.abc import Iterable

from fastapi import HTTPException, status
from neo4j.exceptions import Neo4jError

from app.core.config import Settings
from app.core.kg_rules import is_allowed_entity_type, is_allowed_relation_type, normalize_entity_type, relation_direction_matches
from app.db.neo4j import get_neo4j_manager
from app.repositories.neo4j_graph import Neo4jGraphRepository
from app.schemas.graph import (
    EntityDetailResponse,
    GraphEdge,
    GraphEdgeUpsert,
    GraphNode,
    GraphNodeUpsert,
    GraphSnapshot,
    PathQueryResponse,
    PhysicianPathCompareResponse,
    PhysicianNodeCompareResponse,
    PhysicianSubgraphCompareResponse,
    SearchResponse,
)
from app.services.physician_compare_service import PhysicianCompareService
from app.services.demo_data import EDGES, NODES, append_audit


class GraphService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.repository = None
        if not settings.demo_mode:
            manager = get_neo4j_manager()
            self.repository = Neo4jGraphRepository(manager.driver, settings.neo4j_database)

    def _use_repository(self) -> bool:
        if self.repository is None:
            return False
        try:
            return self.repository.is_available()
        except Exception:
            return False

    def search(self, query: str = '', entity_type: str = '', source: str = '', source_case: str = '') -> SearchResponse:
        if self._use_repository():
            items = self.repository.search(query, entity_type, source, source_case)
            return SearchResponse(total=len(items), items=items)

        filtered = [
            node
            for node in NODES
            if self._node_matches(node, entity_type, source, source_case)
            and (not query or query in node.name or (node.summary and query in node.summary))
        ]
        return SearchResponse(total=len(filtered), items=filtered)

    def graph_totals(self) -> tuple[int, int]:
        if self.settings.demo_mode:
            return len(NODES), len(EDGES)
        if self.repository is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 仓库未初始化，无法统计图谱总量。')
        if not self._use_repository():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 当前不可用，无法统计图谱总量。')
        return self.repository.graph_totals()

    def snapshot(self, source: str = '', source_case: str = '', entity_type: str = '') -> GraphSnapshot:
        if self._use_repository():
            return self.repository.snapshot(source, source_case, entity_type)

        nodes = [node for node in NODES if self._node_matches(node, entity_type, source, source_case)]
        node_ids = {node.id for node in nodes}
        edges = [edge for edge in EDGES if edge.source in node_ids and edge.target in node_ids and self._edge_matches(edge, source, source_case)]
        return GraphSnapshot(nodes=nodes, edges=edges)

    def entity_detail(self, entity_id: str) -> EntityDetailResponse:
        if self._use_repository():
            entity = self.repository.get_entity(entity_id)
            if entity is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Entity not found')
            relations, neighbors = self.repository.get_entity_neighbors(entity_id)
            return EntityDetailResponse(entity=entity, relations=relations, neighbors=neighbors)

        entity = next((node for node in NODES if node.id == entity_id), None)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Entity not found')
        relations = [edge for edge in EDGES if edge.source == entity.id or edge.target == entity.id]
        related_ids = {relation.source for relation in relations} | {relation.target for relation in relations}
        neighbors = [node for node in NODES if node.id in related_ids and node.id != entity.id]
        return EntityDetailResponse(entity=entity, relations=relations, neighbors=neighbors)

    def path_query(self, source_name: str, target_name: str, max_depth: int = 4, source_case: str = '') -> PathQueryResponse:
        if max_depth < 1 or max_depth > 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='路径最大深度必须在 1 到 8 之间')
        if self._use_repository():
            try:
                snapshot = self.repository.get_path(source_name, target_name, max_depth, source_case)
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
            return PathQueryResponse(
                nodes=snapshot.nodes,
                edges=snapshot.edges,
                description=(
                    f'找到 {len(snapshot.edges)} 条路径关系'
                    if snapshot.edges
                    else '未找到符合条件的路径'
                ),
            )

        snapshot = self._demo_shortest_path(source_name, target_name, max_depth, source_case)
        return PathQueryResponse(
            nodes=snapshot.nodes,
            edges=snapshot.edges,
            description=(
                f'找到 {len(snapshot.edges)} 条路径关系'
                if snapshot.edges
                else '未找到符合条件的路径'
            ),
        )

    def compare_physician_nodes(self, disease: str = '中风') -> PhysicianNodeCompareResponse:
        if self.settings.demo_mode:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='节点比较只支持真实 Neo4j + GDS，当前处于演示模式。')
        if self.repository is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 仓库未初始化，无法执行节点比较。')
        try:
            if not self.repository.is_available():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 当前不可用，无法执行节点比较。')
            contexts = self.repository.get_physician_node_compare_contexts(disease)
            similarity = self.repository.get_physician_node_similarity(disease)
            fastrp_payload = self.repository.get_physician_fastrp_payload(disease)
            return PhysicianCompareService().compare_nodes(disease, contexts, similarity, fastrp_payload)
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Neo4jError as exc:
            detail = getattr(exc, 'message', '') or str(exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'节点比较执行失败：{detail}') from exc

    def compare_physician_paths(self, disease: str = '中风') -> PhysicianPathCompareResponse:
        if self.settings.demo_mode:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='辨证路径比较只支持真实 Neo4j，当前处于演示模式。')
        if self.repository is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 仓库未初始化，无法执行辨证路径比较。')
        try:
            if not self.repository.is_available():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 当前不可用，无法执行辨证路径比较。')
            contexts = self.repository.get_physician_node_compare_contexts(disease)
            return PhysicianCompareService().compare_paths(disease, contexts)
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Neo4jError as exc:
            detail = getattr(exc, 'message', '') or str(exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'辨证路径比较执行失败：{detail}') from exc

    def compare_physician_subgraphs(self, disease: str = '中风') -> PhysicianSubgraphCompareResponse:
        if self.settings.demo_mode:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='子图比较只支持真实 Neo4j，当前处于演示模式。')
        if self.repository is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 仓库未初始化，无法执行子图比较。')
        try:
            if not self.repository.is_available():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 当前不可用，无法执行子图比较。')
            contexts = self.repository.get_physician_node_compare_contexts(disease)
            return PhysicianCompareService().compare_subgraphs(disease, contexts)
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Neo4jError as exc:
            detail = getattr(exc, 'message', '') or str(exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'子图比较执行失败：{detail}') from exc

    def export_physician_subgraphs(self, disease: str = '中风') -> tuple[str, bytes]:
        if self.settings.demo_mode:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='子图导出只支持真实 Neo4j，当前处于演示模式。')
        if self.repository is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 仓库未初始化，无法执行子图导出。')
        try:
            if not self.repository.is_available():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 当前不可用，无法执行子图导出。')
            contexts = self.repository.get_physician_node_compare_contexts(disease)
            similarity = self.repository.get_physician_node_similarity(disease)
            fastrp_payload = self.repository.get_physician_fastrp_payload(disease)
            return PhysicianCompareService().export_subgraphs(disease, contexts, similarity, fastrp_payload)
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Neo4jError as exc:
            detail = getattr(exc, 'message', '') or str(exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'子图导出执行失败：{detail}') from exc

    def export_physician_compare_report(self, disease: str = '中风') -> tuple[str, bytes, dict[str, int]]:
        if self.settings.demo_mode:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='论文导出只支持真实 Neo4j，当前处于演示模式。')
        if self.repository is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 仓库未初始化，无法执行论文导出。')
        try:
            if not self.repository.is_available():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Neo4j 当前不可用，无法执行论文导出。')
            contexts = self.repository.get_physician_node_compare_contexts(disease)
            similarity = self.repository.get_physician_node_similarity(disease)
            fastrp_payload = self.repository.get_physician_fastrp_payload(disease)
            return PhysicianCompareService().export_paper_report(disease, contexts, similarity, fastrp_payload)
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Neo4jError as exc:
            detail = getattr(exc, 'message', '') or str(exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'论文导出执行失败：{detail}') from exc

    def entities(self) -> Iterable[GraphNode]:
        if self._use_repository():
            return self.repository.list_entities()
        return NODES

    def relations(self) -> Iterable[GraphEdge]:
        if self._use_repository():
            return self.repository.list_relations()
        return EDGES

    def create_entity(self, payload: GraphNodeUpsert) -> GraphNode:
        entity = self._normalize_node(GraphNode(**payload.model_dump()))
        self._validate_entity(entity)
        if self._use_repository():
            append_audit('保存节点', entity.id)
            return self.repository.upsert_entity(entity)
        if any(node.id == payload.id for node in NODES):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Entity id already exists')
        NODES.append(entity)
        append_audit('保存节点', entity.id)
        return entity

    def update_entity(self, entity_id: str, payload: GraphNodeUpsert) -> GraphNode:
        entity = self._normalize_node(GraphNode(**payload.model_dump()))
        if self._use_repository():
            append_audit('保存节点', entity.id)
            return self.repository.upsert_entity(entity)
        for index, node in enumerate(NODES):
            if node.id == entity_id:
                NODES[index] = entity
                append_audit('保存节点', entity.id)
                return entity
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Entity not found')

    def delete_entity(self, entity_id: str) -> None:
        if self._use_repository():
            self.repository.delete_entity(entity_id)
            append_audit('删除节点', entity_id)
            return
        index = next((idx for idx, node in enumerate(NODES) if node.id == entity_id), None)
        if index is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Entity not found')
        NODES.pop(index)
        EDGES[:] = [edge for edge in EDGES if edge.source != entity_id and edge.target != entity_id]
        append_audit('删除节点', entity_id)

    def delete_entities(self, entity_ids: list[str]) -> int:
        valid_ids = [entity_id for entity_id in entity_ids if entity_id]
        if not valid_ids:
            return 0
        if self._use_repository():
            self.repository.delete_entities(valid_ids)
            for entity_id in valid_ids:
                append_audit('批量删除节点', entity_id)
            return len(valid_ids)

        existing_ids = {node.id for node in NODES}
        target_ids = [entity_id for entity_id in valid_ids if entity_id in existing_ids]
        if not target_ids:
            return 0
        NODES[:] = [node for node in NODES if node.id not in target_ids]
        EDGES[:] = [edge for edge in EDGES if edge.source not in target_ids and edge.target not in target_ids]
        for entity_id in target_ids:
            append_audit('批量删除节点', entity_id)
        return len(target_ids)

    def create_relation(self, payload: GraphEdgeUpsert) -> GraphEdge:
        relation = self._normalize_edge(GraphEdge(**payload.model_dump()))
        self._validate_relation(relation)
        if self._use_repository():
            append_audit('保存关系', relation.id)
            return self.repository.upsert_relation(relation)
        if any(edge.id == payload.id for edge in EDGES):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Relation id already exists')
        EDGES.append(relation)
        append_audit('保存关系', relation.id)
        return relation

    def update_relation(self, relation_id: str, payload: GraphEdgeUpsert) -> GraphEdge:
        relation = self._normalize_edge(GraphEdge(**payload.model_dump()))
        if self._use_repository():
            append_audit('保存关系', relation.id)
            return self.repository.upsert_relation(relation)
        for index, edge in enumerate(EDGES):
            if edge.id == relation_id:
                EDGES[index] = relation
                append_audit('保存关系', relation.id)
                return relation
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Relation not found')

    def delete_relation(self, relation_id: str) -> None:
        if self._use_repository():
            self.repository.delete_relation(relation_id)
            append_audit('删除关系', relation_id)
            return
        index = next((idx for idx, edge in enumerate(EDGES) if edge.id == relation_id), None)
        if index is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Relation not found')
        EDGES.pop(index)
        append_audit('删除关系', relation_id)

    def delete_relations(self, relation_ids: list[str]) -> int:
        valid_ids = [relation_id for relation_id in relation_ids if relation_id]
        if not valid_ids:
            return 0
        if self._use_repository():
            self.repository.delete_relations(valid_ids)
            for relation_id in valid_ids:
                append_audit('批量删除关系', relation_id)
            return len(valid_ids)

        existing_ids = {edge.id for edge in EDGES}
        target_ids = [relation_id for relation_id in valid_ids if relation_id in existing_ids]
        if not target_ids:
            return 0
        EDGES[:] = [edge for edge in EDGES if edge.id not in target_ids]
        for relation_id in target_ids:
            append_audit('批量删除关系', relation_id)
        return len(target_ids)

    def merge_graph(self, nodes: list[GraphNode], edges: list[GraphEdge], source: str, source_case: str) -> dict[str, int]:
        if self._use_repository():
            return self.repository.merge_graph(nodes, edges, source, source_case)

        stats = {
            'created_nodes': 0,
            'merged_nodes': 0,
            'created_relations': 0,
            'deduplicated_relations': 0,
        }
        for node in nodes:
            existing = next((item for item in NODES if item.id == node.id), None)
            if existing:
                existing.name = node.name
                existing.label = node.label
                existing.type = node.type
                existing.summary = existing.summary or node.summary
                existing.source = existing.source or node.source
                existing.source_cases = self._merge_unique(existing.source_cases, node.source_cases)
                existing.source_batches = self._merge_unique(existing.source_batches, node.source_batches)
                stats['merged_nodes'] += 1
                continue

            normalized = self._normalize_node(node)
            normalized.source = normalized.source or source
            normalized.source_cases = self._merge_unique(normalized.source_cases, [source_case])
            normalized.source_batches = self._merge_unique(normalized.source_batches, [source])
            NODES.append(normalized)
            stats['created_nodes'] += 1

        for edge in edges:
            existing = next((item for item in EDGES if item.id == edge.id), None)
            if existing:
                existing.label = existing.label or edge.label
                existing.source_cases = self._merge_unique(existing.source_cases, edge.source_cases)
                existing.source_batches = self._merge_unique(existing.source_batches, edge.source_batches)
                stats['deduplicated_relations'] += 1
                continue

            EDGES.append(self._normalize_edge(edge))
            stats['created_relations'] += 1

        return stats

    def import_standardized_csv(self, load_csv_uri: str, node_count: int, edge_count: int) -> dict[str, int]:
        if not self._use_repository():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='当前环境未启用 Neo4j，无法执行 LOAD CSV 导入')
        try:
            return self.repository.import_standardized_csv(load_csv_uri, node_count, edge_count)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Neo4jError as exc:
            detail = getattr(exc, 'message', '') or str(exc)
            if 'load' in detail.lower() and 'csv' in detail.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f'Neo4j 无法读取导入文件 {load_csv_uri}。'
                        f'请确认宿主机目录 `{self.settings.neo4j_import_host_dir}` 已挂载到容器 `{self.settings.neo4j_import_container_dir}`，'
                        '并允许 LOAD CSV 读取本地文件。'
                    ),
                ) from exc
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Neo4j 导入失败：{detail}') from exc

    @staticmethod
    def _normalize_name(name: str) -> str:
        return ' '.join((name or '').strip().split())

    @staticmethod
    def _merge_unique(existing: list[str] | None, incoming: list[str]) -> list[str]:
        merged: list[str] = []
        for value in (existing or []) + incoming:
            cleaned = (value or '').strip()
            if cleaned and cleaned not in merged:
                merged.append(cleaned)
        return merged

    def _normalize_node(self, node: GraphNode) -> GraphNode:
        node.name = self._normalize_name(node.name)
        if not node.source_cases and node.source:
            node.source_cases = []
        node.source_cases = self._merge_unique(node.source_cases, [])
        node.source_batches = self._merge_unique(node.source_batches, [])
        return node

    def _normalize_edge(self, edge: GraphEdge) -> GraphEdge:
        edge.source_cases = self._merge_unique(edge.source_cases, [])
        edge.source_batches = self._merge_unique(edge.source_batches, [])
        return edge

    def _validate_entity(self, node: GraphNode) -> None:
        node.type = normalize_entity_type(node.type)
        node.label = node.label or node.type
        if not is_allowed_entity_type(node.type):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'不支持的实体类型：{node.type}')

    def _validate_relation(self, edge: GraphEdge) -> None:
        edge.type = (edge.type or '').strip()
        edge.label = edge.label or edge.type
        if not is_allowed_relation_type(edge.type):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'不支持的关系类型：{edge.type}')
        source_node = self._find_entity(edge.source)
        target_node = self._find_entity(edge.target)
        if source_node is None or target_node is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='关系起点或终点节点不存在')
        source_type = normalize_entity_type(source_node.type)
        target_type = normalize_entity_type(target_node.type)
        if not relation_direction_matches(edge.type, source_type, target_type):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'关系方向不符合规则：{source_type} -[{edge.type}]-> {target_type}')

    def _find_entity(self, entity_id: str) -> GraphNode | None:
        if self._use_repository():
            return self.repository.get_entity(entity_id)
        return next((node for node in NODES if node.id == entity_id), None)

    def _node_matches(self, node: GraphNode, entity_type: str = '', source: str = '', source_case: str = '') -> bool:
        return (
            (not entity_type or node.type == entity_type)
            and (not source or node.source == source)
            and (not source_case or source_case in node.source_cases)
        )

    def _edge_matches(self, edge: GraphEdge, source: str = '', source_case: str = '') -> bool:
        return (not source or source in edge.source_batches) and (not source_case or source_case in edge.source_cases)

    def _demo_physician_subgraphs(self, disease: str) -> list[GraphSnapshot]:
        disease_nodes = [node for node in NODES if node.type == 'B病名' and node.name == disease]
        snapshots: list[GraphSnapshot] = []
        for disease_node in disease_nodes:
            doctor_ids = {
                edge.source
                for edge in EDGES
                if edge.target == disease_node.id and self._find_demo_node(edge.source, 'A医家') is not None
            } | {
                edge.target
                for edge in EDGES
                if edge.source == disease_node.id and self._find_demo_node(edge.target, 'A医家') is not None
            }
            for doctor_id in doctor_ids:
                allowed_types = {'A医家', 'B病名', 'C证型', 'D病因', 'E病机'}
                node_ids = {doctor_id, disease_node.id}
                frontier = {doctor_id, disease_node.id}
                for _ in range(4):
                    next_frontier: set[str] = set()
                    for edge in EDGES:
                        if edge.source in frontier:
                            next_frontier.add(edge.target)
                        if edge.target in frontier:
                            next_frontier.add(edge.source)
                    typed_next = {
                        node_id
                        for node_id in next_frontier
                        if (node := self._find_demo_node(node_id)) is not None and node.type in allowed_types
                    }
                    node_ids |= typed_next
                    frontier = typed_next
                nodes = [node for node in NODES if node.id in node_ids and node.type in allowed_types]
                edge_list = [edge for edge in EDGES if edge.source in node_ids and edge.target in node_ids]
                snapshots.append(GraphSnapshot(nodes=nodes, edges=edge_list))
        return snapshots

    @staticmethod
    def _find_demo_node(node_id: str, entity_type: str = '') -> GraphNode | None:
        return next((node for node in NODES if node.id == node_id and (not entity_type or node.type == entity_type)), None)

    def _demo_shortest_path(self, source_name: str, target_name: str, max_depth: int, source_case: str = '') -> GraphSnapshot:
        source_node = self._find_unique_demo_node_by_name(source_name, source_case)
        target_node = self._find_unique_demo_node_by_name(target_name, source_case)
        depth = int(max_depth)
        queue: list[tuple[str, list[GraphEdge]]] = [(source_node.id, [])]
        visited = {source_node.id}
        for current_id, path_edges in queue:
            if len(path_edges) >= depth:
                continue
            for edge in EDGES:
                if not self._edge_matches(edge, '', source_case):
                    continue
                neighbor_id = ''
                if edge.source == current_id:
                    neighbor_id = edge.target
                elif edge.target == current_id:
                    neighbor_id = edge.source
                if not neighbor_id or neighbor_id in visited:
                    continue
                next_edges = path_edges + [edge]
                if neighbor_id == target_node.id:
                    node_ids = {source_node.id, target_node.id}
                    for item in next_edges:
                        node_ids.add(item.source)
                        node_ids.add(item.target)
                    nodes = [node for node in NODES if node.id in node_ids and (not source_case or source_case in node.source_cases)]
                    return GraphSnapshot(nodes=nodes, edges=next_edges)
                visited.add(neighbor_id)
                queue.append((neighbor_id, next_edges))
        return GraphSnapshot(nodes=[], edges=[])

    def _find_unique_demo_node_by_name(self, name: str, source_case: str = '') -> GraphNode:
        normalized = self._normalize_name(name)
        if not normalized:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='实体名称不能为空')
        matches = [
            node
            for node in NODES
            if node.name == normalized and (not source_case or source_case in node.source_cases)
        ]
        if not matches:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'未找到实体：{normalized}')
        if len(matches) > 1:
            types = '、'.join(node.type for node in matches)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'实体名称不唯一：{normalized}（{types}）')
        return matches[0]

