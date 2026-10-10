// ToolsKit search engine. Data comes from the generated assets/tk-data.js (window.TKD) — never hard-code tools here.
// Result kinds, strongest first:
//   exact    the query is a tool name or a listed synonym (for example "kg to lb")
//   match    every word of the query is found in one tool's name, synonyms or category
//   category the query names a category ("pdf", "qr")
//   related  NOT a match — shown only after an honest "No tool currently matches" message
// Unsupported intents ("pdf to word") are listed in src/data/search.json and never return an unrelated tool as if it did the job.
(()=>{
const D=window.TKD||{tools:[],cats:[],unsupported:[]};
const SW=D.sw||{};
// letters that do not decompose under NFD are mapped by hand (Polish ł, German ß, Nordic ø/æ, ...)
const SPECIAL={'ł':'l','ß':'ss','ø':'o','æ':'ae','œ':'oe','đ':'d','ı':'i','ð':'d','þ':'th'};
const norm=s=>String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[łßøæœđıðþ]/g,c=>SPECIAL[c]);
const words=s=>norm(s).split(/[^\p{L}\p{N}]+/u).filter(Boolean);
const STOP=new Set((SW.stop||'a an the of for and in my me how do i can free online tool tools make create build please want need use using with on get'.split(' ')).map(norm));
const CONN=new Set((SW.conn||['to','into','from','2']).map(norm));
const FILLER=new Set((SW.filler||['convert','file','files','document','documents','change','turn']).map(norm));
// word match: exact; prefix ("compress" ~ "compressor" in either direction, up to 2 extra letters so plurals and -er forms line up)
const wm=(q,w)=>q===w||(q.length>=3&&w.startsWith(q))||(w.length>=3&&q.startsWith(w)&&q.length-w.length<=2);
const toks=s=>words(s).filter(w=>!STOP.has(w));
const tools=D.tools.map((t,i)=>{
  const phrases=[t.name,...(t.phrases||[])].map((p,k)=>({w:toks(p),name:k===0}));
  const cat=D.cats.find(c=>c.key===t.catKey);
  const hay=new Set([...phrases.flatMap(p=>p.w),...toks(t.cat),...((cat&&cat.syn)||[]).flatMap(toks)]);
  return {t,i,phrases,hay:[...hay]};
});
const subseq=(q,p)=>{let j=0;for(const w of p){if(j<q.length&&wm(q[j],w))j++;}return j===q.length;};
const contiguous=(q,p)=>{for(let s=0;s+q.length<=p.length;s++){let ok=true;for(let k=0;k<q.length;k++)if(!wm(q[k],p[s+k])){ok=false;break;}if(ok)return true;}return false;};
const phraseIn=(pat,qs)=>{for(let s=0;s+pat.length<=qs.length;s++){let ok=true;for(let k=0;k<pat.length;k++)if(qs[s+k]!==pat[k]){ok=false;break;}if(ok)return true;}return false;};
const unsupp=(D.unsupported||[]).map(u=>({...u,pats:u.patterns.map(p=>words(p))}));
const catTools=k=>D.tools.filter(t=>t.catKey===k);

function relatedFor(entry,qtokens){
  const out=[];const add=t=>{if(t&&!out.includes(t))out.push(t);};
  if(entry){for(const r of entry.related||[]){if(r.startsWith('cat:'))catTools(r.slice(4)).forEach(add);else add(D.tools.find(t=>t.id===r));}}
  else{ // tokens that name a category, or appear in a tool, give honest "related" suggestions
    for(const q of qtokens){const c=D.cats.find(c=>toks(c.name).concat((c.syn||[]).flatMap(toks)).some(w=>wm(q,w)));if(c)catTools(c.key).forEach(add);}
  }
  return out.slice(0,6);
}

function search(raw){
  const q=String(raw||'').trim();
  const all=words(q);let qt=toks(q);
  if(!qt.length)return {kind:'empty',q,results:[],related:[]};
  const hasConn=qt.some(w=>CONN.has(w));
  if(hasConn)qt=qt.filter(w=>!FILLER.has(w));
  const scored=[];
  for(const e of tools){
    let best=0;
    for(const p of e.phrases){
      if(!p.w.length)continue;
      const base=p.name?100:90;
      if(p.w.length===qt.length&&qt.every((w,k)=>wm(w,p.w[k]))){best=Math.max(best,base);continue;}
      if(contiguous(qt,p.w)){best=Math.max(best,base-20);continue;}
      if(p.w.length>=2&&contiguous(p.w,qt)){best=Math.max(best,base-25);continue;}
      if(hasConn&&subseq(qt,p.w)){best=Math.max(best,base-30);}
    }
    if(!best&&!hasConn&&qt.every(w=>e.hay.some(h=>wm(w,h))))best=40;
    if(best)scored.push([e.t,best,e.i]);
  }
  scored.sort((a,b)=>b[1]-a[1]||a[2]-b[2]);
  const top=scored.length?scored[0][1]:0;
  // an unsupported intent only wins when no tool genuinely matches it by name/synonym
  const hit=unsupp.find(u=>u.pats.some(p=>phraseIn(p,all)));
  if(hit&&top<70){
    return {kind:'none',q,results:[],related:relatedFor(hit,qt),message:(D.ui&&D.ui.no_tool_for||'No {label} is currently available on ToolsKit.').replace('{label}',hit.label),note:hit.note||''};
  }
  if(scored.length){
    const topCat=scored[0][0].catKey;
    const keep=top>=70?scored.filter(s=>s[1]>=70||(s[1]>=40&&s[0].catKey===topCat)):scored;
    const results=keep.map(s=>s[0]);
    const isCat=qt.length===1&&D.cats.some(c=>toks(c.name).concat((c.syn||[]).flatMap(toks)).some(w=>wm(qt[0],w)));
    return {kind:top>=90&&!isCat?'exact':(isCat?'category':'match'),q,results,related:[]};
  }
  return {kind:'none',q,results:[],related:relatedFor(null,qt),message:(D.ui&&D.ui.no_tool_generic)||'No tool currently matches this request.',note:''};
}
window.TKS={search,words,toks};
})();
