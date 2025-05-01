import networkx.generators.random_graphs as r_graphs
import networkx as nx
import matplotlib.pyplot as plt

G = r_graphs.watts_strogatz_graph(20, 5, 0.1)

pos = nx.kamada_kawai_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', font_size=12, node_size=1000)

plt.show()