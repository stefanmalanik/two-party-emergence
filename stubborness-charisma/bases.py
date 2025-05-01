from __future__ import annotations
from typing import List, Dict
from abc import ABC, abstractmethod 

import networkx.generators.random_graphs as r_graphs
import numpy as np

from votingrules import VotingRule

class Voter:
    def __init__(self, id, internal_opinion, charisma, stubborness):
        self.id = id
        self.internal_opinion = internal_opinion
        self.expressed_opinion = internal_opinion
        self.charisma = charisma
        self.stubborness = stubborness

    def adjust_opinion(self, other: Voter):
        self.expressed_opinion = (1 - other.charisma) * self.expressed_opinion + other.charisma * other.expressed_opinion
        self.expressed_opinion = (1 - self.stubborness) * self.expressed_opinion + self.stubborness * self.internal_opinion

    def cast_vote(self, candidates):
        # Implement the simplest voting rule: always vote for the candidate with the closest opinion
        closest_cand = min(candidates, key=lambda x: abs(x.internal_policy - self.expressed_opinion))
        return closest_cand      
    
class VoterFactory(ABC):
    @abstractmethod
    def create(self, id) -> Voter:
        pass

class Candidate:
    def __init__(self, id, internal_policy):
        self.id = id
        self.internal_policy = internal_policy 

class CandidateFactory(ABC):
    @abstractmethod
    def create(self, id) -> Candidate:
        pass


class World:

    
    def __init__(self, V, C, voting_rule: VotingRule, BA_graph_param = 3):
        self.V = V
        self.C = C
        self.voting_rule = voting_rule
        self.BA_graph_param = BA_graph_param

        self.G = None
        self.voters = None
        self.candidates = None
    
    def generate_voters(self, voter_factory: VoterFactory):
        self.G = r_graphs.barabasi_albert_graph(self.V, self.BA_graph_param)
        self.voters = []
        for node in self.G.nodes():
            v = voter_factory.create(node)
            self.G.nodes[node]['info'] = v
            self.voters.append(v)
    
    def generate_candidates(self, candidate_factory: CandidateFactory):
        self.candidates = []
        for i in range(self.C):
            c = candidate_factory.create(i)
            self.candidates.append(c)
        self.candidates.sort(key=lambda x: x.internal_policy)
    
    def get_voting_result(self) -> Dict:
        return self.voting_rule.get_voting_result(self.voters, self.candidates)
