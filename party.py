###### party.py
# 
####

# Internal imports
import utils
from agents import Member

# External imports
import numpy as np
import random
from mesa import Agent, Model, space, time
from mesa.datacollection import DataCollector
import networkx as nx
from importlib import import_module
import sys
from scipy import stats


class Party_model(Model):
    '''
    description: a Party object holds the environment parameters and manages all the agents.
    inputs:
        - prob_stimulus: optional, probability that a stimulus happens to all agents each step
        - prob_interaction = optional, probability that an agent interacts each step,
        - prob_move = optional, probability that an agent moves community,
        - until_eligible = optional, steps needed for new agents to be allowed to vote,
        - characteristics_affected = optional, dictionary of affected characteristics when agent is
          exposed to stimulus
    functions:
        - add_agent(agent): adds an agent to the model
        - step(): updates environment and takes a step for each agent
        - get_pps(): returns data of all agents' political participation over time
    '''

    def __init__(self,
                 prob_stimulus = None,
                 prob_interaction = None,
                 prob_move = None,
                 prob_link = None,
                 network = None,
                 params = None,
                 dynamic = False):
        '''
        description: initializes new Model object
        inputs:
            - prob_stimulus: probability that a stimulus happens to all agents each step
            - prob_interaction = probability that an agent interacts each step,
            - prob_move = probability that an agent moves community,
            - until_eligible = steps needed for new agents to be allowed to vote,
            - characteristics_affected = dictionary of effect of stimulus on agent
        '''
        self.description = 'A model for testing.'
        if params is None:
            params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))
        
        if prob_stimulus is None:
            prob_stimulus = params.prob_stimulus
        if prob_interaction is None:
            prob_interaction = params.prob_interaction
        if prob_move is None:
            prob_move = params.prob_move
        if prob_link is None:
            prob_link = params.prob_link
        

        self.n_runs = params.n_runs
        self.char_distr = params.char_distr
        self.prob_stimulus = utils.set_valid(prob_stimulus, upper = 1, verbose = True, name = 'p')
        self.prob_interaction = utils.set_valid(prob_interaction, upper = 1, verbose = True, name = 'q')
        self.prob_move = utils.set_valid(prob_move, upper = 1, verbose = True, name = 'r')
        self.prob_link = utils.set_valid(prob_link, upper = 1, verbose = True, name = 'linkage')
        self.until_eligible = params.until_eligible
        self.characteristics_affected = params.characteristics_affected
        self.edges_per_step = params.edges_per_step
        self.n_agents = params.n_agents
        self.m_barabasi = params.m_barabasi
        self.fermi_alpha = params.fermi_alpha
        self.fermi_b = params.fermi_b
        self.dynamic = dynamic
        self.network = network if network is not None else params.networks[0]

        self.schedule = time.RandomActivation(self)
        self.time = 0
        self.agents = np.array([])
        self.stimulus = False

        self.datacollector = DataCollector(model_reporters = {"voters" : lambda m : self.get_voters()},
                                           agent_reporters = {"political participation" : "pps"})

        # create network
        self.graph = None
        if self.network == 'fully_connected':
            self.graph = nx.complete_graph(n = self.n_agents)
        elif self.network == "holme_kim":
            self.graph = nx.powerlaw_cluster_graph(n = self.n_agents, m = self.m_barabasi, p = prob_link)
        elif self.network == 'homophily':
            self.graph = nx.Graph()
        elif self.network == "not_connected":
            self.graph = nx.Graph()
        else:
            raise Exception(f"'{self.network}' is not a valid model structure")


        self.init_agents()
        self.running = True
        self.datacollector.collect(self)

    def add_agent(self, agent):
        '''
        description: adds agent to the model
        input:
            - agent object to add to the model
        '''
        self.agents = np.append(self.agents, agent)
        self.schedule.add(agent)

        # Attaches agent to node
        if (self.network == "homophily") or (self.network == "not_connected"):
            self.graph.add_node(agent)
        else:
            self.graph = nx.relabel_nodes(self.graph, {agent.unique_id: agent})

    def init_agents(self):
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
                        self,
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
            self.add_agent(agent)


    def step(self):
        '''
        description: updates environment and takes a step for each agent
        '''
        # check whether stimulus happens for all agents
        self.stimulus = random.uniform(0, 1) < self.prob_stimulus

        # TODO might be worth collecting after the step?
        self.schedule.step()
        self.datacollector.collect(self)


    def get_voters(self):
        return len([True for agent in self.agents if agent.pps >= 2])
