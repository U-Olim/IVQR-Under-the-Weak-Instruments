"""Read-only payload inventory; write diagnostics to a new external directory.

Usage: python -B scripts/audit_repository.py REPOSITORY OUTPUT_DIRECTORY
Git metadata is excluded from payload reports. Near-duplicate token overlap is
a screening measure, not a determination that research evidence is redundant.
"""
import collections
import csv
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
if out == root or root in out.parents:
    raise SystemExit('Write audit outputs outside the repository.')
out.mkdir(exist_ok=False)
tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=root, text=True).splitlines())
ignored = set(subprocess.check_output(['git', 'ls-files', '--others', '--ignored', '--exclude-standard'], cwd=root, text=True).splitlines())
rows = []
groups = collections.defaultdict(list)
texts = {}
for p in sorted(root.rglob('*')):
    if not p.is_file() or '.git' in p.relative_to(root).parts:
        continue
    rel = p.relative_to(root).as_posix()
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    rows.append(dict(path=rel, bytes=len(data), sha256=digest,
                     git_status='tracked' if rel in tracked else 'ignored' if rel in ignored else 'untracked'))
    groups[digest].append(rel)
    if p.suffix.lower() in {'.tex', '.bib', '.r', '.py', '.md', '.txt', '.yml', '.csv'} and len(data) < 250000:
        try:
            text = data.decode('utf-8-sig')
        except UnicodeDecodeError:
            continue
        texts[rel] = text
with (out/'inventory.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['path','bytes','sha256','git_status'])
    writer.writeheader(); writer.writerows(rows)
duplicates = [dict(sha256=h, paths=ps) for h, ps in groups.items() if len(ps)>1]
(out/'exact_duplicates.json').write_text(json.dumps(duplicates, indent=2), encoding='utf-8')
near = []
names = sorted(texts)
for i, a in enumerate(names):
    for b in names[i+1:]:
        x, y = texts[a], texts[b]
        if x == y or min(len(x),len(y)) < 100 or min(len(x),len(y))/max(len(x),len(y)) < .7:
            continue
        # Token multiset overlap is fast, flags related implementations and avoids
        # quadratic character matching on large numerical CSVs.
        cx = collections.Counter(re.findall(r'\w+',x.lower()))
        cy = collections.Counter(re.findall(r'\w+',y.lower()))
        score = 2*sum((cx & cy).values())/(sum(cx.values())+sum(cy.values()))
        if score >= .85:
            near.append(dict(first=a,second=b,token_overlap=round(score,6)))
(out/'near_duplicates.json').write_text(json.dumps(near,indent=2),encoding='utf-8')
edges = []; missing = []
for rel, text in texts.items():
    if not rel.startswith('article/') or not rel.endswith('.tex'):
        continue
    for cmd, name in re.findall(r'\\(input|include|includegraphics|addbibresource)(?:\[[^\]]*\])?\{([^}]+)\}', text):
        p = root/'article'/name
        if cmd in {'input','include'} and not p.suffix:
            p=p.with_suffix('.tex')
        edge=dict(source=rel, command=cmd, target=p.relative_to(root).as_posix(), exists=p.is_file())
        edges.append(edge)
        if not p.is_file(): missing.append(edge)
(out/'latex_dependencies.json').write_text(json.dumps(edges,indent=2),encoding='utf-8')
summary=dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),
             exact_groups=len(duplicates),redundant_instances=sum(len(d['paths'])-1 for d in duplicates),
             near_pairs=len(near),latex_edges=len(edges),missing_dependencies=missing,
             top_level=dict(collections.Counter(r['path'].split('/')[0] for r in rows)))
(out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
