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
from matplotlib.ticker import MaxNLocator
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

import random
import copy
import math
import numpy as np
from importlib import reload

from typing import List, Tuple, Dict, Any

# %%
import bases
reload(bases)
from bases import *
import votingrules
reload(votingrules)
from votingrules import *
import generators
reload(generators)
from generators import *  


# %%
def plot_degrees(G, ax=None):
    pos = nx.nx_agraph.graphviz_layout(G, prog='neato')
    degrees = dict(G.degree())

    # Sort nodes by degree (in descending order)
    sorted_nodes = sorted(degrees, key=degrees.get, reverse=True)

    norm = Normalize(vmin=min(degrees.values()), vmax=max(degrees.values()))
    cmap = plt.colormaps['viridis']
    node_colors = [cmap(norm(degrees[node])) for node in sorted_nodes]


    # Draw the graph
    nx.draw(G, pos, ax=ax, with_labels=False, nodelist=sorted_nodes, node_color=node_colors, node_size=100)

    fig = plt.gcf()
    norm = Normalize(vmin=min(degrees.values()), vmax=max(degrees.values()))
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Degree')


# %%
def plot_votes(G, candidates: List[Candidate], ax=None):
    pos = nx.nx_agraph.graphviz_layout(G, prog='neato')
    all_votes = {node: G.nodes[node]['info'].cast_vote(candidates).id for node in G.nodes()}

    norm = Normalize(vmin=min([x.id for x in candidates]), vmax=max([x.id for x in candidates]))
    cmap = plt.colormaps['viridis']
    node_colors = [cmap(norm(all_votes[node])) for node in G.nodes()]

    node_line_width = [v.stubbornness for i, v in G.nodes(data='info')]
    max_stub = max(node_line_width)
    if max_stub < 1e-6:
        node_line_width = [1] * len(node_line_width)
    else:
        node_line_width = [np.interp(sv, [0, max_stub], [0.5, 4]) for sv in node_line_width]
    print([float(x) for x in node_line_width])

    # Draw the graph
    nx.draw(G, pos, ax=ax, 
            with_labels=False, 
            nodelist=G.nodes(), 
            node_color=node_colors,
            node_size=100, 
            linewidths=node_line_width, 
            edgecolors='black')

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.6)
    cbar.set_label('Candidate ID')
    cbar.ax.yaxis.set_major_locator(MaxNLocator(integer=True))


# %%
def perform_edge_adjustment(world: World):
    for e in random.choices(list(world.G.edges()), k=20):
        choice = random.choice([0, 1])
        chosen_nodeid = e[choice]
        other_nodeid = e[1 - choice]
        world.G.nodes[chosen_nodeid]['info'].adjust_opinion(world.G.nodes[other_nodeid]['info'])
    

def get_results(world: World, repetitions=1000):
    while True:
        result = world.get_voting_result()
        yield result
        for i in range(repetitions):
            perform_edge_adjustment(world)



# %%
C = 4
V = 25

world = World(V, C, PluralityVoting())
world.generate_voters(UniformVoter(stubbornness_dist=(0,0.5)))
world.generate_candidates(FixedCandidate(C))

# %%
num_rows = 1
num_cols = 2
res_gen = get_results(world, 100)
fig, ax = plt.subplots(num_rows, num_cols, figsize=(6.5, 3))
for i in range(num_rows * num_cols):
    row = i // num_cols
    col = i % num_cols
    result = next(res_gen)
    print(f"Round {i}: Candidate {result[0][0].id} won with {result[0][1]} votes")
    plot_votes(world.G, world.candidates, ax=ax[col])
plt.savefig('stubbornness.svg', bbox_inches='tight')

# %%
C = 4
V = 30

base_world = World(V, C, PluralityVoting())
base_world.generate_candidates(FixedCandidate(C))
base_world.generate_voters(UniformVoter())

num_rows = 3
num_cols = 3
ch_vals, st_vals = np.meshgrid(np.linspace(0, 0.3, num_cols), np.linspace(0, 0.1, num_rows))
fig, ax = plt.subplots(num_rows, num_cols, figsize=(11, 7), sharex=True, sharey=True)
print(st_vals)
print(ch_vals)
for row in range(num_rows):
    for col in range(num_cols):
        curr_world = copy.deepcopy(base_world)
        st_max = st_vals[row, col]
        ch_max = ch_vals[row, col]
        for v in curr_world.voters:
            v.stubbornness *= st_max
            v.charisma *= ch_max
        result_gen = get_results(curr_world, 1000)
        # Skip 1st result because it is the initial state
        next(result_gen)
        result = next(result_gen)
        print(f"Round with max stubbornness {st_max :.3f}: Candidate {result[0][0].id} won with {result[0][1]} votes")
        plot_votes(curr_world.G, curr_world.candidates, ax=ax[row, col])
# Add column labels on top
for j, ax_y in enumerate(ax[0]):
    ax_y.set_title(f'max $ch$: {ch_vals[0, j]}', fontsize=12,pad=10)

# Add row labels on the left
for i, ax_x in enumerate(ax[:, 0]):
    ax_x.text(-0.3, 0.5, f'max $st$: {st_vals[i, 0]}',
            transform=ax_x.transAxes,  # interpret x, y in axis coords
            fontsize=12,
            va='center', ha='right',
            rotation=90)
plt.savefig('ch-st.svg', bbox_inches='tight')

# %%
