"""Exact small-core experiments for a proposed repair-local Hall network.

Every tested graph is a uniform leaf corona. Canonical bipartite dominating
sets reduce exactly to maximum induced bipartite core sets when a >= 2.
The tested network is a proposed stronger local allocation, not the theorem.
"""
from fractions import Fraction
from itertools import combinations, permutations
from random import Random
from verify_repair_audit import optimal_a
import json


def components_coloring(adj, mask):
    unseen = mask
    result = []
    while unseen:
        start = unseen & -unseen
        zero, one, frontier = start, 0, start
        unseen ^= start
        color = 0
        while frontier:
            neighbors = 0
            working = frontier
            while working:
                bit = working & -working
                neighbors |= adj[bit.bit_length()-1]
                working ^= bit
            neighbors &= mask
            same = zero if color == 0 else one
            if neighbors & same:
                return None
            fresh = neighbors & unseen
            unseen ^= fresh
            if color == 0:
                one |= fresh
            else:
                zero |= fresh
            frontier = fresh
            color ^= 1
        result.append((zero, one))
    return result


def canonical_core(adj):
    n = len(adj)
    best = None
    for k in range(n, -1, -1):
        for indices in combinations(range(n), k):
            mask = sum(1 << i for i in indices)
            comps = components_coloring(adj, mask)
            if comps is None:
                continue
            b = sum(1 << i for i in indices if adj[i] & mask)
            edges = sum((adj[i] & mask).bit_count() for i in indices)//2
            key = (b.bit_count(), -edges, mask)
            if best is None or key < best[0]:
                best = key, mask, b
        if best is not None:
            return best[1:]


def canonical_weighted_core(adj, leaves):
    best = None
    for mask in range(1 << len(adj)):
        if components_coloring(adj, mask) is None:
            continue
        selected = [i for i in range(len(adj)) if mask >> i & 1]
        weight = sum(leaves[i]-1 for i in selected)
        b = sum(1 << i for i in selected if adj[i] & mask)
        edges = sum((adj[i] & mask).bit_count() for i in selected)//2
        key = (-weight, b.bit_count(), -edges, mask)
        if best is None or key < best[0]:
            best = key, mask, b
    return best[1:]


def repair_hall(adj, delta, leaves=None, include_positive_pool=False):
    a = optimal_a(delta)
    assert a >= 2
    A = 2 + a*(delta-a-1)
    B = delta+a-1
    scale = delta-3
    lam = 2*A-B
    if leaves is None:
        leaves = [a]*len(adj)
        selected, owners = canonical_core(adj)
    else:
        selected, owners = canonical_weighted_core(adj, leaves)
    gamma = sum(leaves)-sum(leaves[u]-1 for u in range(len(adj)) if selected >> u & 1)
    order = len(adj)+sum(leaves)
    assert gamma*(A+B) <= A*order
    comps = components_coloring(adj, owners)
    supports = [i for i in range(len(adj)) if not selected >> i & 1]
    capacity = {}
    for u in range(len(adj)):
        if owners >> u & 1:
            su = (adj[u] & ~selected).bit_count()
            capacity[u] = scale*(A*leaves[u]-B)-lam*su
            assert capacity[u] >= 0
    demands, eligible = {}, {}
    positive_external = 0
    positive_resources = {}
    for w in supports:
        beta = (adj[w] & owners).bit_count()
        # Z0 consists of the pendant vertices attached to core supports
        # which have B neighbors. If beta=0 the core is outside W_B.
        if beta == 0:
            continue
        chi = scale*(A-B*leaves[w])+lam*beta
        if chi >= 0:
            positive_external += chi
            positive_resources[w] = chi
            continue
        demands[w] = -chi
        repair_options_union = 0
        for left, right in comps:
            ln = adj[w] & left
            rn = adj[w] & right
            if ln.bit_count() <= rn.bit_count():
                repair_options_union |= ln
            if rn.bit_count() <= ln.bit_count():
                repair_options_union |= rn
        eligible[w] = repair_options_union
    negatives = list(demands)
    for size in range(1, len(negatives)+1):
        for cut in combinations(negatives, size):
            neighbors = 0
            for w in cut:
                neighbors |= eligible[w]
            available = sum(c for u, c in capacity.items() if neighbors >> u & 1)
            if include_positive_pool:
                cut_mask = sum(1<<w for w in cut)
                available += sum(c for q,c in positive_resources.items() if (adj[q]&neighbors) or (adj[q]&cut_mask))
            debt = sum(demands[w] for w in cut)
            if available < debt:
                return {'delta': delta, 'a': a, 'leaves':leaves, 'core_order':len(adj),
                        'core_edges':[[u,v] for u in range(len(adj)) for v in range(u+1,len(adj)) if adj[u] >> v & 1],
                        'selected_core':[u for u in range(len(adj)) if selected >> u & 1],
                        'owners':[u for u in capacity], 'cut':list(cut),
                        'eligible_owners':[u for u in capacity if neighbors >> u & 1],
                        'capacity_scaled':available, 'demand_scaled':debt,
                        'scale':scale, 'owner_capacities_scaled':capacity,
                        'negative_demands_scaled':demands,
                        'positive_external_scaled':positive_external,
                        'selected_isolated_core':[u for u in range(len(adj)) if (selected & ~owners) >> u & 1]}
    return None


