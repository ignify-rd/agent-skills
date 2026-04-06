#!/usr/bin/env python3
"""Convert test design .md to .xmind file."""
import re
import json
import sys
import zipfile
import uuid
import argparse
import os


def gen_id():
    return uuid.uuid4().hex[:20]


def parse_md_to_tree(md_text):
    lines = md_text.split('\n')
    root = None
    stack = []

    for line in lines:
        m = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            node = {'title': title, 'children': []}

            if level == 1:
                root = node
                stack = [(level, node)]
            else:
                while stack and stack[-1][0] >= level:
                    stack.pop()
                if stack:
                    stack[-1][1]['children'].append(node)
                stack.append((level, node))

    return root


def build_content_json(root_node, sheet_title):
    def build_topic(node):
        t = {'id': gen_id(), 'title': node['title']}
        children = node.get('children', [])
        if children:
            t['children'] = {'attached': [build_topic(c) for c in children]}
        return t

    root_topic = build_topic(root_node)
    root_topic['structureClass'] = 'org.xmind.ui.map.unbalanced'

    sheet = {
        'id': gen_id(),
        'title': sheet_title,
        'rootTopic': root_topic,
        'topicPositioning': 'fixed',
    }
    return json.dumps([sheet], ensure_ascii=False, indent=2)


def create_xmind(md_path, output_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    root = parse_md_to_tree(md_text)
    if not root:
        print("ERROR: No headings found in markdown", file=sys.stderr)
        sys.exit(1)

    content_json = build_content_json(root, root['title'])
    metadata = json.dumps({'creator': {'name': 'QC Beast', 'version': '1.0'}})
    manifest = json.dumps({'file-entries': {'content.json': {}, 'metadata.json': {}}})

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('content.json', content_json)
        zf.writestr('metadata.json', metadata)
        zf.writestr('META-INF/manifest.json', manifest)

    content = json.loads(content_json)
    def count_nodes(t):
        n = 1
        for c in t.get('children', {}).get('attached', []):
            n += count_nodes(c)
        return n
    total = count_nodes(content[0]['rootTopic'])
    print(f"XMind created: {output_path} ({total} nodes)")
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Input .md file')
    parser.add_argument('--output', help='Output .xmind file (default: same name as input)')
    args = parser.parse_args()

    output = args.output or args.input.replace('.md', '.xmind')
    create_xmind(args.input, output)
