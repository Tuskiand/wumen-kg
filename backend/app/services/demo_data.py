from datetime import datetime
from uuid import uuid4

from app.schemas.admin import AuditRecord, DashboardStats, ImportTask, VersionRecord
from app.schemas.graph import GraphEdge, GraphNode


NODES = [
    GraphNode(id='doctor-001', name='薛雪', label='A医家', type='A医家', summary='吴门医家，擅长内风与痰证辨治。', source='吴门医案·卷一', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphNode(id='disease-001', name='中风', label='B病名', type='B病名', summary='以猝然昏仆、口眼㖞斜、半身不遂为主要表现。', source='吴门医案·卷一', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphNode(id='pattern-001', name='风痰闭阻证', label='C证型', type='C证型', summary='风痰闭阻经络，清窍不利。', source='吴门医案·卷一', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphNode(id='cause-001', name='风痰上扰', label='D病因', type='D病因', summary='外风引动痰浊，上蒙清窍。', source='吴门医案·卷一', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphNode(id='mechanism-001', name='痰阻清窍', label='E病机', type='E病机', summary='痰浊闭阻清窍，经络不畅。', source='吴门医案·卷一', source_cases=['中风'], source_batches=['吴门医案·卷一']),
]

EDGES = [
    GraphEdge(id='e1', source='doctor-001', target='disease-001', type='A医家-B病名', label='A医家-B病名', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e2', source='doctor-001', target='pattern-001', type='A医家-C证型', label='A医家-C证型', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e3', source='doctor-001', target='cause-001', type='A医家-D病因', label='A医家-D病因', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e4', source='doctor-001', target='mechanism-001', type='A医家-E病机', label='A医家-E病机', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e5', source='disease-001', target='pattern-001', type='B病名-C证型', label='B病名-C证型', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e6', source='disease-001', target='cause-001', type='B病名-D病因', label='B病名-D病因', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e7', source='disease-001', target='mechanism-001', type='B病名-E病机', label='B病名-E病机', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e8', source='cause-001', target='mechanism-001', type='D病因-E病机', label='D病因-E病机', source_cases=['中风'], source_batches=['吴门医案·卷一']),
    GraphEdge(id='e9', source='pattern-001', target='mechanism-001', type='C证型-E病机', label='C证型-E病机', source_cases=['中风'], source_batches=['吴门医案·卷一']),
]

IMPORTS = [
    ImportTask(
        id='import-20260309-01',
        name='第一批图谱导入',
        created_at='2026-03-09 09:30',
        status='completed',
        summary='节点 5 个，关系 9 条。',
        source_case='中风',
        source='吴门医案·卷一',
        created_nodes=5,
        merged_nodes=0,
        created_relations=9,
        deduplicated_relations=0,
    ),
    ImportTask(
        id='import-20260308-02',
        name='关系增量修正',
        created_at='2026-03-08 16:40',
        status='validating',
        summary='待校验关系 9 条。',
        source_case='中风',
        source='吴门医案·卷一',
    ),
]

VERSIONS = [
    VersionRecord(id='v1.0.0', name='一期基线数据', created_at='2026-03-09 10:00', status='published'),
    VersionRecord(id='v1.1.0-rc1', name='字段映射修订', created_at='2026-03-09 11:15', status='draft'),
]

AUDITS = [
    AuditRecord(id='audit-01', actor='admin', action='导入发布', target='v1.0.0', created_at='2026-03-09 10:05', result='成功'),
    AuditRecord(id='audit-02', actor='editor', action='编辑节点', target='disease-001', created_at='2026-03-09 10:36', result='成功'),
]

DASHBOARD = DashboardStats(node_count=5, edge_count=9, import_success_rate=98.4, last_publish_at='2026-03-09 10:05')


def append_audit(action: str, target: str, actor: str = 'admin', result: str = '成功') -> None:
    AUDITS.insert(
        0,
        AuditRecord(
            id=f'audit-{uuid4().hex[:8]}',
            actor=actor,
            action=action,
            target=target,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M'),
            result=result,
        ),
    )


def append_import_task(name: str, status: str, summary: str, **extra) -> ImportTask:
    task = ImportTask(
        id=f'import-{uuid4().hex[:12]}',
        name=name,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M'),
        status=status,
        summary=summary,
        **extra,
    )
    IMPORTS.insert(0, task)
    return task

