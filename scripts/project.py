#!/usr/bin/env python3
"""Create non-overwriting film records; check traceability, timing and evidence.
No renderer, network, media generation or subjective approval is performed.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess

CHECKS = ('facts', 'motion', 'readability', 'sync', 'audio', 'playback')

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def init(root):
    root.mkdir(parents=True, exist_ok=False)
    (root/'assets').mkdir()
    (root/'output').mkdir()
    (root/'brief.md').write_text('# 产品宣传视频任务\n\n受众：待确认\n产品定位：待提炼\n核心诉求：待提炼\n交付阶段：内容对齐\n时长与渠道：待确定\n已确认内容：无\n音色与配乐：按会话授权选择\n', encoding='utf-8')
    write_json(root/'sources.json', {'sources': [], 'assets': []})
    write_json(root/'claims.json', {'claims': []})
    write_json(root/'shots.json', {'shots': []})
    write_json(root/'review.json', {'video': None, 'checks': [
        {'id': k, 'status': 'pending', 'evidence': [], 'note': ''} for k in CHECKS]})
    print(f'Created {root}')

def check(root, release=False):
    errors, pending = [], []
    def need(condition, message):
        if not condition:
            errors.append(message)
    def path_of(value):
        p = Path(value)
        return p if p.is_absolute() else root/p
    def file_exists(value):
        return isinstance(value, str) and bool(value.strip()) and path_of(value).is_file()
    def read(name, key):
        try:
            d = json.loads((root/name).read_text(encoding='utf-8'))
            if not isinstance(d, dict) or not isinstance(d.get(key), list):
                raise ValueError(f'{key} must be an array')
            return d
        except (OSError, ValueError) as exc:
            errors.append(f'{name}: {exc}')
            return {key: []}
    def index(items, label):
        out = {}
        for item in items:
            if not isinstance(item, dict):
                errors.append(f'{label}: entry must be an object')
                continue
            ident = item.get('id')
            if not isinstance(ident, str) or not ident.strip():
                errors.append(f'{label}: nonempty id required')
                continue
            need(ident not in out, f'{label}: duplicate id {ident}')
            out[ident] = item
        return out
    def refs(item, key, pool, label, required=False):
        value = item.get(key, [])
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            errors.append(f'{label}: {key} must be an array of ids')
            return []
        need(not required or bool(value), f'{label}: {key} cannot be empty')
        for ident in value:
            need(ident in pool, f'{label}: unknown {key} {ident}')
        return value
    def number(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)

    data = read('sources.json', 'sources')
    sources = index(data['sources'], 'source')
    raw_assets = data.get('assets', [])
    if not isinstance(raw_assets, list):
        errors.append('assets must be an array')
        raw_assets = []
    assets = index(raw_assets, 'asset')
    claims = index(read('claims.json', 'claims')['claims'], 'claim')
    shots = index(read('shots.json', 'shots')['shots'], 'shot')
    review = read('review.json', 'checks')
    if not sources: pending.append('no sources recorded')
    if not claims: pending.append('no claims recorded')
    if not shots: pending.append('no shots recorded')
    for ident, item in sources.items():
        need(bool(item.get('title')), f'{ident}: source title required')
        need(bool(item.get('url') or item.get('path')), f'{ident}: source path or url required')
        if item.get('path'): need(file_exists(item['path']), f'{ident}: source file missing')
    for ident, item in assets.items():
        need(item.get('source_id') in sources, f'{ident}: unknown source_id')
        need(item.get('status') in ('usable', 'placeholder', 'missing'), f'{ident}: invalid asset status')
        if item.get('status') == 'usable':
            need(file_exists(item.get('path')), f'{ident}: usable asset file missing')
        elif any(isinstance(sh, dict) and isinstance(sh.get('asset_ids'), list) and ident in sh['asset_ids'] for sh in shots.values()):
            pending.append(f'{ident}: used asset is {item.get("status")}')
    for ident, item in claims.items():
        refs(item, 'source_ids', sources, ident, True)
        need(bool(item.get('text')) and bool(item.get('locator')), f'{ident}: claim text and locator required')
        need(item.get('status') in ('supported', 'planned', 'unverified'), f'{ident}: invalid claim status')
    ranges = []
    for ident, item in shots.items():
        a, b = item.get('start'), item.get('end')
        valid = number(a) and number(b) and 0 <= a < b
        need(valid, f'{ident}: invalid start/end')
        used = refs(item, 'claim_ids', claims, ident, not bool(item.get('nonfactual_reason')))
        refs(item, 'asset_ids', assets, ident)
        need(bool(item.get('narration') or item.get('silent_reason')), f'{ident}: narration or silent_reason required')
        for c in used:
            if c in claims and claims[c].get('status') == 'unverified':
                pending.append(f'{ident}: uses unverified claim {c}')
            if c in claims and claims[c].get('status') == 'planned':
                need(item.get('planning_disclosed') is True, f'{ident}: planned claim must be disclosed in narration/copy')
        events = item.get('events', [])
        need(isinstance(events, list) and bool(events), f'{ident}: content events required')
        if isinstance(events, list):
            for e in events:
                if not isinstance(e, dict):
                    errors.append(f'{ident}: event must be an object')
                    continue
                t = e.get('at')
                need(valid and number(t) and a <= t < b, f'{ident}: event outside shot')
                need(all(isinstance(e.get(k), str) and e[k].strip() for k in ('kind','cue','meaning')),
                     f'{ident}: event kind/cue/meaning required')
        hold = item.get('read_hold')
        if hold is not None:
            need(isinstance(hold, dict) and valid and number(hold.get('start')) and number(hold.get('end'))
                 and a <= hold['start'] < hold['end'] <= b, f'{ident}: invalid reading hold')
        if valid: ranges.append((a, b, ident))
    ranges.sort()
    for prior, following in zip(ranges, ranges[1:]):
        if following[0] < prior[1]:
            # Crossfades are valid when explicitly described, not universally banned.
            desc = shots[following[2]].get('overlap_reason')
            need(bool(desc), f'{following[2]}: overlapping shot needs overlap_reason')
    checks = index(review['checks'], 'review')
    for ident in CHECKS:
        item = checks.get(ident)
        if not item:
            pending.append(f'{ident}: review missing')
            continue
        status = item.get('status')
        need(status in ('pass','fail','pending','not_applicable'), f'{ident}: invalid review status')
        if status == 'fail': errors.append(f'{ident}: review failed: {item.get("note", "")}')
        if status == 'pending': pending.append(f'{ident}: review pending')
        if status == 'not_applicable': need(bool(item.get('note')), f'{ident}: not_applicable needs reason')
        evidence = item.get('evidence', [])
        need(isinstance(evidence, list), f'{ident}: evidence must be file path array')
        if status == 'pass':
            need(isinstance(evidence, list) and bool(evidence), f'{ident}: passed review needs evidence')
            if isinstance(evidence, list):
                for f in evidence: need(file_exists(f), f'{ident}: evidence file missing: {f}')
    video = review.get('video')
    if release:
        need(file_exists(video), 'release video file missing')
        if file_exists(video):
            probe = shutil.which('ffprobe')
            need(bool(probe), 'ffprobe is needed for release structure check')
            if probe:
                try:
                    r = subprocess.run([probe, '-v','error','-show_entries','stream=codec_type,width,height:format=duration',
                                        '-of','json',str(path_of(video))], capture_output=True, text=True, timeout=30, check=True)
                    info = json.loads(r.stdout)
                    need(any(s.get('codec_type') == 'video' for s in info.get('streams', [])), 'no video stream')
                    need(float(info.get('format', {}).get('duration', 0)) > 0, 'video has no positive duration')
                except (subprocess.SubprocessError, ValueError) as exc:
                    errors.append(f'video probe failed: {exc}')
    report = {'record_errors': errors, 'pending': pending,
              'record_check': 'ready' if not errors and not pending else 'incomplete',
              'scope': 'Record integrity only; facts, motion quality and listening require actual review.'}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors or (release and pending) else 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init').add_argument('project', type=Path)
    c = sub.add_parser('check')
    c.add_argument('project', type=Path)
    c.add_argument('--release', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'init': init(args.project.resolve()); return 0
        return check(args.project.resolve(), args.release)
    except FileExistsError:
        parser.exit(2, 'Refusing to overwrite an existing project directory.\n')
    except OSError as exc:
        parser.exit(2, f'{exc}\n')

if __name__ == '__main__':
    raise SystemExit(main())
