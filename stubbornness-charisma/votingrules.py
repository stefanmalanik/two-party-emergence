from typing import Dict
from abc import ABC, abstractmethod 

class VotingRule(ABC):
    @abstractmethod
    def get_voting_result(self, voters, candidates) -> Dict:
        pass

class PluralityVoting(VotingRule):
    
    def get_voting_result(self, voters, candidates):
        # Implement plurality voting rule
        votes = {}
        for v in voters:
            voted_cand = v.cast_vote(candidates)
            if voted_cand.id in votes:
                votes[voted_cand.id][1] += 1
            else:
                votes[voted_cand.id] = [voted_cand, 1]
        votes = list(votes.values())
        # Sort by number of votes, prioritizing lower ids in case of equality
        votes.sort(key=lambda x: (x[1], -x[0].id), reverse=True)

        return votes