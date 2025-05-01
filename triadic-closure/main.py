import networkx as nx
import networkx.generators.random_graphs as r_graphs
import numpy as np

from base import Universe

G = r_graphs.erdos_renyi_graph(50, 0.5)
U = Universe(G)

round_i = 1
while True:
    res = U.transform_round()
    if not res:
        break
    print(res)
    round_i += 1
print(f"Stabilized in {round_i} rounds.")