(()=>{
const S=TKI.str('word-counter'), N=x=>TKI.num(x), inp=document.getElementById('wcText'), out=document.getElementById('wcResult');
const graphemes=t=>{try{let n=0;for(const _ of new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(t))n++;return n;}catch(e){return [...t].length;}};
function calc(){
  const t=inp.value;
  if(!t.trim()){out.dataset.err='0';out.textContent='—';return;}
  const words=t.trim().split(/\s+/).filter(Boolean).length;
  const chars=graphemes(t), noSp=graphemes(t.replace(/\s/g,''));
  const sentences=(t.match(/[^.!?…]+[.!?…]+(?=\s|$)|[^.!?…\s][^.!?…]*$/g)||[]).filter(s=>/[\p{L}\p{N}]/u.test(s)).length;
  const paragraphs=t.split(/\n\s*\n/).filter(p=>p.trim()).length;
  const mins=words/200, read=mins<1?S.read_lt1:TKI.f(S.read_n,{n:N(Math.round(mins))});
  const cell=(l,v)=>'<div><dt>'+l+'</dt><dd>'+v+'</dd></div>';
  out.dataset.err='0';
  out.innerHTML='<dl class="wc-grid">'+cell(S.words,N(words))+cell(S.chars,N(chars))+cell(S.chars_ns,N(noSp))+cell(S.sentences,N(sentences))+cell(S.paragraphs,N(paragraphs))+cell(S.reading,read)+'</dl>';
}
inp.addEventListener('input',calc);
calc();
})();
