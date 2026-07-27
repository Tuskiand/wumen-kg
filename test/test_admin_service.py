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
    neo4j_exceptions_module = ModuleType("neo4j.exceptions")

    class Neo4jError(Exception):
        pass

    neo4j_exceptions_module.Neo4jError = Neo4jError
    sys.modules["neo4j"] = neo4j_module
    sys.modules["neo4j.exceptions"] = neo4j_exceptions_module

from app.core.config import Settings
from app.services.admin_service import AdminService
from app.services.demo_data import DASHBOARD


class AdminServiceDashboardTestCase(unittest.TestCase):
    def test_dashboard_uses_live_graph_totals_when_provided(self) -> None:
        service = AdminService(Settings(demo_mode=False))

        result = service.dashboard((58, 70))

        self.assertEqual(result.node_count, 58)
        self.assertEqual(result.edge_count, 70)
        self.assertEqual(result.import_success_rate, DASHBOARD.import_success_rate)
        self.assertEqual(result.last_publish_at, DASHBOARD.last_publish_at)


if __name__ == "__main__":
    unittest.main()
