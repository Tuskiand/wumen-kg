from functools import lru_cache

from neo4j import GraphDatabase

from app.core.config import Settings, get_settings


class Neo4jManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver = None

    def connect(self) -> None:
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._settings.neo4j_uri,
                auth=(self._settings.neo4j_username, self._settings.neo4j_password),
            )

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            self.connect()
        return self._driver


@lru_cache
def get_neo4j_manager() -> Neo4jManager:
    return Neo4jManager(get_settings())
