# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import networkx.generators.random_graphs as r_graphs
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from IPython.display import display, clear_output

import random
import time
import copy
import math
import numpy as np
from importlib import reload


# %%
import base
reload(base)
from base import Universe


# %%
def draw_graph(G, pos):
    clear_output(wait=True)
    ec = ['green' if t == 'f' else 'red' for u, v, t in G.edges(data='type')]
    el = {(u, v): G.edges[u, v]['unstab'] for u, v in G.edges}
    nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color = ec, font_size=12, node_size=1000)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=el, label_pos=0.1)
    plt.show()  # Redraw the figure

def find_stable_distribution(G):
    friend_G = nx.Graph()
    for u, v in G.edges:
        if G.edges[u, v]['type'] == 'f':
            friend_G.add_edge(u, v)
    conn = nx.node_connected_component(friend_G, 0)
    A = len(conn)
    res = [A, G.order() - A]
    
    return tuple(sorted(res))


# %%
# %matplotlib inline
G = r_graphs.erdos_renyi_graph(22, 0.5)
U = Universe(G, 0.2)
pos = nx.kamada_kawai_layout(U.G)
# draw_graph(U.G, pos)

# %%
# %matplotlib inline
pos = nx.kamada_kawai_layout(U.G)
output = display(display_id=True)
round_i = 1
while True:
    res = U.transform_round()
    if not res:
        break
    # print(res)
    # update_graph(U.G, pos)
    round_i += 1
# draw_graph(U.G, pos)
print(f"Stabilized in {round_i} rounds.")
print(f"Distribution: {find_stable_distribution(U.G)}")

        

# %%
def run_round(n, p_f, p_favor_e):
    G = r_graphs.erdos_renyi_graph(n, p_f)
    U = Universe(G, p_favor_e)
    round_i = 1
    while True:
        res = U.transform_round()
        if not res:
            break
        round_i += 1
    print(f"Stabilized in {round_i} rounds.")
    return round_i, find_stable_distribution(U.G)

def run_rounds(n, p_f, p_favor_e, rds):
    dist_dct = {}
    cnt_s = 0
    for i in range(rds):
        cnt, dist = run_round(n, p_f, p_favor_e)
        if dist not in dist_dct:
            dist_dct[dist] = 0
        dist_dct[dist] += 1
        cnt_s += cnt

    print(f"Avg stab: {cnt_s / rds}")
    print(f"Dist of res: {dist_dct}")

run_rounds(19, 0.5, 0.0, 20)


# %%
