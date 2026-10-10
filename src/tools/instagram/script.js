function copyBtn(text){ const L=window.TK_LIMIT; return `<span class="note">${text.length}${L?' / '+L:''} characters${L&&text.length>L?' — over the limit':''}</span> <button type="button" class="btn btn-secondary btn-sm" data-copy="${encodeURIComponent(text)}">Copy</button>`; }
function renderList(items){ return items.map(t=>`<div class="tk-item"><div>${TKU.esc(t)}</div><div>${copyBtn(t)}</div></div>`).join(''); }

const capTemplates = {
  Casual: t=>[`Just vibing with ${t} today.`, `${t} kind of day. No complaints here.`, `Living for moments like this — ${t}.`],
  Professional: t=>[`Sharing a look at ${t}.`, `Another step forward with ${t}.`, `Proud to highlight ${t} this week.`],
  Playful: t=>[`Plot twist: ${t} happened and it was iconic.`, `${t}?? Yes please, more of this.`, `Warning: too much fun had during ${t}.`],
  Inspirational: t=>[`Every ${t} is a reminder to keep going.`, `Grateful for ${t} and everything it taught me.`, `Small moments like ${t} add up to something bigger.`]
};
document.getElementById('capGen').addEventListener('click', ()=>{
  const topic=document.getElementById('capTopic').value.trim(); if(!topic){ document.getElementById('capOut').replaceChildren(); TKU.fail('capTopic','Enter a topic.'); return; } const tone=document.getElementById('capTone').value, cta=document.getElementById('capCta').value.trim();
  let caps=capTemplates[tone](topic); if(cta) caps=caps.map(c=>`${c} ${cta}`);
  document.getElementById('capOut').innerHTML=renderList(caps);
});
