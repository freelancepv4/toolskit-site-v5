(()=>{
const S=TKI.str('percentage'), N=(x,o)=>TKI.num(x,Object.assign({maximumFractionDigits:2},o)), B=t=>'<strong>'+t+'</strong>';
const v=id=>parseFloat(document.getElementById(id).value);
const show=(id,html,bad)=>{const o=document.getElementById(id);o.dataset.err=bad?'1':'0';o[bad?'textContent':'innerHTML']=html;};
function a(){const p=v('pcA1'),y=v('pcA2');if(isNaN(p)||isNaN(y))return show('pcRes1',S.err_numbers,1);show('pcRes1',TKI.f(S.a_res,{p:N(p),y:N(y),r:B(N(p/100*y))}));}
function b(){const x=v('pcB1'),y=v('pcB2');if(isNaN(x)||isNaN(y))return show('pcRes2',S.err_numbers,1);if(y===0)return show('pcRes2',S.err_zero_whole,1);show('pcRes2',TKI.f(S.b_res,{x:N(x),y:N(y),r:B(N(x/y*100))}));}
function c(){const f=v('pcC1'),t=v('pcC2');if(isNaN(f)||isNaN(t))return show('pcRes3',S.err_numbers,1);if(f===0)return show('pcRes3',S.err_zero_from,1);
  const ch=(t-f)/Math.abs(f)*100, k=ch>0?S.c_up:ch<0?S.c_down:S.c_same;show('pcRes3',TKI.f(k,{r:B(N(Math.abs(ch))),f:N(f),t:N(t),d:N(Math.abs(t-f))}));}
function d(){const pr=v('pcD1'),p=v('pcD2');if(isNaN(pr)||isNaN(p))return show('pcRes4',S.err_numbers,1);const save=pr*p/100;show('pcRes4',TKI.f(S.d_res,{fin:B(N(pr-save)),save:N(save)}));}
const map={pcA1:a,pcA2:a,pcB1:b,pcB2:b,pcC1:c,pcC2:c,pcD1:d,pcD2:d};
Object.keys(map).forEach(id=>document.getElementById(id).addEventListener('input',map[id]));
a();b();c();d();
})();
