(function(){
 'use strict';
 const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
 const data=window.GUIDE_DATA, home=$('#home'), chapters=$$('.chapter'), sidebar=$('#sidebar');
 let active='home', lastFocus=null;
 function read(key){try{return localStorage.getItem(key)}catch{return null}}
 function write(key,value){try{localStorage.setItem(key,value)}catch{}}
 document.body.classList.add('js-ready');
 if(read('wguide-theme')==='night')document.body.classList.add('night');
 if(read('wguide-font')==='large')document.body.classList.add('font-large');
 function progress(){const max=document.documentElement.scrollHeight-innerHeight;$('#reading-progress').style.width=(max>0?Math.min(100,scrollY/max*100):0)+'%'}
 function route(){
   let target=decodeURIComponent(location.hash.slice(1)||'home');
   const element=document.getElementById(target);
   let chapter=element&&element.closest('.chapter');
   if(!element){target='home';chapter=null}
   active=chapter?chapter.id:'home';
   home.hidden=active!=='home';
   chapters.forEach(c=>c.hidden=c.id!==active);
   $$('.sidebar a[data-chapter]').forEach(a=>{const selected=a.dataset.chapter===active;a.classList.toggle('active',selected);selected?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current')});
   sidebar.classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false');
   document.title=(active==='home'?'Light & Shadow':data.chapters.find(c=>c.id===active)?.title)+' — Human Priest / WoW: Forever';
   requestAnimationFrame(()=>{
     if(target!==active&&target!=='home'){document.getElementById(target)?.scrollIntoView();}
     else window.scrollTo({top:0,behavior:'instant'});
     progress();
   });
 }
 window.addEventListener('hashchange',route);window.addEventListener('scroll',progress,{passive:true});
 $('#menu-toggle').addEventListener('click',()=>{const v=sidebar.classList.toggle('open');$('#menu-toggle').setAttribute('aria-expanded',String(v))});
 $('#theme-toggle').addEventListener('click',()=>{const v=document.body.classList.toggle('night');write('wguide-theme',v?'night':'day');$('#theme-toggle').setAttribute('aria-pressed',String(v))});
 $('#theme-toggle').setAttribute('aria-pressed',String(document.body.classList.contains('night')));
 $$('.font-toggle').forEach(b=>b.addEventListener('click',()=>{const v=document.body.classList.toggle('font-large');write('wguide-font',v?'large':'normal');$$('.font-toggle').forEach(x=>x.setAttribute('aria-pressed',String(v)))}));
 $$('.font-toggle').forEach(x=>x.setAttribute('aria-pressed',String(document.body.classList.contains('font-large'))));
 $$('.print-guide').forEach(b=>b.addEventListener('click',()=>window.print()));
 const dialog=$('#search-dialog'), input=$('#search-input'), results=$('#search-results');
 function openSearch(){lastFocus=document.activeElement;dialog.hidden=false;document.body.style.overflow='hidden';input.focus()}
 function closeSearch(){dialog.hidden=true;document.body.style.overflow='';lastFocus?.focus()}
 $('#search-open').addEventListener('click',openSearch);$('#search-close').addEventListener('click',closeSearch);
 dialog.addEventListener('click',e=>{if(e.target===dialog)closeSearch()});
 function escape(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
 function highlight(s,q){const pos=s.toLowerCase().indexOf(q.toLowerCase());return pos<0?escape(s):escape(s.slice(0,pos))+'<mark>'+escape(s.slice(pos,pos+q.length))+'</mark>'+escape(s.slice(pos+q.length))}
 input.addEventListener('input',()=>{
   const q=input.value.trim();results.innerHTML='';
   if(q.length<2){$('#search-count').textContent='Search the entire guide, including builds, tables and sources.';return}
   const terms=q.toLowerCase().split(/\s+/);
   const matches=data.search.filter(s=>terms.every(t=>(s.title+' '+s.text).toLowerCase().includes(t))).slice(0,40);
   $('#search-count').textContent=matches.length?matches.length+' matching sections'+(matches.length===40?' (first 40 shown)':''):'No results. Try a spell, profession or a shorter phrase.';
   for(const m of matches){
     let pos=m.text.toLowerCase().indexOf(terms[0]);pos=Math.max(0,pos-65);
     const snippet=(pos?'…':'')+m.text.slice(pos,pos+220)+(m.text.length>pos+220?'…':'');
     const a=document.createElement('a');a.className='search-result';a.href='#'+m.id;
     a.innerHTML='<small>'+escape(m.chapter)+'</small><strong>'+highlight(m.title,q)+'</strong><p>'+highlight(snippet,q)+'</p>';
     a.addEventListener('click',()=>{closeSearch();if(location.hash==='#'+m.id)requestAnimationFrame(()=>document.getElementById(m.id)?.scrollIntoView())});results.append(a);
   }
 });
 document.addEventListener('keydown',e=>{
   if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();dialog.hidden?openSearch():closeSearch()}
   if(e.key==='Escape'){if(!dialog.hidden)closeSearch();sidebar.classList.remove('open');$('#menu-toggle').setAttribute('aria-expanded','false')}
   if(e.key==='Tab'&&!dialog.hidden){const items=Array.from(dialog.querySelectorAll('input,button,a[href]'));const first=items[0],last=items[items.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}
 });
 const planner=data.legacy;
 if(planner&&planner.plans.length){
   const select=$('#plan-choice');
   planner.plans.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=p.name;select.append(o)});
   function updatePlanner(){
     const out=window.LegacyPlanner.allocate(planner,select.value,$('#earned-points').value);
     $('#spent-points').textContent=out.spent;$('#account-points').textContent=out.account;$('#banked-points').textContent=Math.max(0,out.account-out.spent);
     const box=$('#allocations');box.innerHTML='';
     Object.entries(out.ranks).forEach(([id,n])=>{const t=planner.traits.find(t=>t.id===id);const el=document.createElement('span');el.className='allocation';el.textContent=t.name+' ';const b=document.createElement('b');b.textContent=n+'/'+t.maxRanks;el.append(b);box.append(el)});
     if(!out.spent){const p=document.createElement('p');p.textContent='Zero points is a complete starting plan. Level your Priest, gather while questing, and earn your first class milestone before buying into a long prerequisite chain.';box.append(p)}
     $('#plan-description').textContent=out.plan.description;
     $('#plan-next').textContent=out.errors.length?'This allocation needs review: '+out.errors.join('; '):(out.next?'Next point: '+planner.traits.find(t=>t.id===out.next).name+'.':'All 16 character points assigned. Further account points do not raise this character’s launch cap.');
     $('#plan-caveat').textContent=out.plan.caveat||'';
   }
   select.addEventListener('change',updatePlanner);$('#earned-points').addEventListener('input',updatePlanner);updatePlanner();
 }
 $$('.prose pre').forEach(pre=>{
   const text=pre.querySelector('code')?.textContent||pre.textContent;
   const b=document.createElement('button');b.className='copy-code';b.textContent='Copy';b.setAttribute('aria-label','Copy macro');
   b.addEventListener('click',async()=>{
     try{if(navigator.clipboard&&isSecureContext)await navigator.clipboard.writeText(text);else{const t=document.createElement('textarea');t.value=text;document.body.append(t);t.select();if(!document.execCommand('copy'))throw new Error('Copy failed');t.remove()}b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1600)}
     catch{b.textContent='Select text to copy';const r=document.createRange();r.selectNodeContents(pre.querySelector('code')||pre);const s=getSelection();s.removeAllRanges();s.addRange(r)}
   });pre.append(b);
 });
 route();
})();
