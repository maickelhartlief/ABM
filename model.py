import utils

import numpy as np
import random

class Model(object):

    def __init__(self,
                 p = 0,
                 q = 0,
                 r = 0,
                 characteristics_affected = []):
        self.p = utils.set_valid('p', p, max = 1)
        self.q = utils.set_valid('q', q, max = 1)
        self.r = utils.set_valid('r', r, max = 1)
        self.characteristics_affected = characteristics_affected

        self.time = 0
        self.agents = np.array([])


    def add_agent(self, agent):
        self.agents = np.append(self.agents, agent)


    def removed_agent(self, agent):
        self.agents = np.delete(self.agents, agent)


    def step(self):
        self.time += 1
        stimulus = random.uniform(0, 1) < self.p
        for agent in self.agents:
            if stimulus:
                agent.stimulus()
            if random.uniform(0, 1) < self.q:
                agent.interact()
            if random.uniform(0, 1) < self.r:
                agent.move_community()
            agent.age()
            agent.update_pp()


    def get_pps(self):
        return np.array([agent.pps for agent in self.agents])


