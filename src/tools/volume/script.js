const cFrom=document.getElementById('cFrom'), cTo=document.getElementById('cTo');

const units = {liters:1, milliliters:0.001, "cubic meters":1000, "us gallons":3.785411784, "us fluid ounces":0.0295735296, cups:0.2365882365, "us pints":0.473176473, "imperial pints":0.56826125, "imperial gallons":4.54609};
Object.keys(units).forEach(u=>{ cFrom.add(new Option(u,u)); cTo.add(new Option(u,u)); });
cFrom.value='liters'; cTo.value='us gallons';
function calc(){
  const v=parseFloat(document.getElementById('cIn').value); const out=document.getElementById('cResult');
  if(isNaN(v)){ out.textContent='Enter a valid number.'; return; }
  const base=v*units[cFrom.value]; const r=base/units[cTo.value];
  out.innerHTML = `${v} ${cFrom.value} = <strong>${r.toLocaleString(undefined,{maximumFractionDigits:6})}</strong> ${cTo.value}`;
}

['input','change'].forEach(ev=>{ document.getElementById('cIn').addEventListener(ev,calc); cFrom.addEventListener(ev,calc); cTo.addEventListener(ev,calc); });
document.getElementById('cSwap').addEventListener('click', ()=>{ const a=cFrom.value; cFrom.value=cTo.value; cTo.value=a; calc(); });
calc();
