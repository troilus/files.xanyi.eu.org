#!/usr/bin/env python3
import os
import json
from datetime import datetime, timezone

EXCLUDE_DIRS = {'.git', '.github', '__pycache__'}
EXCLUDE_FILES = {'files.json', 'generate-index.py'}


def build_tree(dir_path, rel_path=""):
    entries = []
    try:
        names = sorted(os.listdir(dir_path))
    except PermissionError:
        return entries

    for name in names:
        if name.startswith('.') or name in EXCLUDE_DIRS or name in EXCLUDE_FILES:
            continue
        full_path = os.path.join(dir_path, name)
        entry_rel = os.path.join(rel_path, name).replace('\\', '/') if rel_path else name

        try:
            st = os.stat(full_path)
            mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
        except OSError:
            continue

        if os.path.isdir(full_path):
            children = build_tree(full_path, entry_rel)
            entries.append({
                'name': name,
                'type': 'dir',
                'path': entry_rel,
                'mtime': mtime,
                'children': children,
            })
        else:
            entries.append({
                'name': name,
                'type': 'file',
                'path': entry_rel,
                'size': st.st_size,
                'mtime': mtime,
            })

    return entries


def count_files(tree):
    return sum(1 for e in tree if e['type'] == 'file') + sum(
        count_files(e['children']) for e in tree if e['type'] == 'dir'
    )


if __name__ == '__main__':
    repo_root = os.path.dirname(os.path.abspath(__file__))
    tree = build_tree(repo_root)
    total = count_files(tree)

    output = {
        'updated': datetime.now(timezone.utc).isoformat(),
        'fileCount': total,
        'tree': tree,
    }

    out_path = os.path.join(repo_root, 'files.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"OK — {total} files indexed → files.json")
