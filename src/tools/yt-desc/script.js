function copyBtn(text){ const L=window.TK_LIMIT; return `<span class="note">${text.length}${L?' / '+L:''} characters${L&&text.length>L?' — over the limit':''}</span> <button type="button" class="btn btn-secondary btn-sm" data-copy="${encodeURIComponent(text)}">Copy</button>`; }
function renderList(items){ return items.map(t=>`<div class="tk-item"><div>${TKU.esc(t)}</div><div>${copyBtn(t)}</div></div>`).join(''); }

document.getElementById('descGen').addEventListener('click', ()=>{
  const topic=document.getElementById('descTopic').value.trim(); if(!topic){ document.getElementById('descOut').replaceChildren(); TKU.fail('descTopic','Enter a topic.'); return; }
  const kwRaw=document.getElementById('descKeywords').value.trim();
  const kws=kwRaw?kwRaw.split(',').map(k=>k.trim()).filter(Boolean):[];
  const cta=document.getElementById('descCta').value.trim()||'Subscribe for more videos like this.';
  let desc=`In this video, we take a closer look at ${topic}.`;
  if(kws.length) desc+=` Topics covered include ${kws.join(', ')}.`;
  desc+=`\n\n${cta}\n\n`;
  if(kws.length) desc+=kws.map(k=>'#'+k.replace(/\s+/g,'')).join(' ');
  document.getElementById('descOut').innerHTML=`<div>${desc.replace(/\n/g,'<br>')}</div>${copyBtn(desc)}`;
});
