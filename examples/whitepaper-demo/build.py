#!/usr/bin/env python3
"""Build the public fictional demo. Supply actual speech timing; no private assets."""
import argparse,html,json,shutil
from pathlib import Path
P=Path(__file__).parent

def main():
    a=argparse.ArgumentParser();a.add_argument('project',type=Path);a.add_argument('--timing',required=True,type=Path);args=a.parse_args()
    root=args.project.resolve();film=root/'film';film.mkdir(parents=True,exist_ok=True)
    timing=json.loads(args.timing.read_text());starts=timing['starts'];D=timing['duration']
    if len(starts)!=4 or starts[0]!=0 or not all(starts[i]<starts[i+1] for i in range(3)) or starts[-1]>=D:raise ValueError('Four ordered scene starts and duration required')
    template=(P/'index.tpl.html').read_text();js=[]
    def to(s,v,t,d=.5):js.append(f'tl.to({json.dumps(s)},{json.dumps(dict(v,duration=d,ease="power3.out"))},{t});')
    def show(s,t):to(s,{'opacity':1},t)
    for i,t in enumerate(starts):
        js.append(f'tl.set("#s{i}",{{opacity:1}},{t});')
        if i<3:js.append(f'tl.set("#s{i}",{{opacity:0}},{starts[i+1]});')
    js+=['PWFRecipes.lines(tl,["#headline"],[.2]);','PWF.steps(tl,["#import0","#search0","#source0"],[3.1,4.1,5.3]);']
    js.append('PWFRecipes.stroke(tl,"#intro1",5.8);PWFRecipes.stroke(tl,"#intro2",6.2);')
    t=starts[1];show('#ui1',t+.15)
    cue=timing.get('workflow_cues',[.5,2,4])
    for i,(word,step) in enumerate(zip(['import','search','source'],cue)):
        show('#label-'+word,t+step);js.append(f'PWF.focus(tl,"#focus-{word}",{t+step+.25},{min(starts[2]-.25,t+step+1.15)});')
    t=starts[2];show('#ui2',t+.1)
    js.append(f'PWFRecipes.layout(tl,[{{target:"#ui2",from:{{x:0,y:0,scale:1}},to:{{x:-240,y:-25,scale:.8}}}}],{t+.7},{{duration:.8}});')
    show('#source-card',t+1.8);js.append(f'PWFRecipes.stroke(tl,"#source-wire",{t+2.35});PWFRecipes.follow(tl,"#source-dot","#source-wire",{t+3.15},{{duration:1.1}});')
    t=starts[3];js.append(f'PWFRecipes.lines(tl,["#end1","#end2"],[{t+.2},{t+1.1}]);');show('#endnote',t+2)
    caps=[]
    for i,c in enumerate(timing['captions']):
        caps.append(f'<div id="cap{i}" class="caption">{html.escape(c["text"])}</div>')
        js.append(f'tl.set("#cap{i}",{{opacity:1}},{c["start"]});tl.set("#cap{i}",{{opacity:0}},{c["end"]});')
    js.append(f'tl.to("#endnote",{{x:0,duration:.01}},{D-.01});')
    H=template.replace('__DURATION__',str(D)).replace('__CAPTIONS__',''.join(caps)).replace('__TIMELINE__',''.join(js))
    (film/'index.html').write_text(H)
    shutil.copy2(P/'whitepaper.md',root/'whitepaper.md');shutil.copy2(P/'narration.txt',root/'narration.txt')
    print(film)
if __name__=='__main__':main()
