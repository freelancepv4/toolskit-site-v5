function copyBtn(text){ const L=window.TK_LIMIT; return `<span class="note">${text.length}${L?' / '+L:''} characters${L&&text.length>L?' — over the limit':''}</span> <button type="button" class="btn btn-secondary btn-sm" data-copy="${encodeURIComponent(text)}">Copy</button>`; }
function renderList(items){ return items.map(t=>`<div class="tk-item"><div>${TKU.esc(t)}</div><div>${copyBtn(t)}</div></div>`).join(''); }

document.getElementById('hashGen').addEventListener('click', ()=>{
  const raw=document.getElementById('hashTopic').value.trim(); const count=Math.min(30,Math.max(5,parseInt(document.getElementById('hashCount').value)||15));
  const out=document.getElementById('hashOut'); if(!raw){ out.replaceChildren(); TKU.fail('hashTopic','Enter a topic.'); return; }
  const clean=raw.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu,'').split(/\s+/).filter(Boolean); const base=clean.join('');
  const suffixes=['daily','life','love','gram','community','vibes','style','world','addict','lover','ideas','inspo','moments','goals','tips'];
  const generic=['instagood','photooftheday','trending','explorepage','picoftheday'];
  let tags=new Set(); clean.forEach(w=>tags.add('#'+w));
  suffixes.forEach(s=>{ if(tags.size<count) tags.add('#'+base+s); });
  generic.forEach(g=>{ if(tags.size<count) tags.add('#'+g); });
  const list=Array.from(tags).slice(0,count);
  out.innerHTML=`<div>${list.join(' ')}</div>${copyBtn(list.join(' '))}`;
});
