let cvExp=[{company:'',role:'',dates:'',desc:''}], cvEdu=[{school:'',degree:'',dates:''}];
function cvField(kind,i,f,label,val,wide){const id=`cv-${kind}-${f}-${i}`;return `<div class="field"${wide?' style="flex:1 1 100%"':''}><label for="${id}">${label}</label><input type="text" id="${id}" value="${esc(val)}" data-${kind}="${i}" data-f="${f}"></div>`;}
function renderCvExp(){
  document.getElementById('cvExpList').innerHTML = cvExp.map((e,i)=>`
    <div class="cv-item" role="group" aria-label="Experience ${i+1}">
      <div class="row">${cvField('exp',i,'company','Company',e.company)}${cvField('exp',i,'role','Role',e.role)}${cvField('exp',i,'dates','Dates',e.dates)}</div>
      <div class="row">${cvField('exp',i,'desc','Description',e.desc,1)}</div>
      ${cvExp.length>1?`<button type="button" class="btn btn-secondary btn-sm" data-rmexp="${i}" aria-label="Remove experience ${i+1}">Remove</button>`:''}
    </div>`).join('');
  document.querySelectorAll('[data-exp]').forEach(inp=>inp.addEventListener('input', e=>{ cvExp[e.target.dataset.exp][e.target.dataset.f]=e.target.value; updateCvPreview(); }));
  document.querySelectorAll('[data-rmexp]').forEach(btn=>btn.addEventListener('click', ()=>{ cvExp.splice(btn.dataset.rmexp,1); renderCvExp(); updateCvPreview(); document.getElementById('cvAddExp').focus(); }));
}
function renderCvEdu(){
  document.getElementById('cvEduList').innerHTML = cvEdu.map((e,i)=>`
    <div class="cv-item" role="group" aria-label="Education ${i+1}">
      <div class="row">${cvField('edu',i,'school','School',e.school)}${cvField('edu',i,'degree','Degree',e.degree)}${cvField('edu',i,'dates','Dates',e.dates)}</div>
      ${cvEdu.length>1?`<button type="button" class="btn btn-secondary btn-sm" data-rmedu="${i}" aria-label="Remove education ${i+1}">Remove</button>`:''}
    </div>`).join('');
  document.querySelectorAll('[data-edu]').forEach(inp=>inp.addEventListener('input', e=>{ cvEdu[e.target.dataset.edu][e.target.dataset.f]=e.target.value; updateCvPreview(); }));
  document.querySelectorAll('[data-rmedu]').forEach(btn=>btn.addEventListener('click', ()=>{ cvEdu.splice(btn.dataset.rmedu,1); renderCvEdu(); updateCvPreview(); document.getElementById('cvAddEdu').focus(); }));
}
document.getElementById('cvAddExp').addEventListener('click', ()=>{ cvExp.push({company:'',role:'',dates:'',desc:''}); renderCvExp(); updateCvPreview(); });
document.getElementById('cvAddEdu').addEventListener('click', ()=>{ cvEdu.push({school:'',degree:'',dates:''}); renderCvEdu(); updateCvPreview(); });
function esc(s){ return (s||'').replace(/[<>&"]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c])); }
function updateCvPreview(){
  const name=esc(document.getElementById('cvName').value)||'Your Name', title=esc(document.getElementById('cvTitle').value);
  const contact=[document.getElementById('cvEmail').value,document.getElementById('cvPhone').value,document.getElementById('cvLocation').value].filter(Boolean).map(esc).join(' · ');
  const summary=esc(document.getElementById('cvSummary').value);
  const skills=document.getElementById('cvSkills').value.split(',').map(s=>s.trim()).filter(Boolean).map(esc);
  let html=`<p class="cv-name">${name}</p>`;
  if(title) html+=`<p style="margin:2px 0;color:#555">${title}</p>`;
  if(contact) html+=`<p style="margin:2px 0;font-size:.85rem;color:#555">${contact}</p>`;
  if(summary) html+=`<p style="margin-top:14px">${summary}</p>`;
  if(skills.length) html+=`<h3 class="cv-sec">Skills</h3><p style="font-size:.9rem">${skills.join(' · ')}</p>`;
  if(cvExp.some(e=>e.company||e.role)){ html+=`<h3 class="cv-sec">Experience</h3>`;
    cvExp.forEach(e=>{ if(e.company||e.role) html+=`<div style="margin-bottom:8px"><strong>${esc(e.role)}</strong>${e.company?' — '+esc(e.company):''} <span style="color:#777;font-size:.85rem">${esc(e.dates)}</span><br><span style="font-size:.9rem">${esc(e.desc)}</span></div>`; }); }
  if(cvEdu.some(e=>e.school||e.degree)){ html+=`<h3 class="cv-sec">Education</h3>`;
    cvEdu.forEach(e=>{ if(e.school||e.degree) html+=`<div style="margin-bottom:6px"><strong>${esc(e.degree)}</strong>${e.school?' — '+esc(e.school):''} <span style="color:#777;font-size:.85rem">${esc(e.dates)}</span></div>`; }); }
  document.getElementById('cvPreview').innerHTML=html;
}
['cvName','cvTitle','cvEmail','cvPhone','cvLocation','cvSummary','cvSkills'].forEach(id=>document.getElementById(id).addEventListener('input', updateCvPreview));
document.getElementById('cvPrint').addEventListener('click', ()=>window.print());
document.getElementById('cvPrint2').addEventListener('click', ()=>window.print());
const cvGrid=document.getElementById('cvGrid');
function cvView(v,focus){cvGrid.dataset.view=v;document.getElementById('cvTabEdit').setAttribute('aria-pressed',v==='edit');document.getElementById('cvTabPrev').setAttribute('aria-pressed',v==='preview');
  if(focus){const h=document.getElementById(v==='edit'?'cvEditH':'cvPrevH');h.scrollIntoView({block:'start'});h.focus({preventScroll:true});}}
document.getElementById('cvTabEdit').addEventListener('click',()=>cvView('edit',1));
document.getElementById('cvTabPrev').addEventListener('click',()=>cvView('preview',1));
document.getElementById('cvSeePrev').addEventListener('click',()=>cvView('preview',1));
document.getElementById('cvBackEdit').addEventListener('click',()=>cvView('edit',1));
document.getElementById('cvSave').addEventListener('click', ()=>{
  const status=document.getElementById('cvSaveStatus');
  try{
    const draft={name:document.getElementById('cvName').value,title:document.getElementById('cvTitle').value,email:document.getElementById('cvEmail').value,phone:document.getElementById('cvPhone').value,location:document.getElementById('cvLocation').value,summary:document.getElementById('cvSummary').value,skills:document.getElementById('cvSkills').value,exp:cvExp,edu:cvEdu};
    localStorage.setItem('toolskit_cv_draft', JSON.stringify(draft));
    status.textContent='Draft saved to this browser.';
  }catch(e){ status.textContent='Could not save (local storage unavailable).'; }
});
document.getElementById('cvClear').addEventListener('click', ()=>{ try{localStorage.removeItem('toolskit_cv_draft');}catch(e){} document.getElementById('cvSaveStatus').textContent='Draft cleared.'; });
(function loadDraft(){
  try{
    const raw=localStorage.getItem('toolskit_cv_draft'); if(!raw) return;
    const d=JSON.parse(raw);
    document.getElementById('cvName').value=d.name||''; document.getElementById('cvTitle').value=d.title||'';
    document.getElementById('cvEmail').value=d.email||''; document.getElementById('cvPhone').value=d.phone||'';
    document.getElementById('cvLocation').value=d.location||''; document.getElementById('cvSummary').value=d.summary||'';
    document.getElementById('cvSkills').value=d.skills||''; cvExp=d.exp&&d.exp.length?d.exp:cvExp; cvEdu=d.edu&&d.edu.length?d.edu:cvEdu;
  }catch(e){}
})();
renderCvExp(); renderCvEdu(); updateCvPreview();
