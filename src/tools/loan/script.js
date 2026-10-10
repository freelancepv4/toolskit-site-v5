(()=>{
const S=TKI.str('loan'), N=x=>TKU.n2(x);
function calc(){
  const P=parseFloat(document.getElementById('loanPrincipal').value), annualRate=parseFloat(document.getElementById('loanRate').value), years=parseFloat(document.getElementById('loanTerm').value);
  const out=document.getElementById('loanResult');
  if(isNaN(P)||isNaN(annualRate)||isNaN(years)||years<=0){ out.dataset.err='1'; out.textContent=S.err_numbers; return; }
  out.dataset.err='0';
  const r=annualRate/100/12, n=years*12;
  const payment = r===0 ? P/n : P*r/(1-Math.pow(1+r,-n));
  const total=payment*n, interest=total-P;
  out.innerHTML = TKI.f(S.out_monthly,{v:'<strong>'+N(payment)+'</strong>'})+'<br>'+TKI.f(S.out_totals,{interest:N(interest),total:N(total)});
}
['loanPrincipal','loanRate','loanTerm'].forEach(id=>document.getElementById(id).addEventListener('input',calc));
calc();
})();
