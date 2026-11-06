const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const data=JSON.parse(fs.readFileSync(new URL('../content/legacy-planner.json','file://'+__filename)));
const research=JSON.parse(fs.readFileSync(new URL('../research/legacy-planner-research.json','file://'+__filename)));
const {allocate}=require('../assets/planner.js');

test('Every recommended allocation matches its independently validated research snapshot',()=>{
 for(const plan of data.plans){
  for(let budget=0;budget<=16;budget++){
   const result=allocate(data,plan.id,budget);
   assert.deepEqual(result.errors,[],plan.id+' at '+budget);
   assert.equal(result.spent,budget);
   assert.deepEqual(result.ranks,research.recommendations[plan.id].snapshots[budget].allocation);
  }
 }
});
test('Account earnings beyond sixteen cannot increase character spending',()=>{
 for(const p of data.plans)for(let n=17;n<=65;n++)assert.equal(allocate(data,p.id,n).spent,16);
});
test('Zero, partial and invalid input stay bounded',()=>{
 for(const p of data.plans){
  assert.equal(allocate(data,p.id,0).spent,0);
  assert.equal(allocate(data,p.id,-5).spent,0);
  assert.equal(allocate(data,p.id,NaN).spent,0);
  assert.equal(allocate(data,p.id,3.9).spent,3);
  assert.equal(allocate(data,p.id,1000).account,65);
 }
});
test('Prerequisite violations fail before spending a point',()=>{
 const invalid={...data,plans:[{id:'bad',steps:['talented']}]};
 const result=allocate(invalid,'bad',1);
 assert.equal(result.spent,0);assert.ok(result.errors.length);
 const rankOverflow={...data,plans:[{id:'bad',steps:Array(16).fill('thrill')}]};
 assert.equal(allocate(rankOverflow,'bad',16).spent,5);
});
test('The first character and established alt have deliberately different early priorities',()=>{
 assert.deepEqual(allocate(data,'firstPriest',5).ranks,{thrill:5});
 assert.deepEqual(allocate(data,'altLeveling',10).ranks,{rested:5,talented:5});
});
