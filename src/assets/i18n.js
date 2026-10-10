// Shared i18n helpers, loaded on every page after the generated tk-data-<lang>.js (window.TKD).
// TKD.str.<toolId> holds a tool's strings (English base, overridden per language); TKD.ui holds shared interface strings.
window.TKI=(()=>{
 const lang=(document.documentElement.lang||'en').toLowerCase(), base=lang.split('-')[0];
 const f=(s,v)=>String(s==null?'':s).replace(/\{(\w+)\}/g,(m,k)=>v&&k in v?v[k]:m);
 let pr;try{pr=new Intl.PluralRules(lang);}catch(e){pr=null;}
 // p(S,'pages',3) looks up S.pages_one / _few / _many / _other by the language's plural rules
 const p=(S,k,n,v)=>{const r=pr?pr.select(n):(n===1?'one':'other');return f(S[k+'_'+r]!=null?S[k+'_'+r]:(S[k+'_other']!=null?S[k+'_other']:S[k]),Object.assign({n},v));};
 // numbers: translated pages use their own language; English pages follow the visitor's browser locale, like the converters
 const loc=base==='en'?undefined:lang;
 const num=(n,o)=>Number.isFinite(n)?n.toLocaleString(loc,o):'—';
 const ui=(k,d,v)=>f((window.TKD&&TKD.ui&&TKD.ui[k]!=null)?TKD.ui[k]:d,v);
 return {lang,base,f,p,num,ui,loc,t:(k,d)=>(window.TKD&&TKD.ui&&TKD.ui[k])||d||k,str:id=>(window.TKD&&TKD.str&&TKD.str[id])||{}};
})();
