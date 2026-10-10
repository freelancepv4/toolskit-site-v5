// Privacy-first analytics layer. Does NOTHING (no requests, no cookies) unless the site owner sets
// window.TK_ANALYTICS={ga4:'G-…'} AND the visitor has granted consent via TKA.setConsent(true).
// Only allow-listed, non-personal parameters are ever sent; file names, contents, input values and search text are never included.
(()=>{
 const CFG=window.TK_ANALYTICS||{}, ALLOW=['tool_id','category','mode','result_count'];
 const consent=()=>{try{return localStorage.getItem('tk_consent')==='granted';}catch(e){return false;}};
 let on=false;
 const boot=()=>{ if(on||!CFG.ga4||!consent())return; on=true; window.dataLayer=window.dataLayer||[]; window.gtag=function(){dataLayer.push(arguments);}; gtag('js',new Date()); gtag('config',CFG.ga4);
  const s=document.createElement('script'); s.async=true; s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(CFG.ga4); document.head.append(s); };
 const tool=()=>{const T=(window.TK&&TK.TOOLS)||[];return T.find(t=>location.pathname.endsWith(t.url));};
 const track=(name,p={})=>{ const c={}; ALLOW.forEach(k=>{if(p[k]!=null)c[k]=String(p[k]).slice(0,60);});
  c.lang=p.lang||document.documentElement.lang||'en'; c.mode=/[?&]embed=1/.test(location.search)?'embed':'full'; const t=tool(); if(t&&!c.tool_id){c.tool_id=t.id;c.category=t.catKey;}
  document.dispatchEvent(new CustomEvent('tk:event',{detail:{name,params:c}})); if(on&&window.gtag)gtag('event',name,c); };
 window.TKA={track,boot,setConsent:v=>{try{localStorage.setItem('tk_consent',v?'granted':'denied');}catch(e){} if(v)boot();}};
 boot(); let used=false;
 if(tool()) track('tool_open');
 const use=()=>{if(!used&&tool()){used=true;track('tool_use');}}; ['input','change','drop'].forEach(e=>document.addEventListener(e,ev=>{if(ev.target.closest&&ev.target.closest('main .panel'))use();},true));
 document.addEventListener('tk:complete',()=>track('tool_complete'));
 document.addEventListener('tk:search',e=>track('search',{result_count:e.detail.result_count}));
 document.addEventListener('tk:searchclick',e=>track('search_result_click',{tool_id:e.detail.tool_id}));
 document.addEventListener('click',e=>{ if(e.target.closest('a[download]'))track('download'); const l=e.target.closest('.tk-lang a'); if(l)track('language_change',{lang:l.getAttribute('lang')||''}); });
})();
