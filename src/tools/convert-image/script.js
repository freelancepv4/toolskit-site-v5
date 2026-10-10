let imgState = { img:null, w:0, h:0, size:0, name:'' };
const out=document.getElementById('out'), sel=document.getElementById('fmt'); let lastUrl=null;
TKU.imageInput(img=>{ imgState=img; document.getElementById('ctrl').classList.remove('hidden'); out.textContent='—';
  document.getElementById('origInfo').textContent=`Original: ${img.w}×${img.h} px, ${TKU.kb(img.size)}`; });
document.getElementById('go').addEventListener('click', ()=>{
  if(!imgState.img) return;
  const fmt=sel.value, canvas=document.createElement('canvas'); canvas.width=imgState.w; canvas.height=imgState.h;
  const ctx=canvas.getContext('2d'); if(fmt==='image/jpeg'){ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);} ctx.drawImage(imgState.img,0,0);
  canvas.toBlob(blob=>{
    if(!blob||blob.type!==fmt){ out.textContent='This format is not supported by your browser. Choose another format.'; return; }
    if(lastUrl) URL.revokeObjectURL(lastUrl); lastUrl=URL.createObjectURL(blob);
    const ext=fmt==='image/png'?'png':fmt==='image/webp'?'webp':'jpg', name=`${TKU.base(imgState.name)}.${ext}`;
    out.innerHTML=`Converted: <strong>${TKU.kb(blob.size)}</strong> (${ext.toUpperCase()})<br><a class="btn btn-primary" href="${lastUrl}" download="${TKU.esc(name)}" style="margin-top:8px">Download ${TKU.esc(name)}</a>`;
  }, fmt, 0.9);
});
