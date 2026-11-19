"""Exact arithmetic and independent graph construction checks for the hierarchy."""
from fractions import Fraction
from itertools import combinations
from math import isqrt
from random import Random
from pathlib import Path
import json
from prove_general_cn import matched_core, matching_and_assignment
from continue_hall_proof import bits, dominates

ROOT=Path(__file__).resolve().parent

def degenerate(adj,mask,k):
    while mask:
        removable=next((u for u in bits(mask) if (adj[u]&mask).bit_count()<=k),None)
        if removable is None:
            return False
        mask^=1<<removable
    return True

def candidate(d,k,a):
    return Fraction(k+1+a*(d-a-k),(d-a+1)*(a+1))

def constant(d,k):
    return max([Fraction(1,2)]+[candidate(d,k,a) for a in range(1,d-k)])

def verify_graph(adj,k):
    n=len(adj)
    d=max(x.bit_count() for x in adj)
    core=matched_core(adj)
    groups=matching_and_assignment(adj,core)
    weights={u:len(group)-1 for u,group in groups.items()}
    expected=sum(Fraction(weights[u])*min(Fraction(1),Fraction(k+1,(adj[u]&core).bit_count()+1)) for u in bits(core))
    best=(-1,-1)
    selected_core=0
    sub=core
    while True:
        if degenerate(adj,sub,k):
            key=(sum(weights[u] for u in bits(sub)),sub.bit_count())
            if key>best:
                best,selected_core=key,sub
        if not sub: break
        sub=(sub-1)&core
    assert best[0]>=expected
    assert all(u in bits(selected_core) or adj[u]&selected_core for u in bits(core))
    outside=((1<<n)-1)^core
    covered=0
    for u in bits(selected_core): covered|=adj[u]&outside
    remaining=outside&~covered
    independent=0
    while remaining:
        bit=remaining&-remaining
        u=bit.bit_length()-1
        independent|=bit
        remaining&=~bit&~adj[u]
    selected=selected_core|independent
    assert dominates(adj,selected) and degenerate(adj,selected,k)
    assert not any(adj[u]&selected_core for u in bits(independent))
    budget=n-core.bit_count()-expected
    assert selected.bit_count()<=budget<=constant(d,k)*n
    for u,group in groups.items():
        a=len(group)
        assert (adj[u]&core).bit_count()+a<=d
        local=Fraction(a)-min(Fraction(1),Fraction(k+1,(adj[u]&core).bit_count()+1))*(a-1)
        assert local<=constant(d,k)*(a+1)
    return selected

def main():
    graphs=instances=0
    for n in range(2,7):
        pairs=list(combinations(range(n),2))
        for em in range(1<<len(pairs)):
            adj=[0]*n
            for i,(u,v) in enumerate(pairs):
                if em>>i&1:
                    adj[u]|=1<<v
                    adj[v]|=1<<u
            if not all(adj): continue
            for k in range(4):
                verify_graph(adj,k)
                instances+=1
            graphs+=1
    rng=Random(20261009)
    random_graphs=0
    for _ in range(350):
        n=rng.randint(7,14)
        adj=[0]*n
        p=rng.uniform(.15,.85)
        for u,v in combinations(range(n),2):
            if rng.random()<p:
                adj[u]|=1<<v
                adj[v]|=1<<u
        if not all(adj):continue
        for k in range(4):verify_graph(adj,k)
        random_graphs+=1
    arithmetic=0
    for k in range(16):
        for d in range(1,201):
            val=constant(d,k)
            assert (val==Fraction(1,2))==(d<=2*k+3)
            if d>=2*k+4:
                if k==0:a=d//2
                else:
                    rad=4*(k+1)*d*(d-2*k)+k*k
                    a=(isqrt(rad)-2*d+k)//(2*k)
                    q=lambda x:k*x*x+(2*d-k)*x-d*d+(2*k+1)*d
                    while q(a)<0:a+=1
                    while a>1 and q(a-1)>=0:a-=1
                    b=d-k-1
                    assert q(b)==(k+1)*(b*b+b+k)
                assert 1<=a<=d-k-1 and candidate(d,k,a)==val
            for a in range(1,d-k):
                den=(d-a+1)*(a+1)
                assert candidate(d,k,a)-Fraction(1,2)==Fraction((a-1)*(d-2*k-1-a),2*den)
                if a<d-k-1:
                    den2=(d-a)*(a+2)
                    q=k*a*a+(2*d-k)*a-d*d+(2*k+1)*d
                    assert candidate(d,k,a+1)-candidate(d,k,a)==Fraction(-q,den*den2)
            arithmetic+=1
    result={'exhaustive_graphs_through_six_vertices':graphs,'exhaustive_k_0_through_3_instances':instances,'random_graphs':random_graphs,'random_k_instances':4*random_graphs,'exact_parameter_pairs':arithmetic,'status':'all checks passed'}
    (ROOT/'output/pdf/domination_chain_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
