// Shared workspace for the 6 PDF tools. All processing runs in the browser; same pdf-lib / pdf.js operations as the original pages.
// Every user-visible string comes from TKD.str.pdf (src/strings/pdf.json), so the workspace can be shown in any language.
(()=>{
// Libraries are served from ToolsKit's own /assets/vendor/ folder (no third-party CDN): pdf-lib 1.17.1, pdf.js 3.11.174, JSZip 3.10.1. See THIRD_PARTY_NOTICES.md.
const V=new URL('vendor/',document.currentScript.src).href, L={lib:V+'pdf-lib.min.js',pdfjs:V+'pdf.min.js',zip:V+'jszip.min.js'};
const S=TKI.str('pdf'), F=TKI.f, N=(n,o)=>TKI.num(n,o);
const MAX=150*1048576, $=(s,r=document)=>r.querySelector(s);
const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e;};
const d1={minimumFractionDigits:1,maximumFractionDigits:1};
const fmt=n=>n<1024?N(n)+' B':n<1048576?N(n/1024,d1)+' KB':N(n/1048576,d1)+' MB';
const loaded={}, lib=k=>loaded[k]||(loaded[k]=new Promise((ok,no)=>{const s=el('script');s.src=L[k];s.onload=()=>{if(k==='pdfjs')pdfjsLib.GlobalWorkerOptions.workerSrc=V+'pdf.worker.min.js';ok();};s.onerror=()=>{delete loaded[k];no(new Error('LOAD'));};document.head.append(s);}));
const isPdf=f=>f.type==='application/pdf'||/\.pdf$/i.test(f.name), isImg=f=>/^image\/(jpeg|png)$/.test(f.type)||/\.(jpe?g|png)$/i.test(f.name);
const base=n=>n.replace(/\.[^.]+$/,'')||'file', out=(name,d,type)=>{const b=new Blob([d],{type});return {name,blob:b,size:b.size};};
const human=e=>{const m=(e&&(e.message||e.name))||''; return /encrypt|password/i.test(m)?S.err_password:m==='LOAD'?S.err_load:S.err_generic;};
const pdfPages=async f=>(await PDFLib.PDFDocument.load(await f.arrayBuffer())).getPageCount();
const T={
merge:{lib:['lib'],kind:'pdf',multi:1,reorder:1,min:2,go:S.merge_go,busy:S.merge_busy,count:pdfPages,
 async run(fs,o,p){const {PDFDocument}=PDFLib,m=await PDFDocument.create();let i=0;for(const x of fs){const s=await PDFDocument.load(await x.file.arrayBuffer());(await m.copyPages(s,s.getPageIndices())).forEach(q=>m.addPage(q));p(++i/fs.length);}
  return {outs:[out(S.out_merged,await m.save(),'application/pdf')],info:[F(S.info_merged_files,{n:N(fs.length)}),F(S.info_total_pages,{n:N(m.getPageCount())})]};}},
split:{lib:['lib'],kind:'pdf',go:S.split_go,busy:S.split_busy,count:pdfPages,
 opts:`<div class="field"><label for="range">${S.split_label}</label><input id="range" type="text" inputmode="numeric" placeholder="${S.split_placeholder}" autocomplete="off" aria-describedby="rh"><p class="help" id="rh"></p></div>`,
 onrender:(r,fs)=>{if(fs[0])$('#rh',r).textContent=F(S.split_help,{n:fs[0].pages?N(fs[0].pages):'?'});},read:r=>$('#range',r).value,
 async run(fs,v){const max=fs[0].pages,idx=new Set(),bad=[];v.split(',').map(s=>s.trim()).filter(Boolean).forEach(t=>{const m=t.match(/^(\d+)(?:\s*-\s*(\d+))?$/);if(!m){bad.push(t);return;}const a=+m[1],b=m[2]?+m[2]:a;if(a<1||b<a||b>max){bad.push(t);return;}for(let q=a;q<=b;q++)idx.add(q-1);});
  if(!idx.size||bad.length)throw {user:F(S.split_err,{max:N(max)})+(bad.length?' '+F(S.split_err_check,{bad:bad.join(', ')}):'')};
  const {PDFDocument}=PDFLib,s=await PDFDocument.load(await fs[0].file.arrayBuffer()),o=await PDFDocument.create();(await o.copyPages(s,[...idx].sort((a,b)=>a-b))).forEach(q=>o.addPage(q));
  return {outs:[out(base(fs[0].file.name)+S.out_extracted_suffix,await o.save(),'application/pdf')],info:[F(S.info_extracted,{n:N(idx.size),max:N(max)})]};}},
rotate:{lib:['lib'],kind:'pdf',go:S.rotate_go,busy:S.rotate_busy,count:pdfPages,
 opts:`<fieldset class="ws-fs"><legend>${S.rotate_legend}</legend><label><input type="radio" name="deg" value="90" checked> ${S.rotate_cw}</label><label><input type="radio" name="deg" value="180"> 180°</label><label><input type="radio" name="deg" value="270"> ${S.rotate_ccw}</label></fieldset>`,
 read:r=>+$('input[name=deg]:checked',r).value,
 async run(fs,deg){const {PDFDocument,degrees}=PDFLib,d=await PDFDocument.load(await fs[0].file.arrayBuffer());d.getPages().forEach(p=>p.setRotation(degrees((p.getRotation().angle+deg)%360)));
  return {outs:[out(base(fs[0].file.name)+S.out_rotated_suffix,await d.save(),'application/pdf')],info:[F(S.info_rotated,{n:N(d.getPageCount()),deg:N(deg)})]};}},
compress:{lib:['lib'],kind:'pdf',go:S.compress_go,busy:S.compress_busy,count:pdfPages,
 async run(fs){const f=fs[0].file,b=await f.arrayBuffer(),d=await PDFLib.PDFDocument.load(b),r=await d.save({useObjectStreams:true}),sm=r.byteLength<b.byteLength;
  return {outs:[out(base(f.name)+S.out_compressed_suffix,r,'application/pdf')],info:[F(S.info_original,{size:fmt(b.byteLength)}),F(S.info_result,{size:fmt(r.byteLength)})+(sm?' '+F(S.info_smaller,{pct:N(Math.max(0,100-r.byteLength/b.byteLength*100),d1)}):'')],warn:sm?'':S.compress_warn};}},
p2i:{lib:['pdfjs','zip'],kind:'pdf',go:S.p2i_go,busy:S.p2i_busy,
 count:async f=>(await pdfjsLib.getDocument({data:await f.arrayBuffer()}).promise).numPages,
 opts:`<div class="field"><label for="scale">${S.p2i_quality}</label><select id="scale"><option value="1.5">${S.p2i_standard}</option><option value="2.5">${S.p2i_high}</option></select></div>`,read:r=>+$('#scale',r).value,
 async run(fs,sc,p){const f=fs[0].file,pdf=await pdfjsLib.getDocument({data:await f.arrayBuffer()}).promise,bl=[];
  for(let i=1;i<=pdf.numPages;i++){const pg=await pdf.getPage(i),vp=pg.getViewport({scale:sc}),c=el('canvas');c.width=vp.width;c.height=vp.height;await pg.render({canvasContext:c.getContext('2d'),viewport:vp}).promise;
   const b=await new Promise(r=>c.toBlob(r,'image/png'));c.width=c.height=0;if(!b)throw {user:S.p2i_err};bl.push(b);p(i/pdf.numPages);}
  const n=base(f.name);if(bl.length===1)return {outs:[{name:n+S.out_page_png_suffix,blob:bl[0],size:bl[0].size}],info:[S.p2i_info_one]};
  const z=new JSZip();bl.forEach((b,i)=>z.file(F(S.zip_entry,{n:i+1}),b));const zb=await z.generateAsync({type:'blob'});return {outs:[{name:n+S.out_pages_zip_suffix,blob:zb,size:zb.size}],info:[F(S.p2i_info_zip,{n:N(bl.length)})]};}},
i2p:{lib:['lib'],kind:'img',multi:1,go:S.i2p_go,busy:S.i2p_busy,
 async run(fs,o,p){const d=await PDFLib.PDFDocument.create();let i=0;for(const x of fs){const b=await x.file.arrayBuffer(),png=x.file.type==='image/png'||/\.png$/i.test(x.file.name),im=png?await d.embedPng(b):await d.embedJpg(b),pg=d.addPage([im.width,im.height]);pg.drawImage(im,{x:0,y:0,width:im.width,height:im.height});p(++i/fs.length);}
  return {outs:[out(S.out_images,await d.save(),'application/pdf')],info:[F(S.i2p_info,{n:N(fs.length)})]};}}
};
function mount(root){
 const C=T[root.dataset.tool],NEXT=JSON.parse(root.dataset.next||'[]'),NEXTL=root.dataset.nextLabel||'';let fs=[],urls=[],busy=false;
 // initial texts come from the server-rendered drop zone (already in the page language), so nothing is defined twice
 C.title=$('#title',root).textContent;C.hint=$('#hint',root).textContent;C.choose=$('#choose',root).firstChild.nodeValue;const OR=$('.tk-drop-msg',root).textContent;
 root.innerHTML=`<div class="tk-drop" id="drop"><p class="tk-drop-title" id="title"></p><p class="tk-drop-msg">${OR}</p><label class="btn btn-primary" id="choose">x<input class="tk-vh" type="file" id="inp"></label><p class="tk-drop-msg" id="hint"></p></div>
<div id="list" hidden></div><div id="opts" hidden></div><div class="cta-row" id="act" hidden style="justify-content:flex-start"><button class="btn btn-primary" id="go" type="button"></button><button class="btn btn-secondary" id="rs" type="button">${S.reset_all}</button></div>
<div class="tk-progress" id="prog" role="progressbar" aria-label="${S.progress}" aria-valuemin="0" aria-valuemax="100" hidden><span></span></div><p class="tk-drop-msg" id="st" role="status" aria-live="polite"></p><div class="tk-alert tk-alert-err" id="err" role="alert" hidden></div><div class="ws-res" id="res" hidden></div>`;
 const g=i=>$('#'+i,root),drop=g('drop'),inp=g('inp'),list=g('list'),opts=g('opts'),act=g('act'),go=g('go'),prog=g('prog'),st=g('st'),err=g('err'),res=g('res'),title=g('title');
 inp.accept=C.kind==='pdf'?'application/pdf,.pdf':'image/jpeg,image/png,.jpg,.jpeg,.png'; if(C.multi)inp.multiple=true;
 title.textContent=C.title;g('choose').firstChild.nodeValue=C.choose;g('hint').textContent=C.hint;go.textContent=C.go;if(C.opts)opts.innerHTML=C.opts;
 const showErr=m=>{err.textContent=m;err.hidden=false;};
 const p=f=>{prog.removeAttribute('data-indeterminate');const v=Math.round(f*100);prog.style.setProperty('--p',v+'%');prog.setAttribute('aria-valuenow',v);};
 async function add(l){
  err.hidden=true;res.hidden=true;const bad=[];let ok=[...l].filter(f=>{if(!(C.kind==='pdf'?isPdf(f):isImg(f))){bad.push(F(S.bad_type,{name:f.name}));return false;}if(f.size>MAX){bad.push(F(S.too_large,{name:f.name,limit:fmt(MAX)}));return false;}return true;});
  if(bad.length)showErr(bad.join(' ')+' '+(C.kind==='pdf'?S.choose_pdf:S.use_images));
  if(!ok.length)return; if(!C.multi){ok=ok.slice(0,1);fs=[];}
  st.textContent=S.reading;try{for(const k of C.lib)await lib(k);}catch(e){showErr(human(e));st.textContent='';return;}
  for(const f of ok){const o={file:f};if(C.count){try{o.pages=await C.count(f);}catch(e){o.err=human(e);}}fs.push(o);}
  st.textContent='';render();
 }
 function render(){
  list.replaceChildren();const has=fs.length>0;
  fs.forEach((o,i)=>{const r=el('div','tk-file'),n=el('div','tk-file-name');n.append(el('strong','',(C.multi?(i+1)+'. ':'')+o.file.name),el('div','tk-drop-msg',[fmt(o.file.size),o.pages?F(S.pages_label,{n:N(o.pages)}):''].filter(Boolean).join(' · ')));
   if(o.err)n.append(el('div','err-text',o.err));r.append(n);
   if(C.reorder)[['↑',-1,'up'],['↓',1,'down']].forEach(([s,d,w],k)=>{const b=el('button','btn btn-secondary btn-sm',s);b.type='button';b.setAttribute('aria-label',F(w==='up'?S.move_up:S.move_down,{name:o.file.name}));b.disabled=i+d<0||i+d>=fs.length;
    b.onclick=()=>{[fs[i],fs[i+d]]=[fs[i+d],fs[i]];render();const nb=list.children[i+d].querySelectorAll('button');(nb[k].disabled?nb[1-k]:nb[k]).focus();};r.append(b);});
   const x=el('button','btn btn-danger btn-sm',S.remove);x.type='button';x.setAttribute('aria-label',F(S.remove_aria,{name:o.file.name}));x.onclick=()=>{fs.splice(i,1);render();inp.focus();};r.append(x);list.append(r);});
  list.hidden=opts.hidden=act.hidden=!has;drop.hidden=has&&!C.multi;title.textContent=has?S.add_more:C.title;
  go.disabled=fs.length<(C.min||1)||fs.some(o=>o.err);st.textContent=has&&C.min&&fs.length<C.min?F(S.add_min,{n:N(C.min)}):'';
  if(C.onrender)C.onrender(root,fs);
 }
 function reset(){urls.forEach(URL.revokeObjectURL);urls=[];fs=[];res.hidden=err.hidden=prog.hidden=true;st.textContent='';inp.value='';title.textContent=C.title;render();inp.focus();}
 g('rs').onclick=reset;
 inp.onchange=()=>{add(inp.files);inp.value='';};
 ['dragenter','dragover'].forEach(e=>drop.addEventListener(e,ev=>{ev.preventDefault();drop.dataset.state='drag';}));
 ['dragleave','drop'].forEach(e=>drop.addEventListener(e,ev=>{ev.preventDefault();delete drop.dataset.state;}));
 drop.addEventListener('drop',ev=>add(ev.dataTransfer.files));
 go.onclick=async()=>{
  if(busy)return;busy=true;err.hidden=res.hidden=true;go.classList.add('is-loading');go.setAttribute('aria-busy','true');go.disabled=true;
  prog.hidden=false;prog.setAttribute('data-indeterminate','');prog.removeAttribute('aria-valuenow');prog.style.setProperty('--p','0%');drop.dataset.state='busy';st.textContent=C.busy;
  await new Promise(r=>setTimeout(r,30));
  try{finish(await C.run(fs,C.read?C.read(root):null,p));}catch(e){showErr(e&&e.user?e.user:human(e));st.textContent='';}
  finally{busy=false;go.classList.remove('is-loading');go.removeAttribute('aria-busy');go.disabled=false;prog.hidden=true;delete drop.dataset.state;}
 };
 function finish(r){
  st.textContent='';urls.forEach(URL.revokeObjectURL);urls=[];res.replaceChildren();
  const box=el('div','tk-alert tk-alert-ok'),in_=el('div'),h=el('h2','',S.done);h.tabIndex=-1;in_.append(h,...r.info.map(t=>el('p','',t)));box.append(in_);res.append(box);
  if(r.warn){const w=el('div','tk-alert tk-alert-warn',r.warn);w.style.marginTop='var(--s3)';res.append(w);}
  const row=el('div','cta-row');r.outs.forEach(o=>{const a=el('a','btn btn-primary',F(S.download,{name:o.name,size:fmt(o.size)})),u=URL.createObjectURL(o.blob);urls.push(u);a.href=u;a.download=o.name;row.append(a);});
  const back=el('button','btn btn-secondary',S.change_settings);back.type='button';back.onclick=()=>{res.hidden=true;render();go.focus();};
  const again=el('button','btn btn-secondary',S.start_over);again.type='button';again.onclick=reset;row.append(back,again);res.append(row);
  if(NEXT.length){const n=el('p','ws-next');n.append(NEXTL+' ');NEXT.forEach(([t,u])=>{const a=el('a','',t);a.href=u;n.append(a);n.append(' ');});res.append(n);}
  list.hidden=opts.hidden=act.hidden=drop.hidden=true;res.hidden=false;h.focus();document.dispatchEvent(new CustomEvent('tk:complete'));
 }
 render();
}
const r=$('#tk-ws');if(r)mount(r);
})();
