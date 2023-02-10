###### party.py
# Specifies the Party_model class which is a subclass of a mesa.Model. This 
# represents the environment of the model and handles all global functionality 
# like environment variables, data collection, initializing agents, and calling 
# the agents' step functions each step.
####

# Internal imports
from utils import get_config, set_valid
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
    Description: a Party object holds the environment parameters and manages all the agents.
    Inputs:
        - prob_stimulus: probability that a stimulus happens to all agents each step
        - prob_interaction: probability that an agent interacts each step,
        - prob_move: probability that an agent moves community,
        - prob_link: probability that an agent creates a link to another agent during initialization
        - network: which network structure to initialize the social network of agents with
        - params: parameters imported from config/[name].py
        - dynamic: whether the network structure changes over time
    Functions:
        - add_agent(agent): adds an agent to the model
        - init_agents(): initialize all agents of the model 
                         (must be done in the model for mesa's sensitivity analysis)
        - step(): updates model environment and takes a step for each agent
        - get_voters(): returns the number of voters in the model (#agents where agent.pps >= 2)
    '''
    params = import_module('configs.' + ('normal' if len(sys.argv) < 2 else sys.argv[1]))

    def __init__(self,
                prob_stimulus = params.prob_stimulus,
                 prob_interaction = params.prob_interaction,
                 prob_move = params.prob_move,
                 prob_link = params.prob_link,              
                 dynamic = False,
                 params = None):
        '''
        Description: initializes new Model object
        Inputs:
            - prob_stimulus: probability that a stimulus happens to all agents each step
            - prob_interaction: probability that an agent interacts each step,
            - prob_move: probability that an agent moves community,
            - prob_link: probability that an agent creates a link to another agent during initialization
            - network: which network structure to initialize the social network of agents with
            - params: parameters imported from config/[name].py
            - dynamic: whether the network structure changes over time
        '''
        
        # Handle Initializing when not provided
        if params is None:
            params = get_config()
        if prob_stimulus is None:
            prob_stimulus = params.prob_stimulus
        if prob_interaction is None:
            prob_interaction = params.prob_interaction
        if prob_move is None:
            prob_move = params.prob_move
        if prob_link is None:
            prob_link = params.prob_link
        if network is None:
            network = params.networks[0]
        
        # Initialize probabilities and check whether they are in range [0,1]
        self.prob_stimulus = set_valid(prob_stimulus, 
                                       upper = 1, 
                                       verbose = True, 
                                       name = 'prob_stimulus')
        self.prob_interaction = set_valid(prob_interaction, 
                                          upper = 1, 
                                          verbose = True, 
                                          name = 'prob_interaction')
        self.prob_move = set_valid(prob_move, 
                                   upper = 1, 
                                   verbose = True, 
                                   name = 'prob_move')
        self.prob_link = set_valid(prob_link, 
                                   upper = 1, 
                                   verbose = True, 
                                   name = 'linkage')
        
        # Initialize parameters based on config
        self.char_distr = params.char_distr
        self.until_eligible = params.until_eligible
        self.characteristics_affected = params.characteristics_affected
        self.edges_per_step = params.edges_per_step
        self.n_agents = params.n_agents
        self.m_barabasi = params.m_barabasi
        self.fermi_alpha = params.fermi_alpha
        self.fermi_b = params.fermi_b
        self.network = network
        self.dynamic = dynamic
        
        # Initialize standard parameters
        self.schedule = time.RandomActivation(self)
        self.time = 0
        self.agents = np.array([])
        self.stimulus = False
        self.running = True
        self.datacollector = DataCollector(model_reporters = {"voters" : lambda m : self.get_voters()},
                                           agent_reporters = {"political participation" : "pps"})

        # Create graph
        if network == 'fully_connected':
            self.graph = nx.complete_graph(n = self.n_agents)
        elif network == 'holme_kim':
            self.graph = nx.powerlaw_cluster_graph(n = self.n_agents, m = self.m_barabasi, p = prob_link)
        elif network in ['homophily', 'not_connected']:
            self.graph = nx.Graph()
        else:
            raise Exception(f"'{network}' is not a valid model structure")

        # Initialize agents and do first datacollection
        self.init_agents()
        self.datacollector.collect(self)

    def add_agent(self, agent):
        '''
        Description: adds agent to the model and graph
        Input:
            - agent: Agent object to add
        '''

        self.agents = np.append(self.agents, agent)
        self.schedule.add(agent)

        # Attach agent to node in graph
        if self.network in ['homophily', 'not_connected']:
            self.graph.add_node(agent)
        else:
            self.graph = nx.relabel_nodes(self.graph, {agent.unique_id: agent})

    def init_agents(self):
        '''
        Description: initialize all agents of the model and add them to the model (must be done 
                     in the model for mesa's sensitivity analysis).
        '''

        # Generate agent characteristics:
        if self.char_distr == 'normal': # Truncated normal distribution, to stay within limits
            mu = 2
            distr = stats.truncnorm(-mu, mu, loc = mu, scale = 1)
            samples = distr.rvs(self.n_agents * 8)
            characteristics = np.reshape(samples, (self.n_agents, 8))
        elif self.char_distr == 'uniform': # Uniform distribution within limits
            characteristics = np.random.uniform(1, 5, (self.n_agents, 8))

        # Intialize each agent
        for idx in range(self.n_agents):
            agent = Member(idx,
                        self,
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
            
            # Add agent to model
            self.add_agent(agent)


    def step(self):
        '''
        Description: updates environment and takes a step for each agent
        '''
        # check whether stimulus happens for all agents
        self.stimulus = random.uniform(0, 1) < self.prob_stimulus

        # TODO might be worth collecting after the step?
        self.schedule.step()
        self.datacollector.collect(self)


    def get_voters(self):
        return len([True for agent in self.agents if agent.pps >= 2])
