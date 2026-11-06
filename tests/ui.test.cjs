const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM}=require('jsdom');
const html=fs.readFileSync(require('node:path').join(__dirname,'../dist/index.html'),'utf8');
async function boot(){
 const dom=new JSDOM(html,{runScripts:'dangerously',url:'https://guide.local/',pretendToBeVisual:true,beforeParse(w){w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=()=>{};}});
 await new Promise(r=>setTimeout(r,50));return dom;
}
test('Overview, chapter navigation and active menu remain in sync',async()=>{
 const dom=await boot();const w=dom.window,d=w.document;
 assert.equal(d.querySelector('#home').hidden,false);
 assert.equal(d.querySelectorAll('.chapter:not([hidden])').length,0);
 w.location.hash='#holy';await new Promise(r=>setTimeout(r,50));
 assert.equal(d.querySelector('#home').hidden,true);
 assert.equal(d.querySelectorAll('.chapter:not([hidden])').length,1);
 assert.equal(d.querySelector('.chapter:not([hidden])').id,'holy');
 assert.equal(d.querySelector('.sidebar [aria-current="page"]').dataset.chapter,'holy');
 w.location.hash='#nonexistent';await new Promise(r=>setTimeout(r,50));
 assert.equal(d.querySelector('#home').hidden,false);dom.window.close();
});
test('Search finds spell guidance and safely renders unusual input',async()=>{
 const dom=await boot();const w=dom.window,d=w.document;
 d.querySelector('#search-open').click();assert.equal(d.querySelector('#search-dialog').hidden,false);
 const input=d.querySelector('#search-input');input.value='Divine Grace';input.dispatchEvent(new w.Event('input'));
 assert.ok(d.querySelectorAll('.search-result').length>1);
 const link=d.querySelector('.search-result');assert.ok(d.getElementById(link.hash.slice(1)));
 input.value='<script>alert(1)</script>';input.dispatchEvent(new w.Event('input'));
 assert.equal(d.querySelectorAll('#search-results script').length,0);
 d.querySelector('#search-close').click();assert.equal(d.querySelector('#search-dialog').hidden,true);dom.window.close();
});
test('Planner input updates allocations and never grants more than sixteen points',async()=>{
 const dom=await boot();const w=dom.window,d=w.document;
 const input=d.querySelector('#earned-points');input.value='5';input.dispatchEvent(new w.Event('input'));
 assert.equal(d.querySelector('#spent-points').textContent,'5');assert.match(d.querySelector('#allocations').textContent,/Thrill of Adventure 5\/5/);
 input.value='65';input.dispatchEvent(new w.Event('input'));assert.equal(d.querySelector('#spent-points').textContent,'16');
 assert.equal(d.querySelector('#banked-points').textContent,'49');
 const choice=d.querySelector('#plan-choice');choice.value='flightLeveling';choice.dispatchEvent(new w.Event('change'));
 assert.match(d.querySelector('#allocations').textContent,/Frequent Flier 1\/1/);dom.window.close();
});
test('Reading controls, mobile menu and offline macro controls initialize',async()=>{
 const dom=await boot();const d=dom.window.document;
 d.querySelector('#theme-toggle').click();assert.ok(d.body.classList.contains('night'));
 d.querySelector('.font-toggle').click();assert.ok(d.body.classList.contains('font-large'));
 d.querySelector('#menu-toggle').click();assert.equal(d.querySelector('#menu-toggle').getAttribute('aria-expanded'),'true');
 assert.ok(d.querySelectorAll('.copy-code').length>=5);dom.window.close();
});
