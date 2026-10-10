(()=>{
const S=TKI.str('vat'), N=x=>TKU.n2(x);
function calc(){
  const amount=parseFloat(document.getElementById('vatAmount').value), rate=parseFloat(document.getElementById('vatRate').value);
  const dir=document.getElementById('vatDir').value, out=document.getElementById('vatResult');
  if(isNaN(amount)||isNaN(rate)){ out.dataset.err='1'; out.textContent=S.err_numbers; return; }
  out.dataset.err='0';
  let net,gross,vat;
  if(dir==='net-to-gross'){ net=amount; gross=net*(1+rate/100); vat=gross-net; } else { gross=amount; net=gross/(1+rate/100); vat=gross-net; }
  out.innerHTML = TKI.f(S.out,{net:'<strong>'+N(net)+'</strong>',vat:N(vat),gross:'<strong>'+N(gross)+'</strong>'});
}
['vatAmount','vatRate'].forEach(id=>document.getElementById(id).addEventListener('input',calc));
document.getElementById('vatDir').addEventListener('change',calc);
calc();
})();
