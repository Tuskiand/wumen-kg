import os
import csv
import re
from collections import OrderedDict

def parse_entity(text):
    """从形如 '元气积伤，内虚暴脱(病机)' 的字符串中提取名称和类型。"""
    text = text.strip()
    match = re.match(r'^(.*)\((.*)\)$', text)
    if match:
        name = match.group(1).strip()
        etype = match.group(2).strip()
        return name, etype
    else:
        return text, 'unknown'

def convert_file(input_file, output_nodes, output_rels):
    """转换单个关系文件，生成 nodes 和 rels 文件。"""
    entity_map = {}          # (name, type) -> id
    type_counter = {}        # type -> 计数

    def get_entity_id(name, etype):
        key = (name, etype)
        if key not in entity_map:
            counter = type_counter.get(etype, 0) + 1
            type_counter[etype] = counter
            entity_id = f"{etype}_{counter}"
            entity_map[key] = entity_id
        return entity_map[key]

    # 读取关系文件
    rows = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = [col.strip() for col in reader.fieldnames]
        reader = csv.DictReader(f, fieldnames=fieldnames)
        rows = list(reader)

    # 收集所有实体并分配ID
    for row in rows:
        subj = row['subject'].strip()
        obj = row['object'].strip()
        subj_name, subj_type = parse_entity(subj)
        obj_name, obj_type = parse_entity(obj)
        get_entity_id(subj_name, subj_type)
        get_entity_id(obj_name, obj_type)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_nodes), exist_ok=True)

    # 写入 nodes.csv
    with open(output_nodes, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'type', 'label'])
        for (name, etype), eid in entity_map.items():
            writer.writerow([eid, name, etype, etype])

    # 写入 rels.csv
    with open(output_rels, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['start_id', 'end_id', 'type'])
        for row in rows:
            subj = row['subject'].strip()
            obj = row['object'].strip()
            relation = row['relation'].strip()
            subj_name, subj_type = parse_entity(subj)
            obj_name, obj_type = parse_entity(obj)
            start_id = get_entity_id(subj_name, subj_type)
            end_id = get_entity_id(obj_name, obj_type)
            writer.writerow([start_id, end_id, relation])

    print(f"处理完成: {input_file} → {output_nodes} ({len(entity_map)} 节点), {output_rels} ({len(rows)} 关系)")

def batch_convert(input_dir='.', pattern='_relations.csv', output_dir='output'):
    """
    批量转换目录下所有符合 pattern 的关系文件，生成文件到 output_dir 中。
    
    Args:
        input_dir: 输入文件所在目录，默认为当前目录
        pattern: 文件名匹配模式，默认为 '_relations.csv'
        output_dir: 输出目录，默认为当前目录下的 'output' 文件夹
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(pattern):
            base = filename[:-len(pattern)]   # 去掉后缀得到前缀
            input_path = os.path.join(input_dir, filename)
            output_nodes = os.path.join(output_dir, f'nodes_{base}.csv')
            output_rels = os.path.join(output_dir, f'rels_{base}.csv')
            convert_file(input_path, output_nodes, output_rels)

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    batch_convert(
        input_dir=os.path.join(base_dir, '1'),
        pattern='_relations.csv',
        output_dir=os.path.join(base_dir, 'output'),
    )