/* Product Whitepaper Film motion helpers. Deterministic GSAP timeline, no timers.
 * SVG connections illustrate documented relationships, not measured execution.
 */
window.PWF = Object.freeze({
  reveal(tl, target, at, options = {}) {
    tl.fromTo(target, {opacity:0, y:options.offset ?? 24},
      {opacity:1, y:0, duration:options.duration ?? .55, ease:options.ease ?? 'power3.out', immediateRender:false}, at);
  },
  mask(tl, target, at, duration = .65) {
    tl.fromTo(target, {clipPath:'inset(0 100% 0 0)', opacity:1},
      {clipPath:'inset(0 0% 0 0)', opacity:1, duration, ease:'expo.inOut', immediateRender:false}, at);
  },
  draw(tl, target, at, duration = .7) {
    const path = document.querySelector(target);
    if (!path) throw new Error(`Missing path ${target}`);
    const length = path.getTotalLength();
    gsap.set(path, {strokeDasharray:length, strokeDashoffset:length});
    tl.to(path, {opacity:1, strokeDashoffset:0, duration, ease:'power2.inOut'}, at);
  },
  signal(tl, target, points, at, step = .3) {
    if (points.length < 2) throw new Error('A signal needs at least two points');
    gsap.set(target, {attr:{cx:points[0][0],cy:points[0][1]}});
    tl.to(target,{opacity:1,duration:.06},at);
    points.slice(1).forEach((p,i) => tl.to(target,
      {attr:{cx:p[0],cy:p[1]},duration:step,ease:'none'},at+i*step));
    tl.to(target,{opacity:0,duration:.12},at+(points.length-1)*step);
  },
  steps(tl, targets, cues) {
    if (targets.length !== cues.length) throw new Error('Each step needs one narration cue');
    targets.forEach((target,i) => {
      this.reveal(tl,target,cues[i]);
      tl.to(target,{borderColor:'#2869cc',backgroundColor:'#e0ecff',duration:.35},cues[i]+.25);
    });
  },
  focus(tl, target, at, end) {
    if (!(end > at)) throw new Error('Focus interval must be positive');
    tl.to(target,{opacity:1,duration:.18},at);
    tl.to(target,{opacity:0,duration:.18},end);
  },
  reflow(tl, target, destination, at, duration = .85) {
    // destination is a caller-defined stable landing; text must be checked after motion.
    tl.to(target,{...destination,duration,ease:'expo.inOut'},at);
  },
  camera(tl, target, destination, at, duration = .8) {
    tl.to(target,{...destination,duration,ease:'power2.inOut'},at);
  },
  count(tl, target, from, to, at, duration = .8) {
    // Use only when source evidence supplies the metric; never generate claims.
    const proxy = {value:from}; const element=document.querySelector(target);
    tl.to(proxy,{value:to,duration,ease:'power2.out',onUpdate:()=>{element.textContent=Math.round(proxy.value);}},at);
  }
});

/* Additional video-timeline recipes. Independently authored from documented
 * animation concepts; source mapping: references/recipe-sources.md.
 * No plugin code, interaction handlers, randomness, loops or wall-clock timers.
 */
window.PWFRecipes = Object.freeze({
  layout(tl, items, at, options = {}) {
    const duration = options.duration ?? .8;
    const stagger = options.stagger ?? .08;
    items.forEach((item, i) => {
      if (!item.target || !item.from || !item.to) throw new Error('Layout needs target/from/to');
      // Explicit frame states replace event-time DOM measurements (FLIP-inspired).
      tl.fromTo(item.target, item.from, {...item.to, duration,
        ease:options.ease ?? 'expo.inOut', immediateRender:false}, at+i*stagger);
    });
  },
  stroke(tl, target, at, options = {}) {
    const path = document.querySelector(target);
    if (!path) throw new Error(`Missing path ${target}`);
    const length = path.getTotalLength();
    const from = options.from ?? 0, to = options.to ?? 1;
    if (!(0 <= from && from <= 1 && 0 <= to && to <= 1)) throw new Error('Stroke progress must be in [0,1]');
    gsap.set(path,{strokeDasharray:`${length} ${length}`,strokeDashoffset:length*(1-from)});
    tl.fromTo(path,{opacity:0,strokeDashoffset:length*(1-from)},
      {opacity:1,strokeDashoffset:length*(1-to),duration:options.duration ?? .8,
       ease:options.ease ?? 'power2.inOut',immediateRender:false},at);
  },
  follow(tl, target, pathTarget, at, options = {}) {
    const path = document.querySelector(pathTarget), dot = document.querySelector(target);
    if (!path || !dot) throw new Error('Follow needs an SVG path and SVG circle');
    const length = path.getTotalLength(), proxy = {progress:options.from ?? 0};
    const start = proxy.progress, end = options.to ?? 1;
    if (!(start>=0 && start<=1 && end>=0 && end<=1)) throw new Error('Follow progress must be in [0,1]');
    const place = () => {
      const point = path.getPointAtLength(length*proxy.progress);
      dot.setAttribute('cx',point.x);dot.setAttribute('cy',point.y);
    };
    place();
    const duration = options.duration ?? 1.2;
    tl.to(dot,{opacity:1,duration:.06},at);
    tl.fromTo(proxy,{progress:start},{progress:end,duration,ease:options.ease ?? 'none',
      immediateRender:false,onUpdate:place},at);
    tl.to(dot,{opacity:0,duration:.12},at+duration);
  },
  lines(tl, targets, cues, options = {}) {
    if (targets.length !== cues.length) throw new Error('Each text line needs one cue');
    targets.forEach((target,i) => tl.fromTo(target,
      {yPercent:105,opacity:0},{yPercent:0,opacity:1,duration:options.duration ?? .65,
       ease:options.ease ?? 'power4.out',immediateRender:false},cues[i]));
  }
});
