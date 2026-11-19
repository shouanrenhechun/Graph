"""Exact deterministic 13-state tree DP; no matching certificates are counted.

State vector is closed under the binary operation graft(root_tree, child_tree).
Each state records the root label, outstanding neighbor requirements, and
whether it has an internally forced matching obligation. Only forests supported.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import json

# label, J-neighbor-among-children, W-neighbor-among-children, matching flag.
# For J: flag=1 means some free child can serve this root.
# For D/S: flag=1 means one demanding J child occupies the root.
STATES = [
    ('J',0,0,0), ('J',0,0,1),
    ('D',0,0,0), ('D',1,0,0), ('D',1,0,1),
    ('S',0,0,0), ('S',0,1,0), ('S',1,0,0), ('S',1,0,1),
    ('S',1,1,0), ('S',1,1,1),
    ('W',0,0,0), ('T',0,0,0),
]
NAMES = ['J_need','J_done','D_noJ','D_free','D_used','S_noJ_noW',
         'S_noJ_yesW','S_yesJ_noW_free','S_yesJ_noW_used',
         'S_yesJ_yesW_free','S_yesJ_yesW_used','W','T']
INDEX = {s:i for i,s in enumerate(STATES)}
BASE = (2,0,1,0,0,2,0,0,0,0,0,1,1)
FINAL = (0,1,0,1,1,0,0,0,0,1,1,1,1)

def transition(i,j):
    r,a,b,m=STATES[i]
    s,c,d,k=STATES[j]
    if (r=='J' and s in ('J','W','T')) or (s=='J' and r in ('W','T')):
        return None
    if (r=='S' and s=='T') or (s=='S' and r=='T'):
        return None
    # Validate the child root, now that its parent label is known.
    if s=='D' and not(c or r=='J'):
        return None
    if s=='S' and (not(c or r=='J') or not(d or r in ('W','T'))):
        return None
    if r=='J':
        # All allowed child labels here are D or S.
        dest=(r,0,0,int(m or not k))
    elif r in ('D','S'):
        demand=(s=='J' and k==0)
        if m and demand:
            return None
        dest=(r,int(a or s=='J'),int(b or s in ('W','T')) if r=='S' else 0,
              int(m or demand))
    else:
        dest=(r,0,0,0)
    denominator=2 if r in ('J','S') and s in ('J','S') else 1
    return INDEX[dest],denominator

TRANSITIONS = [(i,j,*t) for i in range(13) for j in range(13)
               if (t:=transition(i,j)) is not None]

def graft(x,y):
    # Exact for integer tree vectors, floats for normalized exploratory vectors.
    out=[0]*13
    integers=all(isinstance(a,int) for a in x) and all(isinstance(a,int) for a in y)
    for i,j,k,d in TRANSITIONS:
        prod=x[i]*y[j]
        if integers:
            assert prod%d==0
            out[k]+=prod//d
        else:
            out[k]+=prod/d
    return tuple(out)

def total(vector):
    return sum(a*b for a,b in zip(vector,FINAL))

def rooted_vector(adj,root=0,parent=-1):
    # Iterative postorder: each edge is visited a constant number of times.
    # This also avoids a Python recursion limit on long paths.
    stack=[root];parents={root:parent};children={};order=[]
    while stack:
        v=stack.pop();order.append(v);children[v]=[]
        remaining=adj[v]
        if parents[v]>=0:remaining &= ~(1<<parents[v])
        while remaining:
            bit=remaining&-remaining;remaining^=bit;u=bit.bit_length()-1
            if u in parents:raise ValueError('Expected an acyclic rooted component.')
            parents[u]=v;children[v].append(u);stack.append(u)
    vectors={}
    for v in reversed(order):
        vec=BASE
        for child in children[v]:vec=graft(vec,vectors.pop(child))
        vectors[v]=vec
    return vectors[root]

def count_tree(adj):
    if not adj:return 1
    # Caller must supply a tree. A disconnected forest is handled componentwise.
    return total(rooted_vector(adj))

def verify(max_n=10):
    from verification import count_tau,path_adj,graph6_adj
    known=json.loads((Path(__file__).parent/'trees_results.json').read_text())
    count=0
    for row in known:
        if row['n']>max_n:continue
        for code in row['graphs']:
            adj=graph6_adj(code.encode())
            exact=count_tau(adj)
            for root in range(len(adj)):
                assert total(rooted_vector(adj,root))==exact,(code,root)
                count+=1
    for n in range(1,17):
        adj=path_adj(n)
        assert count_tree(adj)==count_tau(adj)
    print('Rooted DP agrees on saved extremal trees at',count,'root choices, and paths through n=16.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:verify()
    else:print(json.dumps({'states':STATES,'base':BASE,'final':FINAL,'transitions':TRANSITIONS},indent=2))
