from mesa import Agent, Model, space, time
import random
import numpy as np

class Party(Agent):
    """
    A political party within a Landscape
    """
    def __init__(self,
                 model,
                 unique_id,
                 loc,
                 fitness = 1):
                 self.unique_id = unique_id
                 self.model = model
                 self.loc = loc
                 self.fitness = fitness

    # step: update fitness
    def step():
        # subject to stimulus
        # interact agents
        # leave community
        # find another community and add to that
        raise NotImplementedError


    def advance():
        # update fitness here?
        raise NotImplementedError

    def update_fitness():
        raise NotImplementedError


class Landscape(Model):
    """
    A political landscape; single grid of 10 x 10
    """
    def __init__(self,
                 num_parties,
                 width = 10,
                 height = 10,
                 new_party_chance = 0.01
                 ):
                 self.width = width
                 self.height = height
                 self.grid = space.SingleGrid(self.width, self.height, False)

                 # TODO Is dit de handigste scheduler?
                 self.schedule = time.SimultaneousActivation(self)
                 #self.parties = []
                 self.num_agents = num_parties
                 self.new_party_chance = new_party_chance
                 self.total_parties_made = 0

                 for i in range(self.num_agents):
                     # Move to empty doesnt work in this context so find_empty is used
                     loc = self.grid.find_empty()
                     assert loc, "More parties than places in grid; the political landscape is too full!"

                     #TEMP
                     fitness = random.random()
                     new_party = Party(self, i, loc, fitness)
                     self.grid.place_agent(new_party, loc)
                     self.schedule.add(new_party)

                     # Kan ook uit scheduler gehaald worden vgm; even kijken wat handiger is
                     #self.parties.append(new_party)
                     self.total_parties_made += 1

    # during timestep:
    # random chance to generate new party
    # updates fitnesses of parties
    # find least fit party -> disappear due to selection pressure, merge or spinoff
    def timestep(self):

        # Random chance to generate a new party
        if random.random() <= self.new_party_chance:
            self.new_party()

        # implement scheduler
        # self.schedule.step()
        #
        # # fitness should be calculated in advance?
        # self.schedule.advance()
        # calculate fitness for  each party after all parties have been update
        agent_list = self.schedule.agents

        min_fit_id = np.argmin([agent.fitness for agent in agent_list])
        least_fit = self.schedule.agents[min_fit_id]
        min_fit = least_fit.fitness
        if min_fit < 0.01:#(1 - (1 / len(agent_list))):
            self.remove_party(least_fit)
            print("removed")
        else:
            neighbors = self.grid.get_neighbors(least_fit.loc, True)
            random_neighbor = random.choice(neighbors)
            self.merge(least_fit, random_neighbor)
            print("merged")

        print(min_fit)

    def new_party(self, fitness = None):
        # Find empty location in the grid
        loc = self.grid.find_empty()

        # Use the total_parties_made counter as the id of the new party
        self.total_parties_made += 1
        if not fitness:

            new_party = Party(self, self.total_parties_made,  loc)
        else:
            new_party = Party(self, self.total_parties_made,  loc, fitness)
        neighbors = self.grid.get_neighbors(loc, True)
        self.grid.place_agent(new_party, loc)
        self.schedule.add(new_party)

        # now get people in party :)

    def remove_party(self, party):
        self.grid.remove_agent(party)
        self.schedule.remove(party)

    def merge(self, least_fit_party, neighbor_party):
        new_fitness = neighbor_party.fitness + least_fit_party.fitness

        if random.random() < 0.99:
            # spinoff
            self.new_party(new_fitness)
        else:
            # merge
            least_fit_party.fitness = new_fitness
            # do things with population etc

        self.remove_party(least_fit_party)
        self.remove_party(neighbor_party)


if __name__ == '__main__':
    obj = Landscape(5)
    obj.timestep()
