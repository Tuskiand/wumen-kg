from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import HTTPException, UploadFile, status

from app.core.config import Settings
from app.schemas.admin import AuditRecord, DashboardStats, ImportTask, VersionRecord
from app.services.csv_import_parser import CsvImportParser
from app.services.demo_data import AUDITS, DASHBOARD, IMPORTS, VERSIONS, append_audit, append_import_task
from app.services.import_runtime import PENDING_IMPORTS, PendingImport


@dataclass
class MergeStats:
    created_nodes: int
    merged_nodes: int
    created_relations: int
    deduplicated_relations: int


class AdminService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def dashboard(self, graph_totals: tuple[int, int]) -> DashboardStats:
        node_count, edge_count = graph_totals
        return DashboardStats(
            node_count=node_count,
            edge_count=edge_count,
            import_success_rate=DASHBOARD.import_success_rate,
            last_publish_at=DASHBOARD.last_publish_at,
        )

    def import_tasks(self) -> list[ImportTask]:
        return IMPORTS

    def versions(self) -> list[VersionRecord]:
        return VERSIONS

    def audits(self) -> list[AuditRecord]:
        return AUDITS

    async def validate_import(self, files: list[UploadFile], source: str, source_case: str, schema: str | None = None) -> ImportTask:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No files uploaded')
        parsed = await CsvImportParser.parse(files, source, source_case, schema)
        schema_summary = f'，schema {parsed.schema}' if parsed.schema else '，未指定 schema'
        task = append_import_task(
            'CSV导入校验',
            'completed',
            f'来源 {source}，来源医案 {source_case}{schema_summary}，解析到 {parsed.node_count} 个节点、{parsed.edge_count} 条关系，校验通过。',
            source=source,
            source_case=source_case,
            schema=parsed.schema,
        )
        PENDING_IMPORTS[task.id] = PendingImport(
            source=source,
            source_case=source_case,
            schema=parsed.schema,
            host_csv_path=parsed.host_csv_path,
            load_csv_uri=parsed.load_csv_uri,
            node_count=parsed.node_count,
            edge_count=parsed.edge_count,
            warnings=parsed.warnings,
        )
        append_audit('导入校验', task.id)
        return task

    def execute_import(self, task_id: str, importer) -> ImportTask:
        payload = PENDING_IMPORTS.get(task_id)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Import task not found or expired')
        if not os.path.exists(payload.host_csv_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='导入临时文件不存在，请重新校验后再执行导入')
        stats = importer(payload.load_csv_uri, payload.node_count, payload.edge_count)
        task = append_import_task(
            'CSV追加导入',
            'completed',
            f"来源 {payload.source}，来源医案 {payload.source_case}{f'，schema {payload.schema}' if payload.schema else '，未指定 schema'}，新增节点 {stats['created_nodes']} 个，重复节点 {stats['merged_nodes']} 个，新增关系 {stats['created_relations']} 条，重复关系 {stats['deduplicated_relations']} 条。",
            source=payload.source,
            source_case=payload.source_case,
            schema=payload.schema,
            created_nodes=stats['created_nodes'],
            merged_nodes=stats['merged_nodes'],
            created_relations=stats['created_relations'],
            deduplicated_relations=stats['deduplicated_relations'],
        )
        append_audit('执行导入', task.id)
        os.remove(payload.host_csv_path)
        PENDING_IMPORTS.pop(task_id, None)
        return task
