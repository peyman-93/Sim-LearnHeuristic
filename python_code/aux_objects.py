''' Reviewed by Angel A. Juan 2023.06 for the TOP with stochastic / dynamic travel times '''

''' A class defining Test objects '''
class Test:

    def __init__(self, instanceName, maxTime, firstParam, secondParam, seed, shortSim, longSim, varLevel):
        self.instanceName = instanceName
        self.maxTime = int(maxTime) # maximum computation time (in sec.)
        self.firstParam = float(firstParam) # lower bound for beta in Geom(beta)
        self.secondParam = float(secondParam) # upper bound for beta in Geom(beta)
        self.seed = int(seed)
        self.shortSim = int(shortSim) # number of runs in a short sim
        self.longSim = int(longSim) # number of runs in along sim
        self.varLevel = float(varLevel) # Var[X] = varLevel * E[X]

''' A class defining Node objects '''
class Node:

    def __init__(self, ID, x, y, reward):
        self.ID = ID # node identifier (start = nodes[0]; finish = nodes[-1])
        self.x = x # Euclidean x-coordinate
        self.y = y # Euclidean y-coordinate
        self.reward = reward # reward (is 0 for start/finish depots)
        self.inRoute = None # route to which node belongs
        self.dnEdge = None # arc from start depot to this node
        self.ndEdge = None # arc from this node to finish depot
        self.isLinkedToStart = False # linked to start depot?
        self.isLindedToFinish = False # linked to finish depot?

''' A class defining Edge objects '''
class Edge:

    def __init__(self, origin, end):
        self.origin = origin # origin node of the edge (arc)
        self.end = end # end node of the edge (arc)
        self.cost = 0.0 # edge cost (e.g., travel time, monetary cost, etc.)
        self.savings = 0.0 # edge savings (Clarke & Wright)
        self.invEdge = None # inverse edge (arc)
        self.efficiency = 0.0 # edge efficiency (enriched savings)
        self.type = 0 # 0 = deterministic (default), 1 = stoch, 2 = dynamic

''' A class defining Route objects '''
class Route:

    def __init__(self):
         self.cost = 0.0 # cost of this route
         self.edges = [] # sorted edges in this route
         self.reward = 0.0 # total reward collected in this route

    def reverse(self): # e.g. 0 -> 2 -> 6 -> 0 becomes 0 -> 6 -> 2 -> 0
        size = len(self.edges)
        for i in range(size):
            edge = self.edges[i]
            invEdge = edge.invEdge
            self.edges.remove(edge)
            self.edges.insert(0, invEdge)

''' A class defining Solution objects '''
class Solution:

    last_ID = -1
    def __init__(self):
        Solution.last_ID += 1
        self.ID = Solution.last_ID
        self.routes = [] # routes in this solution
        self.cost = 0.0 # cost of this solution
        self.reward = 0.0 # sol reward under deterministic conditions
        self.reward_sim = 0.0 # sol reward after simulation (stoch/dynamic conditions)
