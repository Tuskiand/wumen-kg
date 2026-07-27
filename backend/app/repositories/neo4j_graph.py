from __future__ import annotations

from uuid import uuid4

import numpy as np
from itertools import combinations
from neo4j import Driver

from app.core.kg_rules import ENTITY_LABEL_ALIASES, ENTITY_TYPES, normalize_entity_type
from app.schemas.graph import GraphEdge, GraphNode, GraphSnapshot


class Neo4jGraphRepository:
    ENTITY_LABEL_MAPPING = ENTITY_LABEL_ALIASES
    ENTITY_TYPE_LABELS = tuple(ENTITY_TYPES)
    DEFAULT_RELATION_TYPE = "\u5173\u8054"
    IMPORT_RELATION_TYPE = "RELATED"
    COMPARE_FEATURE_TYPES = {
        "patterns": ["C证型"],
        "causes": ["D病因"],
        "mechanisms": ["E病机"],
        "overall": ["C证型", "D病因", "E病机"],
    }
    SIMILARITY_METRICS = {
        "jaccard": "JACCARD",
        "overlap": "OVERLAP",
        "cosine": "COSINE",
    }
    FASTRP_EMBEDDING_DIMENSION = 128
    FASTRP_ITERATION_WEIGHTS = [0.0, 1.0, 1.0, 0.5]
    FASTRP_NODE_SELF_INFLUENCE = 0.1
    FASTRP_RANDOM_SEED = 42

    def __init__(self, driver: Driver, database: str) -> None:
        self.driver = driver
        self.database = database

    def is_available(self) -> bool:
        self.driver.verify_connectivity()
        return True

    def search(self, query: str = "", entity_type: str = "", source: str = "", source_case: str = "") -> list[GraphNode]:
        records = self._run(
            """
            MATCH (n)
            WHERE n.id IS NOT NULL
              AND ($query = '' OR n.name CONTAINS $query OR coalesce(n.summary, '') CONTAINS $query)
              AND ($entity_type = '' OR n.type = $entity_type)
              AND ($source = '' OR n.source = $source)
              AND ($source_case = '' OR $source_case IN coalesce(n.source_cases, []))
            RETURN n
            ORDER BY n.name
            LIMIT 100
            """,
            query=query,
            entity_type=entity_type,
            source=source,
            source_case=source_case,
        )
        return [self._node_from_record(record["n"]) for record in records]

    def graph_totals(self) -> tuple[int, int]:
        node_records = self._run(
            """
            MATCH (n)
            WHERE n.id IS NOT NULL
            RETURN count(n) AS total
            """
        )
        edge_records = self._run(
            """
            MATCH ()-[r]->()
            WHERE r.id IS NOT NULL
            RETURN count(r) AS total
            """
        )
        node_count = int(node_records[0]["total"]) if node_records else 0
        edge_count = int(edge_records[0]["total"]) if edge_records else 0
        return node_count, edge_count

    def snapshot(self, source: str = "", source_case: str = "", entity_type: str = "") -> GraphSnapshot:
        node_records = self._run(
            """
            MATCH (n)
            WHERE n.id IS NOT NULL
              AND ($source = '' OR n.source = $source)
              AND ($source_case = '' OR $source_case IN coalesce(n.source_cases, []))
              AND ($entity_type = '' OR n.type = $entity_type)
            RETURN n
            LIMIT 300
            """,
            source=source,
            source_case=source_case,
            entity_type=entity_type,
        )
        node_ids = [record["n"].get("id", "") for record in node_records]
        if not node_ids:
            return GraphSnapshot(nodes=[], edges=[])

        edge_records = self._run(
            """
            MATCH (a)-[r]->(b)
            WHERE r.id IS NOT NULL
              AND a.id IN $node_ids
              AND b.id IN $node_ids
              AND ($source = '' OR $source IN coalesce(r.source_batches, []))
              AND ($source_case = '' OR $source_case IN coalesce(r.source_cases, []))
            RETURN r, a.id AS source, b.id AS target
            LIMIT 500
            """,
            node_ids=node_ids,
            source=source,
            source_case=source_case,
        )
        return GraphSnapshot(
            nodes=[self._node_from_record(record["n"]) for record in node_records],
            edges=[self._edge_from_record(record["r"], record["source"], record["target"]) for record in edge_records],
        )

    def get_entity(self, entity_id: str) -> GraphNode | None:
        records = self._run("MATCH (n {id: $entity_id}) RETURN n LIMIT 1", entity_id=entity_id)
        if not records:
            return None
        return self._node_from_record(records[0]["n"])

    def get_entity_neighbors(self, entity_id: str) -> tuple[list[GraphEdge], list[GraphNode]]:
        edge_records = self._run(
            """
            MATCH (a)-[r]-(b)
            WHERE r.id IS NOT NULL AND (a.id = $entity_id OR b.id = $entity_id)
            RETURN r, startNode(r).id AS source, endNode(r).id AS target,
                   CASE WHEN a.id = $entity_id THEN b ELSE a END AS neighbor
            LIMIT 200
            """,
            entity_id=entity_id,
        )
        edges = [self._edge_from_record(record["r"], record["source"], record["target"]) for record in edge_records]
        seen: set[str] = set()
        neighbors: list[GraphNode] = []
        for record in edge_records:
            node = self._node_from_record(record["neighbor"])
            if node.id not in seen:
                seen.add(node.id)
                neighbors.append(node)
        return edges, neighbors

    def get_path(self, source_name: str, target_name: str, max_depth: int, source_case: str = "") -> GraphSnapshot:
        source_id = self._get_unique_node_id_by_name(source_name, source_case)
        target_id = self._get_unique_node_id_by_name(target_name, source_case)
        depth = int(max_depth)
        if depth < 1 or depth > 8:
            raise ValueError("路径最大深度必须在 1 到 8 之间")
        records = self._run(
            f"""
            MATCH p = shortestPath((a {{id: $source_id}})-[*..{depth}]-(b {{id: $target_id}}))
            WHERE ($source_case = '' OR ALL(rel IN relationships(p) WHERE $source_case IN coalesce(rel.source_cases, [])))
            RETURN [n IN nodes(p) | n] AS nodes,
                   [r IN relationships(p) | {
                     id: r.id,
                     type: coalesce(r.type, type(r)),
                     label: coalesce(r.label, r.type, type(r)),
                     source: startNode(r).id,
                     target: endNode(r).id,
                     source_cases: coalesce(r.source_cases, []),
                     source_batches: coalesce(r.source_batches, [])
                   }] AS rels
            LIMIT 1
            """,
            source_id=source_id,
            target_id=target_id,
            source_case=source_case,
        )
        if not records:
            return GraphSnapshot(nodes=[], edges=[])
        record = records[0]
        return GraphSnapshot(
            nodes=[self._node_from_record(node) for node in record["nodes"]],
            edges=[
                GraphEdge(
                    id=rel.get("id", ""),
                    source=rel.get("source", ""),
                    target=rel.get("target", ""),
                    type=rel.get("type", self.DEFAULT_RELATION_TYPE),
                    label=rel.get("label"),
                    source_cases=list(rel.get("source_cases", []) or []),
                    source_batches=list(rel.get("source_batches", []) or []),
                )
                for rel in record["rels"]
            ],
        )

    def get_physician_disease_subgraphs(self, disease: str) -> list[GraphSnapshot]:
        entity_types = ["A医家", "B病名", "C证型", "D病因", "E病机"]
        records = self._run(
            """
            MATCH (doctor {type: 'A医家'})--(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH DISTINCT doctor, disease
            MATCH p = (doctor)-[*0..4]-(node)
            WHERE disease IN nodes(p)
              AND ALL(item IN nodes(p) WHERE item.type IN $entity_types)
            WITH doctor, collect(p) AS paths
            UNWIND paths AS node_path
            UNWIND nodes(node_path) AS graph_node
            WITH doctor, paths, collect(DISTINCT graph_node) AS graph_nodes
            UNWIND paths AS rel_path
            UNWIND relationships(rel_path) AS graph_rel
            WITH doctor,
                 graph_nodes,
                 collect(DISTINCT {
                   id: graph_rel.id,
                   type: coalesce(graph_rel.type, type(graph_rel)),
                   label: coalesce(graph_rel.label, graph_rel.type, type(graph_rel)),
                   source: startNode(graph_rel).id,
                   target: endNode(graph_rel).id,
                   source_cases: coalesce(graph_rel.source_cases, []),
                   source_batches: coalesce(graph_rel.source_batches, [])
                 }) AS graph_rels
            RETURN doctor, graph_nodes, graph_rels
            ORDER BY doctor.name
            """,
            disease=disease,
            entity_types=entity_types,
        )
        snapshots: list[GraphSnapshot] = []
        for record in records:
            nodes = [self._node_from_record(node) for node in record["graph_nodes"]]
            node_ids = {node.id for node in nodes}
            edges = [
                GraphEdge(
                    id=rel.get("id", ""),
                    source=rel.get("source", ""),
                    target=rel.get("target", ""),
                    type=rel.get("type", self.DEFAULT_RELATION_TYPE),
                    label=rel.get("label"),
                    source_cases=list(rel.get("source_cases", []) or []),
                    source_batches=list(rel.get("source_batches", []) or []),
                )
                for rel in record["graph_rels"]
                if rel.get("source", "") in node_ids and rel.get("target", "") in node_ids
            ]
            snapshots.append(GraphSnapshot(nodes=nodes, edges=edges))
        return snapshots

    def get_physician_node_compare_contexts(self, disease: str) -> list[dict[str, object]]:
        records = self._run(
            """
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, disease, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, disease, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor, disease,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            RETURN doctor, disease, disease_cases
            ORDER BY doctor.name
            """,
            disease=disease,
        )
        contexts: list[dict[str, object]] = []
        for record in records:
            doctor = self._node_from_record(record["doctor"])
            disease_node = self._node_from_record(record["disease"])
            disease_cases = list(record.get("disease_cases", []) or [])
            snapshot = self._get_physician_case_snapshot(doctor.id, disease, disease_cases)
            contexts.append(
                {
                    "doctor": doctor,
                    "disease": disease_node,
                    "source_cases": disease_cases,
                    "snapshot": snapshot,
                }
            )
        return contexts

    def get_physician_node_similarity(self, disease: str) -> dict[str, list[dict[str, object]]]:
        try:
            self._run("CALL gds.list() YIELD name RETURN name LIMIT 1")
        except Exception as exc:  # pragma: no cover - depends on local GDS runtime
            raise ValueError("Neo4j GDS 不可用，节点比较无法执行。") from exc

        return {
            category: self._run_similarity_projection(disease, feature_types)
            for category, feature_types in self.COMPARE_FEATURE_TYPES.items()
        }

    def get_physician_fastrp_payload(self, disease: str) -> dict[str, object]:
        try:
            self._run("CALL gds.list() YIELD name RETURN name LIMIT 1")
        except Exception as exc:  # pragma: no cover - depends on local GDS runtime
            raise ValueError("Neo4j GDS 不可用，FastRP 无法执行。") from exc

        graph_name = f"physician-fastrp-{uuid4().hex}"
        node_query = self._fastrp_projection_node_query()
        relationship_query = self._fastrp_projection_relationship_query()
        with self.driver.session(database=self.database) as session:
            try:
                session.run(
                    """
                    CALL gds.graph.project.cypher(
                        $graph_name,
                        $node_query,
                        $relationship_query,
                        {parameters: {disease: $disease}}
                    )
                    """,
                    graph_name=graph_name,
                    node_query=node_query,
                    relationship_query=relationship_query,
                    disease=disease,
                ).consume()
                embedding_rows = list(
                    session.run(
                        """
                        CALL gds.fastRP.stream($graph_name, {
                            embeddingDimension: $embedding_dimension,
                            iterationWeights: $iteration_weights,
                            nodeSelfInfluence: $node_self_influence,
                            randomSeed: $random_seed
                        })
                        YIELD nodeId, embedding
                        WITH gds.util.asNode(nodeId) AS node, embedding
                        RETURN node.id AS node_id, node.name AS node_name, node.type AS node_type, embedding
                        """,
                        graph_name=graph_name,
                        embedding_dimension=self.FASTRP_EMBEDDING_DIMENSION,
                        iteration_weights=self.FASTRP_ITERATION_WEIGHTS,
                        node_self_influence=self.FASTRP_NODE_SELF_INFLUENCE,
                        random_seed=self.FASTRP_RANDOM_SEED,
                    )
                )
            finally:
                try:
                    session.run("CALL gds.graph.drop($graph_name, false)", graph_name=graph_name).consume()
                except Exception:
                    pass

        feature_embeddings = {
            str(row.get("node_id", "")): np.asarray(row.get("embedding", []), dtype=float)
            for row in embedding_rows
            if str(row.get("node_type", "")) in {"C证型", "D病因", "E病机"}
        }
        feature_meta = {
            str(row.get("node_id", "")): {
                "name": str(row.get("node_name", "")),
                "type": str(row.get("node_type", "")),
            }
            for row in embedding_rows
            if str(row.get("node_type", "")) in {"C证型", "D病因", "E病机"}
        }
        association_rows = self._run(
            """
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature)
            WHERE feature.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN doctor.name AS doctor_name, feature.id AS feature_id, feature.name AS feature_name, feature.type AS feature_type
            ORDER BY doctor.name, feature.type, feature.name, feature.id
            """,
            disease=disease,
        )
        doctor_feature_vectors: dict[str, dict[str, list[np.ndarray]]] = {}
        canonical_feature_vectors: dict[tuple[str, str, str], list[np.ndarray]] = {}
        for row in association_rows:
            doctor_name = str(row.get("doctor_name", ""))
            feature_id = str(row.get("feature_id", ""))
            feature_name = str(row.get("feature_name", ""))
            feature_type = str(row.get("feature_type", ""))
            vector = feature_embeddings.get(feature_id)
            if not doctor_name or vector is None:
                continue
            category = self._feature_category(feature_type)
            doctor_feature_vectors.setdefault(doctor_name, {}).setdefault(category, []).append(vector)
            doctor_feature_vectors.setdefault(doctor_name, {}).setdefault("overall", []).append(vector)
            canonical_feature_vectors.setdefault((doctor_name, category, feature_name), []).append(vector)

        doctor_embeddings: dict[str, dict[str, list[float]]] = {}
        for doctor_name, category_map in doctor_feature_vectors.items():
            doctor_embeddings[doctor_name] = {}
            for category in ("patterns", "causes", "mechanisms", "overall"):
                vectors = category_map.get(category, [])
                if not vectors:
                    doctor_embeddings[doctor_name][category] = []
                    continue
                doctor_embeddings[doctor_name][category] = np.mean(np.asarray(vectors, dtype=float), axis=0).tolist()

        similarity = {
            category: self._pairwise_embedding_similarity(doctor_embeddings, category)
            for category in ("patterns", "causes", "mechanisms", "overall")
        }
        feature_points = [
            {
                "id": f"{doctor_name}:{category}:{feature_name}",
                "label": feature_name,
                "group": category,
                "vector": np.mean(np.asarray(vectors, dtype=float), axis=0).tolist(),
            }
            for (doctor_name, category, feature_name), vectors in canonical_feature_vectors.items()
            if vectors
        ]
        feature_candidates = self._feature_similarity_candidates(canonical_feature_vectors)
        return {
            "similarity": similarity,
            "doctor_embeddings": doctor_embeddings,
            "feature_candidates": feature_candidates,
            "feature_points": feature_points,
        }

    def list_entities(self) -> list[GraphNode]:
        records = self._run("MATCH (n) WHERE n.id IS NOT NULL RETURN n ORDER BY n.name LIMIT 500")
        return [self._node_from_record(record["n"]) for record in records]

    def list_relations(self) -> list[GraphEdge]:
        records = self._run(
            "MATCH (a)-[r]->(b) WHERE r.id IS NOT NULL AND a.id IS NOT NULL AND b.id IS NOT NULL RETURN r, a.id AS source, b.id AS target ORDER BY coalesce(r.label, r.type, type(r)) LIMIT 500"
        )
        return [self._edge_from_record(record["r"], record["source"], record["target"]) for record in records]

    def upsert_entity(self, payload: GraphNode) -> GraphNode:
        self._run(
            """
            MERGE (n {id: $id})
            SET n.name = $name,
                n.label = $label,
                n.type = $type,
                n.normalized_name = $normalized_name,
                n.summary = $summary,
                n.source = $source,
                n.source_cases = $source_cases,
                n.source_batches = $source_batches
            RETURN n
            """,
            **payload.model_dump(),
            normalized_name=self._normalize_name(payload.name),
        )
        self._apply_entity_type_label(payload.id, payload.type)
        return payload

    def delete_entity(self, entity_id: str) -> None:
        self._run("MATCH (n {id: $entity_id}) DETACH DELETE n", entity_id=entity_id)

    def delete_entities(self, entity_ids: list[str]) -> None:
        if not entity_ids:
            return
        self._run("MATCH (n) WHERE n.id IN $entity_ids DETACH DELETE n", entity_ids=entity_ids)

    def upsert_relation(self, payload: GraphEdge) -> GraphEdge:
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._upsert_relation_tx, payload)
        return payload

    def delete_relation(self, relation_id: str) -> None:
        self._run("MATCH ()-[r {id: $relation_id}]-() DELETE r", relation_id=relation_id)

    def delete_relations(self, relation_ids: list[str]) -> None:
        if not relation_ids:
            return
        self._run("MATCH ()-[r]-() WHERE r.id IN $relation_ids DELETE r", relation_ids=relation_ids)

    def merge_graph(self, nodes: list[GraphNode], edges: list[GraphEdge], source: str, source_case: str) -> dict[str, int]:
        with self.driver.session(database=self.database) as session:
            return session.execute_write(self._merge_graph, nodes, edges, source, source_case)

    def import_standardized_csv(self, load_csv_uri: str, node_count: int, edge_count: int) -> dict[str, int]:
        self._assert_unique_ids()
        existing_node_count = self._count_existing_nodes(load_csv_uri)
        existing_relation_count = self._count_existing_relations(load_csv_uri)
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._import_standardized_csv_tx, load_csv_uri)
        return {
            "created_nodes": max(node_count - existing_node_count, 0),
            "merged_nodes": existing_node_count,
            "created_relations": max(edge_count - existing_relation_count, 0),
            "deduplicated_relations": existing_relation_count,
        }

    @classmethod
    def _merge_graph(cls, tx, nodes: list[GraphNode], edges: list[GraphEdge], source: str, source_case: str) -> dict[str, int]:
        stats = {
            "created_nodes": 0,
            "merged_nodes": 0,
            "created_relations": 0,
            "deduplicated_relations": 0,
        }
        for node in nodes:
            existing_record = tx.run(
                """
                MATCH (n {id: $id})
                RETURN n
                LIMIT 1
                """,
                id=node.id,
            ).single()

            if existing_record:
                existing = dict(existing_record["n"])
                tx.run(
                    """
                    MATCH (n {id: $id})
                    SET n.name = $name,
                        n.label = $label,
                        n.type = $type,
                        n.normalized_name = $normalized_name,
                        n.summary = coalesce(n.summary, $summary),
                        n.source = coalesce(n.source, $source),
                        n.source_cases = $source_cases,
                        n.source_batches = $source_batches,
                        n.summary_variants = $summary_variants
                    """,
                    id=node.id,
                    name=node.name,
                    label=node.label,
                    type=node.type,
                    normalized_name=cls._normalize_name(node.name),
                    summary=existing.get("summary") or node.summary,
                    source=existing.get("source") or node.source,
                    source_cases=cls._merge_unique(existing.get("source_cases"), node.source_cases),
                    source_batches=cls._merge_unique(existing.get("source_batches"), node.source_batches),
                    summary_variants=cls._merge_unique(
                        existing.get("summary_variants"),
                        [value for value in [existing.get("summary"), node.summary] if value],
                    ),
                )
                cls._apply_entity_type_label_tx(tx, node.id, node.type)
                stats["merged_nodes"] += 1
                continue

            payload = node.model_dump()
            payload["source_cases"] = cls._merge_unique(payload.get("source_cases"), [source_case])
            payload["source_batches"] = cls._merge_unique(payload.get("source_batches"), [source])
            tx.run(
                """
                CREATE (n {
                  id: $id,
                  name: $name,
                  label: $label,
                  type: $type,
                  normalized_name: $normalized_name,
                  summary: $summary,
                  source: $source,
                  source_cases: $source_cases,
                  source_batches: $source_batches,
                  summary_variants: $summary_variants
                })
                """,
                **payload,
                normalized_name=cls._normalize_name(node.name),
                summary_variants=[node.summary] if node.summary else [],
            )
            cls._apply_entity_type_label_tx(tx, node.id, node.type)
            stats["created_nodes"] += 1

        for edge in edges:
            existing_record = tx.run(
                """
                MATCH ()-[r {id: $id}]->()
                RETURN r
                LIMIT 1
                """,
                id=edge.id,
            ).single()

            relation_type = cls._normalize_relation_type(edge.type)
            if existing_record:
                existing = dict(existing_record["r"])
                merged_source_cases = cls._merge_unique(existing.get("source_cases"), edge.source_cases)
                merged_source_batches = cls._merge_unique(existing.get("source_batches"), edge.source_batches)
                label = existing.get("label") or edge.label or relation_type
                tx.run("MATCH ()-[r {id: $id}]->() DELETE r", id=edge.id)
                cls._create_relation_tx(
                    tx,
                    relation_id=edge.id,
                    source=edge.source,
                    target=edge.target,
                    relation_type=relation_type,
                    label=label,
                    source_cases=merged_source_cases,
                    source_batches=merged_source_batches,
                )
                stats["deduplicated_relations"] += 1
                continue

            cls._create_relation_tx(
                tx,
                relation_id=edge.id,
                source=edge.source,
                target=edge.target,
                relation_type=relation_type,
                label=edge.label or relation_type,
                source_cases=edge.source_cases,
                source_batches=edge.source_batches,
            )
            stats["created_relations"] += 1

        return stats

    @classmethod
    def _upsert_relation_tx(cls, tx, payload: GraphEdge) -> None:
        relation_type = cls._normalize_relation_type(payload.type)
        existing_record = tx.run(
            """
            MATCH ()-[r {id: $id}]->()
            RETURN r
            LIMIT 1
            """,
            id=payload.id,
        ).single()
        source_cases = list(payload.source_cases)
        source_batches = list(payload.source_batches)
        label = payload.label or relation_type
        if existing_record:
            existing = dict(existing_record["r"])
            source_cases = cls._merge_unique(existing.get("source_cases"), payload.source_cases)
            source_batches = cls._merge_unique(existing.get("source_batches"), payload.source_batches)
            label = existing.get("label") or payload.label or relation_type
            tx.run("MATCH ()-[r {id: $id}]->() DELETE r", id=payload.id)

        cls._create_relation_tx(
            tx,
            relation_id=payload.id,
            source=payload.source,
            target=payload.target,
            relation_type=relation_type,
            label=label,
            source_cases=source_cases,
            source_batches=source_batches,
        )

    @classmethod
    def _import_standardized_csv_tx(cls, tx, load_csv_uri: str) -> None:
        tx.run(cls._subject_node_import_query(), load_csv_uri=load_csv_uri)
        tx.run(cls._object_node_import_query(), load_csv_uri=load_csv_uri)
        tx.run(cls._relation_import_query(), load_csv_uri=load_csv_uri)
        for entity_type in cls.ENTITY_TYPE_LABELS:
            target_label = cls._entity_label_from_type(entity_type)
            if not target_label:
                continue
            tx.run(
                cls._import_entity_label_query(target_label),
                load_csv_uri=load_csv_uri,
                entity_type=entity_type,
            )

    @classmethod
    def _create_relation_tx(
        cls,
        tx,
        *,
        relation_id: str,
        source: str,
        target: str,
        relation_type: str,
        label: str | None,
        source_cases: list[str],
        source_batches: list[str],
    ) -> None:
        relation_query = f"""
            MATCH (a {{id: $source}}), (b {{id: $target}})
            CREATE (a)-[r:`{relation_type}` {{
              id: $id,
              type: $type,
              label: $label,
              source_cases: $source_cases,
              source_batches: $source_batches
            }}]->(b)
            RETURN r
        """
        tx.run(
            relation_query,
            id=relation_id,
            source=source,
            target=target,
            type=relation_type,
            label=label,
            source_cases=source_cases,
            source_batches=source_batches,
        )

    def _apply_entity_type_label(self, entity_id: str, entity_type: str) -> None:
        self._run(self._build_entity_label_query(entity_type), entity_id=entity_id)

    @classmethod
    def _apply_entity_type_label_tx(cls, tx, entity_id: str, entity_type: str) -> None:
        tx.run(cls._build_entity_label_query(entity_type), entity_id=entity_id)

    @classmethod
    def _build_entity_label_query(cls, entity_type: str) -> str:
        reset_lines = "\n".join(f"REMOVE n:`{label}`" for label in cls.ENTITY_TYPE_LABELS)
        target_label = cls._entity_label_from_type(entity_type)
        set_clause = f"\nSET n:`{target_label}`" if target_label else ""
        return f"""
            MATCH (n {{id: $entity_id}})
            {reset_lines}
            {set_clause}
            RETURN n
        """

    @classmethod
    def _entity_label_from_type(cls, entity_type: str) -> str | None:
        cleaned = normalize_entity_type(entity_type)
        return cls.ENTITY_LABEL_MAPPING.get(cleaned)

    @classmethod
    def _normalize_relation_type(cls, relation_type: str | None) -> str:
        cleaned = (relation_type or "").replace("`", "").strip()
        return cleaned or cls.DEFAULT_RELATION_TYPE

    def _assert_unique_ids(self) -> None:
        duplicate_node_records = self._run(
            """
            MATCH (n)
            WHERE n.id IS NOT NULL
            WITH n.id AS entity_id, count(*) AS total
            WHERE total > 1
            RETURN entity_id
            LIMIT 1
            """
        )
        if duplicate_node_records:
            raise ValueError(f"Neo4j 中存在重复节点 id：{duplicate_node_records[0]['entity_id']}")

        duplicate_relation_records = self._run(
            """
            MATCH ()-[r]->()
            WHERE r.id IS NOT NULL
            WITH r.id AS relation_id, count(*) AS total
            WHERE total > 1
            RETURN relation_id
            LIMIT 1
            """
        )
        if duplicate_relation_records:
            raise ValueError(f"Neo4j 中存在重复关系 id：{duplicate_relation_records[0]['relation_id']}")

    def _count_existing_nodes(self, load_csv_uri: str) -> int:
        records = self._run(
            """
            LOAD CSV WITH HEADERS FROM $load_csv_uri AS row
            WITH collect(DISTINCT row.subject_id) + collect(DISTINCT row.object_id) AS raw_node_ids
            UNWIND raw_node_ids AS node_id
            WITH DISTINCT node_id
            MATCH (n {id: node_id})
            RETURN count(n) AS total
            """,
            load_csv_uri=load_csv_uri,
        )
        return int(records[0]["total"]) if records else 0

    def _count_existing_relations(self, load_csv_uri: str) -> int:
        records = self._run(
            """
            LOAD CSV WITH HEADERS FROM $load_csv_uri AS row
            WITH DISTINCT row.relation_id AS relation_id
            MATCH ()-[r {id: relation_id}]->()
            RETURN count(r) AS total
            """,
            load_csv_uri=load_csv_uri,
        )
        return int(records[0]["total"]) if records else 0

    def _run(self, cypher: str, **parameters):
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, parameters)
            return list(result)

    def _get_physician_case_snapshot(self, doctor_id: str, disease: str, disease_cases: list[str]) -> GraphSnapshot:
        records = self._run(
            """
            MATCH (doctor {id: $doctor_id, type: 'A医家'})
            MATCH (disease {type: 'B病名', name: $disease})
            MATCH p = (doctor)-[*0..4]-(node)
            WHERE disease IN nodes(p)
              AND ALL(item IN nodes(p) WHERE item.type IN $entity_types)
              AND ALL(item IN nodes(p) WHERE item.type <> 'B病名' OR item.name = $disease)
              AND (
                size($disease_cases) = 0
                OR ALL(rel IN relationships(p) WHERE ANY(source_case IN coalesce(rel.source_cases, []) WHERE source_case IN $disease_cases))
              )
            WITH collect(p) AS paths
            UNWIND paths AS node_path
            UNWIND nodes(node_path) AS graph_node
            WITH paths, collect(DISTINCT graph_node) AS graph_nodes
            UNWIND paths AS rel_path
            UNWIND relationships(rel_path) AS graph_rel
            RETURN graph_nodes,
                   collect(DISTINCT {
                     id: graph_rel.id,
                     type: coalesce(graph_rel.type, type(graph_rel)),
                     label: coalesce(graph_rel.label, graph_rel.type, type(graph_rel)),
                     source: startNode(graph_rel).id,
                     target: endNode(graph_rel).id,
                     source_cases: coalesce(graph_rel.source_cases, []),
                     source_batches: coalesce(graph_rel.source_batches, [])
                   }) AS graph_rels
            """,
            doctor_id=doctor_id,
            disease=disease,
            disease_cases=disease_cases,
            entity_types=["A医家", "B病名", "C证型", "D病因", "E病机"],
        )
        if not records:
            return GraphSnapshot(nodes=[], edges=[])
        record = records[0]
        nodes = [self._node_from_record(node) for node in record["graph_nodes"]]
        node_ids = {node.id for node in nodes}
        edges = [
            GraphEdge(
                id=rel.get("id", ""),
                source=rel.get("source", ""),
                target=rel.get("target", ""),
                type=rel.get("type", self.DEFAULT_RELATION_TYPE),
                label=rel.get("label"),
                source_cases=list(rel.get("source_cases", []) or []),
                source_batches=list(rel.get("source_batches", []) or []),
            )
            for rel in record["graph_rels"]
            if rel.get("source", "") in node_ids and rel.get("target", "") in node_ids
        ]
        return GraphSnapshot(nodes=nodes, edges=edges)

    def _run_similarity_projection(self, disease: str, feature_types: list[str]) -> list[dict[str, object]]:
        graph_name = f"physician-node-compare-{uuid4().hex}"
        node_query = self._similarity_projection_node_query()
        relationship_query = self._similarity_projection_relationship_query()
        results_by_metric: dict[str, dict[tuple[str, str], float]] = {key: {} for key in self.SIMILARITY_METRICS}

        with self.driver.session(database=self.database) as session:
            try:
                session.run(
                    """
                    CALL gds.graph.project.cypher(
                        $graph_name,
                        $node_query,
                        $relationship_query,
                        {parameters: {disease: $disease, feature_types: $feature_types}}
                    )
                    """,
                    graph_name=graph_name,
                    node_query=node_query,
                    relationship_query=relationship_query,
                    disease=disease,
                    feature_types=feature_types,
                ).consume()
                for metric_key, metric_name in self.SIMILARITY_METRICS.items():
                    rows = session.run(
                        """
                        CALL gds.nodeSimilarity.stream($graph_name, {similarityMetric: $metric_name})
                        YIELD node1, node2, similarity
                        WITH gds.util.asNode(node1) AS left_node, gds.util.asNode(node2) AS right_node, similarity
                        WHERE left_node.type = 'A医家' AND right_node.type = 'A医家'
                        RETURN left_node.name AS left_doctor, right_node.name AS right_doctor, round(similarity, 6) AS similarity
                        """,
                        graph_name=graph_name,
                        metric_name=metric_name,
                    )
                    for row in rows:
                        left_doctor = row.get("left_doctor", "")
                        right_doctor = row.get("right_doctor", "")
                        pair_key = tuple(sorted((left_doctor, right_doctor)))
                        results_by_metric[metric_key][pair_key] = float(row.get("similarity", 0.0))
            finally:
                try:
                    session.run("CALL gds.graph.drop($graph_name, false)", graph_name=graph_name).consume()
                except Exception:
                    pass

        pairs = set()
        for metric_map in results_by_metric.values():
            pairs |= set(metric_map.keys())
        return [
            {
                "left_doctor": left_doctor,
                "right_doctor": right_doctor,
                "jaccard": round(results_by_metric["jaccard"].get((left_doctor, right_doctor), 0.0), 6),
                "overlap": round(results_by_metric["overlap"].get((left_doctor, right_doctor), 0.0), 6),
                "cosine": round(results_by_metric["cosine"].get((left_doctor, right_doctor), 0.0), 6),
            }
            for left_doctor, right_doctor in sorted(pairs)
        ]

    @staticmethod
    def _similarity_projection_node_query() -> str:
        return """
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            RETURN DISTINCT id(doctor) AS id
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature)
            WHERE feature.type IN $feature_types
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            WITH feature.type AS feature_type, feature.name AS feature_name, min(id(feature)) AS canonical_feature_id
            RETURN canonical_feature_id AS id
        """

    @staticmethod
    def _similarity_projection_relationship_query() -> str:
        return """
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature)
            WHERE feature.type IN $feature_types
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            WITH feature.type AS feature_type, feature.name AS feature_name, min(id(feature)) AS canonical_feature_id, collect(DISTINCT doctor) AS doctors
            UNWIND doctors AS doctor
            RETURN id(doctor) AS source, canonical_feature_id AS target, 'RELATED' AS type
        """

    @staticmethod
    def _fastrp_projection_node_query() -> str:
        return """
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            RETURN DISTINCT id(doctor) AS id
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            RETURN DISTINCT id(disease) AS id
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature)
            WHERE feature.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN DISTINCT id(feature) AS id
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, disease, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, disease, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor, disease,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (disease)-[disease_feature_rel]-(feature)
            WHERE feature.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(disease_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN DISTINCT id(feature) AS id
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature_a)
            WHERE feature_a.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            MATCH (feature_a)-[feature_rel]-(feature_b)
            WHERE feature_b.type IN ['C证型', 'D病因', 'E病机']
              AND id(feature_a) <> id(feature_b)
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN DISTINCT id(feature_b) AS id
        """

    @staticmethod
    def _fastrp_projection_relationship_query() -> str:
        return """
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            RETURN DISTINCT id(doctor) AS source, id(disease) AS target, 1.0 AS weight
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature)
            WHERE feature.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN DISTINCT id(doctor) AS source, id(feature) AS target, 1.0 AS weight
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, disease, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, disease, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor, disease,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (disease)-[disease_feature_rel]-(feature)
            WHERE feature.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(disease_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN DISTINCT id(disease) AS source, id(feature) AS target, 1.0 AS weight
            UNION
            MATCH (doctor {type: 'A医家'})-[rel]-(disease {type: 'B病名'})
            WHERE disease.name = $disease
            WITH doctor, collect(DISTINCT coalesce(rel.source_cases, [])) AS raw_case_lists
            WITH doctor, reduce(raw_cases = [], case_list IN raw_case_lists | raw_cases + case_list) AS raw_cases
            WITH doctor,
                 reduce(source_cases = [], source_case IN raw_cases |
                     CASE
                         WHEN source_case = '' OR source_case IN source_cases THEN source_cases
                         ELSE source_cases + source_case
                     END
                 ) AS disease_cases
            MATCH (doctor)-[doctor_feature_rel]-(feature_a)
            WHERE feature_a.type IN ['C证型', 'D病因', 'E病机']
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(doctor_feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            MATCH (feature_a)-[feature_rel]-(feature_b)
            WHERE feature_b.type IN ['C证型', 'D病因', 'E病机']
              AND id(feature_a) <> id(feature_b)
              AND (
                size(disease_cases) = 0
                OR ANY(source_case IN coalesce(feature_rel.source_cases, []) WHERE source_case IN disease_cases)
              )
            RETURN DISTINCT id(feature_a) AS source, id(feature_b) AS target, 1.0 AS weight
        """

    @staticmethod
    def _feature_category(feature_type: str) -> str:
        return {
            "C证型": "patterns",
            "D病因": "causes",
            "E病机": "mechanisms",
        }.get(feature_type, "overall")

    def _pairwise_embedding_similarity(
        self,
        doctor_embeddings: dict[str, dict[str, list[float]]],
        category: str,
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        doctor_names = sorted(doctor_embeddings)
        for left_index, left_doctor in enumerate(doctor_names):
            left_vector = np.asarray(doctor_embeddings.get(left_doctor, {}).get(category, []), dtype=float)
            for right_doctor in doctor_names[left_index + 1:]:
                right_vector = np.asarray(doctor_embeddings.get(right_doctor, {}).get(category, []), dtype=float)
                similarity = self._cosine_similarity(left_vector, right_vector)
                rows.append(
                    {
                        "left_doctor": left_doctor,
                        "right_doctor": right_doctor,
                        "jaccard": round(similarity, 6),
                        "overlap": round(similarity, 6),
                        "cosine": round(similarity, 6),
                    }
                )
        return rows

    @staticmethod
    def _cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
        if left.size == 0 or right.size == 0:
            return 0.0
        denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
        if denominator == 0.0:
            return 0.0
        return float(np.dot(left, right) / denominator)

    def _feature_similarity_candidates(
        self,
        canonical_feature_vectors: dict[tuple[str, str, str], list[np.ndarray]],
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        averaged = {
            key: np.mean(np.asarray(vectors, dtype=float), axis=0)
            for key, vectors in canonical_feature_vectors.items()
            if vectors
        }
        keys = sorted(averaged)
        for left_key, right_key in combinations(keys, 2):
            left_doctor, left_category, left_name = left_key
            right_doctor, right_category, right_name = right_key
            if left_doctor == right_doctor or left_category != right_category or left_name == right_name:
                continue
            similarity = self._cosine_similarity(averaged[left_key], averaged[right_key])
            rows.append(
                {
                    "category": left_category,
                    "left_doctor": left_doctor,
                    "left_feature_name": left_name,
                    "right_doctor": right_doctor,
                    "right_feature_name": right_name,
                    "similarity": round(similarity, 6),
                }
            )
        rows.sort(key=lambda item: (-float(item["similarity"]), item["category"], item["left_feature_name"], item["right_feature_name"]))
        return rows[:12]

    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join((name or "").strip().split())

    def _get_unique_node_id_by_name(self, name: str, source_case: str = "") -> str:
        normalized = self._normalize_name(name)
        if not normalized:
            raise ValueError("实体名称不能为空")
        records = self._run(
            """
            MATCH (n)
            WHERE n.id IS NOT NULL
              AND n.name = $name
              AND ($source_case = '' OR $source_case IN coalesce(n.source_cases, []))
            RETURN n.id AS id, n.type AS type
            ORDER BY n.type, n.id
            LIMIT 2
            """,
            name=normalized,
            source_case=source_case,
        )
        if not records:
            raise ValueError(f"未找到实体：{normalized}")
        if len(records) > 1:
            types = "、".join(str(record.get("type", "")) for record in records)
            raise ValueError(f"实体名称不唯一：{normalized}（{types}）")
        return str(records[0]["id"])

    @staticmethod
    def _merge_unique(existing, incoming: list[str]) -> list[str]:
        merged: list[str] = []
        for value in list(existing or []) + incoming:
            cleaned = (value or "").strip()
            if cleaned and cleaned not in merged:
                merged.append(cleaned)
        return merged

    @classmethod
    def _subject_node_import_query(cls) -> str:
        return """
            LOAD CSV WITH HEADERS FROM $load_csv_uri AS row
            WITH DISTINCT
                row.subject_id AS node_id,
                row.subject_name AS node_name,
                row.subject_type AS node_type,
                row.source AS source,
                row.source_case AS source_case
            MERGE (n {id: node_id})
            SET n.name = node_name,
                n.label = node_type,
                n.type = node_type,
                n.normalized_name = trim(node_name),
                n.source = coalesce(n.source, source),
                n.source_cases =
                    CASE
                        WHEN source_case IN coalesce(n.source_cases, []) THEN coalesce(n.source_cases, [])
                        ELSE coalesce(n.source_cases, []) + source_case
                    END,
                n.source_batches =
                    CASE
                        WHEN source IN coalesce(n.source_batches, []) THEN coalesce(n.source_batches, [])
                        ELSE coalesce(n.source_batches, []) + source
                    END
        """

    @classmethod
    def _object_node_import_query(cls) -> str:
        return """
            LOAD CSV WITH HEADERS FROM $load_csv_uri AS row
            WITH DISTINCT
                row.object_id AS node_id,
                row.object_name AS node_name,
                row.object_type AS node_type,
                row.source AS source,
                row.source_case AS source_case
            MERGE (n {id: node_id})
            SET n.name = node_name,
                n.label = node_type,
                n.type = node_type,
                n.normalized_name = trim(node_name),
                n.source = coalesce(n.source, source),
                n.source_cases =
                    CASE
                        WHEN source_case IN coalesce(n.source_cases, []) THEN coalesce(n.source_cases, [])
                        ELSE coalesce(n.source_cases, []) + source_case
                    END,
                n.source_batches =
                    CASE
                        WHEN source IN coalesce(n.source_batches, []) THEN coalesce(n.source_batches, [])
                        ELSE coalesce(n.source_batches, []) + source
                    END
        """

    @classmethod
    def _relation_import_query(cls) -> str:
        return f"""
            LOAD CSV WITH HEADERS FROM $load_csv_uri AS row
            MATCH (a {{id: row.subject_id}})
            MATCH (b {{id: row.object_id}})
            MERGE (a)-[r:`{cls.IMPORT_RELATION_TYPE}` {{id: row.relation_id}}]->(b)
            SET r.type = row.relation,
                r.label = coalesce(r.label, row.relation),
                r.source_cases =
                    CASE
                        WHEN row.source_case IN coalesce(r.source_cases, []) THEN coalesce(r.source_cases, [])
                        ELSE coalesce(r.source_cases, []) + row.source_case
                    END,
                r.source_batches =
                    CASE
                        WHEN row.source IN coalesce(r.source_batches, []) THEN coalesce(r.source_batches, [])
                        ELSE coalesce(r.source_batches, []) + row.source
                    END
        """

    @classmethod
    def _import_entity_label_query(cls, target_label: str) -> str:
        return f"""
            LOAD CSV WITH HEADERS FROM $load_csv_uri AS row
            WITH collect(DISTINCT row.subject_id) + collect(DISTINCT row.object_id) AS raw_node_ids
            UNWIND raw_node_ids AS node_id
            WITH DISTINCT node_id
            MATCH (n {{id: node_id}})
            WHERE n.type = $entity_type
            SET n:`{target_label}`
        """

    @staticmethod
    def _node_from_record(node) -> GraphNode:
        return GraphNode(
            id=node.get("id", ""),
            name=node.get("name", ""),
            label=node.get("label", node.get("type", "\u5b9e\u4f53")),
            type=node.get("type", node.get("label", "\u5b9e\u4f53")),
            summary=node.get("summary"),
            source=node.get("source"),
            source_cases=list(node.get("source_cases", []) or []),
            source_batches=list(node.get("source_batches", []) or []),
        )

    @classmethod
    def _edge_from_record(cls, edge, source: str, target: str) -> GraphEdge:
        relation_type = edge.get("type") or cls.DEFAULT_RELATION_TYPE
        return GraphEdge(
            id=edge.get("id", ""),
            source=source,
            target=target,
            type=relation_type,
            label=edge.get("label") or relation_type,
            source_cases=list(edge.get("source_cases", []) or []),
            source_batches=list(edge.get("source_batches", []) or []),
        )
