import networkx as nx
import networkx.generators.random_graphs as r_graphs
import numpy as np

from base import NoFlipUniverse

G = r_graphs.erdos_renyi_graph(50, 0.5)
U = NoFlipUniverse(G)

round_cnt = 1
flip_cnt = 0
while True:
    res = U.transform_round()
    if res is None:
        break
    if len(res) > 0:
        # Edge flipped in round
        flip_cnt += 1
    round_cnt += 1
print(f"Stabilized in {round_cnt} rounds with {flip_cnt} flips.")