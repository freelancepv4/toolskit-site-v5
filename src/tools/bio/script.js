function copyBtn(text){ const L=window.TK_LIMIT; return `<span class="note">${text.length}${L?' / '+L:''} characters${L&&text.length>L?' — over the limit':''}</span> <button type="button" class="btn btn-secondary btn-sm" data-copy="${encodeURIComponent(text)}">Copy</button>`; }
function renderList(items){ return items.map(t=>`<div class="tk-item"><div>${TKU.esc(t)}</div><div>${copyBtn(t)}</div></div>`).join(''); }

document.getElementById('bioGen').addEventListener('click', ()=>{
  const name=document.getElementById('bioName').value.trim()||'Your Name', role=document.getElementById('bioRole').value.trim()||'creator';
  const kwRaw=document.getElementById('bioKeywords').value.trim(); const kws=kwRaw?kwRaw.split(',').map(k=>k.trim()).filter(Boolean):[];
  const kwText=kws.length?kws.join(' • '):'';
  const bios=[`${name} | ${role}${kwText?' — '+kwText:''}`,`${role.charAt(0).toUpperCase()+role.slice(1)} sharing ${kws[0]||'my work'} one post at a time.`,`${name} · ${role}${kws.length?' · into '+kws.join(', '):''}`];
  document.getElementById('bioOut').innerHTML=renderList(bios);
});
