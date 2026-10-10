// Shared by every page. All tool/category data comes from the generated assets/tk-data.js (window.TKD); search logic lives in search.js.
const ROOT=(document.currentScript&&new URL('../',document.currentScript.src))||new URL('/',location.href);
const TKT=(window.TKD&&TKD.tools)||[];
const UI=(window.TKD&&TKD.ui)||{};
const tx=(k,d)=>window.TKI?TKI.t(k,UI[k]||d):(UI[k]||d);
const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x)e.textContent=x;return e;};
const NS='http://www.w3.org/2000/svg', href=t=>new URL(t.url.slice(1),ROOT).href;
const allHref=q=>new URL(((window.TKD&&TKD.allUrl)||'/tools/').slice(1)+(q?'?q='+encodeURIComponent(q):''),ROOT).href;
const match=q=>window.TKS?TKS.search(q).results:[];
// One tool-card markup, identical to the server-rendered cards (see build/build.py: card()).
function card(t){
  const a=el('article','tool-card tk-tool'); a.dataset.id=t.id;
  const i=el('span','ico'), s=document.createElementNS(NS,'svg'), u=document.createElementNS(NS,'use');
  s.setAttribute('width','22'); s.setAttribute('height','22'); s.setAttribute('aria-hidden','true'); u.setAttribute('href','#'+t.icon); s.append(u); i.append(s);
  const m=el('p','tk-meta'); m.append(el('span','',t.cat)); if(t.badge) m.append(el('span','tk-local',t.badge));
  const b=el('a','btn btn-secondary btn-sm',tx('open','Open tool')); b.href=href(t); b.append(el('span','tk-vh',': '+t.name));
  a.append(i,el('h3','',t.name),el('p','',t.desc),m,b); return a;
}
const recent=()=>{try{return JSON.parse(localStorage.getItem('tk_recent')||'[]').map(id=>TKT.find(t=>t.id===id)).filter(Boolean);}catch(e){return [];}};
window.TK={TOOLS:TKT,match,card,recent};

