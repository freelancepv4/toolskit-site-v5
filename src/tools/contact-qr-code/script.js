const vq=s=>s.replace(/([\\,;])/g,'\\$1');
function buildQRContent(){ 
const name=document.getElementById('qrName').value.trim(), phone=document.getElementById('qrContactPhone').value.trim(), email=document.getElementById('qrContactEmail').value.trim();
if(!name) return '';
return `BEGIN:VCARD\nVERSION:3.0\nFN:${vq(name)}\n${phone?('TEL:'+vq(phone)+'\n'):''}${email?('EMAIL:'+vq(email)+'\n'):''}END:VCARD`;
 }
document.getElementById('qrGenBtn').addEventListener('click', ()=>{
  const wrap=document.getElementById('qrCanvasWrap'), dl=document.getElementById('qrDownloads');
  wrap.innerHTML=''; dl.innerHTML='';
  const content=buildQRContent();
  if(!content){ TKU.fail('qrName','Enter a name.'); return; }
  const size=Math.min(600,Math.max(120,parseInt(document.getElementById('qrSize').value)||280));
  const fg=document.getElementById('qrFg').value, bg=document.getElementById('qrBg').value;
  try{
    new QRCode(wrap, { text:content, width:size, height:size, colorDark:fg, colorLight:bg, correctLevel:QRCode.CorrectLevel.M });
    setTimeout(()=>{
      const canvas=wrap.querySelector('canvas'), img=wrap.querySelector('img');
      let dataUrl = canvas ? canvas.toDataURL('image/png') : (img ? img.src : null);
      if(dataUrl){ const a=document.createElement('a'); a.href=dataUrl; a.download='qr-code.png'; a.className='btn btn-primary'; a.textContent='Download PNG'; dl.appendChild(a); }
    }, 50);
  }catch(e){ wrap.textContent='Could not generate QR code. Try shorter input.'; }
});
