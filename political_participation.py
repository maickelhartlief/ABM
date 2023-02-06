'''
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
'''

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from importlib import import_module
import sys
from mesa import time
from schedule import RandomActivationPP
from agents import Member
from scipy import stats
import numpy as np
from party import Party_model
import random

class PPmodel(Model):
    description = 'A model for testing.'
    params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))
    def __init__(self,
                 prob_stimulus = params.prob_stimulus,
                 prob_interaction = params.prob_interaction,
                 prob_move = params.prob_move,
                 prob_link = params.prob_link,
                 until_eligible = params.until_eligible,
                 characteristics_affected = params.characteristics_affected,
                 network = params.networks,
                 edges_per_step = params.edges_per_step,
                 n_agents = params.n_agents,
                 m_barabasi = params.m_barabasi,
                 fermi_alpha = params.fermi_alpha,
                 fermi_b = params.fermi_b,
                 n_runs = params.n_runs,
                 char_distr = params.char_distr):
        '''
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        '''
        super().__init__()
        # Set parameters
        self.prob_stimulus = prob_stimulus
        self.prob_interaction = prob_interaction
        self.prob_move = prob_move
        self.prob_link = prob_link
        self.until_eligible = until_eligible
        self.characteristics_affected = characteristics_affected
        self.network = network
        self.edges_per_step = edges_per_step
        self.n_agents = n_agents
        self.m_barabasi = m_barabasi
        self.fermi_alpha = fermi_alpha
        self.fermi_b = fermi_b
        self.n_runs = n_runs
        self.char_distr = char_distr

        self.schedule = RandomActivationPP(self)
        self.datacollector = DataCollector(
            {"Voters": lambda m: m.schedule.get_voters()})

        # Create Party
        self.party = Party_model(prob_stimulus = self.prob_stimulus,
                            prob_interaction = self.prob_interaction,
                            prob_move = self.prob_move,
                            prob_link = self.prob_link,
                            until_eligible = self.until_eligible,
                            characteristics_affected = self.characteristics_affected,
                            network = self.network,
                            edges_per_step = self.edges_per_step,
                            n_agents = self.n_agents,
                            m_barabasi = self.m_barabasi,
                            fermi_alpha = self.fermi_alpha,
                            fermi_b = self.fermi_b)

        # Create agent characteristics:
        if self.char_distr == 'normal': # truncated normal distribution, to stay within limits
            mu = 2
            distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
            samples = distr.rvs(self.n_agents * 8)
            characteristics = np.reshape(samples, (self.n_agents, 8))
        elif self.char_distr == 'uniform': # uniform distribution within limits
            characteristics = np.random.uniform(1, 5, (self.n_agents, 8))

        # intialize each agent
        for idx in range(self.n_agents):
            agent = Member(idx,
                        self.party,
                        # NOTE: This was a flat 20% probability, butit is more natural to make this chance related to prob_move.
                        until_eligible = 0 if random.uniform(0, 1) > self.prob_move else self.until_eligible,
                        vote_duty = random.uniform(0, 1) < .03,
                        active = characteristics[idx, 0],
                        overt = characteristics[idx, 1],
                        autonomous = characteristics[idx, 2],
                        approaching = characteristics[idx, 3],
                        continuous = characteristics[idx, 4],
                        outtaking = characteristics[idx, 5],
                        expressive = characteristics[idx, 6],
                        social = characteristics[idx, 7],
                        ses = random.randint(1, 3))
            self.party.add_agent(agent)
            self.schedule.add(agent)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step(self.party)
        self.datacollector.collect(self)

    def run_model(self, step_count=200):
        if self.verbose:
            print('Initial number wolves: ',
                  self.schedule.get_breed_count(Wolf))
            print('Initial number sheep: ',
                  self.schedule.get_breed_count(Sheep))

        for i in range(step_count):
            print("------")
            print(i)
            self.step()

        if self.verbose:
            print('')
            print('Final number wolves: ',
                  self.schedule.get_breed_count(Wolf))
            print('Final number sheep: ',
                  self.schedule.get_breed_count(Sheep))
