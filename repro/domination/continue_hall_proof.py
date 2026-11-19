"""Exact checks for the Z1 matching lemma and enlarged Hall resource graph."""
from explore_global_allocation import components_coloring, repair_hall
from random import Random
from itertools import combinations
from fractions import Fraction
from verify_repair_audit import optimal_a
import json


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def dominates(adj, mask):
    covered = mask
    for u in bits(mask):
        covered |= adj[u]
    return covered == (1 << len(adj))-1


def canonical_dom(adj):
    for k in range(1, len(adj)+1):
        best = None
        for indices in combinations(range(len(adj)), k):
            mask = sum(1 << u for u in indices)
            if not dominates(adj, mask) or components_coloring(adj, mask) is None:
                continue
            owners = sum(1 << u for u in indices if adj[u]&mask)
            edges = sum((adj[u]&mask).bit_count() for u in indices)//2
            key = owners.bit_count(), -edges, mask
            if best is None or key < best[0]:
                best = key, mask, owners
        if best:
            return best[1:]


def hall_matching(adj, left, right):
    matched = {}
    def augment(u, seen):
        for v in bits(adj[u]&right):
            if v in seen:
                continue
            seen.add(v)
            if v not in matched or augment(matched[v], seen):
                matched[v] = u
                return True
        return False
    return all(augment(u, set()) for u in bits(left))


def test_z1(trials=3000):
    rng = Random(1009)
    nonempty = 0
    checked = 0
    for trial in range(trials):
        n = rng.randint(3, 12)
        adj = [0]*n
        probability = rng.uniform(.08, .8)
        for u in range(n):
            for v in range(u+1, n):
                if rng.random() < probability:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        if any(not a for a in adj):
            continue
        checked += 1
        selected, owners = canonical_dom(adj)
        outside = ((1 << n)-1)^selected
        wb = 0
        for u in bits(owners):
            wb |= adj[u]&outside
        w0 = outside^wb
        z1 = sum(1 << u for u in bits(selected^owners) if adj[u]&w0)
        assert hall_matching(adj, z1, w0)
        nonempty += bool(z1)
    return {'generated': trials, 'no_isolate_graphs_checked': checked,
            'nonempty_z1_cases': nonempty, 'all_matchable': True}


def test_enlarged(trials=18000):
    rng = Random(9010)
    checked = 0
    for trial in range(trials):
        delta = rng.randint(8, 18)
        n = rng.randint(5, 13)
        adj = [0]*n
        prob = rng.uniform(.12, .9)
        for u in range(n):
            for v in range(u+1, n):
                if rng.random() < prob:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        if any(a.bit_count() >= delta for a in adj):
            continue
        leaves = [rng.randint(1, delta-a.bit_count()) for a in adj]
        result = repair_hall(adj, delta, leaves, include_positive_pool=True)
        checked += 1
        if result:
            return {'checked': checked, 'first_failure': result}
    return {'checked': checked, 'first_failure': None}


def test_singleton_algebra(max_delta=70):
    checked = 0
    for delta in range(6, max_delta+1):
        a = optimal_a(delta)
        A, b = 2+a*(delta-a-1), delta+a-1
        lam = Fraction(2*A-b, delta-3)
        omega, c = A+lam, A-b
        assert A >= b and A+2*lam-2*b >= 0
        assert A+(2*lam-b)*Fraction(delta,3) >= 0
        for r in range(delta//2+1):
            for beta in range(2*r, delta+1):
                for t in range(1, delta-beta+1):
                    debt = b*t-A-lam*beta
                    if debt <= 0:
                        continue
                    assert t >= r+1
                    for z in range(delta-beta-t+1):
                        # A full gain supplies one further Omega unit.
                        assert omega*(t-r)+c*z >= debt
                        checked += 1
                        if z >= r:
                            assert omega*(t-r-1)+c*z >= debt
                            checked += 1
                        if z == r-1:
                            tau = beta-r-1
                            assert omega*(t-r-1)+lam*tau+c*z >= debt
                            checked += 1
    return {'delta_range':[6,max_delta], 'resource_lower_bounds_checked':checked,
            'all_singleton_cases_pass':True}


if __name__ == '__main__':
    result = {'z1_matching': test_z1(), 'enlarged_hall': test_enlarged(),
              'singleton_algebra': test_singleton_algebra()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
