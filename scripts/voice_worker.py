#!/usr/bin/env python3
"""Run only in the configured local MLX/Qwen TTS environment. No auto-download."""
import argparse, hashlib, importlib.metadata, json, os
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('model','profile','text-file','out'):p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise ValueError('Refusing to overwrite speech')
    if not a.model.is_dir():raise ValueError('Local model directory is missing; no download fallback')
    profile=json.loads(a.profile.read_text());ref=a.profile.parent/profile['ref_audio']
    digest=hashlib.sha256(ref.read_bytes()).hexdigest()
    if digest!=profile['reference_sha256']:raise ValueError('Voice reference hash changed; do not reuse previous approval')
    text=a.text_file.read_text().strip()
    if not text or len(text)>1000:raise ValueError('Provide one nonempty narration segment, at most 1000 characters')
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    import numpy as np
    import mlx.core as mx
    from mlx_audio.tts.utils import load_model
    from mlx_audio.audio_io import write
    from mlx_audio.utils import load_audio
    mx.set_cache_limit(256*1024*1024);mx.random.seed(42)
    model=load_model(str(a.model));reference=load_audio(str(ref),sample_rate=model.sample_rate)
    opts=dict(text=text,ref_audio=reference,ref_text=profile['ref_text'],language='Chinese',temperature=.65,
              max_tokens=3600,repetition_penalty=1.1,top_p=.95,stream=False,verbose=False)
    chunks=[]
    for result in model._generate_icl(**opts):chunks.append(np.asarray(result.audio));sr=result.sample_rate
    if not chunks:raise ValueError('No audio returned')
    x=np.concatenate(chunks)
    if not np.isfinite(x).all() or np.max(np.abs(x))<1e-5:raise ValueError('Invalid or silent speech output')
    peak=float(np.max(np.abs(x)))
    if peak>.98:x=x*(.98/peak)
    a.out.parent.mkdir(parents=True,exist_ok=True);write(str(a.out),x,sr)
    # A signal ending audit is not a listening or semantic-completeness verdict.
    win=max(1,int(sr*.01));rms=np.array([np.sqrt(np.mean(x[i:i+win]**2)) for i in range(0,len(x),win)])
    threshold=max(float(rms.max())*.015,1e-5);quiet=0
    for value in rms[::-1]:
        if value>threshold:break
        quiet+=win/sr
    record={'text':text,'audio_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'reference_sha256':digest,
            'model':str(a.model),'duration':len(x)/sr,'sample_rate':sr,'seed':42,'temperature':.65,
            'repetition_penalty':1.1,'raw_audio':str(a.out),'quiet_tail_seconds':round(quiet,3),
            'ending_review_needed':quiet<.35,'status':'pending-listening','mlx_audio_version':importlib.metadata.version('mlx-audio')}
    a.out.with_suffix('.voice.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print(f'Generated {len(x)/sr:.2f}s. New text and sentence ending require listening; raw audio unchanged.')
if __name__=='__main__':main()
