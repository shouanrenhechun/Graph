"use strict";

// No packages are required. Run with: node verify_domination_equality.js
// This file performs finite checks of the proof; it does not replace the proof.
function runVerification() {
  function pop(x) { let count=0; for(;x;x&=x-1) count++; return count; }
  function degenerate(adj,set,k) {
    let remaining=set;
    while(remaining) {
      let removed=false;
      for(let v=0;v<adj.length;v++) {
        if(((remaining>>v)&1) && pop(adj[v]&remaining)<=k) {
          remaining&=~(1<<v); removed=true;
        }
      }
      if(!removed) return false;
    }
    return true;
  }
  function structuralEquality(adj,weights) {
    let remaining=(1<<adj.length)-1;
    while(remaining) {
      let first=0; while(!((remaining>>first)&1)) first++;
      let component=1<<first, frontier=component;
      while(frontier) {
        let next=0;
        for(let v=0;v<adj.length;v++) if((frontier>>v)&1) next|=adj[v];
        next&=~component; component|=next; frontier=next;
      }
      for(let v=0;v<adj.length;v++) if((component>>v)&1) {
        if(adj[v] !== (component&~(1<<v)) || weights[v]!==weights[first]) return false;
      }
      remaining&=~component;
    }
    return true;
  }

  const lemma={graphs:0,weightedCases:0,equalities:0,failures:[]};
  for(let n=2;n<=6;n++) {
    const edges=[];
    for(let u=0;u<n;u++) for(let v=u+1;v<n;v++) edges.push([u,v]);
    for(let edgeMask=0;edgeMask<2**edges.length;edgeMask++) {
      const adj=Array(n).fill(0);
      edges.forEach(([u,v],i)=>{
        if((edgeMask>>i)&1) {adj[u]|=1<<v;adj[v]|=1<<u;}
      });
      const degrees=adj.map(pop), minimum=Math.min(...degrees);
      if(minimum===0) continue;
      lemma.graphs++;
      for(let k=0;k<minimum;k++) {
        const feasible=[];
        for(let set=0;set<2**n;set++) if(degenerate(adj,set,k)) feasible.push(set);
        const patterns=[Array(n).fill(1),Array.from({length:n},(_,v)=>v%3+1)];
        for(const weights of patterns) {
          let optimum=0;
          for(const set of feasible) {
            let total=0;
            for(let v=0;v<n;v++) if((set>>v)&1) total+=weights[v];
            optimum=Math.max(optimum,total);
          }
          // lcm(1,...,6)=60, so these calculations are exact integers.
          const expectation60=degrees.reduce(
            (sum,d,v)=>sum+weights[v]*Math.min(60,(k+1)*60/(d+1)),0);
          const equality=60*optimum===expectation60;
          const structure=structuralEquality(adj,weights);
          lemma.weightedCases++;
          if(equality) lemma.equalities++;
          if(equality!==structure || 60*optimum<expectation60) {
            lemma.failures.push({n,edgeMask,k,weights,optimum,expectation60,structure});
          }
        }
      }
    }
  }

  function exactDomination(adj,k) {
    const full=(1<<adj.length)-1;
    let optimum=adj.length;
    for(let set=1;set<=full;set++) {
      const size=pop(set); if(size>=optimum) continue;
      let covered=set;
      for(let v=0;v<adj.length;v++) if((set>>v)&1) covered|=adj[v];
      if(covered===full && degenerate(adj,set,k)) optimum=size;
    }
    return optimum;
  }
  const exteriorEdges=[];
  for(const [k,m,a] of [[0,3,2],[1,5,2]]) {
    const n=m*(a+1),adj=Array(n).fill(0);
    function edge(u,v) {adj[u]|=1<<v;adj[v]|=1<<u;}
    for(let u=0;u<m;u++) {
      for(let v=u+1;v<m;v++) edge(u,v);
      for(let t=0;t<a;t++) edge(u,m+u*a+t);
    }
    const baseline=exactDomination(adj,k),values=[];
    for(let u=m;u<n;u++) for(let v=u+1;v<n;v++) {
      const changed=adj.slice(); changed[u]|=1<<v;changed[v]|=1<<u;
      values.push(exactDomination(changed,k));
    }
    exteriorEdges.push({
      k,m,a,n,baseline,addedLeafEdges:values.length,
      minimumAfter:Math.min(...values),maximumAfter:Math.max(...values),
      allStrict:values.every(value=>value<baseline)
    });
  }

  function gcd(a,b) {return b===0?a:gcd(b,a%b);}
  function fraction(n,d) {
    const g=gcd(n,d);return {n:n/g,d:d/g};
  }
  function optimize(delta,k) {
    let best={n:1,d:2},parameters=[];
    for(let a=1;a<=delta-k-1;a++) {
      const n=k+1+a*(delta-a-k),d=(delta-a+1)*(a+1);
      if(n*best.d>best.n*d) {best=fraction(n,d);parameters=[a];}
      else if(n*best.d===best.n*d) parameters.push(a);
    }
    return {best,parameters};
  }
  const formula={cases:0,failures:[]};
  for(let k=0;k<=30;k++) for(let delta=1;delta<=300;delta++) {
    const actual=optimize(delta,k);
    if(delta>=2*k+4) {
      const root=k===0?(delta-1)/2:
        (Math.sqrt(4*(k+1)*delta*(delta-2*k)+k*k)-2*delta+k)/(2*k);
      // The tolerance only stabilizes exactly integral roots in the floating check.
      const a=Math.ceil(root-1e-11);
      const n=k+1+a*(delta-a-k),d=(delta-a+1)*(a+1);
      if(n*actual.best.d!==actual.best.n*d) formula.failures.push({delta,k,a,actual});
      const q=k*a*a+(2*delta-k)*a-delta*delta+(2*k+1)*delta;
      const expected=q===0?[a,a+1]:[a];
      if(JSON.stringify(expected)!==JSON.stringify(actual.parameters)) {
        formula.failures.push({delta,k,a,actual,expected});
      }
    } else if(actual.best.n!==1 || actual.best.d!==2) {
      formula.failures.push({delta,k,actual,reason:"half threshold"});
    }
    if(k===0) {
      const denominator=Math.floor((delta+2)*(delta+2)/4);
      if((denominator-delta)*actual.best.d!==actual.best.n*denominator) {
        formula.failures.push({delta,k,actual,reason:"known k=0 formula"});
      }
    }
    formula.cases++;
  }
  const table=[];
  for(let delta=6;delta<=15;delta++) {
    const {best,parameters}=optimize(delta,1);
    table.push({
      Delta:delta,constant:best.n+"/"+best.d,
      a:parameters,core:parameters.map(a=>delta-a+1)
    });
  }
  const allPass=lemma.failures.length===0 && formula.failures.length===0
    && exteriorEdges.every(x=>x.allStrict)
    && lemma.graphs===28263 && lemma.weightedCases===85116;
  const result={
    date:"2026-10-09",
    scope:"Finite exact checks of the positive-weight selection equality lemma and exterior-edge strictness; formula checks do not replace analytic proofs.",
    lemma,exteriorEdges,formula,k1Table:table,allPass
  };
  if(!allPass) throw new Error(JSON.stringify(result));
  return result;
}

if(typeof module!=="undefined") module.exports={runVerification};
if(typeof require!=="undefined" && require.main===module) {
  process.stdout.write(JSON.stringify(runVerification(),null,2)+"\n");
}
