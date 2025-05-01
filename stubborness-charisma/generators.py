import numpy as np

from bases import Voter, Candidate, VoterFactory, CandidateFactory

class UniformVoter(VoterFactory):
    def __init__(self, stubborness_dist = (0, 1), charisma_dist = (0, 1)):
        self.stubborness_dist = stubborness_dist
        self.charisma_dist = charisma_dist
    def create(self, id):
        v = Voter(id, np.random.uniform(0, 1), np.random.uniform(*self.charisma_dist), np.random.uniform(*self.stubborness_dist))
        return v

class UniformCandidate(CandidateFactory):
    def create(self, id):
        c = Candidate(id, np.random.uniform(0, 1))
        return c

class FixedCandidate(CandidateFactory):
    def __init__(self, C):
        self.C = C

    def create(self, id):
        c = Candidate(id, (id + 1) / (self.C + 1))
        return c