def fixed_repair_corona():
    # cor(K_6,3), delta=8. Selected core vertices 0,1; four supports.
    adj = [sum(1<<j for j in range(6) if j != i) for i in range(6)]
    result = repair_hall(adj, 8)
    assert result is None
    return {'graph':'cor(K_6,3)', 'delta':8, 'canonical_D_size':14,
            'owner_capacity':str(Fraction(88,5)),
            'debt_per_support':str(Fraction(44,5)),
            'all_fixed_repairs_owner_0':True,
            'minimal_bad_cut_size':3,
            'bad_cut_demand':str(Fraction(132,5)),
            'bad_cut_capacity':str(Fraction(88,5)),
            'all_minimum_repair_options_network_feasible':True}


def singleton_obstruction_delta9():
    # A targeted nonuniform corona: B is two disjoint selected edges;
    # z1,z2 are selected isolated core vertices; w has t=3,beta=4,z=2.
    # Five zero-weight core supports q_i saturate the four B owners.
    names = ['u1','v1','u2','v2','z1','z2','w'] + [f'q{i}' for i in range(1,6)]
    adj = [0]*len(names)
    edges = [(0,1),(2,3)] + [(6,u) for u in range(6)] + [(q,u) for q in range(7,12) for u in range(4)]
    for u,v in edges:
        adj[u] |= 1<<v
        adj[v] |= 1<<u
    leaves = [2]*6+[3]+[1]*5
    assert all(adj[u].bit_count()+leaves[u] <= 9 for u in range(len(adj)))
    selected,owners = canonical_weighted_core(adj,leaves)
    assert selected == sum(1<<i for i in range(6))
    assert owners == 15
    failure = repair_hall(adj,9,leaves)
    assert failure is not None and failure['cut'] == [6]
    assert failure['capacity_scaled'] == 0 and failure['demand_scaled'] == 4
    assert repair_hall(adj,9,leaves,include_positive_pool=True) is None
    order = len(adj)+sum(leaves)
    gamma = sum(leaves)-sum(leaves[u]-1 for u in range(len(adj)) if selected >> u & 1)
    assert order == 32 and gamma == 14
    # Build the complete graph to verify responsibilities for all four repairs.
    full = [set() for _ in range(order)]
    for u,v in edges:
        full[u].add(v); full[v].add(u)
    leaf_groups = {}
    cursor = len(adj)
    for u,a in enumerate(leaves):
        leaf_groups[u] = list(range(cursor,cursor+a))
        for leaf in leaf_groups[u]:
            full[u].add(leaf); full[leaf].add(u)
        cursor += a
    D = set(range(6)) | set(leaf_groups[6]) | {leaf_groups[q][0] for q in range(7,12)}
    Z0 = set(leaf_groups[6]) | {leaf_groups[q][0] for q in range(7,12)}
    assert len(D) == gamma
    assert all(v in D or full[v]&D for v in range(order))
    assert all(v in D or full[v] & (D-Z0) for v in range(order))
    repairs=[]
    for left in (0,1):
        for right in (2,3):
            U={left,right}; T=set(leaf_groups[6])|U
            remainder={v for v in range(order) if v not in D-T and not full[v]&(D-T) and v!=6 and v not in full[6]}
            private={leaf for u in U for leaf in leaf_groups[u]}
            assert remainder == private and len(remainder)==4
            assert not any(full[v]&remainder for v in remainder)
            repairs.append([names[u] for u in sorted(U)])
    return {'core_vertex_names':names,'core_edges_named':[[names[u],names[v]] for u,v in edges],
            'leaves_per_core':dict(zip(names,leaves)), 'order':order,'delta':9,
            'canonical_D_size':gamma,'canonical_selected_core':names[:6],
            'negative_support':'w','t':3,'beta':4,'rho':2,'retained_Z_neighbors':2,
            'all_minimum_repairs':repairs,'local_gain':0,'local_extra_private_count':0,
            'local_tau':0,'local_delta':0,'compensation_points':0,'repeated_incidence_tokens':0,
            'debt':str(Fraction(2,3)), 'available_repair_local_capacity':'0',
            'positive_charge_per_q':str(Fraction(64,3)),
            'positive_pool_network_feasible':True,
            'global_ratio':str(Fraction(gamma,order)), 'candidate':str(Fraction(17,28)),
            'native_owner_network_failure':failure}


