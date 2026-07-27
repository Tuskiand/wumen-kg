import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "neo4j" not in sys.modules:
    neo4j_module = ModuleType("neo4j")
    neo4j_module.Driver = object
    neo4j_module.GraphDatabase = SimpleNamespace(driver=lambda *args, **kwargs: object())
    neo4j_exceptions_module = ModuleType("neo4j.exceptions")

    class Neo4jError(Exception):
        pass

    neo4j_exceptions_module.Neo4jError = Neo4jError
    sys.modules["neo4j"] = neo4j_module
    sys.modules["neo4j.exceptions"] = neo4j_exceptions_module

from app.core.config import Settings
from app.schemas.graph import (
    GraphEdge,
    GraphNode,
    GraphSnapshot,
    PhysicianEmbeddingScatterPoint,
    PhysicianFeatureEmbedding,
    PhysicianDoctorScore,
    PhysicianCategoryScores,
    PhysicianNodeCompareResponse,
    PhysicianNodeCompareSummary,
    PhysicianPathCompareResponse,
    PhysicianPathCompareSummary,
    PhysicianPathEmbeddingProfile,
    PhysicianPathProfile,
    PhysicianPathCompleteness,
    PhysicianPathSimilarityPair,
    PhysicianSubgraphCompareResponse,
    PhysicianSubgraphCompareSummary,
    PhysicianSubgraphEmbeddingProfile,
    PhysicianSimilarityGroup,
    SharedCompareNodeGroup,
)
from app.services.graph_service import GraphService


def make_doctor(node_id: str, name: str) -> GraphNode:
    return GraphNode(
        id=node_id,
        name=name,
        label="A医家",
        type="A医家",
        source_cases=[],
        source_batches=[],
    )


class FakeRepository:
    def __init__(self, *, available: bool = True, contexts=None, similarity=None, fastrp_payload=None) -> None:
        self.available = available
        self.contexts = contexts or []
        self.similarity = similarity or {"patterns": [], "causes": [], "mechanisms": [], "overall": []}
        self.fastrp_payload = fastrp_payload or {}
        self.total_counts = (0, 0)
        self.context_calls: list[str] = []
        self.similarity_calls: list[str] = []
        self.fastrp_calls: list[str] = []
        self.path_calls: list[tuple[str, str, int, str]] = []
        self.total_calls = 0

    def is_available(self) -> bool:
        return self.available

    def graph_totals(self):
        self.total_calls += 1
        return self.total_counts

    def get_path(self, source_name: str, target_name: str, max_depth: int, source_case: str):
        self.path_calls.append((source_name, target_name, max_depth, source_case))
        return GraphSnapshot(
            nodes=[
                GraphNode(id="disease-1", name=source_name, label="B病名", type="B病名"),
                GraphNode(id="mechanism-1", name=target_name, label="E病机", type="E病机"),
            ],
            edges=[
                GraphEdge(id="edge-1", source="disease-1", target="mechanism-1", type="B病名-E病机", label="B病名-E病机")
            ],
        )

    def get_physician_node_compare_contexts(self, disease: str):
        self.context_calls.append(disease)
        return self.contexts

    def get_physician_node_similarity(self, disease: str):
        self.similarity_calls.append(disease)
        return self.similarity

    def get_physician_fastrp_payload(self, disease: str):
        self.fastrp_calls.append(disease)
        return self.fastrp_payload


