#!/usr/bin/env node
// Uses real configured GSAP with plain targets and mock SVG geometry.
// Checks scheduling/rewind invariants; does not replace rendered-frame review.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),vm=require('node:vm'),assert=require('node:assert/strict');
const config=JSON.parse(fs.readFileSync(process.argv[2]||path.join(os.homedir(),'.config/product-whitepaper-film/runtime.json'),'utf8'));
const engine={exports:{}};vm.runInNewContext(fs.readFileSync(config.gsap,'utf8'),{module:engine,exports:engine.exports,console,setTimeout,clearTimeout,Date,Math});
const {gsap}=engine.exports;
const svg={getTotalLength:()=>1000,getPointAtLength:l=>({x:l/10,y:(l/100)**2}),opacity:0,strokeDashoffset:1000,strokeDasharray:''};
const dot={opacity:0,values:{},setAttribute(k,v){this.values[k]=Number(v);}};
const context={window:{},document:{querySelector:s=>({'#path':svg,'#dot':dot}[s])},gsap};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/motion/pwf-motion.js'),'utf8'),context);
const R=context.window.PWFRecipes;
function close(a,b){assert.ok(Math.abs(a-b)<.0001,`${a} != ${b}`);}
function seek(tl,t){tl.seek(t,false);}
const motion=gsap.timeline({paused:true});R.follow(motion,'#dot','#path',1,{duration:2});
seek(motion,2);close(dot.values.cx,50);close(dot.values.cy,25);
const reference=JSON.stringify(dot.values);
for(const t of [1.1,2.8,1.5,3.15,2])seek(motion,t);
assert.equal(JSON.stringify(dot.values),reference);close(dot.opacity,1);
seek(motion,.5);close(dot.opacity,0);
const stroke=gsap.timeline({paused:true});R.stroke(stroke,'#path',1,{from:.2,to:.8,duration:2,ease:'none'});
seek(stroke,2);close(svg.strokeDashoffset,500);
seek(stroke,2.8);seek(stroke,1.2);seek(stroke,2);close(svg.strokeDashoffset,500);
const card={x:0,y:0,scale:1};const layout=gsap.timeline({paused:true});R.layout(layout,[{target:card,from:{x:0,y:0,scale:1},to:{x:300,y:100,scale:.5}}],1,{duration:2,ease:'none'});
seek(layout,2);close(card.x,150);close(card.scale,.75);seek(layout,2.7);seek(layout,1.2);seek(layout,2);close(card.x,150);
const line={opacity:0,yPercent:105};const text=gsap.timeline({paused:true});R.lines(text,[line],[1],{duration:2,ease:'none'});seek(text,2);close(line.yPercent,52.5);seek(text,2.7);seek(text,.5);seek(text,2);close(line.opacity,.5);close(line.yPercent,52.5);
assert.throws(()=>R.lines(text,[line],[]),/cue/);assert.throws(()=>R.stroke(stroke,'#path',0,{to:2}),/progress/);assert.throws(()=>R.follow(motion,'#dot','#missing',0),/needs/);
gsap.globalTimeline.clear();gsap.ticker.sleep();
console.log('PASS: real-GSAP arbitrary-time seek/rewind, curved SVG positions, partial stroke progress, layout landing, line reveal and invalid inputs.');
