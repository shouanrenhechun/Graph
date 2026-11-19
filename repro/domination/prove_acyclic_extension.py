"""Checks for the induced-forest dominating-set extension of the C_delta theorem."""
from itertools import combinations
import json
from prove_general_cn import (exhaustive_six, random_general, random_matching_core,
                             equality_constructions, construct, is_forest)
from continue_hall_proof import dominates
from explore_global_allocation import components_coloring


def corona_cycle_four(leaves):
    adj = [0]*(4*(leaves+1))
    for u in range(4):
        v = (u+1)%4
        adj[u] |= 1 << v
        adj[v] |= 1 << u
        for leaf in range(4+u*leaves,4+(u+1)*leaves):
            adj[u] |= 1 << leaf
            adj[leaf] |= 1 << u
    return adj


def exact_domination(adj, acyclic):
    for size in range(1,len(adj)+1):
        for group in combinations(range(len(adj)),size):
            mask = sum(1 << u for u in group)
            valid = is_forest(adj,mask) if acyclic else components_coloring(adj,mask) is not None
            if valid and dominates(adj,mask):
                return size
    raise AssertionError('no valid dominating set')


def extension_examples():
    core = 15
    adj1 = corona_cycle_four(1)
    assert components_coloring(adj1,core) is not None and not is_forest(adj1,core)
    assert construct(adj1,4,lambda graph:core)[0] == 4
    assert construct(adj1,4,lambda graph:core,acyclic=True)[0] == 4
    adj2 = corona_cycle_four(2)
    bip,acyclic = exact_domination(adj2,False),exact_domination(adj2,True)
    assert (bip,acyclic) == (4,5)
    assert construct(adj2,4,lambda graph:core,acyclic=True)[0] == 5
    return {'old_bipartite_extension_can_have_a_cycle':True,
            'old_cycle_example':'cor(C4,1)',
            'modified_forest_construction_size_on_old_example':4,
            'pointwise_parameters_need_not_equal':{'graph':'cor(C4,2)','order':12,
                                                   'maximum_degree':4,'gamma_bip':bip,
                                                   'gamma_acyclic':acyclic}}


if __name__ == '__main__':
    result = {'all_isolate_free_graphs_order_2_to_6_checked':exhaustive_six(acyclic=True),
              'both_core_constructions_checked':True,
              'random_general_graphs_checked':random_general(trials=1500,acyclic=True),
              'random_matching_core_graphs_checked':random_matching_core(trials=600,acyclic=True),
              'sharp_corona_constructions_checked':equality_constructions(acyclic=True),
              'domination_induced_forest_and_bound_all_pass':True,
              'examples':extension_examples()}
    print(json.dumps(result,ensure_ascii=False,indent=2))
