#!/usr/bin/env python3
"""Local runtime bridge: doctor, configure, example, check, render, voice, mux.
Calls separately installed tools. No weights, voices or credentials bundled.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = Path.home()/'.config/product-whitepaper-film/runtime.json'

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def read_config(path):
    if not path.is_file(): raise ValueError(f'Runtime not configured: {path}. Run configure first.')
    cfg=json.loads(path.read_text())
    cmd=cfg.get('hyperframes_command')
    if not isinstance(cmd,list) or not cmd or any(not isinstance(x,str) for x in cmd):
        raise ValueError('hyperframes_command must be a nonempty argv array')
    return cfg

def run(argv, cwd=None, timeout=600, log=None):
    # argv, never shell=True; paths and narration are not shell code.
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('w') as out:
            result=subprocess.run(argv,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
        if result.returncode: raise ValueError(f'Command failed ({result.returncode}); see {log}')
        return None
    return subprocess.run(argv,cwd=cwd,check=True,timeout=timeout)

def fresh(path):
    if path.exists(): raise ValueError(f'Refusing to overwrite {path}')
    path.parent.mkdir(parents=True, exist_ok=True)

def probe(path):
    ffprobe=shutil.which('ffprobe')
    if not ffprobe: raise ValueError('ffprobe is missing')
    r=subprocess.run([ffprobe,'-v','error','-show_entries','stream=codec_type,width,height,sample_rate:format=duration','-of','json',str(path)],capture_output=True,text=True,timeout=30,check=True)
    return json.loads(r.stdout)

def doctor(cfg, verify):
    result={'tools':{},'voice':{},'note':'File/module availability only; new speech remains pending listening.'}
    for name in ('node','npx','ffmpeg','ffprobe'):
        result['tools'][name]=shutil.which(name)
    gsap=Path(cfg.get('gsap',''))
    result['tools']['gsap_file']=str(gsap) if gsap.is_file() else None
    if verify:
        r=subprocess.run(cfg['hyperframes_command']+['--version'],capture_output=True,text=True,timeout=60)
        result['tools']['hyperframes']={'ok':r.returncode==0,'version':r.stdout.strip(),'error':r.stderr[-800:] if r.returncode else None}
    v=cfg.get('voice',{})
    for k in ('python','model','profile'):
        f=Path(v.get(k,''));result['voice'][k+'_exists']=f.exists() and (f.is_file() if k!='model' else f.is_dir())
    if result['voice']['profile_exists']:
        f=Path(v['profile']);p=json.loads(f.read_text());ref=f.parent/p['ref_audio']
        result['voice']['reference_hash_matches']=ref.is_file() and hashlib.sha256(ref.read_bytes()).hexdigest()==p['reference_sha256']
    if verify and result['voice']['python_exists']:
        r=subprocess.run([v['python'],'-c','import mlx.core,mlx_audio,numpy'],capture_output=True,text=True,timeout=60)
        result['voice']['modules_import']=r.returncode==0
        if r.returncode:result['voice']['module_error']=r.stderr[-800:]
    result['ready_for_example']=all(result['tools'].get(x) for x in ('node','npx','ffmpeg','ffprobe','gsap_file')) and (not verify or result['tools']['hyperframes']['ok'])
    result['ready_for_voice']=all(result['voice'].get(x) for x in ('python_exists','model_exists','profile_exists','reference_hash_matches')) and (not verify or result['voice'].get('modules_import',False))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['ready_for_example'] else 1

def example(cfg, root, fonts, template="gallery") :
    if not Path(cfg.get('gsap','')).is_file():raise ValueError('Configured GSAP file is missing')
    fresh(root)
    run([sys.executable,str(SKILL/'scripts/project.py'),'init',str(root)])
    film=root/'film';assets=film/'assets';assets.mkdir(parents=True)
    shutil.copy2(SKILL/'examples'/('recipe-gallery.html' if template=='recipes' else 'gallery.html'),film/'index.html')
    shutil.copy2(SKILL/'assets/motion/pwf-motion.js',assets/'pwf-motion.js')
    shutil.copy2(cfg['gsap'],assets/'gsap.min.js')
    text=(film/'index.html').read_text()
    (root/'chars.txt').write_text(''.join(sorted(set(c for c in text if ord(c)>0x2e80))))
    dump(film/'package.json',{'name':'pwf-example','private':True,'type':'module'})
    dump(film/'hyperframes.json',{'paths':{'assets':'assets'},'authoringSkill':'product-whitepaper-film'})
    (root/'assets/SOURCES.md').write_text('Synthetic demonstration; no actual product claims. GSAP is copied from the configured local runtime, not licensed by this Skill. Noto webfonts, when fetched, retain SIL OFL.\n')
    if fonts:
        run([sys.executable,str(SKILL/'scripts/fonts.py'),'--html',str(film/'index.html'),'--out',str(assets/'fonts'),'--download'],timeout=180)
    else:print('Fonts not fetched: run fonts before rendering Chinese text.')
    print(f'Example ready: {film}')

def check(cfg, film):
    report=film.parent/'quality/hyperframes-check.json';report.parent.mkdir(exist_ok=True,parents=True)
    r=subprocess.run(cfg['hyperframes_command']+['check','--json'],cwd=film,capture_output=True,text=True,timeout=180)
    report.write_text(r.stdout)
    if r.returncode:raise ValueError(f'HyperFrames check failed: {r.stderr[-500:]}; see {report}')
    try:
        data=json.loads(r.stdout)
    except ValueError:raise ValueError(f'Cannot parse check output; see {report}')
    errors=[k for k,v in data.items() if isinstance(v,dict) and v.get('errorCount',0)>0]
    if errors or data.get('ok') is False:raise ValueError(f'Check errors in {errors}; see {report}')
    print(f'Technical check completed; review warnings: {report}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('configure');c.add_argument('--gsap',required=True,type=Path);c.add_argument('--hyperframes-command',required=True,help='JSON argv array, preferably an installed or cached version')
    c.add_argument('--tts-python',type=Path);c.add_argument('--model',type=Path);c.add_argument('--voice-profile',type=Path)
    d=sub.add_parser('doctor');d.add_argument('--verify',action='store_true')
    e=sub.add_parser('example');e.add_argument('project',type=Path);e.add_argument('--fetch-fonts',action='store_true');e.add_argument('--template',choices=('gallery','recipes'),default='gallery')
    f=sub.add_parser('fonts');f.add_argument('project',type=Path)
    for action in ('check','render','preview'):
        q=sub.add_parser(action);q.add_argument('film',type=Path)
        if action=='render':q.add_argument('--out',required=True,type=Path)
        if action=='preview':q.add_argument('--port',type=int,default=3040)
    v=sub.add_parser('voice');v.add_argument('--text-file',required=True,type=Path);v.add_argument('--out',required=True,type=Path)
    m=sub.add_parser('mux');m.add_argument('--video',required=True,type=Path);m.add_argument('--audio',required=True,type=Path);m.add_argument('--out',required=True,type=Path);m.add_argument('--listening-review',type=Path);m.add_argument('--preview-unreviewed',action='store_true',help='Create a listening preview, never a speech-approved final')
    a=p.parse_args()
    try:
        if a.command=='configure':
            fresh(a.config)
            voice_args=[a.tts_python,a.model,a.voice_profile]
            if any(voice_args) and not all(voice_args):raise ValueError('Provide all three voice paths together')
            cmd=json.loads(a.hyperframes_command)
            if not isinstance(cmd,list) or not cmd or any(not isinstance(x,str) for x in cmd):raise ValueError('hyperframes command must be a nonempty JSON argv array')
            cfg={'gsap':str(a.gsap.resolve()),'hyperframes_command':cmd}
            if all(voice_args):cfg['voice']={k:str(v.absolute()) for k,v in zip(('python','model','profile'),voice_args)}
            dump(a.config,cfg);print(f'Local config saved: {a.config}');return 0
        cfg=read_config(a.config)
        if a.command=='doctor':return doctor(cfg,a.verify)
        if a.command=='example':example(cfg,a.project.resolve(),a.fetch_fonts,a.template)
        elif a.command=='fonts':
            root=a.project.resolve();run([sys.executable,str(SKILL/'scripts/fonts.py'),'--html',str(root/'film/index.html'),'--out',str(root/'film/assets/fonts'),'--download'],timeout=180)
        elif a.command=='check':check(cfg,a.film.resolve())
        elif a.command=='preview':run(cfg['hyperframes_command']+['preview','--port',str(a.port)],cwd=a.film.resolve(),timeout=60)
        elif a.command=='render':
            film=a.film.resolve();out=a.out.resolve();fresh(out);check(cfg,film)
            run(cfg['hyperframes_command']+['render','.', '-q','high','--fps','30','-o',str(out)],cwd=film,log=film.parent/'quality/render.log')
            info=probe(out)
            if not any(s.get('codec_type')=='video' for s in info.get('streams',[])):raise ValueError('Renderer output has no video stream')
            run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])
            dump(out.with_suffix('.probe.json'),info);print(out)
        elif a.command=='voice':
            v=cfg.get('voice',{})
            if not all(v.get(k) for k in ('python','model','profile')):raise ValueError('Local voice has not been configured; no voice fallback is permitted')
            out=a.out.resolve();fresh(out)
            run([v['python'],str(SKILL/'scripts/voice_worker.py'),'--model',v['model'],'--profile',v['profile'],
                 '--text-file',str(a.text_file.resolve()),'--out',str(out)],timeout=600,log=out.with_suffix('.generation.log'))
            print(f'Generated local voice, pending listening: {out}')
        elif a.command=='mux':
            out=a.out.resolve();fresh(out);vi=probe(a.video);au=probe(a.audio)
            duration=float(vi['format']['duration']);audio_duration=float(au['format']['duration'])
            side=a.audio.with_suffix('.voice.json');speech=json.loads(side.read_text()) if side.is_file() else {}
            if a.listening_review:
                review=json.loads(a.listening_review.read_text())
                if review.get('status')!='listened_complete' or review.get('audio_sha256')!=hashlib.sha256(a.audio.read_bytes()).hexdigest() or not review.get('notes'):
                    raise ValueError('Listening review must match this audio hash and include actual completion notes')
                speech={**speech,'status':'listened_complete'}
            if speech.get('status')=='pending-listening' and not a.preview_unreviewed:
                raise ValueError('New speech is pending listening. Use --preview-unreviewed only for a review sample, or supply a verified listening record.')
            if audio_duration>duration+.025:raise ValueError('Audio exceeds picture duration; extend the picture, do not truncate speech')
            if not any(s.get('codec_type')=='audio' for s in au.get('streams',[])):raise ValueError('Audio input has no audio stream')
            run(['ffmpeg','-y','-v','error','-i',str(a.video.resolve()),'-i',str(a.audio.resolve()),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-shortest','-movflags','+faststart',str(out)])
            run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])
            dump(out.with_suffix('.probe.json'),probe(out))
            dump(out.with_suffix('.review.json'),{'speech_status':speech.get('status','source-review-not-recorded'),'preview_unreviewed':a.preview_unreviewed,'audio_sha256':hashlib.sha256(a.audio.read_bytes()).hexdigest()})
            print(out)
        return 0
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
