from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaDefinition:
    key: str
    entity_types: tuple[str, ...]
    entity_label_aliases: dict[str, str]
    relation_rules: dict[str, tuple[str, str] | tuple[tuple[str, str], ...]]


TCM_ENTITY_TYPES = (
    "A医家",
    "B病名",
    "C证型",
    "D病因",
    "E病机",
)

TCM_ENTITY_LABEL_ALIASES = {
    "A医家": "A医家",
    "医家": "A医家",
    "Physician": "A医家",
    "B病名": "B病名",
    "病名": "B病名",
    "Disease Name": "B病名",
    "DiseaseName": "B病名",
    "C证型": "C证型",
    "证型": "C证型",
    "Syndrome Pattern": "C证型",
    "SyndromePattern": "C证型",
    "D病因": "D病因",
    "病因": "D病因",
    "Etiology": "D病因",
    "E病机": "E病机",
    "病机": "E病机",
    "Pathogenesis": "E病机",
}

TCM_RELATION_RULES = {
    "A医家-B病名": ("A医家", "B病名"),
    "A医家-C证型": ("A医家", "C证型"),
    "A医家-D病因": ("A医家", "D病因"),
    "A医家-E病机": ("A医家", "E病机"),
    "B病名-C证型": ("B病名", "C证型"),
    "B病名-D病因": ("B病名", "D病因"),
    "B病名-E病机": ("B病名", "E病机"),
    "C证型-D病因": ("C证型", "D病因"),
    "C证型-E病机": ("C证型", "E病机"),
    "D病因-E病机": ("D病因", "E病机"),
}

TCM_SCHEMA = SchemaDefinition(
    key="tcm",
    entity_types=TCM_ENTITY_TYPES,
    entity_label_aliases=TCM_ENTITY_LABEL_ALIASES,
    relation_rules=TCM_RELATION_RULES,
)

SCHEMA_DEFINITIONS = {
    TCM_SCHEMA.key: TCM_SCHEMA,
}

ENTITY_TYPES = TCM_SCHEMA.entity_types
ENTITY_LABEL_ALIASES = TCM_SCHEMA.entity_label_aliases
RELATION_RULES = TCM_SCHEMA.relation_rules
RELATION_TYPES = tuple(TCM_SCHEMA.relation_rules.keys())


def normalize_schema(value: str | None) -> str | None:
    cleaned = (value or "").strip().lower()
    return cleaned or None


def get_available_schemas() -> tuple[str, ...]:
    return tuple(SCHEMA_DEFINITIONS.keys())


def get_schema_definition(schema: str | None) -> SchemaDefinition | None:
    schema_key = normalize_schema(schema)
    if schema_key is None:
        return None
    return SCHEMA_DEFINITIONS.get(schema_key)


def normalize_entity_type(value: str | None, schema: str | None = None) -> str:
    cleaned = (value or "").strip()
    schema_definition = get_schema_definition(schema)
    if schema_definition is None:
        return cleaned
    return schema_definition.entity_label_aliases.get(cleaned, cleaned)


def is_allowed_entity_type(value: str | None, schema: str | None = None) -> bool:
    schema_definition = get_schema_definition(schema)
    if schema_definition is None:
        return True
    return normalize_entity_type(value, schema) in schema_definition.entity_types


def is_allowed_relation_type(value: str | None, schema: str | None = None) -> bool:
    schema_definition = get_schema_definition(schema)
    if schema_definition is None:
        return True
    return (value or "").strip() in schema_definition.relation_rules


def get_relation_types(schema: str | None = None) -> tuple[str, ...]:
    schema_definition = get_schema_definition(schema)
    if schema_definition is None:
        return ()
    return tuple(schema_definition.relation_rules.keys())


def get_entity_types(schema: str | None = None) -> tuple[str, ...]:
    schema_definition = get_schema_definition(schema)
    if schema_definition is None:
        return ()
    return schema_definition.entity_types


def relation_direction_matches(relation_type: str, source_type: str, target_type: str, schema: str | None = None) -> bool:
    schema_definition = get_schema_definition(schema)
    if schema_definition is None:
        return True
    rule = schema_definition.relation_rules.get((relation_type or "").strip())
    if not rule:
        return False
    if isinstance(rule[0], tuple):
        return (source_type, target_type) in rule
    return (source_type, target_type) == rule
