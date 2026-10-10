let imgState = { img:null, w:0, h:0, size:0, type:'', name:'' };
const $=id=>document.getElementById(id), rw=$('rw'), rh=$('rh'), rfmt=$('rfmt'), rq=$('rq'), rqWrap=$('rqWrap'), rnote=$('rnote'), out=$('out');
const MIME={jpeg:'image/jpeg',png:'image/png',webp:'image/webp'}, EXT={'image/jpeg':'jpg','image/png':'png','image/webp':'webp'}, NAME={'image/jpeg':'JPEG','image/png':'PNG','image/webp':'WebP'};
const MAXSIDE=10000, MAXPIXELS=50e6;
const canWebp=(()=>{try{return document.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp')===0;}catch(e){return false;}})();
const srcMime=()=>{const t=imgState.type;if(EXT[t])return t;const m=/\.(jpe?g|png|webp)$/i.exec(imgState.name||'');return m?MIME[m[1].toLowerCase().replace('jpg','jpeg')]:null;};
const mayHaveAlpha=()=>srcMime()!=='image/jpeg';
function sameMime(){const s=srcMime();return s&&(s!=='image/webp'||canWebp)?s:'image/png';}
function fillFormats(){
  const s=srcMime(), same=sameMime(); rfmt.replaceChildren();
  const label=s?`Same as original (${NAME[same]})${same!==s?' – WebP is not supported here':''}`:'Same as original (saved as PNG)';
  rfmt.add(new Option(label,'same')); rfmt.add(new Option('JPEG','image/jpeg')); rfmt.add(new Option('PNG','image/png')); if(canWebp) rfmt.add(new Option('WebP','image/webp')); rfmt.value='same'; sync();
}
const chosen=()=>rfmt.value==='same'?sameMime():rfmt.value;
function sync(){
  const m=chosen(), lossy=m!=='image/png'; rqWrap.hidden=!lossy;
  rnote.hidden=!(m==='image/jpeg'&&mayHaveAlpha()); rnote.textContent='JPEG has no transparency: transparent areas become white.';
}
rfmt.addEventListener('change',sync);
TKU.imageInput(img=>{
  imgState=img; $('ctrl').classList.remove('hidden');
  $('origInfo').textContent=`Original: ${img.w}×${img.h} px, ${TKU.kb(img.size)}${srcMime()?', '+NAME[srcMime()]:''}`;
  rw.value=img.w; rh.value=img.h; [rw,rh].forEach(TKU.clearInvalid); out.textContent='—'; fillFormats();
});
rw.addEventListener('input',()=>{ if($('lock').checked&&imgState.w&&rw.value) rh.value=Math.max(1,Math.round(rw.value*(imgState.h/imgState.w))); });
rh.addEventListener('input',()=>{ if($('lock').checked&&imgState.h&&rh.value) rw.value=Math.max(1,Math.round(rh.value*(imgState.w/imgState.h))); });
let lastUrl=null;
$('go').addEventListener('click',()=>{
  if(!imgState.img) return;
  const w=Math.round(+rw.value), h=Math.round(+rh.value); let bad=false;
  [[rw,w],[rh,h]].forEach(([el,v])=>{ if(!(v>=1)){TKU.setInvalid(el,'Enter a whole number of 1 or more.');bad=true;} else if(v>MAXSIDE){TKU.setInvalid(el,`Enter ${MAXSIDE} or less.`);bad=true;} });
  if(!bad&&w*h>MAXPIXELS){TKU.setInvalid(rw,'This size is too large for a browser to process safely. Use a smaller width or height.');bad=true;}
  const q=+rq.value; if(!rqWrap.hidden&&!(q>=1&&q<=100)){TKU.setInvalid(rq,'Enter a quality from 1 to 100.');bad=true;}
  if(bad){ out.textContent='Fix the highlighted fields.'; (document.querySelector('[aria-invalid=true]')||rw).focus(); return; }
  [rw,rh,rq].forEach(TKU.clearInvalid);
  const mime=chosen(), canvas=document.createElement('canvas'); canvas.width=w; canvas.height=h;
  const ctx=canvas.getContext('2d'); if(!ctx){out.textContent='Could not resize this image in your browser.';return;}
  if(mime==='image/jpeg'){ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);}
  ctx.imageSmoothingEnabled=true; ctx.imageSmoothingQuality='high'; ctx.drawImage(imgState.img,0,0,w,h);
  canvas.toBlob(blob=>{
    if(!blob||blob.type!==mime){ out.textContent=`Could not save as ${NAME[mime]} in this browser. Choose another format.`; return; }
    if(lastUrl) URL.revokeObjectURL(lastUrl); lastUrl=URL.createObjectURL(blob);
    const name=`${TKU.base(imgState.name)}-${w}x${h}.${EXT[mime]}`;
    const bigger=blob.size>imgState.size&&w*h<=imgState.w*imgState.h;
    out.innerHTML=`New size: <strong>${w}×${h} px</strong>, ${NAME[mime]}, ${TKU.kb(blob.size)}${bigger?'<br><span class="note">This file is larger than your original. Try a lower quality, or save as JPEG or WebP.</span>':''}<br><a class="btn btn-primary" href="${lastUrl}" download="${TKU.esc(name)}" style="margin-top:8px">Download ${TKU.esc(name)}</a>`;
  }, mime, mime==='image/png'?undefined:q/100);
});
