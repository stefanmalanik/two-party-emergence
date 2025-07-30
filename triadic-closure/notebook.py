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
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from IPython.display import display, clear_output

import random
import time
import copy
import math
import numpy as np
import pandas as pd
from importlib import reload


# %%
import base
reload(base)
from base import NoFlipUniverse, ForceFlipUniverse


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
    friend_G.add_nodes_from(G.nodes)
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
NFU = NoFlipUniverse(G)
FFU = ForceFlipUniverse(G, 0.1)
pos = nx.kamada_kawai_layout(NFU.G)
draw_graph(NFU.G, pos)

# %%
# %matplotlib inline
pos = nx.kamada_kawai_layout(NFU.G)
round_i = 1
while True:
    res = NFU.transform_round()
    if res is None:
        break
    # print(res)
    round_i += 1
draw_graph(NFU.G, pos)
print(f"Stabilized in {round_i} rounds.")
print(f"Distribution: {find_stable_distribution(NFU.G)}")

        

# %%
def run_round(n, p_friend, p_favor_e=None):
    G = r_graphs.erdos_renyi_graph(n, p_friend)
    if p_favor_e is None:
        U = NoFlipUniverse(G)
    else:
        U = ForceFlipUniverse(G, p_favor_e)
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
    return round_cnt, flip_cnt, find_stable_distribution(U.G)

def run_rounds(rds, n, p_friend, p_favor_e=None):
    results = []
    for i in range(rds):
        print(f"{i+1}/{rds}")
        rnd_cnt, flip_cnt, party_dist = run_round(n, p_friend, p_favor_e)
        party_dist = min(party_dist)
        results.append((rnd_cnt, flip_cnt, p_favor_e, party_dist, n))
    df = pd.DataFrame(results, columns=['round_cnt', 'flip_cnt', 'p_favor_e', 'dist', 'n'])
    return df


# %%
df = run_rounds(20, 25, 0.5)
df.describe()

# %%
n = 25
df_curr = df[df['n'] == n]
s1 = df_curr['round_cnt']
s2 = df_curr['dist']

# Create main plot
fig, ax1 = plt.subplots(figsize=(6, 3))

# Histogram for series1 on bottom x-axis
counts1, bins1, patches1 = ax1.hist(s1, bins=10, alpha=0.5, color='blue', edgecolor='black', label='Series 1')
ax1.set_xlabel('# rounds to convergence', color='blue')
ax1.tick_params(axis='x', labelcolor='blue')
ax1.set_ylabel('Frequency')

# Create a twin x-axis on the top
ax2 = ax1.twiny()

# Histogram for series2 on top x-axis
counts2, bins2, patches2 = ax2.hist(s2, bins=10, range=(0,10), alpha=0.5, color='red', edgecolor='black', label='Series 2')
ax2.set_xlabel('Size of smaller clique', color='red')
ax2.tick_params(axis='x', labelcolor='red')

# Layout and title
plt.title(f'Histogram of Graph with n={n}')
plt.savefig(f'histogram-{n}.svg', bbox_inches='tight')
plt.show()

# %%
df_save = df

# %%
df_save

# %%
