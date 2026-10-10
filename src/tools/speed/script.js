const cFrom=document.getElementById('cFrom'), cTo=document.getElementById('cTo');

const units = {"m/s":1, "km/h":0.277777778, mph:0.44704, knots:0.514444444};
Object.keys(units).forEach(u=>{ cFrom.add(new Option(u,u)); cTo.add(new Option(u,u)); });
cFrom.value='km/h'; cTo.value='mph';
function calc(){
  const v=parseFloat(document.getElementById('cIn').value); const out=document.getElementById('cResult');
  if(isNaN(v)){ out.textContent='Enter a valid number.'; return; }
  const base=v*units[cFrom.value]; const r=base/units[cTo.value];
  out.innerHTML = `${v} ${cFrom.value} = <strong>${r.toLocaleString(undefined,{maximumFractionDigits:6})}</strong> ${cTo.value}`;
}

['input','change'].forEach(ev=>{ document.getElementById('cIn').addEventListener(ev,calc); cFrom.addEventListener(ev,calc); cTo.addEventListener(ev,calc); });
document.getElementById('cSwap').addEventListener('click', ()=>{ const a=cFrom.value; cFrom.value=cTo.value; cTo.value=a; calc(); });
calc();
