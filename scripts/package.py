#!/usr/bin/env python3
"""Build an allowlisted distributable; never include local media/runtime secrets."""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
ALLOWED={'.md','.py','.cjs','.js','.html','.json','.yaml','.yml','.txt'}
# New public files require explicit review before inclusion.
PUBLIC_FILES=frozenset(('.gitignore', 'LICENSE', 'README.md', 'SKILL.md', 'THIRD_PARTY_NOTICES.md', 'VALIDATION.md', 'agents/openai.yaml', 'assets/motion/pwf-motion.js', 'examples/gallery.html', 'examples/recipe-gallery.html', 'examples/whitepaper-demo/build.py', 'examples/whitepaper-demo/index.tpl.html', 'examples/whitepaper-demo/narration.txt', 'examples/whitepaper-demo/timing.json', 'examples/whitepaper-demo/whitepaper.md', 'references/content.md', 'references/fonts.md', 'references/motion.md', 'references/origin.md', 'references/product-case.md', 'references/recipe-sources.md', 'references/recipes.md', 'references/release.md', 'references/runtime.md', 'references/verification.md', 'requirements.txt', 'scripts/film.py', 'scripts/fonts.py', 'scripts/package.py', 'scripts/project.py', 'scripts/verify_recipes.cjs', 'scripts/voice_worker.py'))
SENSITIVE_PATTERNS = {
    'personal path': r'/(?:Users|home)/[^/\s]+/|[A-Za-z]:\\Users\\[^\\\s]+',
    'email': r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
    'phone': r'(?<!\d)(?:\+?86[ -]?)?1[3-9]\d{9}(?!\d)',
    'private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'API credential': r'\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})',
    'environment secret': r'(?im)^\s*[A-Z][A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY)\s*=\s*[^\s#]{8,}',
}
def sensitive_categories(text):
    return [name for name, pattern in SENSITIVE_PATTERNS.items() if re.search(pattern,text)]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.out.exists():raise SystemExit('Refusing to overwrite package')
    items=[]
    for f in sorted(root.rglob('*')):
        if f.is_symlink():raise SystemExit(f'Symlink not allowed: {f.relative_to(root)}')
        if not f.is_file() or '__pycache__' in f.parts:continue
        rel=f.relative_to(root)
        if rel.as_posix() not in PUBLIC_FILES:raise SystemExit(f'File needs public-content review: {rel}')
        if f.name in ('runtime.json','.env') or any(x in rel.parts for x in ('node_modules','.venv','.git','.hyperframes','output','renders')):raise SystemExit(f'Private/generated path: {rel}')
        if f.suffix not in ALLOWED and f.name not in ('LICENSE','.gitignore'):raise SystemExit(f'Unapproved file type: {rel}')
        data=f.read_bytes();text=data.decode('utf-8')
        findings=sensitive_categories(text)
        if findings:raise SystemExit(f'Possible sensitive content in {rel}: {", ".join(findings)}')
        items.append((rel,data))
    a.out.parent.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(a.out,'w',zipfile.ZIP_DEFLATED) as z:
        for rel,data in items:
            info=zipfile.ZipInfo('product-whitepaper-film/'+rel.as_posix(),date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            z.writestr(info,data)
    report={'archive':a.out.name,'file_count':len(items),'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'files':[{'path':str(r),'sha256':hashlib.sha256(d).hexdigest()} for r,d in items],
            'scope':'Explicit public-file list and sensitive-pattern scan; manual review still required.'}
    a.out.with_suffix('.manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('archive','file_count','sha256')},ensure_ascii=False))
if __name__=='__main__':main()