document.addEventListener('DOMContentLoaded',()=>{
const $=s=>document.querySelector(s);
if(/[?&]embed=1/.test(location.search)) document.documentElement.dataset.theme='light';
const yr=$('#yr'); if(yr) yr.textContent=new Date().getFullYear();
const main=$('main'); if(main){ main.id=main.id||'main'; main.tabIndex=-1; }
// recently used: tool IDs only, stored on this device
try{ const cur=TKT.find(t=>location.pathname===t.url||location.pathname===t.url.replace(/\.html$/,'')||(t.url.endsWith('/')&&location.pathname===t.url+'index.html')); if(cur){ const r=JSON.parse(localStorage.getItem('tk_recent')||'[]').filter(i=>i!==cur.id); r.unshift(cur.id); localStorage.setItem('tk_recent',JSON.stringify(r.slice(0,6))); } }catch(e){}
// mobile nav (current page/section is marked server-side with aria-current)
const mb=$('#menuBtn'), nav=$('#catnav');
if(mb&&nav){
  mb.setAttribute('aria-expanded','false'); mb.setAttribute('aria-controls','catnav');
  mb.addEventListener('click',()=>mb.setAttribute('aria-expanded',String(nav.classList.toggle('open'))));
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&nav.classList.contains('open')){ nav.classList.remove('open'); mb.setAttribute('aria-expanded','false'); mb.focus(); }});
}
// search combobox (header, home hero, 404)
const inp=$('#toolSearch'), box=$('#searchResults');
if(inp&&box){
  const live=el('span','tk-vh'); live.setAttribute('aria-live','polite'); inp.after(live);
  box.setAttribute('role','listbox'); box.setAttribute('aria-label',tx('results','Tool results'));
  inp.setAttribute('role','combobox'); inp.setAttribute('aria-autocomplete','list'); inp.setAttribute('aria-expanded','false'); inp.setAttribute('aria-controls','searchResults');
  let items=[], act=-1;
  const close=()=>{ box.classList.add('hidden'); inp.setAttribute('aria-expanded','false'); inp.removeAttribute('aria-activedescendant'); act=-1; };
  const mark=i=>{ items.forEach((a,j)=>{ a.classList.toggle('is-active',j===i); a.setAttribute('aria-selected',String(j===i)); }); act=i;
    if(i>=0){ inp.setAttribute('aria-activedescendant',items[i].id); items[i].scrollIntoView({block:'nearest'}); } else inp.removeAttribute('aria-activedescendant'); };
  const opt=(t,i)=>{ const a=el('a'); a.href=href(t); a.id='sr-'+i; a.dataset.id=t.id; a.setAttribute('role','option'); a.setAttribute('aria-selected','false');
    a.append(el('span','sr-n',t.name),el('span','sr-c',t.cat),el('span','sr-d',t.desc)); return a; };
  const note=(txt,strong)=>{ const m=el('div','sr-none'); m.setAttribute('role','presentation'); if(strong){ m.append(el('strong','',txt)); } else m.textContent=txt; return m; };
  const search=()=>{
    const q=inp.value.trim(); if(!q){ close(); live.textContent=''; return; }
    const r=TKS.search(q); box.replaceChildren(); box.classList.remove('hidden'); inp.setAttribute('aria-expanded','true'); items=[];
    if(r.kind==='none'){
      box.append(note(r.message,true)); if(r.note) box.append(note(r.note));
      if(r.related.length){ box.append(note(tx('related','Related tools')+':')); r.related.forEach((t,i)=>{ const a=opt(t,i); box.append(a); items.push(a); }); }
      const a=el('a','sr-all',tx('browse_all','Browse all tools →')); a.href=allHref(''); a.id='sr-all'; a.setAttribute('role','option'); a.setAttribute('aria-selected','false'); box.append(a); items.push(a);
      live.textContent=r.message+(r.related.length?' '+TKI.p(UI,'n_related',r.related.length):'');
    } else {
      r.results.slice(0,7).forEach((t,i)=>{ const a=opt(t,i); box.append(a); items.push(a); });
      if(r.results.length>1){ const a=el('a','sr-all',tx('see_all','See all {n} matching tools →').replace('{n}',r.results.length)); a.href=allHref(q); a.id='sr-all'; a.setAttribute('role','option'); a.setAttribute('aria-selected','false'); box.append(a); items.push(a); }
      live.textContent=tx('found','{n} tools found').replace('{n}',r.results.length);
    }
    act=-1; inp.removeAttribute('aria-activedescendant');
  };
  inp.addEventListener('input',search);
  inp.addEventListener('keydown',e=>{
    if(e.key==='ArrowDown'){ e.preventDefault(); if(box.classList.contains('hidden')) search(); if(items.length) mark((act+1)%items.length); }
    else if(e.key==='ArrowUp'){ e.preventDefault(); if(items.length) mark(act<=0?items.length-1:act-1); }
    else if(e.key==='Enter'&&inp.value.trim()){ e.preventDefault(); const q=inp.value.trim(); const r=TKS.search(q);
      document.dispatchEvent(new CustomEvent('tk:search',{detail:{result_count:r.results.length}}));
      // go straight to a tool only when the query unambiguously names exactly one; otherwise show the results page (which is honest about no match)
      const one=r.kind==='exact'&&r.results.length===1?r.results[0]:null;
      location.href=act>=0?items[act].href:(one?href(one):allHref(q)); }
    else if(e.key==='Escape'){ if(!box.classList.contains('hidden')) close(); else inp.value=''; }
  });
  box.addEventListener('click',e=>{const a=e.target.closest('a[data-id]'); if(a)document.dispatchEvent(new CustomEvent('tk:searchclick',{detail:{tool_id:a.dataset.id}}));});
  document.addEventListener('click',e=>{ if(!inp.contains(e.target)&&!box.contains(e.target)) close(); });
}
// All Tools page: honest search + category filter + recently used
const fi=$('#filterInput');
if(fi){
  const chips=[...document.querySelectorAll('[data-chip]')], dir=$('#directory'), ml=$('#matchList'), cnt=$('#resultCount'), none=$('#noResults');
  let cat=''; const p=new URLSearchParams(location.search), h=location.hash.slice(1);
  if(chips.some(c=>c.dataset.chip===h)) cat=h; fi.value=p.get('q')||'';
  const apply=()=>{
    const q=fi.value.trim(); chips.forEach(c=>c.setAttribute('aria-pressed',String(c.dataset.chip===cat)));
    if(q){
      const r=TKS.search(q), list=r.results.filter(t=>!cat||t.catKey===cat);
      ml.replaceChildren(...list.map(card)); ml.hidden=!list.length; dir.hidden=true; none.hidden=!!list.length;
      if(!list.length){
        $('#nrMsg').textContent=r.kind==='none'?r.message:tx('no_in_cat','No tool in this category matches this request.');
        const n=$('#nrNote'); n.textContent=r.note||''; n.hidden=!r.note;
        const rel=r.kind==='none'?r.related:[]; $('#nrRelated').replaceChildren(...rel.map(card)); $('#nrRelWrap').hidden=!rel.length;
      }
      cnt.textContent=list.length?TKI.p(UI,'n_tools',list.length):tx('none_tools','No tools found'); return;
    }
    ml.hidden=true; none.hidden=true; dir.hidden=false;
    dir.querySelectorAll('[data-sec]').forEach(s=>{ s.hidden=s.dataset.sec==='cat'?(!!cat&&s.dataset.cat!==cat):(!!cat||s.dataset.empty==='1'); });
    cnt.textContent=cat?TKI.p(UI,'n_tools',dir.querySelectorAll('[data-sec=cat][data-cat='+cat+'] article').length):'';
  };
  chips.forEach(c=>c.addEventListener('click',()=>{ cat=c.dataset.chip; history.replaceState(null,'',cat?'#'+cat:location.pathname+location.search); apply(); }));
  fi.addEventListener('input',apply);
  const rec=recent(), rs=$('#recent');
  if(rs&&rec.length){ $('#recentGrid').replaceChildren(...rec.map(card)); rs.dataset.empty='0'; }
  $('#clearRecent')?.addEventListener('click',()=>{ try{localStorage.removeItem('tk_recent');}catch(e){} rs.dataset.empty='1'; apply(); fi.focus(); });
  apply();
}
// QR pages: regenerate as the user types (removes the separate "Generate" step; button remains)
const qb=$('#qrGenBtn');
if(qb&&typeof buildQRContent==='function'){ let tm; const pn=$('.panel'); pn.addEventListener('input',()=>{ clearTimeout(tm); tm=setTimeout(()=>{ if(buildQRContent()) qb.click(); },400); }); }
// polite status for the image-info line (results are announced by tool-ui.js, once)
document.querySelectorAll('#origInfo').forEach(e=>e.setAttribute('aria-live','polite'));
// language choice: remembered on this device only (localStorage, no cookie). It is never used to redirect; the chooser on the home page just lists the last used language first.
document.addEventListener('click',e=>{const a=e.target.closest('a[data-lang]');if(a){try{localStorage.setItem('tk_lang',a.dataset.lang);}catch(x){}}});
try{const pref=localStorage.getItem('tk_lang'),ls=$('.lang-list');if(ls&&pref){const a=ls.querySelector('a[data-lang="'+pref+'"]');if(a&&!a.hasAttribute('aria-current')){a.classList.add('is-pref');ls.prepend(a.parentNode);}}}catch(x){}
document.addEventListener('click',e=>document.querySelectorAll('details.tk-lang[open]').forEach(d=>{ if(!d.contains(e.target)) d.open=false; }));
document.addEventListener('keydown',e=>{ if(e.key==='Escape') document.querySelectorAll('details.tk-lang[open]').forEach(d=>{ d.open=false; d.querySelector('summary').focus(); }); });
});

function downloadBytes(bytes, filename, mime){
  const blob=new Blob([bytes],{type:mime||'application/pdf'}), url=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=url; a.download=filename; a.click(); setTimeout(()=>URL.revokeObjectURL(url),5000);
}
