"""Integer-only counterexample certificate, using Python's standard library.

Run: python counterexample_verify.py
The explicit subfamily proof needs only lower_bound() and an integer comparison.
The original 13-state DP and direct small-graph enumeration are extra checks.
"""
import json
from decimal import Decimal, localcontext
from pathlib import Path
from forest_dp import rooted_vector, total
from verification import count_tau


def tree(m=26, ell=5):
    edges = []
    hubs = []
    size = 1
    for _ in range(ell):
        hub = size
        size += 1
        hubs.append(hub)
        edges.append((0, hub))
        for _ in range(m):
            a, b, c = size, size + 1, size + 2
            size += 3
            edges.extend(((hub, a), (a, b), (b, c)))
    adj = [0] * size
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    assert len(edges) == size - 1
    return adj, hubs, edges


def lower_bound(m, ell):
    free = 22 ** m
    occupied = 4 * m * 22 ** (m - 1)
    return 4 * (free + occupied) ** ell - 2 * occupied ** ell


def direct_restricted_count(adj, hubs):
    """Original definitions; no DP or matching characterization is used.

    Hubs are never in J or S. An uncovered hub must belong to T.
    The central root is never in S. These restrictions define the subfamily.
    """
    n = len(adj)
    full = (1 << n) - 1
    hub_mask = sum(1 << h for h in hubs)
    forbidden_s = hub_mask | 1
    answer = 0
    for j in range(1 << n):
        if j & hub_mask:
            continue
        neighbors = 0
        independent = True
        for v in range(n):
            if j >> v & 1:
                neighbors |= adj[v]
                if adj[v] & j:
                    independent = False
                    break
        if not independent:
            continue
        white = j
        while white:
            old = white
            for v in range(n):
                if white >> v & 1:
                    continue
                hit = adj[v] & white
                if hit and not hit & (hit - 1):
                    white ^= hit
            if white == old:
                break
        if white:
            continue
        w = full ^ (j | neighbors)
        nw = 0
        for v in range(n):
            if w >> v & 1:
                nw |= adj[v]
        boundary = neighbors & nw & ~forbidden_s
        mandatory_t = hub_mask & w
        s = boundary
        while True:
            ns = 0
            for v in range(n):
                if s >> v & 1:
                    ns |= adj[v]
            allowed_t = w & ~ns
            if mandatory_t & allowed_t == mandatory_t:
                # All induced subgraphs of a tree are bipartite forests.
                support = j | s
                edge_count = sum((adj[v] & support).bit_count()
                                 for v in range(n) if support >> v & 1) // 2
                components = support.bit_count() - edge_count
                answer += 1 << (components + allowed_t.bit_count()
                                - mandatory_t.bit_count())
            if not s:
                break
            s = (s - 1) & boundary
    return answer


def verify():
    checks = []
    for m, ell in [(1, 1), (1, 2), (2, 1), (3, 1), (1, 3)]:
        adj, hubs, _ = tree(m, ell)
        direct = direct_restricted_count(adj, hubs)
        assert direct == lower_bound(m, ell), (m, ell, direct)
        tau_direct = count_tau(adj)
        assert tau_direct == total(rooted_vector(adj))
        assert direct <= tau_direct
        checks.append({'m': m, 'ell': ell, 'n': len(adj),
                       'restricted': direct, 'tau': tau_direct})
    m, ell = 26, 5
    adj, hubs, edges = tree(m, ell)
    n = len(adj)
    assert n == 396
    tau = total(rooted_vector(adj))
    for root in [hubs[0], n - 1]:
        assert total(rooted_vector(adj, root)) == tau
    bound = lower_bound(m, ell)
    target = 8 ** (n // 2)
    assert bound <= tau
    assert 1000 * bound > 1001 * target  # more than 0.1% violation
    assert 200 * bound > 201 * target  # in fact, more than 0.5%
    reduced_left, reduced_right = 802334527 * 11 ** 125, 2 ** 462
    assert bound == 2 ** 132 * reduced_left
    assert reduced_left > reduced_right
    assert tau * tau > 8 ** n
    with localcontext() as ctx:
        ctx.prec = 35
        lower_ratio = str(Decimal(bound) / Decimal(target))
        tau_ratio = str(Decimal(tau) / Decimal(target))
    record = {
        'm': m, 'ell': ell, 'n': n, 'edges_count': len(edges),
        'maximum_degree': max(a.bit_count() for a in adj),
        'subfamily_count': str(bound), 'tau': str(tau),
        'conjectured_bound': str(target),
        'integer_certificate': '1000 * subfamily_count > 1001 * 8**198',
        'integer_certificate_margin': str(1000 * bound - 1001 * target),
        'stronger_integer_certificate': '200 * subfamily_count > 201 * 8**198',
        'reduced_integer_comparison': '802334527 * 11**125 > 2**462',
        'reduced_integer_margin': str(reduced_left - reduced_right),
        'subfamily_ratio_decimal': lower_ratio, 'tau_ratio_decimal': tau_ratio,
        'small_direct_definition_checks': checks,
        'edges': edges,
    }
    out = Path(__file__).with_name('counterexample_certificate.json')
    out.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps({k: record[k] for k in
          ['n', 'maximum_degree', 'subfamily_ratio_decimal', 'tau_ratio_decimal',
           'integer_certificate']}, indent=2))
    print('PASS: direct definitions on small cases; exact subfamily inequality; '
          'original tree DP at three different roots.')


if __name__ == '__main__':
    verify()
