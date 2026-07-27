import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.physician_compare_service import PhysicianCompareService


class PhysicianCompareServiceImportTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        PhysicianCompareService._word2vec_class = None

    def test_load_word2vec_class_imports_submodule_once(self) -> None:
        fake_word2vec = object()
        fake_module = SimpleNamespace(Word2Vec=fake_word2vec)
        with patch.object(PhysicianCompareService, "_word2vec_class", None), patch(
            "app.services.physician_compare_service.importlib.import_module",
            return_value=fake_module,
        ) as import_module:
            first = PhysicianCompareService._load_word2vec_class()
            second = PhysicianCompareService._load_word2vec_class()

        self.assertIs(first, fake_word2vec)
        self.assertIs(second, fake_word2vec)
        import_module.assert_called_once_with("gensim.models.word2vec")


if __name__ == "__main__":
    unittest.main()
