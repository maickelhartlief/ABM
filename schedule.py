from collections import defaultdict
from mesa.time import RandomActivation


class RandomActivationPP(RandomActivation):
    '''
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask breed...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step() method.
    '''
    def __init__(self, model):
        super().__init__(model)
        self.voters = 0

    def add(self, agent):
        '''
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        '''
        self._agents[agent.unique_id] = agent

    def step(self, party):
        '''
        Executes the step of each agent breed, one at a time, in random order.

        Args:
            by_breed: If True, run all agents of a single breed before running
                      the next one.
        '''
        party.step()
        self.voters = party.get_voters()
        super().step()

    def get_voters(self):
        '''
        Returns amount of voters in current population
        '''
        return self.voters
