"""Independent exact verification of a general bipartite-domination bound.

The proof is analytic; these checks validate the construction on all
isolate-free graphs through six vertices and on additional random graphs.
"""
from fractions import Fraction
from itertools import combinations
from random import Random
from functools import lru_cache
import json
from explore_global_allocation import components_coloring
from continue_hall_proof import bits, dominates
from verify_repair_audit import optimal_a


def minimum_dom(adj):
    for k in range(1, len(adj)+1):
        for group in combinations(range(len(adj)), k):
            mask = sum(1 << u for u in group)
            if dominates(adj, mask):
                return mask
    raise AssertionError('no dominating set')


def matched_core(adj):
    """One endpoint per maximum matching edge, oriented towards unmatched nodes."""
    @lru_cache(None)
    def maximum_matching(mask):
        if not mask:
            return ()
        bit = mask & -mask
        u = bit.bit_length()-1
        rest = mask^bit
        best = maximum_matching(rest)
        for v in bits(adj[u]&rest):
            option = ((u,v),)+maximum_matching(rest^(1 << v))
            if len(option)>len(best):
                best = option
        return best
    full = (1 << len(adj))-1
    matching = maximum_matching(full)
    matched = sum((1 << u)+(1 << v) for u,v in matching)
    unmatched = full^matched
    assert not any(adj[u]&unmatched for u in bits(unmatched))
    core = 0
    for u,v in matching:
        nu, nv = adj[u]&unmatched, adj[v]&unmatched
        if nv&~nu:
            assert not nu&~nv
            chosen = v
        else:
            chosen = u
        assert (adj[chosen]&unmatched) == (nu|nv)
        core |= 1 << chosen
    assert dominates(adj,core)
    return core


def matching_and_assignment(adj, core):
    outside = ((1 << len(adj))-1)^core
    matched = {}
    def augment(u, seen):
        for v in bits(adj[u]&outside):
            if v in seen:
                continue
            seen.add(v)
            if v not in matched or augment(matched[v], seen):
                matched[v] = u
                return True
        return False
    for u in bits(core):
        assert augment(u, set()), ('minimum domination matching failed', adj, core)
    assignment = {u: set() for u in bits(core)}
    for v in bits(outside):
        u = matched[v] if v in matched else next(bits(adj[v]&core))
        assignment[u].add(v)
    assert all(group for group in assignment.values())
    return assignment


def is_forest(adj, mask):
    components = components_coloring(adj, mask)
    if components is None:
        return False
    edges = sum((adj[u]&mask).bit_count() for u in bits(mask))//2
    return edges == mask.bit_count()-len(components)


def construct(adj, delta, core_builder=minimum_dom, acyclic=False):
    core = core_builder(adj)
    assignment = matching_and_assignment(adj, core)
    weights = {u:len(group)-1 for u,group in assignment.items()}
    best = None
    subset = core
    while True:
        valid = is_forest(adj, subset) if acyclic else components_coloring(adj, subset) is not None
        if valid:
            key = sum(weights[u] for u in bits(subset)), subset.bit_count()
            if best is None or key > best[0]:
                best = key, subset
        if not subset:
            break
        subset = (subset-1)&core
    bip_core = best[1]
    # Max weight, then maximum cardinality, implies core domination.
    covered_core = bip_core
    covered_outside = 0
    outside = ((1 << len(adj))-1)^core
    for u in bits(bip_core):
        covered_core |= adj[u]&core
        covered_outside |= adj[u]&outside
    assert covered_core == core
    remaining = outside^covered_outside
    independent = 0
    available = remaining
    while available:
        bit = available & -available
        u = bit.bit_length()-1
        independent |= bit
        available &= ~bit & ~adj[u]
    selected = bip_core | independent
    assert dominates(adj, selected)
    assert components_coloring(adj, selected) is not None
    if acyclic:
        assert is_forest(adj, selected)
    assert not any(adj[u]&bip_core for u in bits(independent))
    expected_gain = sum(Fraction(weights[u])*min(Fraction(1),Fraction(2,(adj[u]&core).bit_count()+1)) for u in bits(core))
    assert best[0][0] >= expected_gain
    analytical_budget = len(adj)-core.bit_count()-expected_gain
    assert selected.bit_count() <= analytical_budget
    a = optimal_a(delta)
    candidate = Fraction(2+a*(delta-a-1),(delta-a+1)*(a+1))
    assert analytical_budget <= candidate*len(adj)
    assert selected.bit_count() <= candidate*len(adj)
    return selected.bit_count(), candidate


