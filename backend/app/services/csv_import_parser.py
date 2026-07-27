from __future__ import annotations

import csv
import hashlib
import re
from collections import OrderedDict
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.kg_rules import (
    get_available_schemas,
    get_entity_types,
    get_relation_types,
    get_schema_definition,
    is_allowed_entity_type,
    is_allowed_relation_type,
    normalize_entity_type,
    normalize_schema,
    relation_direction_matches,
)

ENTITY_PATTERN = re.compile(r"^(?P<name>.+)\((?P<type>[^()]+)\)$")
EXPECTED_HEADERS = ["subject", "relation", "object"]


@dataclass
class ParsedImport:
    host_csv_path: str
    load_csv_uri: str
    node_count: int
    edge_count: int
    warnings: list[str]
    schema: str | None


class CsvImportParser:
    @staticmethod
    async def parse(files: list[UploadFile], source: str, source_case: str, schema: str | None = None) -> ParsedImport:
        if len(files) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='当前只支持上传一个三列表 CSV 文件')

        csv_file = files[0]
        source = source.strip()
        source_case = source_case.strip()
        schema_key = CsvImportParser._normalize_schema(schema)
        if not source:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='来源不能为空')
        if not source_case:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='来源医案不能为空')

        headers, rows = await CsvImportParser._read_csv(csv_file)
        CsvImportParser._validate_headers(headers, csv_file.filename or 'CSV')
        if not rows:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='CSV 不能为空')

        scope = CsvImportParser._build_scope(source, source_case)
        node_rows: OrderedDict[tuple[str, str], dict[str, str]] = OrderedDict()
        edge_rows: OrderedDict[str, dict[str, str]] = OrderedDict()

        for index, row in enumerate(rows, start=2):
            subject_raw = CsvImportParser._require_cell(row, 'subject', index)
            relation = CsvImportParser._require_cell(row, 'relation', index)
            object_raw = CsvImportParser._require_cell(row, 'object', index)

            subject_name, subject_type = CsvImportParser._parse_entity(subject_raw, 'subject', index, schema_key)
            object_name, object_type = CsvImportParser._parse_entity(object_raw, 'object', index, schema_key)

            if schema_key and not is_allowed_relation_type(relation, schema_key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV 第 {index} 行存在不允许的关系类型：{relation}。schema `{schema_key}` 仅允许：{', '.join(get_relation_types(schema_key))}",
                )
            if schema_key and not relation_direction_matches(relation, subject_type, object_type, schema_key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'CSV 第 {index} 行关系方向不符合 schema `{schema_key}` 规则：{subject_type} -[{relation}]-> {object_type}',
                )

            subject_id = CsvImportParser._build_node_id(scope, subject_name, subject_type)
            object_id = CsvImportParser._build_node_id(scope, object_name, object_type)
            relation_id = CsvImportParser._build_relation_id(scope, subject_id, relation, object_id)

            node_rows.setdefault(
                (subject_name, subject_type),
                {
                    'id': subject_id,
                    'name': subject_name,
                    'type': subject_type,
                },
            )
            node_rows.setdefault(
                (object_name, object_type),
                {
                    'id': object_id,
                    'name': object_name,
                    'type': object_type,
                },
            )
            edge_rows.setdefault(
                relation_id,
                {
                    'relation_id': relation_id,
                    'subject_id': subject_id,
                    'subject_name': subject_name,
                    'subject_type': subject_type,
                    'relation': relation,
                    'object_id': object_id,
                    'object_name': object_name,
                    'object_type': object_type,
                    'source': source,
                    'source_case': source_case,
                },
            )

        host_csv_path, load_csv_uri = CsvImportParser._write_standardized_csv(edge_rows.values())
        return ParsedImport(
            host_csv_path=host_csv_path,
            load_csv_uri=load_csv_uri,
            node_count=len(node_rows),
            edge_count=len(edge_rows),
            warnings=[],
            schema=schema_key,
        )

    @staticmethod
    async def _read_csv(file: UploadFile) -> tuple[list[str], list[dict[str, str]]]:
        content = await file.read()
        for encoding in ('utf-8-sig', 'utf-8', 'gbk'):
            try:
                text = content.decode(encoding)
                reader = csv.DictReader(StringIO(text))
                raw_headers = reader.fieldnames or []
                headers = [header.strip() for header in raw_headers if header is not None]
                rows = [{(key or '').strip(): (value or '').strip() for key, value in row.items()} for row in reader]
                return headers, rows
            except UnicodeDecodeError:
                continue
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{file.filename} 编码不支持，请使用 UTF-8 或 GBK')

    @staticmethod
    def _validate_headers(headers: list[str], filename: str) -> None:
        if headers != EXPECTED_HEADERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'{filename} 表头必须严格为 subject,relation,object',
            )

    @staticmethod
    def _normalize_schema(schema: str | None) -> str | None:
        schema_key = normalize_schema(schema)
        if schema_key is None:
            return None
        if get_schema_definition(schema_key) is None:
            allowed = ', '.join(get_available_schemas())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'不支持的 schema：{schema}。当前可选：{allowed}',
            )
        return schema_key

    @staticmethod
    def _require_cell(row: dict[str, str], field_name: str, index: int) -> str:
        value = (row.get(field_name) or '').strip()
        if not value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'CSV 第 {index} 行缺少 {field_name}')
        return value

    @staticmethod
    def _parse_entity(raw_value: str, field_name: str, index: int, schema: str | None) -> tuple[str, str]:
        match = ENTITY_PATTERN.match(raw_value.strip())
        if match is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'CSV 第 {index} 行 {field_name} 格式错误，必须为 名称(类型)',
            )

        name = ' '.join(match.group('name').strip().split())
        entity_type = normalize_entity_type(match.group('type').strip(), schema)
        if not name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'CSV 第 {index} 行 {field_name} 名称不能为空')
        if not entity_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'CSV 第 {index} 行 {field_name} 类型不能为空')
        if schema and not is_allowed_entity_type(entity_type, schema):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV 第 {index} 行存在不允许的实体类型：{entity_type}。schema `{schema}` 仅允许：{', '.join(get_entity_types(schema))}",
            )
        return name, entity_type

    @staticmethod
    def _build_scope(source: str, source_case: str) -> str:
        return hashlib.sha1(f'{source}::{source_case}'.encode('utf-8')).hexdigest()[:16]

    @staticmethod
    def _build_node_id(scope: str, name: str, entity_type: str) -> str:
        digest = hashlib.sha1(f'{scope}::{entity_type}::{name}'.encode('utf-8')).hexdigest()[:20]
        return f'{scope}::n::{digest}'

    @staticmethod
    def _build_relation_id(scope: str, subject_id: str, relation: str, object_id: str) -> str:
        digest = hashlib.sha1(f'{scope}::{subject_id}::{relation}::{object_id}'.encode('utf-8')).hexdigest()[:20]
        return f'{scope}::r::{digest}'

    @staticmethod
    def _write_standardized_csv(rows) -> tuple[str, str]:
        settings = get_settings()
        host_dir = Path(settings.neo4j_import_host_dir).expanduser()
        if not host_dir.is_absolute():
            host_dir = Path(__file__).resolve().parents[2] / host_dir
        host_dir.mkdir(parents=True, exist_ok=True)

        filename = f'import_{uuid4().hex}.csv'
        host_csv_path = host_dir / filename
        with host_csv_path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    'relation_id',
                    'subject_id',
                    'subject_name',
                    'subject_type',
                    'relation',
                    'object_id',
                    'object_name',
                    'object_type',
                    'source',
                    'source_case',
                ],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        return str(host_csv_path), f'file:///{filename}'
