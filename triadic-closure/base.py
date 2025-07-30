import random

import networkx as nx
import numpy as np

from utils import ListDict

class NoFlipUniverse:
    def __init__(self, G: nx.Graph):
        self.G = self.create_graph(G)

        # Cache edge instability
        for u, v in self.G.edges:
            self.G.edges[u, v]['unstab'] = self.get_edge_unstab(u, v)
        
        # Keep track of unstable edges
        self.unstab_edges = ListDict()
        for u, v in self.G.edges:
            if self.G.edges[u, v]['unstab'] > 0:
                self.unstab_edges.add(frozenset([u, v]))

    def get_edge_unstab(self, u: int, v: int) -> int:
        unstab_value = 0
        for w in self.G.nodes:
            if w == u or w == v:
                continue
            if not self.is_stable_tri((u, v, w)):
                unstab_value += 1
        return unstab_value
    
    @classmethod
    def create_graph(cls, G: nx.Graph) -> nx.Graph:
        new_G = nx.Graph()
        # Create complete graph with friend / enemy edges
        for u in G.nodes:
            for v in G.nodes:
                if u == v:
                    continue
                if not G.has_edge(u, v):
                    new_G.add_edge(u, v, type= 'e')
                else:
                    new_G.add_edge(u, v, type= 'f')
        return new_G
    
    def get_tri_enemies(self, tri: tuple[int, int, int]) -> int:
        edge_types = []
        for u, v in [(0, 1), (1, 2), (2, 0)]:
            assert tri[u] != tri[v], "Triangle vertices must be distinct"
            edge_types.append(self.G.get_edge_data(tri[u], tri[v])['type'])
        
        return edge_types.count('e')
    
    def is_stable_tri(self, tri: tuple[int, int, int]) -> bool:
        enemy_count = self.get_tri_enemies(tri)
        if enemy_count == 0:
            return True
        if enemy_count == 2:
            return True
        return False

    def flip_edge(self, u: int, v: int) -> None:
        assert frozenset([u, v]) in self.unstab_edges, f"Edge ({u}, {v}) is stable"

        def increm_edge(u: int, v: int):
            assert self.G.edges[u, v]['unstab'] < len(self.G) - 2, f"Invalid increment of ({u}, {v})"
            self.G.edges[u, v]['unstab'] += 1
            if self.G.edges[u, v]['unstab'] == 1:
                self.unstab_edges.add(frozenset([u, v]))
        def decrem_edge(u: int, v: int):
            assert self.G.edges[u, v]['unstab'] > 0, f"Invalid decrement of ({u}, {v})"
            self.G.edges[u, v]['unstab'] -= 1
            if self.G.edges[u, v]['unstab'] == 0:
                self.unstab_edges.remove(frozenset([u, v]))

        # Update edge instability
        for w in self.G.nodes:
            if w == u or w == v:
                continue
            if self.is_stable_tri((u, v, w)):
                increm_edge(u, v)
                increm_edge(v, w)
                increm_edge(u, w)
            else:
                decrem_edge(u, v)
                decrem_edge(v, w)
                decrem_edge(u, w)

        self.G.edges[u, v]['type'] = 'e' if self.G.edges[u, v]['type'] == 'f' else 'f'

    def get_random_unstab_tri(self) -> tuple[int, int, int] | None:
        # Sample random edge from unstable edges
        if len(self.unstab_edges) == 0:
            return None
        a, b = self.unstab_edges.choose_random()

        # Randomize order of a, b
        a, b = random.choice([(a, b), (b, a)])

        # Find a random unstable triangle
        perm = np.random.permutation(list(self.G.nodes))
        for c in perm:
            c = int(c)
            if c == a or c == b:
                continue
            if not self.is_stable_tri((a, b, c)):
                # Must exist
                return (a, b, c)
        assert False, f"No unstable triangle found along ({a}, {b})"
    
    @classmethod
    def push_away(cls, x, k):
        return (x ** k) / ((x ** k) + ((1 - x) ** k))
    
    def transform_round(self) -> tuple[()] | tuple[int, int] | None:
        tri = self.get_random_unstab_tri()
        if tri is None:
            return None
        
        u, v, w = tri
        # We work in unstable triangle tri from the point of view of u
        # Either flip edge (u, v) or (u, w) according to friends of u
        
        same_votes = 0
        total_friends = 0
        for a in self.G.neighbors(u):
            if a == v:
                continue
            # Only care about friends of u
            if self.G.edges[u, a]['type'] == 'e':
                continue

            total_friends += 1
            # Count votes for (u, v)
            if self.G.edges[a, v]['type'] == self.G.edges[u, v]['type']:
                same_votes += 1
        

        # Intrinsic probability of flipping (u, v) is 0.5
        p_change_uw = (same_votes + 0.5) / (total_friends + 1)
        p_change_uw = self.push_away(p_change_uw, 2)

        if np.random.random() < p_change_uw:
            # Flip (u, w)
            self.flip_edge(u, w)
            return (u, w)

        # Do not flip anything otherwise
        return ()

        # Flip (u, v)
        # self.flip_edge(u, v)
        # return (u, v)


class ForceFlipUniverse(NoFlipUniverse):

    def __init__(self, G: nx.Graph, enemy_priority: float):
        super().__init__(G)
        self.enemy_priority = enemy_priority

    def transform_round(self) -> tuple[()] | tuple[int, int] | None:
        tri = self.get_random_unstab_tri()
        if tri is None:
            return None
        
        u, v, w = tri
        # We work in unstable triangle tri from the point of view of u
        # Either flip edge (u, v) or (u, w) according to friends of u
        
        # Incentivize friend edges to be picked in a 1-enemy triangle
        def is_enemy(a, b):
            return self.G.edges[a, b]['type'] == 'e'
        if self.get_tri_enemies((u, v, w)) == 1:
            if random.random() < self.enemy_priority:
                # Pick the two friend edges to potentially flip
                # (u, v) and (u, w) are friends, (u, w) is enemy
                if is_enemy(u, v):
                    # u, v -> v, w
                    u, v, w = w, u, v
                elif is_enemy(u, w):
                    # u, w -> v, w
                    u, v, w = v, u, w
                else:
                    # As is
                    pass
        same_votes = 0
        total_friends = 0
        for a in self.G.neighbors(u):
            if a == v:
                continue
            # Only care about friends of u
            if self.G.edges[u, a]['type'] == 'e':
                continue

            total_friends += 1
            # Count votes for (u, v)
            if self.G.edges[a, v]['type'] == self.G.edges[u, v]['type']:
                same_votes += 1
        

        # Intrinsic probability of flipping (u, v) is 0.5
        p_change_uw = (same_votes + 0.5) / (total_friends + 1)
        p_change_uw = self.push_away(p_change_uw, 2)

        if np.random.random() < p_change_uw:
            # Flip (u, w)
            self.flip_edge(u, w)
            return (u, w)

        # Flip (u, v) instead
        self.flip_edge(u, v)
        return (u, v)