def exhaustive_six(acyclic=False):
    checked = 0
    for n in range(2,7):
        pairs = list(combinations(range(n),2))
        for edge_mask in range(1 << len(pairs)):
            adj = [0]*n
            for index,(u,v) in enumerate(pairs):
                if edge_mask >> index & 1:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
            if any(not a for a in adj):
                continue
            construct(adj,max(4,max(a.bit_count() for a in adj)),acyclic=acyclic)
            construct(adj,max(4,max(a.bit_count() for a in adj)),matched_core,acyclic=acyclic)
            checked += 1
    return checked


def random_general(trials=5000, acyclic=False):
    rng = Random(61009)
    checked = 0
    for trial in range(trials):
        n = rng.randint(7,22)
        delta = rng.randint(4,min(15,n-1))
        adj = [0]*n
        pairs = list(combinations(range(n),2))
        rng.shuffle(pairs)
        p = rng.uniform(.08,.95)
        for u,v in pairs:
            if adj[u].bit_count()<delta and adj[v].bit_count()<delta and rng.random()<p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        if any(not a for a in adj):
            continue
        construct(adj,delta,acyclic=acyclic)
        checked += 1
    return checked


def random_matching_core(trials=1200, acyclic=False):
    rng = Random(41009)
    checked = 0
    for trial in range(trials):
        n = rng.randint(7,14)
        adj = [0]*n
        p = rng.uniform(.12,.9)
        for u,v in combinations(range(n),2):
            if rng.random()<p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        if any(not a for a in adj):
            continue
        construct(adj,max(4,max(a.bit_count() for a in adj)),matched_core,acyclic=acyclic)
        checked += 1
    return checked


def cn_values():
    rows = []
    for delta in range(4,31):
        a = optimal_a(delta)
        value = Fraction(2+a*(delta-a-1),(delta-a+1)*(a+1))
        k = delta-a+1
        gamma = 2+a*(k-2)
        order = k*(a+1)
        assert Fraction(gamma,order) == value
        rows.append({'delta':delta,'optimal_a':a,'core_clique_order':k,
                     'constant':str(value),'equality_graph_order':order,
                     'equality_graph_gamma_bip':gamma})
    return rows


def equality_constructions(acyclic=False):
    checked = 0
    for delta in range(4,19):
        a = optimal_a(delta)
        k = delta-a+1
        adj = [0]*(k*(a+1))
        for u,v in combinations(range(k),2):
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        for u in range(k):
            for leaf in range(k+u*a,k+(u+1)*a):
                adj[u] |= 1 << leaf
                adj[leaf] |= 1 << u
        core = (1 << k)-1
        size,value = construct(adj,delta,lambda graph:core,acyclic=acyclic)
        assert size == 2+a*(k-2)
        assert size == value*len(adj)
        checked += 1
    return checked


if __name__ == '__main__':
    result = {'all_isolate_free_graphs_order_2_to_6_checked':exhaustive_six(),
              'both_minimum_domination_and_maximum_matching_core_checked':True,
              'random_general_graphs_checked':random_general(),
              'random_maximum_matching_core_graphs_checked':random_matching_core(),
              'sharp_corona_constructions_checked':equality_constructions(),
              'construction_matching_domination_bipartiteness_bound_all_pass':True,
              'cn_table':cn_values()}
    print(json.dumps(result,ensure_ascii=False,indent=2))
