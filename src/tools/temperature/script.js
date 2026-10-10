const cFrom=document.getElementById('cFrom'), cTo=document.getElementById('cTo');

const tempConvert = { toCelsius: {celsius:v=>v, fahrenheit:v=>(v-32)*5/9, kelvin:v=>v-273.15},
  fromCelsius: {celsius:c=>c, fahrenheit:c=>c*9/5+32, kelvin:c=>c+273.15} };
['celsius','fahrenheit','kelvin'].forEach(u=>{ cFrom.add(new Option(u,u)); cTo.add(new Option(u,u)); });
cFrom.value='celsius'; cTo.value='fahrenheit';
function calc(){
  const v=parseFloat(document.getElementById('cIn').value); const out=document.getElementById('cResult');
  if(isNaN(v)){ out.textContent='Enter a valid number.'; return; }
  const c=tempConvert.toCelsius[cFrom.value](v); const r=tempConvert.fromCelsius[cTo.value](c);
  out.innerHTML = `${v} ${cFrom.value} = <strong>${r.toLocaleString(undefined,{maximumFractionDigits:4})}</strong> ${cTo.value}`;
}

['input','change'].forEach(ev=>{ document.getElementById('cIn').addEventListener(ev,calc); cFrom.addEventListener(ev,calc); cTo.addEventListener(ev,calc); });
document.getElementById('cSwap').addEventListener('click', ()=>{ const a=cFrom.value; cFrom.value=cTo.value; cTo.value=a; calc(); });
calc();