class GraphServiceNodeCompareTestCase(unittest.TestCase):
    def test_path_query_uses_entity_names_for_repository_lookup(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(available=True)
        service.repository = repository

        result = service.path_query("中风", "痰阻清窍", 4, "吴门案")

        self.assertEqual(repository.path_calls, [("中风", "痰阻清窍", 4, "吴门案")])
        self.assertEqual(result.nodes[0].name, "中风")
        self.assertEqual(result.edges[0].type, "B病名-E病机")

    def test_path_query_reports_ambiguous_or_missing_entity_names(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(available=True)
        service.repository = repository
        repository.get_path = lambda *args: (_ for _ in ()).throw(ValueError("实体名称不唯一：中风（B病名、C证型）"))

        with self.assertRaises(HTTPException) as context:
            service.path_query("中风", "痰阻清窍")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("实体名称不唯一", context.exception.detail)

    def test_graph_totals_returns_demo_counts_in_demo_mode(self) -> None:
        service = GraphService(Settings(demo_mode=True))

        node_count, edge_count = service.graph_totals()

        self.assertGreater(node_count, 0)
        self.assertGreater(edge_count, 0)

    def test_graph_totals_requires_available_repository_outside_demo_mode(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        service.repository = FakeRepository(available=False)

        with self.assertRaises(HTTPException) as context:
            service.graph_totals()

        self.assertEqual(context.exception.status_code, 503)
        self.assertIn("Neo4j 当前不可用", context.exception.detail)

    def test_graph_totals_fetches_live_counts_from_repository(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(available=True)
        repository.total_counts = (58, 70)
        service.repository = repository

        result = service.graph_totals()

        self.assertEqual(result, (58, 70))
        self.assertEqual(repository.total_calls, 1)

    def test_compare_physician_nodes_rejects_demo_mode(self) -> None:
        service = GraphService(Settings(demo_mode=True))

        with self.assertRaises(HTTPException) as context:
            service.compare_physician_nodes("中风")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("演示模式", context.exception.detail)

    def test_compare_physician_nodes_requires_available_repository(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        service.repository = FakeRepository(available=False)

        with self.assertRaises(HTTPException) as context:
            service.compare_physician_nodes("中风")

        self.assertEqual(context.exception.status_code, 503)
        self.assertIn("Neo4j 当前不可用", context.exception.detail)

    def test_compare_physician_nodes_fetches_repository_data_and_delegates_to_compare_service(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(
            available=True,
            contexts=[{"doctor": make_doctor("doctor-1", "张三")}],
            similarity={"patterns": [], "causes": [], "mechanisms": [], "overall": []},
            fastrp_payload={"similarity": {"patterns": [], "causes": [], "mechanisms": [], "overall": []}},
        )
        service.repository = repository
        expected = PhysicianNodeCompareResponse(
            disease="中风",
            doctor_count=1,
            doctors=[make_doctor("doctor-1", "张三")],
            similarity=PhysicianSimilarityGroup(),
            fastrp_similarity=PhysicianSimilarityGroup(),
            shared_nodes=SharedCompareNodeGroup(),
            doctor_profiles=[],
            rwr=[],
            doctor_feature_embeddings=[
                PhysicianFeatureEmbedding(doctor=make_doctor("doctor-1", "张三"))
            ],
            similarity_overview=[
                PhysicianDoctorScore(
                    doctor=make_doctor("doctor-1", "张三"),
                    scores=PhysicianCategoryScores(),
                )
            ],
            feature_similarity_candidates=[],
            embedding_points=[
                PhysicianEmbeddingScatterPoint(
                    id="doctor-1",
                    label="张三",
                    group="FastRP",
                    x=0.0,
                    y=0.0,
                )
            ],
            summary=PhysicianNodeCompareSummary(
                primary_similarity_metric="Jaccard",
                primary_embedding_metric="FastRP cosine",
                shared_node_count=0,
                pairwise_comparison_count=0,
                primary_restart_probability=0.25,
                message="ok",
            ),
        )

        with patch("app.services.graph_service.PhysicianCompareService") as compare_service_cls:
            compare_service_cls.return_value.compare_nodes.return_value = expected

            result = service.compare_physician_nodes("中风")

        self.assertIs(result, expected)
        self.assertEqual(repository.context_calls, ["中风"])
        self.assertEqual(repository.similarity_calls, ["中风"])
        self.assertEqual(repository.fastrp_calls, ["中风"])
        compare_service_cls.return_value.compare_nodes.assert_called_once_with(
            "中风",
            repository.contexts,
            repository.similarity,
            repository.fastrp_payload,
        )

    def test_compare_physician_paths_rejects_demo_mode(self) -> None:
        service = GraphService(Settings(demo_mode=True))

        with self.assertRaises(HTTPException) as context:
            service.compare_physician_paths("中风")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("演示模式", context.exception.detail)

    def test_compare_physician_paths_fetches_contexts_and_delegates(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(
            available=True,
            contexts=[{"doctor": make_doctor("doctor-1", "张三")}],
        )
        service.repository = repository
        expected = PhysicianPathCompareResponse(
            disease="中风",
            doctor_count=1,
            doctors=[make_doctor("doctor-1", "张三")],
            shared_paths=[],
            doctor_profiles=[],
            similarity_pairs=[
                PhysicianPathSimilarityPair(
                    left_doctor="张三",
                    right_doctor="李四",
                    shared_path_count=0,
                    union_path_count=0,
                    path_jaccard=0.0,
                    metapath2vec_cosine=0.0,
                )
            ],
            embeddings=[
                PhysicianPathEmbeddingProfile(
                    doctor=make_doctor("doctor-1", "张三"),
                    vector=[],
                )
            ],
            embedding_points=[],
            summary=PhysicianPathCompareSummary(
                shared_path_count=0,
                pairwise_comparison_count=0,
                primary_similarity_metric="Path Jaccard",
                embedding_metric="Metapath2Vec cosine",
                message="ok",
            ),
        )

        with patch("app.services.graph_service.PhysicianCompareService") as compare_service_cls:
            compare_service_cls.return_value.compare_paths.return_value = expected

            result = service.compare_physician_paths("中风")

        self.assertIs(result, expected)
        self.assertEqual(repository.context_calls, ["中风"])
        compare_service_cls.return_value.compare_paths.assert_called_once_with("中风", repository.contexts)

    def test_compare_physician_subgraphs_rejects_demo_mode(self) -> None:
        service = GraphService(Settings(demo_mode=True))

        with self.assertRaises(HTTPException) as context:
            service.compare_physician_subgraphs("中风")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("演示模式", context.exception.detail)

    def test_compare_physician_subgraphs_fetches_contexts_and_delegates(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(
            available=True,
            contexts=[{"doctor": make_doctor("doctor-1", "张三")}],
        )
        service.repository = repository
        expected = PhysicianSubgraphCompareResponse(
            disease="中风",
            doctor_count=1,
            doctors=[make_doctor("doctor-1", "张三")],
            similarity_pairs=[],
            shared_nodes=SharedCompareNodeGroup(),
            shared_edges=[],
            doctor_profiles=[],
            embeddings=[
                PhysicianSubgraphEmbeddingProfile(
                    doctor=make_doctor("doctor-1", "张三"),
                    graph2vec_vector=[],
                )
            ],
            embedding_points=[],
            summary=PhysicianSubgraphCompareSummary(
                primary_similarity_metric="子图Jaccard",
                shared_node_count=0,
                shared_edge_count=0,
                pairwise_comparison_count=0,
                vector_similarity_metrics=[],
                message="ok",
            ),
        )

        with patch("app.services.graph_service.PhysicianCompareService") as compare_service_cls:
            compare_service_cls.return_value.compare_subgraphs.return_value = expected

            result = service.compare_physician_subgraphs("中风")

        self.assertIs(result, expected)
        self.assertEqual(repository.context_calls, ["中风"])
        compare_service_cls.return_value.compare_subgraphs.assert_called_once_with("中风", repository.contexts)

    def test_export_physician_subgraphs_fetches_contexts_and_delegates(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(
            available=True,
            contexts=[{"doctor": make_doctor("doctor-1", "张三")}],
            similarity={"patterns": [], "causes": [], "mechanisms": [], "overall": []},
            fastrp_payload={"similarity": {"patterns": [], "causes": [], "mechanisms": [], "overall": []}},
        )
        service.repository = repository

        with patch("app.services.graph_service.PhysicianCompareService") as compare_service_cls:
            compare_service_cls.return_value.export_subgraphs.return_value = ("physician_subgraphs_中风.zip", b"zip-bytes")

            filename, payload = service.export_physician_subgraphs("中风")

        self.assertEqual(filename, "physician_subgraphs_中风.zip")
        self.assertEqual(payload, b"zip-bytes")
        self.assertEqual(repository.context_calls, ["中风"])
        self.assertEqual(repository.similarity_calls, ["中风"])
        self.assertEqual(repository.fastrp_calls, ["中风"])
        compare_service_cls.return_value.export_subgraphs.assert_called_once_with(
            "中风",
            repository.contexts,
            repository.similarity,
            repository.fastrp_payload,
        )

    def test_export_physician_compare_report_fetches_contexts_and_delegates(self) -> None:
        service = GraphService(Settings(demo_mode=True))
        service.settings.demo_mode = False
        repository = FakeRepository(
            available=True,
            contexts=[{"doctor": make_doctor("doctor-1", "张三")}],
            similarity={"patterns": [], "causes": [], "mechanisms": [], "overall": []},
            fastrp_payload={"similarity": {"patterns": [], "causes": [], "mechanisms": [], "overall": []}},
        )
        service.repository = repository

        with patch("app.services.graph_service.PhysicianCompareService") as compare_service_cls:
            compare_service_cls.return_value.export_paper_report.return_value = (
                "physician_compare_report_中风.zip",
                b"report-bytes",
                {"analysis_ms": 11, "figure_ms": 22, "word_ms": 33, "total_ms": 66},
            )

            filename, payload, timings = service.export_physician_compare_report("中风")

        self.assertEqual(filename, "physician_compare_report_中风.zip")
        self.assertEqual(payload, b"report-bytes")
        self.assertEqual(timings["total_ms"], 66)
        self.assertEqual(repository.context_calls, ["中风"])
        self.assertEqual(repository.similarity_calls, ["中风"])
        self.assertEqual(repository.fastrp_calls, ["中风"])
        compare_service_cls.return_value.export_paper_report.assert_called_once_with(
            "中风",
            repository.contexts,
            repository.similarity,
            repository.fastrp_payload,
        )


if __name__ == "__main__":
    unittest.main()
