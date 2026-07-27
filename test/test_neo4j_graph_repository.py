import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "neo4j" not in sys.modules:
    neo4j_module = ModuleType("neo4j")
    neo4j_module.Driver = object
    neo4j_module.GraphDatabase = SimpleNamespace(driver=lambda *args, **kwargs: object())
    sys.modules["neo4j"] = neo4j_module

from app.repositories.neo4j_graph import Neo4jGraphRepository


class Neo4jGraphRepositoryProjectionQueryTestCase(unittest.TestCase):
    def test_similarity_relationship_query_uses_global_canonical_feature_ids(self) -> None:
        query = Neo4jGraphRepository._similarity_projection_relationship_query()

        self.assertIn("collect(DISTINCT doctor) AS doctors", query)
        self.assertIn("UNWIND doctors AS doctor", query)
        self.assertIn("min(id(feature)) AS canonical_feature_id", query)

    def test_fastrp_node_query_includes_all_feature_nodes_referenced_by_relationships(self) -> None:
        query = Neo4jGraphRepository._fastrp_projection_node_query()

        self.assertIn("MATCH (disease)-[disease_feature_rel]-(feature)", query)
        self.assertIn("RETURN DISTINCT id(feature) AS id", query)
        self.assertIn("MATCH (feature_a)-[feature_rel]-(feature_b)", query)
        self.assertIn("RETURN DISTINCT id(feature_b) AS id", query)


if __name__ == "__main__":
    unittest.main()
