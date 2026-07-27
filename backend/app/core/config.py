from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WuMen Medical Graph API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = True
    demo_mode: bool = True

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    admin_username: str = "admin"
    admin_password: str

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str
    neo4j_database: str = "neo4j"
    neo4j_import_host_dir: str = "neo4j_import"
    neo4j_import_container_dir: str = "/import"

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "wumen_graph"
    mysql_username: str = "root"
    mysql_password: str

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
