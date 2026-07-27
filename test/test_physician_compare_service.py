import io
import json
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.graph import GraphEdge, GraphNode, GraphSnapshot, PhysicianPathEmbeddingProfile
from app.services.physician_compare_service import PhysicianCompareService


def make_node(node_id: str, name: str, node_type: str) -> GraphNode:
    return GraphNode(
        id=node_id,
        name=name,
        label=node_type,
        type=node_type,
        source_cases=[],
        source_batches=[],
    )


def make_edge(edge_id: str, source: str, target: str, edge_type: str, source_case: str) -> GraphEdge:
    return GraphEdge(
        id=edge_id,
        source=source,
        target=target,
        type=edge_type,
        label=edge_type,
        source_cases=[source_case],
        source_batches=[],
    )


class PhysicianCompareServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PhysicianCompareService()

    @staticmethod
    def make_fastrp_payload() -> dict[str, object]:
        return {
            "similarity": {
                "patterns": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 0.91, "overlap": 0.91, "cosine": 0.91}],
                "causes": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 0.32, "overlap": 0.32, "cosine": 0.32}],
                "mechanisms": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 0.88, "overlap": 0.88, "cosine": 0.88}],
                "overall": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 0.77, "overlap": 0.77, "cosine": 0.77}],
            },
            "doctor_embeddings": {
                "张三": {
                    "patterns": [1.0, 0.0, 0.0],
                    "causes": [0.2, 0.8, 0.0],
                    "mechanisms": [0.6, 0.4, 0.0],
                    "overall": [0.5, 0.5, 0.0],
                },
                "李四": {
                    "patterns": [0.9, 0.1, 0.0],
                    "causes": [0.1, 0.9, 0.0],
                    "mechanisms": [0.7, 0.3, 0.0],
                    "overall": [0.45, 0.55, 0.0],
                },
            },
            "feature_candidates": [
                {
                    "category": "patterns",
                    "left_doctor": "张三",
                    "left_feature_name": "痰热内闭证",
                    "right_doctor": "李四",
                    "right_feature_name": "痰热内闭证",
                    "similarity": 0.95,
                }
            ],
            "feature_points": [
                {"id": "pattern-1", "label": "痰热内闭证", "group": "patterns", "vector": [1.0, 0.0, 0.0]},
                {"id": "cause-1", "label": "风邪外袭", "group": "causes", "vector": [0.0, 1.0, 0.0]},
            ],
        }

    @staticmethod
    def make_report_png_bytes() -> bytes:
        from PIL import Image

        image = Image.new("RGB", (1200, 900), color="white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", dpi=(600, 600))
        return buffer.getvalue()

    @staticmethod
    def make_report_docx_bytes() -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", "<?xml version='1.0' encoding='UTF-8'?><Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'></Types>")
            archive.writestr("word/document.xml", "<?xml version='1.0' encoding='UTF-8'?><w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body><w:p><w:r><w:t>report</w:t></w:r></w:p></w:body></w:document>")
        return buffer.getvalue()

    def test_compare_nodes_with_two_doctors_builds_shared_unique_similarity_and_rwr(self) -> None:
        disease = make_node("disease-1", "中风", "B病名")

        doctor_1 = make_node("doctor-1", "张三", "A医家")
        pattern_1 = make_node("pattern-1", "痰热内闭证", "C证型")
        pattern_1_dup = make_node("pattern-1b", "痰热内闭证", "C证型")
        cause_1 = make_node("cause-1", "风邪外袭", "D病因")
        mechanism_shared = make_node("mechanism-1", "痰瘀阻络", "E病机")

        doctor_2 = make_node("doctor-2", "李四", "A医家")
        pattern_2 = make_node("pattern-2", "痰热内闭证", "C证型")
        cause_2 = make_node("cause-2", "肝阳化风", "D病因")
        mechanism_shared_dup = make_node("mechanism-2", "痰瘀阻络", "E病机")

        snapshot_1 = GraphSnapshot(
            nodes=[doctor_1, disease, pattern_1, pattern_1_dup, cause_1, mechanism_shared],
            edges=[
                make_edge("e1", doctor_1.id, disease.id, "A医家-B病名", "case-1"),
                make_edge("e2", doctor_1.id, pattern_1.id, "A医家-C证型", "case-1"),
                make_edge("e3", doctor_1.id, pattern_1_dup.id, "A医家-C证型", "case-1"),
                make_edge("e4", doctor_1.id, cause_1.id, "A医家-D病因", "case-1"),
                make_edge("e5", doctor_1.id, mechanism_shared.id, "A医家-E病机", "case-1"),
                make_edge("e6", disease.id, pattern_1.id, "B病名-C证型", "case-1"),
                make_edge("e7", disease.id, cause_1.id, "B病名-D病因", "case-1"),
                make_edge("e8", disease.id, mechanism_shared.id, "B病名-E病机", "case-1"),
            ],
        )
        snapshot_2 = GraphSnapshot(
            nodes=[doctor_2, disease, pattern_2, cause_2, mechanism_shared_dup],
            edges=[
                make_edge("e9", doctor_2.id, disease.id, "A医家-B病名", "case-2"),
                make_edge("e10", doctor_2.id, pattern_2.id, "A医家-C证型", "case-2"),
                make_edge("e11", doctor_2.id, cause_2.id, "A医家-D病因", "case-2"),
                make_edge("e12", doctor_2.id, mechanism_shared_dup.id, "A医家-E病机", "case-2"),
                make_edge("e13", disease.id, pattern_2.id, "B病名-C证型", "case-2"),
                make_edge("e14", disease.id, cause_2.id, "B病名-D病因", "case-2"),
                make_edge("e15", disease.id, mechanism_shared_dup.id, "B病名-E病机", "case-2"),
            ],
        )

        contexts = [
            {"doctor": doctor_1, "disease": disease, "source_cases": ["case-1"], "snapshot": snapshot_1},
            {"doctor": doctor_2, "disease": disease, "source_cases": ["case-2"], "snapshot": snapshot_2},
        ]
        similarity_rows = {
            "patterns": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 0.5, "overlap": 1.0, "cosine": 0.707107}],
            "causes": [],
            "mechanisms": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 1.0, "overlap": 1.0, "cosine": 1.0}],
            "overall": [{"left_doctor": "张三", "right_doctor": "李四", "jaccard": 0.4, "overlap": 0.8, "cosine": 0.57735}],
        }

        result = self.service.compare_nodes("中风", contexts, similarity_rows, self.make_fastrp_payload())

        self.assertEqual(result.doctor_count, 2)
        self.assertEqual([doctor.name for doctor in result.doctors], ["张三", "李四"])
        self.assertEqual(len(result.shared_nodes.patterns), 1)
        self.assertEqual(result.shared_nodes.patterns[0].node.name, "痰热内闭证")
        self.assertEqual(result.shared_nodes.patterns[0].doctors, ["张三", "李四"])
        self.assertEqual(len(result.shared_nodes.mechanisms), 1)
        self.assertEqual(result.shared_nodes.mechanisms[0].node.name, "痰瘀阻络")

        doctor_1_profile = next(item for item in result.doctor_profiles if item.doctor.name == "张三")
        self.assertEqual([node.name for node in doctor_1_profile.unique.causes], ["风邪外袭"])
        self.assertEqual([node.name for node in doctor_1_profile.shared.patterns], ["痰热内闭证"])
        self.assertEqual([node.name for node in doctor_1_profile.all.patterns], ["痰热内闭证"])

        self.assertEqual(len(result.similarity.overall), 1)
        self.assertAlmostEqual(result.similarity.overall[0].jaccard, 0.4)
        self.assertAlmostEqual(result.similarity.causes[0].jaccard, 0.0)
        self.assertEqual(len(result.fastrp_similarity.overall), 1)
        self.assertAlmostEqual(result.fastrp_similarity.overall[0].cosine, 0.77)
        self.assertEqual(len(result.doctor_feature_embeddings), 2)
        self.assertEqual(result.doctor_feature_embeddings[0].doctor.name, "张三")
        self.assertEqual(result.similarity_overview[0].doctor.name, "张三")
        self.assertEqual(len(result.feature_similarity_candidates), 1)
        self.assertEqual(result.feature_similarity_candidates[0].category, "patterns")
        self.assertEqual(len(result.embedding_points), 2)
        self.assertEqual(result.summary.primary_embedding_metric, "FastRP cosine")

        self.assertEqual(len(result.rwr), 2)
        doctor_1_rwr = next(item for item in result.rwr if item.doctor.name == "张三")
        self.assertEqual(doctor_1_rwr.restart_probability, self.service.PRIMARY_RESTART_PROBABILITY)
        self.assertIn("痰热内闭证", [item.name for item in doctor_1_rwr.rankings.patterns])
        self.assertIn("痰瘀阻络", [item.name for item in doctor_1_rwr.rankings.mechanisms])

    def test_compare_nodes_with_single_doctor_keeps_rwr_and_empty_matrix(self) -> None:
        disease = make_node("disease-1", "中风", "B病名")
        doctor = make_node("doctor-1", "张三", "A医家")
        pattern = make_node("pattern-1", "痰热内闭证", "C证型")
        snapshot = GraphSnapshot(
            nodes=[doctor, disease, pattern],
            edges=[
                make_edge("e1", doctor.id, disease.id, "A医家-B病名", "case-1"),
                make_edge("e2", doctor.id, pattern.id, "A医家-C证型", "case-1"),
                make_edge("e3", disease.id, pattern.id, "B病名-C证型", "case-1"),
            ],
        )

        result = self.service.compare_nodes(
            "中风",
            [{"doctor": doctor, "disease": disease, "source_cases": ["case-1"], "snapshot": snapshot}],
            {"patterns": [], "causes": [], "mechanisms": [], "overall": []},
            {},
        )

        self.assertEqual(result.doctor_count, 1)
        self.assertEqual(result.doctors[0].name, "张三")
        self.assertEqual(result.similarity.overall, [])
        self.assertEqual(len(result.rwr), 1)
        self.assertIn("一位医家", result.summary.message)

    def test_compare_nodes_with_no_contexts_returns_empty_payload(self) -> None:
        result = self.service.compare_nodes(
            "中风",
            [],
            {"patterns": [], "causes": [], "mechanisms": [], "overall": []},
            {},
        )

        self.assertEqual(result.doctor_count, 0)
        self.assertEqual(result.doctors, [])
        self.assertEqual(result.rwr, [])
        self.assertEqual(result.summary.shared_node_count, 0)
        self.assertIn("没有可比较的医家数据", result.summary.message)

    def test_compare_paths_builds_shared_unique_completeness_and_similarity(self) -> None:
        disease = make_node("disease-1", "中风", "B病名")
        doctor_1 = make_node("doctor-1", "张三", "A医家")
        doctor_2 = make_node("doctor-2", "李四", "A医家")
        cause_shared = make_node("cause-1", "风邪外袭", "D病因")
        mechanism_shared = make_node("mechanism-1", "痰瘀阻络", "E病机")
        pattern_shared = make_node("pattern-1", "痰热内闭证", "C证型")
        cause_unique = make_node("cause-2", "气虚生风", "D病因")
        pattern_unique = make_node("pattern-2", "气虚痰阻证", "C证型")

        snapshot_1 = GraphSnapshot(
            nodes=[doctor_1, disease, cause_shared, mechanism_shared, pattern_shared, cause_unique],
            edges=[
                make_edge("e1", doctor_1.id, disease.id, "A医家-B病名", "case-1"),
                make_edge("e2", doctor_1.id, cause_shared.id, "A医家-D病因", "case-1"),
                make_edge("e3", doctor_1.id, mechanism_shared.id, "A医家-E病机", "case-1"),
                make_edge("e4", doctor_1.id, pattern_shared.id, "A医家-C证型", "case-1"),
                make_edge("e5", doctor_1.id, cause_unique.id, "A医家-D病因", "case-1"),
                make_edge("e6", cause_shared.id, mechanism_shared.id, "D病因-E病机", "case-1"),
                make_edge("e7", pattern_shared.id, mechanism_shared.id, "C证型-E病机", "case-1"),
            ],
        )
        snapshot_2 = GraphSnapshot(
            nodes=[doctor_2, disease, cause_shared, mechanism_shared, pattern_shared, pattern_unique],
            edges=[
                make_edge("e8", doctor_2.id, disease.id, "A医家-B病名", "case-2"),
                make_edge("e9", doctor_2.id, cause_shared.id, "A医家-D病因", "case-2"),
                make_edge("e10", doctor_2.id, mechanism_shared.id, "A医家-E病机", "case-2"),
                make_edge("e11", doctor_2.id, pattern_shared.id, "A医家-C证型", "case-2"),
                make_edge("e12", doctor_2.id, pattern_unique.id, "A医家-C证型", "case-2"),
                make_edge("e13", cause_shared.id, mechanism_shared.id, "D病因-E病机", "case-2"),
                make_edge("e14", pattern_shared.id, mechanism_shared.id, "C证型-E病机", "case-2"),
            ],
        )

        with patch.object(
            self.service,
            "_build_path_embedding_profiles",
            return_value=[
                PhysicianPathEmbeddingProfile(doctor=doctor_1, vector=[1.0, 0.0, 0.0]),
                PhysicianPathEmbeddingProfile(doctor=doctor_2, vector=[0.8, 0.2, 0.0]),
            ],
        ):
            result = self.service.compare_paths(
                "中风",
                [
                    {"doctor": doctor_1, "disease": disease, "source_cases": ["case-1"], "snapshot": snapshot_1},
                    {"doctor": doctor_2, "disease": disease, "source_cases": ["case-2"], "snapshot": snapshot_2},
                ],
            )

        self.assertEqual(result.doctor_count, 2)
        self.assertEqual(len(result.shared_paths), 1)
        self.assertEqual(result.shared_paths[0].path.path_type, "D-E-C")
        self.assertEqual(result.shared_paths[0].path.text, "风邪外袭 -> 痰瘀阻络 -> 痰热内闭证")
        self.assertEqual(result.shared_paths[0].doctors, ["张三", "李四"])

        doctor_1_profile = next(item for item in result.doctor_profiles if item.doctor.name == "张三")
        self.assertEqual(doctor_1_profile.completeness.complete_count, 1)
        self.assertEqual(doctor_1_profile.completeness.single_count, 1)
        self.assertEqual([path.text for path in doctor_1_profile.unique_paths], ["气虚生风"])

        doctor_2_profile = next(item for item in result.doctor_profiles if item.doctor.name == "李四")
        self.assertEqual([path.text for path in doctor_2_profile.unique_paths], ["气虚痰阻证"])

        self.assertEqual(len(result.similarity_pairs), 1)
        self.assertEqual(result.similarity_pairs[0].shared_path_count, 1)
        self.assertEqual(result.similarity_pairs[0].union_path_count, 3)
        self.assertAlmostEqual(result.similarity_pairs[0].path_jaccard, 0.333333, places=6)
        self.assertGreater(result.similarity_pairs[0].metapath2vec_cosine, 0.0)
        self.assertEqual(len(result.embeddings), 2)
        self.assertEqual(len(result.embedding_points), 2)
        self.assertEqual(result.summary.primary_similarity_metric, "Path Jaccard")
        self.assertEqual(result.summary.embedding_metric, "Metapath2Vec cosine")

    def test_compare_subgraphs_uses_only_jointly_anchored_core_nodes_and_edges(self) -> None:
        disease = make_node("disease-1", "中风", "B病名")
        doctor_1 = make_node("doctor-1", "张三", "A医家")
        doctor_2 = make_node("doctor-2", "李四", "A医家")
        pattern_shared_1 = make_node("pattern-1", "痰热内闭证", "C证型")
        pattern_shared_2 = make_node("pattern-2", "痰热内闭证", "C证型")
        mechanism_shared_1 = make_node("mechanism-1", "痰瘀阻络", "E病机")
        mechanism_shared_2 = make_node("mechanism-2", "痰瘀阻络", "E病机")
        cause_unique_1 = make_node("cause-1", "风邪外袭", "D病因")
        cause_unique_2 = make_node("cause-2", "肝阳化风", "D病因")
        leaked_cause = make_node("cause-3", "误带病因", "D病因")

        snapshot_1 = GraphSnapshot(
            nodes=[doctor_1, disease, pattern_shared_1, mechanism_shared_1, cause_unique_1, leaked_cause],
            edges=[
                make_edge("e1", doctor_1.id, disease.id, "A医家-B病名", "case-1"),
                make_edge("e2", doctor_1.id, pattern_shared_1.id, "A医家-C证型", "case-1"),
                make_edge("e3", doctor_1.id, mechanism_shared_1.id, "A医家-E病机", "case-1"),
                make_edge("e4", doctor_1.id, cause_unique_1.id, "A医家-D病因", "case-1"),
                make_edge("e5", doctor_1.id, leaked_cause.id, "A医家-D病因", "case-1"),
                make_edge("e6", disease.id, pattern_shared_1.id, "B病名-C证型", "case-1"),
                make_edge("e7", disease.id, mechanism_shared_1.id, "B病名-E病机", "case-1"),
                make_edge("e8", disease.id, cause_unique_1.id, "B病名-D病因", "case-1"),
                make_edge("e9", cause_unique_1.id, mechanism_shared_1.id, "D病因-E病机", "case-1"),
                make_edge("e10", pattern_shared_1.id, mechanism_shared_1.id, "C证型-E病机", "case-1"),
                make_edge("e11", leaked_cause.id, mechanism_shared_1.id, "D病因-E病机", "case-1"),
            ],
        )
        snapshot_2 = GraphSnapshot(
            nodes=[doctor_2, disease, pattern_shared_2, mechanism_shared_2, cause_unique_2],
            edges=[
                make_edge("e12", doctor_2.id, disease.id, "A医家-B病名", "case-2"),
                make_edge("e13", doctor_2.id, pattern_shared_2.id, "A医家-C证型", "case-2"),
                make_edge("e14", doctor_2.id, mechanism_shared_2.id, "A医家-E病机", "case-2"),
                make_edge("e15", doctor_2.id, cause_unique_2.id, "A医家-D病因", "case-2"),
                make_edge("e16", disease.id, pattern_shared_2.id, "B病名-C证型", "case-2"),
                make_edge("e17", disease.id, mechanism_shared_2.id, "B病名-E病机", "case-2"),
                make_edge("e18", disease.id, cause_unique_2.id, "B病名-D病因", "case-2"),
                make_edge("e19", cause_unique_2.id, mechanism_shared_2.id, "D病因-E病机", "case-2"),
                make_edge("e20", pattern_shared_2.id, mechanism_shared_2.id, "C证型-E病机", "case-2"),
            ],
        )

        with patch.object(
            self.service,
            "_build_subgraph_embeddings",
            return_value={
                "vector_embeddings": {
                    "Graph2Vec": {"张三": [0.8, 0.2], "李四": [0.7, 0.3]},
                },
            },
        ):
            result = self.service.compare_subgraphs(
                "中风",
                [
                    {"doctor": doctor_1, "disease": disease, "source_cases": ["case-1"], "snapshot": snapshot_1},
                    {"doctor": doctor_2, "disease": disease, "source_cases": ["case-2"], "snapshot": snapshot_2},
                ],
            )

        self.assertEqual(result.doctor_count, 2)
        self.assertEqual(len(result.shared_nodes.patterns), 1)
        self.assertEqual(result.shared_nodes.patterns[0].node.name, "痰热内闭证")
        self.assertEqual(len(result.shared_nodes.mechanisms), 1)
        self.assertEqual(result.shared_nodes.mechanisms[0].node.name, "痰瘀阻络")
        self.assertEqual(len(result.shared_edges), 6)

        doctor_1_profile = next(item for item in result.doctor_profiles if item.doctor.name == "张三")
        self.assertEqual([node.name for node in doctor_1_profile.unique_nodes.causes], ["风邪外袭"])
        self.assertNotIn("误带病因", [node.name for node in doctor_1_profile.nodes.causes])
        self.assertNotIn("误带病因", [node.name for node in doctor_1_profile.unique_nodes.causes])
        self.assertTrue(any("风邪外袭" in edge.text for edge in doctor_1_profile.unique_edges))
        self.assertFalse(any("误带病因" in edge.text for edge in doctor_1_profile.edges))
        self.assertTrue(any("同时满足 张三 的 A医家-D病因 与 中风 的 B病名-D病因" == node.inclusion_reason for node in doctor_1_profile.audit_nodes if node.name == "风邪外袭"))

        self.assertEqual(len(result.similarity_pairs), 1)
        pair = result.similarity_pairs[0]
        self.assertAlmostEqual(pair.node_jaccard, 0.5)
        self.assertAlmostEqual(pair.edge_jaccard, 0.5)
        self.assertAlmostEqual(pair.subgraph_jaccard, 0.5)
        self.assertGreaterEqual(pair.graph2vec_cosine, -1.0)
        self.assertLessEqual(pair.graph2vec_cosine, 1.0)
        self.assertEqual(len(result.embeddings), 2)
        self.assertEqual(len(result.embedding_points), 2)
        self.assertEqual(result.summary.vector_similarity_metrics, ["Graph2Vec"])

    def test_export_subgraphs_outputs_core_graph_and_vectors(self) -> None:
        disease = make_node("disease-1", "中风", "B病名")
        doctor_1 = make_node("doctor-1", "张三", "A医家")
        doctor_2 = make_node("doctor-2", "李四", "A医家")
        pattern_shared_1 = make_node("pattern-1", "痰热内闭证", "C证型")
        pattern_shared_2 = make_node("pattern-2", "痰热内闭证", "C证型")
        mechanism_shared_1 = make_node("mechanism-1", "痰瘀阻络", "E病机")
        mechanism_shared_2 = make_node("mechanism-2", "痰瘀阻络", "E病机")
        cause_unique_1 = make_node("cause-1", "风邪外袭", "D病因")
        cause_unique_2 = make_node("cause-2", "肝阳化风", "D病因")

        snapshot_1 = GraphSnapshot(
            nodes=[doctor_1, disease, pattern_shared_1, mechanism_shared_1, cause_unique_1],
            edges=[
                make_edge("e1", doctor_1.id, disease.id, "A医家-B病名", "case-1"),
                make_edge("e2", doctor_1.id, pattern_shared_1.id, "A医家-C证型", "case-1"),
                make_edge("e3", doctor_1.id, mechanism_shared_1.id, "A医家-E病机", "case-1"),
                make_edge("e4", doctor_1.id, cause_unique_1.id, "A医家-D病因", "case-1"),
                make_edge("e5", disease.id, pattern_shared_1.id, "B病名-C证型", "case-1"),
                make_edge("e6", disease.id, mechanism_shared_1.id, "B病名-E病机", "case-1"),
                make_edge("e7", disease.id, cause_unique_1.id, "B病名-D病因", "case-1"),
                make_edge("e8", cause_unique_1.id, mechanism_shared_1.id, "D病因-E病机", "case-1"),
                make_edge("e9", pattern_shared_1.id, mechanism_shared_1.id, "C证型-E病机", "case-1"),
            ],
        )
        snapshot_2 = GraphSnapshot(
            nodes=[doctor_2, disease, pattern_shared_2, mechanism_shared_2, cause_unique_2],
            edges=[
                make_edge("e10", doctor_2.id, disease.id, "A医家-B病名", "case-2"),
                make_edge("e11", doctor_2.id, pattern_shared_2.id, "A医家-C证型", "case-2"),
                make_edge("e12", doctor_2.id, mechanism_shared_2.id, "A医家-E病机", "case-2"),
                make_edge("e13", doctor_2.id, cause_unique_2.id, "A医家-D病因", "case-2"),
                make_edge("e14", disease.id, pattern_shared_2.id, "B病名-C证型", "case-2"),
                make_edge("e15", disease.id, mechanism_shared_2.id, "B病名-E病机", "case-2"),
                make_edge("e16", disease.id, cause_unique_2.id, "B病名-D病因", "case-2"),
                make_edge("e17", cause_unique_2.id, mechanism_shared_2.id, "D病因-E病机", "case-2"),
                make_edge("e18", pattern_shared_2.id, mechanism_shared_2.id, "C证型-E病机", "case-2"),
            ],
        )

        with patch.object(
            self.service,
            "_build_path_embedding_profiles",
            return_value=[
                PhysicianPathEmbeddingProfile(doctor=doctor_1, vector=[1.0, 0.0, 0.0]),
                PhysicianPathEmbeddingProfile(doctor=doctor_2, vector=[0.8, 0.2, 0.0]),
            ],
        ), patch.object(
            self.service,
            "_build_subgraph_embeddings",
            return_value={
                "vector_embeddings": {
                    "Graph2Vec": {"张三": [0.8, 0.2], "李四": [0.7, 0.3]},
                },
            },
        ):
            filename, payload = self.service.export_subgraphs(
                "中风",
                [
                    {"doctor": doctor_1, "disease": disease, "source_cases": ["case-1"], "snapshot": snapshot_1},
                    {"doctor": doctor_2, "disease": disease, "source_cases": ["case-2"], "snapshot": snapshot_2},
                ],
                {
                    "patterns": [],
                    "causes": [],
                    "mechanisms": [],
                    "overall": [],
                },
                self.make_fastrp_payload(),
            )

        self.assertEqual(filename, "physician_subgraphs_中风.zip")
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            names = set(archive.namelist())
            self.assertIn("pairwise_similarity.csv", names)
            self.assertIn("shared_nodes.csv", names)
            self.assertIn("node_fastrp_similarity.csv", names)
            self.assertIn("path_pairwise_similarity.csv", names)
            self.assertIn("doctors/张三/core_nodes.csv", names)
            self.assertIn("doctors/张三/relation_node_graph.json", names)
            self.assertIn("doctors/张三/metapath2vec_path_vector.csv", names)
            self.assertIn("doctors/张三/graph2vec_vector.csv", names)
            self.assertIn("doctors/李四/core_edges.csv", names)
            self.assertNotIn("doctors/张三/fgsd_vector.csv", names)
            core_nodes = archive.read("doctors/张三/core_nodes.csv").decode("utf-8")
            self.assertIn("张三", core_nodes)
            self.assertIn("风邪外袭", core_nodes)
            graph_json = archive.read("doctors/张三/relation_node_graph.json").decode("utf-8")
            self.assertIn("\"relation_type\": \"A医家-D病因\"", graph_json)

    def test_export_paper_report_outputs_word_png_tables_and_metadata(self) -> None:
        disease = make_node("disease-1", "中风", "B病名")
        doctor_1 = make_node("doctor-1", "张三", "A医家")
        doctor_2 = make_node("doctor-2", "李四", "A医家")
        pattern_shared_1 = make_node("pattern-1", "痰热内闭证", "C证型")
        pattern_shared_2 = make_node("pattern-2", "痰热内闭证", "C证型")
        mechanism_shared_1 = make_node("mechanism-1", "痰瘀阻络", "E病机")
        mechanism_shared_2 = make_node("mechanism-2", "痰瘀阻络", "E病机")
        cause_unique_1 = make_node("cause-1", "风邪外袭", "D病因")
        cause_unique_2 = make_node("cause-2", "肝阳化风", "D病因")

        snapshot_1 = GraphSnapshot(
            nodes=[doctor_1, disease, pattern_shared_1, mechanism_shared_1, cause_unique_1],
            edges=[
                make_edge("e1", doctor_1.id, disease.id, "A医家-B病名", "case-1"),
                make_edge("e2", doctor_1.id, pattern_shared_1.id, "A医家-C证型", "case-1"),
                make_edge("e3", doctor_1.id, mechanism_shared_1.id, "A医家-E病机", "case-1"),
                make_edge("e4", doctor_1.id, cause_unique_1.id, "A医家-D病因", "case-1"),
                make_edge("e5", disease.id, pattern_shared_1.id, "B病名-C证型", "case-1"),
                make_edge("e6", disease.id, mechanism_shared_1.id, "B病名-E病机", "case-1"),
                make_edge("e7", disease.id, cause_unique_1.id, "B病名-D病因", "case-1"),
                make_edge("e8", cause_unique_1.id, mechanism_shared_1.id, "D病因-E病机", "case-1"),
                make_edge("e9", pattern_shared_1.id, mechanism_shared_1.id, "C证型-E病机", "case-1"),
            ],
        )
        snapshot_2 = GraphSnapshot(
            nodes=[doctor_2, disease, pattern_shared_2, mechanism_shared_2, cause_unique_2],
            edges=[
                make_edge("e10", doctor_2.id, disease.id, "A医家-B病名", "case-2"),
                make_edge("e11", doctor_2.id, pattern_shared_2.id, "A医家-C证型", "case-2"),
                make_edge("e12", doctor_2.id, mechanism_shared_2.id, "A医家-E病机", "case-2"),
                make_edge("e13", doctor_2.id, cause_unique_2.id, "A医家-D病因", "case-2"),
                make_edge("e14", disease.id, pattern_shared_2.id, "B病名-C证型", "case-2"),
                make_edge("e15", disease.id, mechanism_shared_2.id, "B病名-E病机", "case-2"),
                make_edge("e16", disease.id, cause_unique_2.id, "B病名-D病因", "case-2"),
                make_edge("e17", cause_unique_2.id, mechanism_shared_2.id, "D病因-E病机", "case-2"),
                make_edge("e18", pattern_shared_2.id, mechanism_shared_2.id, "C证型-E病机", "case-2"),
            ],
        )
        fake_figure = self.make_report_png_bytes()
        fake_docx = self.make_report_docx_bytes()
        report_figures = {
            "node_similarity_overall_heatmap.png": fake_figure,
            "fastrp_similarity_overall_heatmap.png": fake_figure,
            "fastrp_radar.png": fake_figure,
            "fastrp_scatter.png": fake_figure,
            "path_jaccard_heatmap.png": fake_figure,
            "metapath2vec_similarity_heatmap.png": fake_figure,
            "metapath2vec_scatter.png": fake_figure,
            "subgraph_jaccard_heatmap.png": fake_figure,
            "graph2vec_similarity_heatmap.png": fake_figure,
            "graph2vec_scatter.png": fake_figure,
        }

        with patch.object(
            self.service,
            "_build_path_embedding_profiles",
            return_value=[
                PhysicianPathEmbeddingProfile(doctor=doctor_1, vector=[1.0, 0.0, 0.0]),
                PhysicianPathEmbeddingProfile(doctor=doctor_2, vector=[0.8, 0.2, 0.0]),
            ],
        ), patch.object(
            self.service,
            "_build_subgraph_embeddings",
            return_value={
                "vector_embeddings": {
                    "Graph2Vec": {"张三": [0.8, 0.2], "李四": [0.7, 0.3]},
                },
            },
        ), patch.object(
            self.service,
            "_build_report_figures",
            return_value=report_figures,
        ), patch.object(
            self.service,
            "_build_report_docx",
            return_value=fake_docx,
        ):
            filename, payload, timings = self.service.export_paper_report(
                "中风",
                [
                    {"doctor": doctor_1, "disease": disease, "source_cases": ["case-1"], "snapshot": snapshot_1},
                    {"doctor": doctor_2, "disease": disease, "source_cases": ["case-2"], "snapshot": snapshot_2},
                ],
                {
                    "patterns": [],
                    "causes": [],
                    "mechanisms": [],
                    "overall": [],
                },
                self.make_fastrp_payload(),
            )

        self.assertEqual(filename, "physician_compare_report_中风.zip")
        self.assertGreaterEqual(timings["total_ms"], 0)
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            names = set(archive.namelist())
            self.assertIn("report/physician_compare_中风.docx", names)
            self.assertIn("figures/node_similarity_overall_heatmap.png", names)
            self.assertIn("tables/path_pairwise_similarity.csv", names)
            self.assertIn("tables/timings.csv", names)
            self.assertIn("report_metadata.json", names)
            metadata = json.loads(archive.read("report_metadata.json").decode("utf-8"))
            self.assertIn("timings_ms", metadata)
            self.assertIn("figures", metadata)
            docx_bytes = archive.read("report/physician_compare_中风.docx")
            with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as docx_archive:
                self.assertIn("word/document.xml", set(docx_archive.namelist()))
            png_bytes = archive.read("figures/node_similarity_overall_heatmap.png")
            from PIL import Image

            image = Image.open(io.BytesIO(png_bytes))
            dpi = image.info.get("dpi", (0, 0))
            self.assertGreater(dpi[0], 300)
            self.assertGreater(dpi[1], 300)


if __name__ == "__main__":
    unittest.main()
