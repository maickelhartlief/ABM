'''
TODO:
- meaning of global/local community:
  it seemse like the base model only looks at 1 local community,
  which now means that a person moving always takes the exact
  same characteristics as the previous owner of that house.
  this seems odd.
- implement more analysis
- add voters per iteration as model level data collection
'''

from utils import set_valid, distance_normalizer

import numpy as np
import random
from mesa import Agent, Model, space, time,  DataCollector
import networkx as nx

class Member(Agent):
    '''
    description: an Agent object represents a person in a community that has a political
                 participation based on characteristics, which are in turn modified by
                 interacting with other agents or with the environment
    inputs:
        - name: unique identifier of agent
        - model: model object agent is a part of
        - until_eligible: optional, number of steps until an agent can vote
        - vote_duty: optional, whether agent must vote
        - active: optional, one of the agent's characteristics
        - overt: optional, one of the agent's characteristics
        - autonomous: optional, one of the agent's characteristics
        - continuous: optional, one of the agent's characteristics
        - outtaking: optional, one of the agent's characteristics
        - expressive: optional, one of the agent's characteristics
        - social: optional, one of the agent's characteristics
        - ses: optional, socio-economic status
        - char_modifiers: optional, dictionary with tendencies for characteristics
          to change according to stimulus (>.5 = up, <.5 = down)
    functions:
        - modify_characteristics(characteristic): calculates how much a characteristic
                                                  should be modified during a stimulus
        - stimulus(affected): adjust affected characteristics based on a model-wide stimulus
        - interaction_modifier(): calculates how much characteristics should be modified
                                  during an interaction
        - interact(): handle interaction with a random other agent in the community
        - move_community(): replaces the agent with a new identical agent, simulating the
                            agent moving to a diferent community and another taking its place
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
        '''
        description: initializes a new Agent object
        '''
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
        self.pps = None
        self.char_modifiers = char_modifiers

        # initial settings for contacts and time spent in location
        self.move_community()

        if self.model.graph == "ba":
            # initialize social connections based on similarity
            self.new_social()
            self.remove_social()

        # initialize ppz
        self.update_pp()


    def step(self):
        # perform stimulus if applicable
        if self.model.stimulus:
            self.stimulus(self.model.characteristics_affected.keys())

        # let agent interact according to probability
        if random.uniform(0, 1) < self.model.prob_interaction:
            self.interact()

        # # Let agent make new connection and remove old according to probability
        if self.model.dynamic:
            if random.uniform(0, 1) < self.model.prob_friend:
                self.new_social()
                self.remove_social()

        # move agent according to probability
        if random.uniform(0, 1) < self.model.prob_move:
            self.move_community()

        self.age()
        self.update_pp()


    def modify_characteristic(self, characteristic):
        '''
        description: calculates how much a certain characteristic should change when agent
                     is subjected to a stimulus
        inputs:
            - characteristics: name of the characteristic to modify
        outputs:
            - modification to characteristics
        '''
        return 3 * (self.char_modifiers[characteristic] - random.randint(0, 1)) / (self.autonomous + self.continuous)


    def stimulus(self, affected):
        '''
        description: subject agent to stimulus, affecting (some of) its characteristics
        inputs:
            - affected: list of names of characteristics that are affected by the stimulus
        '''

        # no political participation means no subjection to stimuli
        if self.pps == 0:
            return

        # only these 5 characteristics can be affected by stimuli
        # NOTE: the netlogo code only checks whether values are valid after this step,
        #       meaning that over or underflow in autonomous and continuous will change
        #       the output of modify_charactastics(). we check it immediately.
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
        description: calculates how characteristics should be modified based on an interaction
                     with another agent
        outputs:
            - modification to characteristics
        '''

        # set modification to political participation
        # NOTE: stochasticity here was moved a level up to rejecting / accepting interaction
        mod = 1 / (self.autonomous + self.continuous)

        # modify less when interaction is cynical
        if random.randint(0, int(19 * self.ses)) == 0:
            mod /= 10

        # difference between participants hierin meenemen
        mod /= distance_normalizer(self.distance(partner))

        return mod


    def interact(self):
        '''
        description: attempts to interact with another agent, changing both their characteristics
        '''

        # check whether personality would lead to interaction
        # NOTE: this states that only people that are already politically active actually interact
        #       with others about politics. This seems off, and there are barely interactions in
        #       the model. changing this makes the percentage of voters much more accurate.
        if self.pps < 3 and random.randint(0, 1):
            return
        # if self.social + (self.pps / 3 + 1) + self.active + random.uniform(0, 2.5) <= 10:
        #     return

        # pick interaction partner from friends
        # if len(self.socials_ids):
        #     partner_id = random.choice(self.socials_ids)
        #     partner = [agent for agent in self.model.agents if agent.unique_id == partner_id][0]

        partner = random.choice(self.model.agents)
        while partner == self:
            partner = random.choice(self.model.agents)

        # TODO indexing doesn't work
        # @Do: If you want to do this just use partner.unique_id instead of self.model.graph[partner.unique_id]

        # path length
        if nx.has_path(self.model.graph, self.unique_id, partner.unique_id):
            path_length = nx.shortest_path_length(self.model.graph, self.unique_id, partner.unique_id)
        else:
            return

        # if path_length >= 2:
        #     return

        # calculate probability that interaction is accepted based on path length
        # path length 1 = 0.9, path length 2 = 0.3, path length 3 = 0.1 probability

        p_accept = 1 / ( 1 + np.exp(self.model.fermi_alpha * (path_length - self.model.fermi_b)))

        if p_accept < random.random():
            return
        # check whether partner's personality would accept interaction
        # NOTE: this states that only people that are already politically active actually interact
        #       with others about politics. This seems off, and there are barely interactions in
        #       the model. changing this makes the percentage of voters much more accurate.
        if partner.pps == 0 and random.randint(0, 1):
            return
        # if partner.social + partner.active + partner.approaching + random.uniform(0, 2.5) <= 10:
        #     return

        ## interact
        mod = self.interaction_modifier(partner)
        p_mod = partner.interaction_modifier(self)

        if self.approaching > partner.approaching:
            partner.approaching = set_valid(partner.approaching + p_mod)
        else:
            self.approaching = set_valid(self.approaching + mod)

        pps_diff = self.pps - partner.pps
        if pps_diff > 0:
            partner.active = set_valid(partner.active + p_mod)
            # TODO seems like this should be mod instead of p_mod, but this is what the base model does
            self.overt = set_valid(self.overt + mod)
        elif pps_diff < 0:
            self.active = set_valid(self.active + mod)
            # TODO seems like this should be p_mod instead of mod, but this is what the base model does
            partner.overt = set_valid(partner.overt + p_mod)

        self.contacts += 1
        partner.contacts += 1


    def move_community(self):
        '''
        description: replaces the agent with a new identical agent, simulating the
                     agent moving to a different community and another taking its place
        '''
        self.time_in_community = 1
        self.contacts = 0
        self.until_eligible = self.model.until_eligible


    def age(self):
        '''
        description: updates the agent as time passes
        '''
        self.time_in_community += 1
        if self.until_eligible == 0:
            return

        self.until_eligible -= 1


    def distance(self, partner):
        """
        description: calculate the distance between the self and the partner by Euclidean
        distance between personality traits related to friendship and
        social economic status.
        inputs:
            - partner: Agent to compare with
        output:
            - distance: float; bigger if individuals are less similar

        """
        friend_charact = np.array([self.social, self.autonomous, self.approaching, self.ses])
        p_friend_charact = np.array([partner.social, partner.autonomous, partner.approaching, partner.ses])

        return np.linalg.norm((friend_charact - p_friend_charact))


        # taken from https://github.com/MbBrainz/ABM-project-group8/blob/main/polarization/core/model.py
    @property
    def socials_ids(self):
        """
        description: creates a list of ids that the agent is connected to in the
        social network
        """
        return [social_id for social_id in self.model.graph[self.unique_id]]

    @property
    def unconnected_ids(self):
        """
        description: creates a list of ids that the agent is not connected to in the
        social network
        """
        return [id for id in self.model.graph.nodes if (id not in self.socials_ids + [self.unique_id])]

    def new_social(self):
        """
        Adds a new random connection from the agent with a probability determined by the Fermi-Dirac distribution.
        choice of addition depends on similarity in SES, and characteristics social, approaching and autonomous
        """
        # determine how large the pool of potential candidates is, depending on
        # how many unconnected nodes are left or how many nodes we want to max
        # add per step
        if len(self.unconnected_ids) < self.model.edges_per_step:
            n_potentials = len(self.unconnected_ids)
        else:
            n_potentials = self.model.edges_per_step

        # randomly select 'n_potentials' from people the agent is not connected to
        pot_make_ids = np.random.choice(self.unconnected_ids, size=n_potentials, replace=False)

        # get agents from model.schedule with the id's from the pot_make_ids
        pot_makes = [social for social in self.model.schedule.agents if social.unique_id in pot_make_ids]

        for potential in pot_makes:
            self.consider_connection(potential, method="ADD")

    def remove_social(self):
        """
        Removes a few random connections from the agent with a probability determined by the Fermi-Dirac distribution.
        Choice of removal depends on similarity in on similarity in SES, and characteristics social, approaching and autonomous
        """
        # determine how large the pool of potential candidates is, depending on
        # how many unconnected nodes are left or how many edges we want to max
        # add per step
        if len(self.socials_ids) < self.model.edges_per_step:
            n_potentials = len(self.socials_ids)
        else:
            n_potentials = self.model.edges_per_step

        # randomly select 'n_potentials' from the agent's network
        pot_break_ids = np.random.choice(self.socials_ids, size=n_potentials, replace=False)

        # get agents from model.schedule with the id's from the pot_break_ids
        pot_breaks = [social for social in self.model.schedule.agents if social.unique_id in pot_break_ids]

        for potential in pot_breaks:
            self.consider_connection(potential, method="REMOVE")

    def consider_connection(self, partner, method):
        """
        Calculate the (Fermi Dirac) probability of agent being connected to 'potential agent' and based on method add or remove the connection randomly
        Args:
            partner (Agent): the agent to consider
            method (str): "ADD" or "REMOVE"
        """
        p_ij = 1 / ( 1 + np.exp(self.model.fermi_alpha * (self.distance(partner) - self.model.fermi_b)))
        # self.model.p_accept_list.append(p_ij)

        if method == "ADD":
            if p_ij > random.random():
                self.model.graph.add_edge(self.unique_id, partner.unique_id)
                #print("connection added")

        if method == "REMOVE":
            if p_ij < random.random():
                self.model.graph.remove_edge(self.unique_id, partner.unique_id)


    def update_pp(self):
        '''
        description: calculates the agent's policical participation based on its characteristics
        '''
        self.pps =  0 if random.uniform(0, 1) > .1 else 1

        # agents that aren't eligible do not have to update their pps
        if self.until_eligible: # != 0
            return

        # NOTE: probably a mistake in base model where vote duty alone does not envoke checks for higher levels.
        if self.vote_duty or self.active + self.approaching - (5 / 3) * self.ses > random.randint(2, 4):
            self.pps = 2
        else:
            return

        # increase the level based on characteristics, and stop as soon as 1 check fails.
        # NOTE: base model uses model time, instead of time spent in community of agent. the latter makes much more sense
        if self.active + self.overt + self.approaching + self.social + ((2.5 * self.contacts ) / self.time_in_community)  > random.randint(12, 18):
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
