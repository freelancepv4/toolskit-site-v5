function copyBtn(text){ const L=window.TK_LIMIT; return `<span class="note">${text.length}${L?' / '+L:''} characters${L&&text.length>L?' — over the limit':''}</span> <button type="button" class="btn btn-secondary btn-sm" data-copy="${encodeURIComponent(text)}">Copy</button>`; }
function renderList(items){ return items.map(t=>`<div class="tk-item"><div>${TKU.esc(t)}</div><div>${copyBtn(t)}</div></div>`).join(''); }

document.getElementById('ytGen').addEventListener('click', ()=>{
  const t=document.getElementById('ytTopic').value.trim(); if(!t){ document.getElementById('ytOut').replaceChildren(); TKU.fail('ytTopic','Enter a topic.'); return; }
  const titles=[`${t}: The Complete Beginner's Guide`,`I Tried ${t} For a Week — Here's What Happened`,`5 Things Nobody Tells You About ${t}`,`${t} Explained in 10 Minutes`,`The Truth About ${t}`];
  document.getElementById('ytOut').innerHTML=renderList(titles);
});
