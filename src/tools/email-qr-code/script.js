function buildQRContent(){ 
const email=document.getElementById('qrEmail').value.trim(), subject=document.getElementById('qrSubject').value.trim();
if(!email) return '';
return `mailto:${email}${subject?('?subject='+encodeURIComponent(subject)):''}`;
 }
document.getElementById('qrGenBtn').addEventListener('click', ()=>{
  const wrap=document.getElementById('qrCanvasWrap'), dl=document.getElementById('qrDownloads');
  wrap.innerHTML=''; dl.innerHTML='';
  const content=buildQRContent();
  if(!content){ TKU.fail('qrEmail','Enter an email address.'); return; }
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
