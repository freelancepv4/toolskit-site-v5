// Shared helpers for the non-PDF tools (loaded before each tool's inline script).
window.TKU=(()=>{
 const lg=document.documentElement.lang, loc=lg&&!/^en/i.test(lg)?lg:undefined; // translated pages use their own language; English pages follow the visitor's browser locale, like the converters
 const n2=x=>Number.isFinite(x)?x.toLocaleString(loc,{minimumFractionDigits:2,maximumFractionDigits:2}):'—';
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const kb=b=>b<1048576?(b/1024).toFixed(1)+' KB':(b/1048576).toFixed(2)+' MB';
 const base=n=>(n||'image').replace(/\.[^.]+$/,'')||'image';
 const err=m=>{let a=document.getElementById('tkErr');if(!a){const d=document.getElementById('imgDrop');if(!d)return;a=document.createElement('div');a.id='tkErr';a.className='tk-alert tk-alert-err';a.setAttribute('role','alert');a.style.marginBottom='var(--s3)';d.before(a);}a.textContent=m;a.hidden=!m;};
 // Field-level validation: visible message + aria-invalid + aria-describedby (never colour alone).
 const clearInvalid=el=>{if(!el)return;el.removeAttribute('aria-invalid');const e=document.getElementById(el.id+'-err');if(e){const d=(el.getAttribute('aria-describedby')||'').split(/\s+/).filter(x=>x&&x!==e.id).join(' ');d?el.setAttribute('aria-describedby',d):el.removeAttribute('aria-describedby');e.remove();}};
 const setInvalid=(el,msg)=>{if(!el)return;let e=document.getElementById(el.id+'-err');if(!e){e=document.createElement('p');e.className='err-text';e.id=el.id+'-err';(el.closest('.field')||el.parentNode).append(e);}
  e.textContent=msg;el.setAttribute('aria-invalid','true');const d=(el.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean);if(!d.includes(e.id))d.push(e.id);el.setAttribute('aria-describedby',d.join(' '));
};
 const fail=(id,msg)=>{const el=document.getElementById(id);setInvalid(el,msg);if(el){if(!el.dataset.tkInv){el.dataset.tkInv=1;el.addEventListener('input',()=>clearInvalid(el));}el.focus();}};
 // Image tools: one picker for drop zone + keyboard-accessible button.
 const imageInput=onReady=>{const input=document.getElementById('imgFile'),drop=document.getElementById('imgDrop');
  const load=file=>{if(!file)return;
   if(!/^image\//.test(file.type)&&!/\.(jpe?g|png|webp|gif|bmp|avif)$/i.test(file.name)){err(TKI.ui('img_type','Choose an image file (JPG, PNG or WebP).'));return;}
   const url=URL.createObjectURL(file),img=new Image();
   img.onerror=()=>{URL.revokeObjectURL(url);err(TKI.ui('img_open','This image could not be opened. Try a JPG, PNG or WebP file.'));};
   img.onload=()=>{err('');onReady({img,w:img.naturalWidth,h:img.naturalHeight,size:file.size,type:file.type,name:file.name});};
   img.src=url;};
  input.addEventListener('change',e=>{load(e.target.files[0]);e.target.value='';});
  drop.addEventListener('dragover',e=>{e.preventDefault();drop.dataset.state='drag';});
  ['dragleave','drop'].forEach(t=>drop.addEventListener(t,e=>{e.preventDefault();delete drop.dataset.state;}));
  drop.addEventListener('drop',e=>{if(e.dataTransfer.files.length)load(e.dataTransfer.files[0]);});};
 return {n2,esc,err,kb,base,setInvalid,clearInvalid,fail,imageInput};
})();
document.addEventListener('DOMContentLoaded',()=>{
 const $=s=>document.querySelector(s),p=$('main .panel');
 // ONE polite live region for the whole page. Results are mirrored into it after a short pause, so typing in a calculator
 // does not announce every keystroke, and nothing is announced twice.
 const live=document.createElement('div');live.className='tk-vh';live.id='tkLive';live.setAttribute('role','status');live.setAttribute('aria-live','polite');live.setAttribute('aria-atomic','true');document.body.append(live);
 const say=t=>{live.textContent='';setTimeout(()=>{live.textContent=t;},50);};
 // copy buttons (social generators)
 document.addEventListener('click',e=>{const b=e.target.closest('[data-copy]');if(!b)return;const t=decodeURIComponent(b.dataset.copy),done=()=>{const o=b.textContent;b.textContent=TKI.ui('copied','Copied ✓');say(TKI.ui('copied_sr','Copied to clipboard'));setTimeout(()=>{b.textContent=o;},2000);};
  const fb=()=>{const a=document.createElement('textarea');a.value=t;document.body.append(a);a.select();try{document.execCommand('copy');done();}catch(x){say(TKI.ui('copy_fail','Could not copy. Select the text and copy it manually.'));}a.remove();};
  navigator.clipboard?navigator.clipboard.writeText(t).then(done,fb):fb();});
 if(!p)return;
 // results: announce a settled result once; flag error results
 let timer;const results=[...p.querySelectorAll('.result,#qrCanvasWrap')];
 // tools with several independent result blocks (data-block) announce only the block the user is editing
 let focusRes=null;p.addEventListener('input',e=>{const b=e.target.closest('[data-block]');focusRes=b?b.querySelector('.result'):null;});
 const announce=()=>{clearTimeout(timer);timer=setTimeout(()=>{const last=(focusRes&&focusRes.textContent.trim()?focusRes:null)||results.filter(r=>(r.textContent.trim()&&r.textContent.trim()!=='—')||r.querySelector('canvas,img')).pop();if(!last)return;
   const t=last.id==='qrCanvasWrap'&&last.querySelector('canvas,img')?TKI.ui('qr_ok','QR code generated. Use the Download PNG button.'):last.textContent.replace(/\s+/g,' ').trim();say(t);},700);};
 // error results are flagged by the tool (data-err); the English prefix test only covers the older tools that have not been converted
 const isErr=r=>r.dataset.err==='1'||(r.dataset.err===undefined&&/^(Enter |This format|Could not|Choose )/.test(r.textContent.trim()));
 results.forEach(r=>{if(r.id==='qrCanvasWrap'){r.removeAttribute('role');r.removeAttribute('aria-label');}
  new MutationObserver(()=>{if(r.classList.contains('result'))r.classList.toggle('is-err',isErr(r));announce();}).observe(r,{childList:true,characterData:true,subtree:true});});
 // number fields: visible message + aria-invalid, after the tool's own handler has run
 const nums=[...p.querySelectorAll('input[type=number]')];
 const checkNum=el=>{const v=el.value.trim();let m='';
  if(v===''||el.validity.badInput)m=TKI.ui('enter_number','Enter a number.');
  else if(el.validity.rangeUnderflow)m=TKI.ui('min_msg','Enter a number of {min} or more.',{min:el.min});
  else if(el.validity.rangeOverflow)m=TKI.ui('max_msg','Enter a number of {max} or less.',{max:el.max});
  if(m)TKU.setInvalid(el,m);else TKU.clearInvalid(el);};
 nums.forEach(el=>{['input','change'].forEach(ev=>el.addEventListener(ev,()=>checkNum(el)));});
 // reset button (rendered by the page; this only wires it up)
 const r=document.getElementById('tkReset');
 if(r){const init=[...p.querySelectorAll('input:not([type=file]),select,textarea')].map(e=>[e,/checkbox|radio/.test(e.type)?e.checked:e.value]);
  r.onclick=()=>{init.forEach(([e,v])=>{if(/checkbox|radio/.test(e.type))e.checked=v;else e.value=v;TKU.clearInvalid(e);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));});
   document.querySelectorAll('#qrCanvasWrap,#qrDownloads').forEach(x=>x.replaceChildren());document.querySelectorAll('[id$="Out"]').forEach(x=>x.replaceChildren());
   if(typeof imgState!=='undefined'){imgState={img:null,w:0,h:0,size:0};$('#ctrl')?.classList.add('hidden');const o=$('#out');if(o)o.textContent='—';TKU.err('');}
   const f=p.querySelector('input:not([type=file]),#imgDrop label');if(f)f.focus();};}
 // next-step links that belong to the result: shown once a result exists (file, QR and generator tools)
 const nx=p.querySelector('.tk-next[data-after]');
 if(nx){const upd=()=>{nx.hidden=!p.querySelector('a[download],[data-copy]');};new MutationObserver(upd).observe(p,{childList:true,subtree:true});upd();}
 // QR: low-contrast warning
 const fg=$('#qrFg'),bg=$('#qrBg'),qb=$('#qrGenBtn');
 if(fg&&bg&&qb){const L=h=>{const c=[1,3,5].map(i=>parseInt(h.substr(i,2),16)/255).map(v=>v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4));return .2126*c[0]+.7152*c[1]+.0722*c[2];};
  const w=document.createElement('div');w.className='tk-alert tk-alert-warn';w.hidden=true;w.setAttribute('role','status');w.textContent=TKI.ui('qr_lowcontrast','Low contrast, or a light code on a dark background: this QR code may not scan. Use a dark code on a light background.');qb.before(w);
  const chk=()=>{const a=L(fg.value),b=L(bg.value);w.hidden=!((Math.max(a,b)+.05)/(Math.min(a,b)+.05)<3||a>b);};fg.addEventListener('input',chk);bg.addEventListener('input',chk);chk();}
});
