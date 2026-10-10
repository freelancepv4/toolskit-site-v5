(()=>{
const S=TKI.str('compound'), N=x=>TKU.n2(x);
function calc(){
  const P=parseFloat(document.getElementById('ciPrincipal').value), contrib=parseFloat(document.getElementById('ciContrib').value);
  const annualRate=parseFloat(document.getElementById('ciRate').value), n=parseInt(document.getElementById('ciFreq').value), years=parseFloat(document.getElementById('ciYears').value);
  const out=document.getElementById('ciResult');
  if([P,contrib,annualRate,years].some(isNaN) || years<=0){ out.dataset.err='1'; out.textContent=S.err_numbers; return; }
  out.dataset.err='0';
  const r=annualRate/100, periods=n*years, ratePerPeriod=r/n, growth=Math.pow(1+ratePerPeriod,periods);
  const fvPrincipal=P*growth, fvContrib = ratePerPeriod===0 ? contrib*periods : contrib*((growth-1)/ratePerPeriod);
  const finalValue=fvPrincipal+fvContrib, totalContrib=P+contrib*periods, estInterest=finalValue-totalContrib;
  out.innerHTML = TKI.f(S.out_final,{v:'<strong>'+N(finalValue)+'</strong>'})+'<br>'+TKI.f(S.out_totals,{contrib:N(totalContrib),interest:N(estInterest)});
}
['ciPrincipal','ciContrib','ciRate','ciYears'].forEach(id=>document.getElementById(id).addEventListener('input',calc));
document.getElementById('ciFreq').addEventListener('change',calc);
calc();
})();
