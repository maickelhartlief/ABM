import networkx as nx
import matplotlib.pyplot as plt
from agents import Member
from party import Party_model
import random
from importlib import import_module

params = import_module('configs.normal')

model = Party_model(prob_stimulus = params.prob_stimulus,
                    prob_interaction = params.prob_interaction,
                    prob_move = params.prob_move,
                    prob_friend = params.prob_friend,
                    until_eligible = params.until_eligible,
                    characteristics_affected = params.characteristics_affected,
                    network = params.network,
                    edges_per_step = params.edges_per_step,
                    n_agents = params.n_agents,
                    m_barabasi = params.m_barabasi,
                    fermi_alpha = params.fermi_alpha,
                    fermi_b = params.fermi_b)

agents = [Member(idx,
                 model,
                 until_eligible = random.uniform(0, 1),
                 vote_duty = random.uniform(0, 1) < .03,
                 active = random.uniform(0, 5),
                 overt = random.uniform(0, 5),
                 autonomous = random.uniform(0, 5),
                 approaching = random.uniform(0, 5),
                 continuous = random.uniform(0, 5),
                 outtaking = random.uniform(0, 5),
                 expressive = random.uniform(0, 5),
                 social = random.uniform(0, 5),
                 ses = random.randint(1, 3)) for idx in range(100)]


g1 = nx.barabasi_albert_graph(n = 33, m = 1)
g1 = nx.relabel_nodes(g1, {n : agents[n] for n in range(33)})

g2 = nx.barabasi_albert_graph(n = 33, m = 2)
g2 = nx.relabel_nodes(g2, {n : agents[n + 33] for n in range(33)})

g3 = nx.barabasi_albert_graph(n = 34, m = 3)
g3 = nx.relabel_nodes(g3, {n : agents[n + 66] for n in range(34)})

g4 = nx.compose(nx.compose(g1, g2), g3)
g4.add_edge(list(g4)[1], list(g4)[33])
g4.add_edge(list(g4)[34], list(g4)[60])
g4.add_edge(list(g4)[61], list(g4)[90])
g4.add_edge(list(g4)[90], list(g4)[2])

colors = ['#8f98' + ('' if agent.pps >= 10 else '0') + str(agent.pps) for agent in list(g4)]
print(colors)
nx.draw(g4,
        node_color = colors, 
        node_size = [v * 10 for v in dict(g4.degree).values()])

plt.show()
