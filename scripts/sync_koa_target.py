#!/usr/bin/env python3
"""Render an offline C0 final-system documentation snapshot into MkDocs.

No git clone, network, deployment or publication. This copy is a derived view;
source Markdown in the central repository and product-owner contracts remain primary.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/final-system'
REPO = 'https://github.com/Rejean-McCormick/kOA-Digital-Ecosystem'
LINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)]+)\)')

def target_location(relative: Path) -> Path:
    if relative.name == 'README.md':
        return relative.with_name('index.md')
    return relative

def path_url(rel: Path, ref: str) -> str:
    return f'{REPO}/blob/{quote(ref, safe="/")}/{quote(rel.as_posix(),safe="/")}'

def generate(source: Path, ref: str) -> dict[str, bytes]:
    source=source.resolve()
    if source.name != 'target' or not (source/'functional-chains/README.md').is_file():
        raise ValueError('Expected a central docs/target directory containing functional chains')
    central=source.parent.parent.resolve()
    source_files=[p for p in source.rglob('*') if p.is_file() and p.suffix in ('.md','.json')]
    mapped={p.resolve():target_location(p.relative_to(source)) for p in source_files}
    result={};provenance=[]
    for path in sorted(source_files):
        relative=path.relative_to(source)
        dest=mapped[path.resolve()]
        raw=path.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
        provenance.append({'source':'docs/target/'+relative.as_posix(),'destination':dest.as_posix(),'sha256':sha})
        if path.suffix=='.json':
            result[dest.as_posix()]=raw; continue
        text=raw.decode('utf8')
        def replace(m):
            title, uri=m.groups()
            if uri.startswith(('https://','http://','mailto:','#','data:')): return m.group(0)
            plain,sep,anchor=uri.partition('#')
            if not plain:return m.group(0)
            target=(path.parent/unquote(plain)).resolve()
            if target in mapped:
                local=mapped[target]
                from os.path import relpath
                url=Path(relpath(local, dest.parent)).as_posix()
            else:
                if not target.is_relative_to(central) or not target.exists():
                    raise ValueError(f'Broken or unsafe source link in {relative}: {uri}')
                url=path_url(target.relative_to(central),ref)
            return f'[{title}]({url+("#"+anchor if sep else "")})'
        text=LINK.sub(replace,text)
        preface=f'> **Final-system design mirror** · Canonical source: [`docs/target/{relative.as_posix()}`]({path_url(path.relative_to(central),ref)}) · SHA-256 `{sha}`. Design intent is not deployment proof.\n\n'
        result[dest.as_posix()]=(preface+text).encode('utf8')
    count=sum(k.startswith('functional-chains/chains/FC-') and k.endswith('.md') for k in result)
    if count !=24:raise ValueError(f'Expected 24 chain pages, found {count}')
    m={'format':'koa.docs-portal-final-mirror.v1','status':'DERIVED_TARGET_DESIGN_NOT_DEPLOYMENT','source_repo':REPO,'source_ref':ref,'pages':provenance}
    result['_MANIFEST.json']=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    return result

def verify_bundle(out: Path=OUT) -> list[str]:
    issues=[]
    try: manifest=json.loads((out/'_MANIFEST.json').read_text(encoding='utf8'))
    except (OSError,ValueError) as e:return [f'Missing/invalid bundle manifest: {e}']
    if manifest.get('format')!='koa.docs-portal-final-mirror.v1' or manifest.get('status')!='DERIVED_TARGET_DESIGN_NOT_DEPLOYMENT':
        issues.append('Mirror has wrong schema or evidence level')
    for row in manifest.get('pages',[]):
        path=out/row['destination']
        if not path.is_file():issues.append(f'Missing {path}');continue
        if path.suffix=='.md':
            text=path.read_text(encoding='utf8')
            if row.get('sha256') not in '\n'.join(text.splitlines()[:3]):
                issues.append(f'No source hash visible in {path}')
        else:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
                issues.append(f'Mismatched raw source {path}')
    count=sum(x['destination'].startswith('functional-chains/chains/FC-') for x in manifest.get('pages',[]))
    if count!=24:issues.append(f'Expected 24 chain pages, got {count}')
    return issues

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dir',type=Path,help='Local C0 docs/target root for a deterministic mirror')
    parser.add_argument('--source-ref',default='main',help='Source branch or pinned commit for attribution URL; ZIPs cannot prove remote HEAD')
    parser.add_argument('--output-dir',type=Path,default=OUT)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true');mode.add_argument('--verify-bundle',action='store_true')
    a=parser.parse_args()
    try:
        if a.verify_bundle:
            issues=verify_bundle(a.output_dir)
        else:
            if not a.source_dir:parser.error('--source-dir required for --write/--check')
            rendered=generate(a.source_dir,a.source_ref)
            if a.write:
                a.output_dir.mkdir(parents=True,exist_ok=True)
                for f in a.output_dir.rglob('*'):
                    if f.is_file():f.unlink()
                for path,data in rendered.items():
                    dest=a.output_dir/path; dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
                issues=verify_bundle(a.output_dir)
            else:
                issues=[f'Missing/stale: {p}' for p,bytes_ in rendered.items() if not (a.output_dir/p).is_file() or (a.output_dir/p).read_bytes()!=bytes_]
                issues+=verify_bundle(a.output_dir)
        if issues:
            print('\n'.join('FAIL: '+m for m in issues));return 1
        print('PASS: final-system documentation mirror validated');return 0
    except (ValueError,OSError) as e:print('FAIL:',e);return 1
if __name__=='__main__':raise SystemExit(main())