def verify_rank_two_lemma():
    rng = Random(420)
    checked = 0
    for trial in range(12):
        n = 6
        adj = [0]*n
        for u in range(n):
            for v in range(u+1,n):
                if rng.random() < trial/12:
                    adj[u] |= 1<<v; adj[v] |= 1<<u
        weights = [rng.randint(0,5) for _ in range(n)]
        total = 0
        count = 0
        for order in permutations(range(n)):
            earlier = 0
            forest = 0
            for u in order:
                if (adj[u]&earlier).bit_count() <= 1:
                    forest |= 1<<u
                earlier |= 1<<u
            comps = components_coloring(adj,forest)
            assert comps is not None
            edges = sum((adj[u]&forest).bit_count() for u in range(n) if forest >> u & 1)//2
            assert edges == forest.bit_count()-len(comps)
            total += sum(weights[u] for u in range(n) if forest >> u & 1)
            count += 1
        expected = sum(Fraction(weights[u])*min(Fraction(1),Fraction(2,adj[u].bit_count()+1)) for u in range(n))
        assert Fraction(total,count) == expected
        checked += count
    return {'exact_permutations_checked':checked,'weighted_expectation_identity_verified':True}


def verify_matched_independent_side_theorem():
    rng = Random(710)
    for trial in range(1000):
        delta = rng.randint(4,12)
        n = rng.randint(1,8)
        core = [0]*n
        for u,v in combinations(range(n),2):
            if rng.random()<.4 and core[u].bit_count()<delta-1 and core[v].bit_count()<delta-1:
                core[u] |= 1<<v; core[v] |= 1<<u
        assigned = [rng.randint(1,delta-core[u].bit_count()) for u in range(n)]
        order = n+sum(assigned)
        adj = [0]*order
        for u in range(n):
            adj[u] = core[u]
        cursor = n
        for u,a in enumerate(assigned):
            for q in range(cursor,cursor+a):
                adj[u] |= 1<<q; adj[q] |= 1<<u
            cursor += a
        pairs = [(u,q) for u in range(n) for q in range(n,order) if not (adj[u] >> q & 1)]
        rng.shuffle(pairs)
        for u,q in pairs:
            if rng.random()<.3 and adj[u].bit_count()<delta and adj[q].bit_count()<delta:
                adj[u] |= 1<<q; adj[q] |= 1<<u
        choices=[]
        for mask in range(1<<n):
            if components_coloring(core,mask) is not None:
                weight = sum(assigned[u]-1 for u in range(n) if mask >> u & 1)
                choices.append((-weight,-mask.bit_count(),mask))
        A = min(choices)[2]
        D = A | sum(1<<q for q in range(n,order) if not adj[q]&A)
        assert all(D >> v & 1 or adj[v]&D for v in range(order))
        assert components_coloring(adj,D) is not None
        a = optimal_a(delta)
        numerator = 2+a*(delta-a-1)
        denominator = (delta-a+1)*(a+1)
        assert D.bit_count()*denominator <= numerator*order
    return {'graphs_with_additional_shared_neighbors_checked':1000,
            'constructed_bipartite_dominating_sets_verified':True}


def main():
    rng = Random(20261009)
    checked = 0
    failures = []
    for delta in (8,9,10,11,12):
        a = optimal_a(delta)
        max_degree = delta-a
        for n in range(5,12):
            for trial in range(120):
                adj = [0]*n
                p = rng.uniform(.25,.8)
                pairs = [(u,v) for u in range(n) for v in range(u+1,n)]
                rng.shuffle(pairs)
                for u,v in pairs:
                    if rng.random() < p and adj[u].bit_count() < max_degree and adj[v].bit_count() < max_degree:
                        adj[u] |= 1<<v
                        adj[v] |= 1<<u
                checked += 1
                failure = repair_hall(adj,delta)
                if failure is not None:
                    failures.append(failure)
                    break
            if failures:
                break
        if failures:
            break
    weighted_checked = 0
    weighted_failures = []
    for delta in (8,9,10,11,12):
        for n in range(4,11):
            for trial in range(80):
                adj = [0]*n
                p = rng.uniform(.25,.8)
                pairs = [(u,v) for u in range(n) for v in range(u+1,n)]
                rng.shuffle(pairs)
                for u,v in pairs:
                    if rng.random() < p and adj[u].bit_count() < delta-1 and adj[v].bit_count() < delta-1:
                        adj[u] |= 1<<v
                        adj[v] |= 1<<u
                leaves = [rng.randint(1,delta-adj[u].bit_count()) for u in range(n)]
                weighted_checked += 1
                failure = repair_hall(adj,delta,leaves)
                if failure is not None:
                    weighted_failures.append(failure)
                    break
            if weighted_failures:
                break
        if weighted_failures:
            break
    print(json.dumps({'fixed_repair_corona':fixed_repair_corona(),
                      'singleton_obstruction_delta9':singleton_obstruction_delta9(),
                      'rank_two_forest_lemma_check':verify_rank_two_lemma(),
                      'matched_independent_side_theorem_check':verify_matched_independent_side_theorem(),
                      'tested_core_graphs':checked,
                      'all_options_owner_only_failures':failures,
                      'tested_weighted_core_graphs':weighted_checked,
                      'weighted_owner_only_failures':weighted_failures},indent=2))


if __name__ == '__main__':
    main()
