let imgState = { img:null, w:0, h:0, size:0, name:'' };
const q=document.getElementById('q'), out=document.getElementById('out'); let lastUrl=null;
TKU.imageInput(img=>{ imgState=img; document.getElementById('ctrl').classList.remove('hidden'); out.textContent='—';
  document.getElementById('origInfo').textContent=`Original: ${img.w}×${img.h} px, ${TKU.kb(img.size)}`; });
document.getElementById('go').addEventListener('click', ()=>{
  if(!imgState.img) return;
  const v=+q.value; if(!(v>=1&&v<=100)){ TKU.fail('q','Enter a quality from 1 to 100.'); out.textContent='Fix the highlighted field.'; return; }
  const canvas=document.createElement('canvas'); canvas.width=imgState.w; canvas.height=imgState.h;
  const ctx=canvas.getContext('2d'); ctx.fillStyle='#fff'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.drawImage(imgState.img,0,0);
  canvas.toBlob(blob=>{
    if(!blob){ out.textContent='Could not compress this image in your browser.'; return; }
    if(lastUrl) URL.revokeObjectURL(lastUrl); lastUrl=URL.createObjectURL(blob); const name=`${TKU.base(imgState.name)}-compressed.jpg`;
    out.innerHTML=`Original: ${TKU.kb(imgState.size)} → Compressed: <strong>${TKU.kb(blob.size)}</strong>${blob.size>=imgState.size?'<br><span class="note">Not smaller than the original. Keep your original, or lower the quality.</span>':''}<br><a class="btn btn-primary" href="${lastUrl}" download="${TKU.esc(name)}" style="margin-top:8px">Download ${TKU.esc(name)}</a>`;
  }, 'image/jpeg', v/100);
});
