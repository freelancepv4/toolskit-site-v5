const cFrom=document.getElementById('cFrom'), cTo=document.getElementById('cTo');

const units = {meters:1, kilometers:1000, centimeters:0.01, millimeters:0.001, miles:1609.344, yards:0.9144, feet:0.3048, inches:0.0254};
Object.keys(units).forEach(u=>{ cFrom.add(new Option(u,u)); cTo.add(new Option(u,u)); });
cFrom.value='meters'; cTo.value='feet';
function calc(){
  const v=parseFloat(document.getElementById('cIn').value); const out=document.getElementById('cResult');
  if(isNaN(v)){ out.textContent='Enter a valid number.'; return; }
  const base=v*units[cFrom.value]; const r=base/units[cTo.value];
  out.innerHTML = `${v} ${cFrom.value} = <strong>${r.toLocaleString(undefined,{maximumFractionDigits:6})}</strong> ${cTo.value}`;
}

['input','change'].forEach(ev=>{ document.getElementById('cIn').addEventListener(ev,calc); cFrom.addEventListener(ev,calc); cTo.addEventListener(ev,calc); });
document.getElementById('cSwap').addEventListener('click', ()=>{ const a=cFrom.value; cFrom.value=cTo.value; cTo.value=a; calc(); });
calc();
