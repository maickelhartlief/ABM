###### agents.py
# Speficies the `Member` class which is a subclass of a mesa.Agent. This 
# represents the agents of the model and handles characteristics, interacting, 
# and has the dependent variable political participation.
####

# Internal imports
from utils import set_valid, distance_normalizer

# External imports
import numpy as np
import random
from mesa import Agent, Model, space, time
from mesa.datacollection import DataCollector
import networkx as nx


class Member(Agent):
    '''
    Description: an Agent object represents a person in a community that has a political
                 participation based on characteristics, which are in turn modified by
                 interacting with other agents or with the environment
    Inputs:
        - unique_id: unique identifier of agent
        - model: model object agent is a part of
        - until_eligible: optional, number of steps until an agent can vote
        - vote_duty: optional, whether agent must vote (pps >= 2)
        - active: optional, one of the agent's characteristics
        - overt: optional, one of the agent's characteristics
        - autonomous: optional, one of the agent's characteristics
        - continuous: optional, one of the agent's characteristics
        - outtaking: optional, one of the agent's characteristics
        - expressive: optional, one of the agent's characteristics
        - social: optional, one of the agent's characteristics
        - ses: optional, socio-economic status
        - char_modifiers: optional, dictionary with tendencies for characteristics
          to change according to stimulus (>.5: up, <.5: down, not present: unchanged)
    Functions:
        - step(): performs 1 timestep of the agent
        - modify_characteristics(characteristic): calculates how much a characteristic
                                                  should be modified during a stimulus
        - stimulus(affected): adjust affected characteristics based on a model-wide stimulus
        - interaction_modifier(): calculates how much characteristics should be modified
                                  during an interaction
        - accept_interaction(): 
        - interact(): handle interaction with a random other agent in the community
        - move_community(): replaces the agent with a new identical agent, simulating the
                            agent moving to a diferent community and another taking its place
        - age(): updates the agent as time passes
        - distance(): calculates the distance between the self and the partner by 
                      Euclidean distance between personality traits related to 
                      friendship and socio-economic status.
        social_ids(): creates a list of ids that the agent is connected to in the
                      social network
        unconnected_ids(): creates a list of ids that the agent is not connected to in the
                           social network
        new_social(): adds new connections from the agent based on the Fermi-Dirac distribution.
                      choice of addition depends on similarity in SES, and characteristics 
                      social, approaching and autonomous.
        remove_social(): removes a few random connections from the agent with a probability determined 
                         by the Fermi-Dirac distribution. Choice of removal depends on similarity in on 
                         similarity in SES, and characteristics social, approaching and autonomous.
        consider_connection(partner, method): Calculate the (Fermi Dirac) probability of agent being 
                                              connected to 'potential agent' and based on method add or 
                                              remove the connection randomly.
        - update_pp(): updates the political participation of the agent, based on its
                       characteristics.
    '''

    def __init__(self,
                 unique_id,
                 model,
                 until_eligible = 0,
                 vote_duty = False,
                 active = 0,
                 overt = 0,
                 autonomous = 0,
                 approaching = 0,
                 continuous = 0,
                 outtaking = 0,
                 expressive = 0,
                 social = 0,
                 ses = 0,
                 char_modifiers = {'active' : .5,
                                   'overt' : .5,
                                   'continuous' : .5,
                                   'expressive' : .5,
                                   'outtaking' : .5}):
        
        # Initialize parameters based on inputs
        self.unique_id = unique_id
        self.model = model
        self.until_eligible = until_eligible
        self.vote_duty = vote_duty
        self.active = set_valid(active, verbose = True, name = 'active')
        self.overt = set_valid(overt, verbose = True, name = 'overt')
        self.autonomous = set_valid(autonomous, verbose = True, name = 'autonomous')
        self.approaching = set_valid(approaching, verbose = True, name = 'approaching')
        self.continuous = set_valid(continuous, verbose = True, name = 'continuous')
        self.outtaking = set_valid(outtaking, verbose = True, name = 'outtaking')
        self.expressive = set_valid(expressive, verbose = True, name = 'expressive')
        self.social = set_valid(social, verbose = True, name = 'social')
        self.ses = set_valid(ses, lower = 1, upper = 3, verbose = False, name = 'ses')
        
        # Initialize standard parameters
        self.pps = None
        self.move_community() # Happens to do all the steps necessary for initialization

        # Initialize social connections homophilysed on similarity
        if self.model.network == "homophily":
            self.new_social()
            self.remove_social()

        # Initialize ppz
        self.update_pp()


    def step(self):
        '''
        Description: performs 1 timestep of the agent
        '''

        # Subject to stimulus
        if self.model.stimulus:
            self.stimulus(self.model.characteristics_affected.keys())

        # Interact
        if random.uniform(0, 1) < self.model.prob_interaction:
            self.interact()

        # Modify connections if model is dynamic
        if self.model.dynamic:
                self.new_social()
                self.remove_social()

        # Move community
        if random.uniform(0, 1) < self.model.prob_move:
            self.move_community()

        # Update parameters 
        self.age()
        self.update_pp()


    def modify_characteristic(self, characteristic):
        '''
        Description: calculates how much a certain characteristic should change when agent
                     is subjected to a stimulus
        Inputs:
            - characteristics: name of the characteristic to modify
        Outputs:
            - modification to characteristics
        '''
        return 3 * (self.model.characteristics_affected[characteristic] - random.randint(0, 1)) / (self.autonomous + self.continuous)


    def stimulus(self, affected):
        '''
        Description: subject agent to stimulus, affecting (some of) its characteristics
        Inputs:
            - affected: list of names of characteristics that are affected by the stimulus
        '''

        # No political participation means no subjection to stimuli
        if self.pps == 0:
            return

        # Adjust these characteristics because of stimulus
        if 'active' in affected:
            self.active = set_valid(self.modify_characteristic('active') + self.active)
        if 'overt' in affected:
            self.overt = set_valid(self.modify_characteristic('overt') + self.overt)
        if 'continuous' in affected:
            self.continuous = set_valid(self.modify_characteristic('continuous') + self.continuous)
        if 'expressive' in affected:
            self.expressive = set_valid(self.modify_characteristic('expressive') + self.continuous)
        if 'outtaking' in affected:
            self.outtaking = set_valid(self.modify_characteristic('outtaking') + self.continuous)


    def interaction_modifier(self, partner):
        '''
        Description: calculates how characteristics should be modified based on an interaction
                     with another agent
        Inputs:
            - partner: agent that is being interacted with. modification is based on similarity
        Outputs:
            - modification to characteristics
        '''

        # Set modification based on characteristics
        mod = 1 / (self.autonomous + self.continuous)

        # Modify less when interaction is cynical
        if random.randint(0, int(19 * self.ses)) == 0:
            mod /= 10

        # Modify based on similarity between participants
        return mod / distance_normalizer(self.distance(partner))


    def accept_interaction(self):
        '''
        Description: checks whether agent would have an interaction
        Inputs:
            - 
        '''
        return self.pps < 3 and random.randint(0, 1)


    def interact(self):
        '''
        Description: attempts to interact with another agent, changing both their characteristics
        '''

        # Check whether personality would lead to interaction
        if not self.accept_interaction():
            return
        
        # Pick interaction partner from friends
        partner = random.choice(self.model.agents)
        while partner == self:
            partner = random.choice(self.model.agents)

        # Calculate path length
        if not nx.has_path(self.model.graph, self, partner):
            return
        path_length = nx.shortest_path_length(self.model.graph, self, partner)

        # Calculate probability that interaction is accepted based on path length where
        # P_i(len = 1) ~= 0.9 
        # P_i(len = 2) ~= 0.3
        # P_i(len = 3) ~= 0.1
        if 1 / (1 + np.exp(self.model.fermi_alpha * (path_length - self.model.fermi_b))) < random.random():
            return

        # Check whether partner's personality would lead to interaction
        if not partner.accept_interaction():
            return
        
        # Interact
        mod = self.interaction_modifier(partner)
        p_mod = partner.interaction_modifier(self)

        if self.approaching > partner.approaching:
            partner.approaching = set_valid(partner.approaching + p_mod)
        else:
            self.approaching = set_valid(self.approaching + mod)

        pps_diff = self.pps - partner.pps
        if pps_diff >= 0:
            partner.active = set_valid(partner.active + p_mod)
            self.overt = set_valid(self.overt + mod)
        elif pps_diff <= 0:
            self.active = set_valid(self.active + mod)
            partner.overt = set_valid(partner.overt + p_mod)

        # Update parameters
        self.contacts += 1
        partner.contacts += 1


    def move_community(self):
        '''
        Description: replaces the agent with a new identical agent, simulating the
                     agent moving to a different community and another taking its place
        '''
        self.time_in_community = 1
        self.contacts = 0
        self.until_eligible = self.model.until_eligible


    def age(self):
        '''
        Description: updates the agent as time passes
        '''
        self.time_in_community += 1
        
        if self.until_eligible == 0:
            return
        self.until_eligible -= 1


    def distance(self, partner):
        """
        Description: calculates the distance between the self and the partner by 
                     Euclidean distance between personality traits related to 
                     friendship and socio-economic status.
        Inputs:
            - partner: Agent to compare with
        Outputs:
            - distance between agents' characteristics
        """
        friend_charact = np.array([self.social, self.autonomous, self.approaching, self.ses])
        p_friend_charact = np.array([partner.social, partner.autonomous, partner.approaching, partner.ses])

        return np.linalg.norm((friend_charact - p_friend_charact))


    #### Adepted from https://github.com/MbBrainz/ABM-project-group8/blob/main/polarization/core/model.py
    @property
    def socials_ids(self):
        """
        Description: creates a list of ids that the agent is connected to in the
                     social network
        """
        return list(self.model.graph[self]) if self in self.model.graph.adj.keys() else []


    @property
    def unconnected_ids(self):
        """
        Description: creates a list of ids that the agent is not connected to in the
        social network
        """
        return [id for id in self.model.graph.nodes if (id not in self.socials_ids + [self])]
    

    def new_social(self):
        '''
        Descriptions: adds new connections from the agent based on the Fermi-Dirac distribution.
                      choice of addition depends on similarity in SES, and characteristics 
                      social, approaching and autonomous.
        '''
        
        # Determine how large the pool of potential candidates is, depending on
        # how many unconnected nodes are left or how many nodes we want to max
        # add per step
        n_potentials = min(len(self.unconnected_ids), self.model.edges_per_step)

        # randomly select 'n_potentials' from people the agent is not connected to
        pot_make_ids = np.random.choice(self.unconnected_ids, size=n_potentials, replace=False)

        for potential in self.model.schedule.agents:
            if potential in pot_make_ids:
                self.consider_connection(potential, method="ADD")
        

    def remove_social(self):
        '''
        Description: removes a few random connections from the agent with a probability determined 
                     by the Fermi-Dirac distribution. Choice of removal depends on similarity in on 
                     similarity in SES, and characteristics social, approaching and autonomous.
        '''
        
        # Determine how large the pool of potential candidates is, depending on
        # how many unconnected nodes are left or how many edges we want to max
        # add per step
        if not self.socials_ids:
            return
        n_potentials = min(len(self.socials_ids), self.model.edges_per_step)

        # randomly select 'n_potentials' from the agent's network
        pot_break_ids = np.random.choice(self.socials_ids, size=n_potentials, replace=False)

        # Remove connections
        for potential in self.model.schedule.agents:
            if potential in pot_break_ids:
                self.consider_connection(potential, method = "REMOVE")


    def consider_connection(self, partner, method):
        """
        Description: Calculate the (Fermi Dirac) probability of agent being connected 
                     to 'potential agent' and based on method add or remove the 
                     connection randomly.
        Inputs:
            partner: the agent to consider
            method: "ADD" or "REMOVE", whether the consideration is to add or remove 
                    a link
        """
        p_ij = 1 / ( 1 + np.exp(self.model.fermi_alpha * (self.distance(partner) - self.model.fermi_b)))

        if method == "ADD":
            if p_ij > random.random():
                self.model.graph.add_edge(self, partner)

        if method == "REMOVE":
            if p_ij < random.random():
                self.model.graph.remove_edge(self, partner)
    ####


    def update_pp(self):
        '''
        Description: calculates the agent's policical participation based on its 
                     characteristics. This is based on the Ruegin model, and works 
                     hierarchically (n must be reached before n+1 is considered)
        '''
        self.pps =  0 if random.uniform(0, 1) > .1 else 1

        # Agents that aren't eligible do not have to update their pps
        if self.until_eligible:
            return

        # Increase the level based on characteristics, and stop as soon as 1 check fails.
        if self.vote_duty or self.active + self.approaching - (5 / 3) * self.ses > random.randint(2, 4):
            self.pps = 2
        else:
            return

        if self.active + self.overt + self.approaching + self.social + ((2.5 * self.contacts ) / self.time_in_community) > random.randint(12, 18):
            self.pps = 3
        else:
            return

        if self.overt + self.expressive > random.randint(4, 6):
            self.pps = 4
        else:
            return

        if self.overt + self.autonomous + self.approaching + self.outtaking > random.randint(10, 14):
            self.pps = 5
        else:
            return

        if self.active + self.approaching - self.outtaking + self.expressive - self.social > random.randint(1, 3):
            self.pps = 6
        else:
            return

        if self.overt + self.social + (2.5 * self.contacts ) / self.time_in_community > random.randint(7, 11):
            self.pps = 7
        else:
            return

        if self.active + self.overt + self.approaching + self.outtaking + self.expressive + (5 / 3) * self.ses > random.randint(15, 21):
            self.pps = 8
        else:
            return

        if self.continuous + self.expressive + (5 / 3) * self.ses > random.randint(7, 11):
            self.pps = 9
        else:
            return

        if self.active + self.overt + self.continuous + (5 / 3) * self.ses > random.randint(10, 14):
            self.pps = 10
        else:
            return

        if self.active + self.overt + self.approaching + self.continuous + (2.5 * self.contacts) / self.time_in_community + (5 / 3) * self.ses > random.randint(15, 21):
            self.pps = 11
        else:
            return

        if self.active + self.overt + self.autonomous + self.approaching + self.continuous - self.outtaking + (2.5 * self.contacts) / self.time_in_community + (5 / 3) * self.ses > random.randint(15, 21):
            self.pps = 12
        else:
            return
