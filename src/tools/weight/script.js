const cFrom=document.getElementById('cFrom'), cTo=document.getElementById('cTo');

const units = {kilograms:1, grams:0.001, milligrams:0.000001, pounds:0.45359237, ounces:0.028349523125, tonnes:1000, stones:6.35029318};
Object.keys(units).forEach(u=>{ cFrom.add(new Option(u,u)); cTo.add(new Option(u,u)); });
cFrom.value='kilograms'; cTo.value='pounds';
function calc(){
  const v=parseFloat(document.getElementById('cIn').value); const out=document.getElementById('cResult');
  if(isNaN(v)){ out.textContent='Enter a valid number.'; return; }
  const base=v*units[cFrom.value]; const r=base/units[cTo.value];
  out.innerHTML = `${v} ${cFrom.value} = <strong>${r.toLocaleString(undefined,{maximumFractionDigits:6})}</strong> ${cTo.value}`;
}

['input','change'].forEach(ev=>{ document.getElementById('cIn').addEventListener(ev,calc); cFrom.addEventListener(ev,calc); cTo.addEventListener(ev,calc); });
document.getElementById('cSwap').addEventListener('click', ()=>{ const a=cFrom.value; cFrom.value=cTo.value; cTo.value=a; calc(); });
calc();
