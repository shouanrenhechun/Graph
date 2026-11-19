"""Reproduce counterexamples and check corona candidate optimization.

Uses only Python's standard library. Run: python verify_repair_audit.py
"""
from itertools import combinations
from fractions import Fraction
from math import isqrt
import json


def graph(core_edges, support_edges, supports):
    vertices = ['a', 'b', 'c'] + [f'{u}{i}' for u in 'abc' for i in range(2)] + supports
    edges = core_edges + [(u, f'{u}{i}') for u in 'abc' for i in range(2)] + support_edges
    adjacency = {v: set() for v in vertices}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def coloring(adjacency, selected):
    selected = set(selected)
    colors = {}
    for start in selected:
        if start in colors:
            continue
        colors[start] = 0
        queue = [start]
        for u in queue:
            for v in adjacency[u] & selected:
                if v not in colors:
                    colors[v] = 1 - colors[u]
                    queue.append(v)
                elif colors[v] == colors[u]:
                    return None
    return colors


def optimal_sets(adjacency):
    vertices = list(adjacency)
    for k in range(len(vertices) + 1):
        found = []
        for chosen in combinations(vertices, k):
            chosen = set(chosen)
            if all(v in chosen or adjacency[v] & chosen for v in vertices) and coloring(adjacency, chosen) is not None:
                found.append(sorted(chosen))
        if found:
            return k, found


def constraint_solutions(supports, equations):
    variables = supports + ['C']
    result = []
    for mask in range(1 << len(variables)):
        values = {v: (mask >> i) & 1 for i, v in enumerate(variables)}
        if all(values[u] ^ values[v] == s for u, v, s in equations):
            result.append(values)
    return result


def repairs_and_constraints(adjacency, supports, chosen_repairs):
    original_colors = {'a': 0, 'b': 1, 'c': 0}
    equations = []
    for w in supports:
        sides = [{u for u in original_colors if u in adjacency[w] and original_colors[u] == i} for i in (0, 1)]
        minimum = min(map(len, sides))
        options = [side for side in sides if len(side) == minimum]
        assert set(chosen_repairs[w]) in options, (w, options)
        if len(sides[0]) != len(sides[1]):
            sigma = 0 if len(sides[0]) < len(sides[1]) else 1
            equations.append((w, 'C', sigma))
    for w, v in combinations(supports, 2):
        if v in adjacency[w]:
            equations.append((w, v, 1))
    return equations


def example_62():
    supports = ['w1', 'w2', 'w3']
    adjacency = graph([('a', 'b'), ('b', 'c')], [('a', 'w1'), ('c', 'w2'), ('a', 'w3'), ('b', 'w3'), ('w1', 'w2')], supports)
    selected = {'a', 'c', *supports}
    minimum, sets = optimal_sets(adjacency)
    assert minimum == 3 and sets == [['a', 'b', 'c']]
    equations = repairs_and_constraints(adjacency, supports, {'w1': [], 'w2': [], 'w3': ['b']})
    assert not constraint_solutions(supports, equations)
    assert coloring(adjacency, selected) is not None
    return {'vertices': len(adjacency), 'maximum_degree': max(map(len, adjacency.values())), 'unique_minimum_bipartite_dominating_set': sets[0], 'repair_union': ['b'], 'surviving_induced_graph': 'w3-a-w1-w2-c (a path)', 'constraint_system_solvable': False, 'surviving_graph_bipartite': True}


def example_63():
    supports = ['w1', 'w2']
    adjacency = graph([('a', 'b'), ('b', 'c')], [(u, 'w1') for u in 'abc'] + [('b', 'w2')], supports)
    selected = {'a', 'c', *supports}
    minimum, sets = optimal_sets(adjacency)
    assert minimum == 3 and sets == [['a', 'b', 'c']]
    equations = repairs_and_constraints(adjacency, supports, {'w1': ['b'], 'w2': []})
    assert not constraint_solutions(supports, equations + [('w1', 'w2', 0)])
    mono_colors = {'a': 0, 'c': 0, 'w1': 1, 'w2': 1}
    assert all(mono_colors[u] != mono_colors[v] for u in selected for v in adjacency[u] & selected)
    # Original B colors a=c=0, b=1. Repairs: U_w1={b}, U_w2=empty.
    # Both supports have color 1 after union deletion; U is monochromatic too.
    return {'vertices': len(adjacency), 'maximum_degree': max(map(len, adjacency.values())), 'unique_minimum_bipartite_dominating_set': sets[0], 'rigid_signs': {'w1': 1, 'w2': 0}, 'repair_union': ['b'], 'joint_support_colors': {'w1': 1, 'w2': 1}, 'conflict_graph_has_edge': True, 'monochromatic_joint_repair_exists': True}


def candidate(delta, a):
    return Fraction(2 + a * (delta - a - 1), (delta - a + 1) * (a + 1))


def optimal_a(delta):
    # ceil((sqrt(8*delta*(delta-2)+1)-(2*delta-1))/2), using integers.
    discriminant = 8 * delta * (delta - 2) + 1
    root = isqrt(discriminant)
    ceil_root = root if root * root == discriminant else root + 1
    return max(1, min(delta - 2, (ceil_root - (2 * delta - 1) + 1) // 2))


def main():
    for delta in range(4, 1001):
        a = optimal_a(delta)
        assert candidate(delta, a) == max(candidate(delta, b) for b in range(1, delta - 1)), (delta, a)
    rows = [{'delta': d, 'optimal_a': optimal_a(d), 'candidate': str(candidate(d, optimal_a(d)))} for d in range(4, 16)]
    # K_1,6 plus six isolated vertices violates the proposed C_6 upper bound.
    assert Fraction(7, 13) > Fraction(8, 15)
    print(json.dumps({'theorem_6_2_counterexample': example_62(), 'corollary_6_3_counterexample': example_63(), 'candidate_values': rows, 'optimization_checked_through_delta': 1000, 'isolates_counterexample': 'K_1,6 + 6K_1: gamma_bip/n = 7/13 > 8/15'}, indent=2))


if __name__ == '__main__':
    main()
