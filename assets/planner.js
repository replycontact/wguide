/* Pure, dependency-free Legacy allocation logic, also used by Node tests. */
(function(root){
  'use strict';
  function allocate(data, planId, earned){
    const plan=data.plans.find(p=>p.id===planId);
    if(!plan) throw new Error('Unknown plan');
    const n=Number(earned);
    const account=Math.max(0,Math.min(65,Math.floor(Number.isFinite(n)?n:0)));
    const budget=Math.min(account,16);
    const ranks={}; const treePoints={}; const errors=[];
    let spent=0;
    for(const id of plan.steps.slice(0,budget)){
      const trait=data.traits.find(t=>t.id===id);
      if(!trait){errors.push('Unknown trait '+id);break;}
      const rank=ranks[id]||0;
      if(rank>=trait.maxRanks){errors.push('Rank limit for '+trait.name);break;}
      if((treePoints[trait.tree]||0)<(trait.treePointsRequired||0)){
        errors.push('Tree requirement for '+trait.name);break;
      }
      const prerequisites=trait.prerequisites||{};
      if(Object.keys(prerequisites).some(key=>(ranks[key]||0)<prerequisites[key])){
        errors.push('Prerequisite for '+trait.name);break;
      }
      const cost=trait.costPerRank||1;
      if(spent+cost>budget)break;
      ranks[id]=rank+1;treePoints[trait.tree]=(treePoints[trait.tree]||0)+cost;spent+=cost;
    }
    return {plan,account,budget,spent,ranks,treePoints,errors,next:plan.steps[spent]||null};
  }
  const api={allocate};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.LegacyPlanner=api;
})(typeof window!=='undefined'?window:globalThis);
