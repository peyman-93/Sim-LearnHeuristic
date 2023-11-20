''' Reviewed by Angel A. Juan 2023.06 for the TOP with stochastic / dynamic travel times '''

import time
import copy
import math
import random
import operator
import numpy as np

from aux_objects import Edge, Route, Solution
from simulation import simulation

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        MAIN SIMHEURISTIC ALGORITHM BASED ON THE PJ'S HEURISTIC
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def detExcecution(test, fleetSize, routeMaxCost, nodes, random_numbers):
    # select the best alpha value and efficiency list for computing enchanced savings
    # and generate an initial solution using the selected alpha value and efficiency list
    init_sol, eff_list = genInitSol(test, fleetSize, routeMaxCost, nodes, random_numbers)
    # set initial sol as Our Best Det sol in a Det environment
    OBD = init_sol

    # stage 1: start the main loop searching for better det sols
    elapsed = 0
    start_time = time.time()
    while elapsed < test.maxTime:
        # use the merging process of the PJs heuristic to generate a new det sol
        new_detSol = merging(True, test, fleetSize, routeMaxCost, nodes, eff_list, random_numbers)
        # if new_detSol is promising, update best det and stoch sols if appropriate
        if new_detSol.reward > OBD.reward:

            OBD = new_detSol
            OBD.time = time.time() -  start_time
        elapsed = time.time() - start_time

    # stage 2: refinement of the best k stoch sols
    simulation(OBD, test.longSim, routeMaxCost, test.varLevel) # guarantee that the OBD keeps an acurate estimate

    return OBD


def simExcecution(test, fleetSize, routeMaxCost, nodes, random_numbers):
    # select the best alpha value and efficiency list for computing enchanced savings
    # and generate an initial solution using the selected alpha value and efficiency list
    init_sol, eff_list = genInitSol(test, fleetSize, routeMaxCost, nodes, random_numbers)
    # set initial sol as Our Best Det sol in a Det environment
    OBD = init_sol
    simulation(OBD, test.shortSim, routeMaxCost, test.varLevel)
    list_OBS = []
    list_OBS.append(OBD)
    OBS = OBD

    # stage 1: start the main loop searching for better det and stoch sols
    elapsed = 0
    start_time = time.time()

    while elapsed < test.maxTime:
        # use the merging process of the PJs heuristic to generate a new det sol
        new_detSol = merging(True, test, fleetSize, routeMaxCost, nodes, eff_list, random_numbers)
        # if new_detSol is promising, update best det and stoch sols if appropriate
        if new_detSol.reward > OBS.reward:
            simulation(new_detSol, test.shortSim, routeMaxCost, test.varLevel)

            if new_detSol.reward_sim > OBS.reward_sim:
                OBS = new_detSol
                OBS.time = time.time() - start_time

                list_OBS.append(OBS)
        elapsed = time.time() - start_time

    # stage 2: refinement of the best k stoch sols
    list_OBS.sort(key=lambda sol: sol.reward_sim, reverse=True)
    #OBS = list_OBS[0]

    max_elite = 10  # max number of elite sols to consider
    k = min(max_elite, len(list_OBS))  # number of elite stochastic solutions to consider
    for i in range(0, k):
        new_OBS = list_OBS[i]
        simulation(new_OBS, test.longSim, routeMaxCost, test.varLevel)
        if new_OBS.reward_sim > OBS.reward_sim:
            OBS = new_OBS

    return OBS

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    GENERATE DUMMY SOLUTION
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" Generate Dummy Solution """
def dummySolution(routeMaxCost, nodes):
    sol = Solution()
    for node in nodes[1:-1]: # excludes the start and finish depots
        snEdge = node.dnEdge
        nfEdge = node.ndEdge
        snfRoute = Route() # construct the route (start, node, finish)
        snfRoute.edges.append(snEdge)
        snfRoute.reward += node.reward
        snfRoute.cost += snEdge.cost
        snfRoute.edges.append(nfEdge)
        snfRoute.cost += nfEdge.cost
        node.inRoute = snfRoute # save in node a reference to its current route
        node.isLinkedToStart = True # this node is currently linked to start depot
        node.isLinkedToFinish = True # this node is currently linked to finish depot
        if snfRoute.cost <= routeMaxCost:
            sol.routes.append(snfRoute) # add this route to the solution
            sol.cost += snfRoute.cost
            sol.reward += snfRoute.reward # total reward in route

    return sol

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    SELECT ALPHA, BUILD THE EFFICIENCY LIST AND GENERATE AN INITIAL SOLUTION
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def genInitSol(test, fleetSize, routeMaxCost, nodes, random_numbers):
    # tune the alpha value for generating enhanced savings
    best_reward = 0
    eff_list = []
    for new_alpha in np.linspace(0, 1, 11):
        new_effList = generateEfficiencyList(nodes, new_alpha)
        # obtain a greedy solution (BR = False) for the current alpha value
        sol = merging(True, test, fleetSize, routeMaxCost, nodes, new_effList, random_numbers)
        if sol.reward > best_reward:
            best_reward = sol.reward
            eff_list = new_effList
            init_sol = sol

    return init_sol, eff_list

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    GENERATE EFFICIENCY LIST
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" Generate efficiency list of nodes: construct edges and effList from nodes """
def generateEfficiencyList(nodes, alpha):
    start = nodes[0]
    finish = nodes[-1]
    for node in nodes[1:-1]: # excludes the start and finish depots
        snEdge = Edge(start, node) # creates the (start, node) edge (arc)
        nfEdge = Edge(node, finish) # creates the (node, finish) edge (arc)
        # compute the Euclidean distance as cost
        snEdge.cost = math.sqrt((node.x - start.x)**2 + (node.y - start.y)**2)
        nfEdge.cost = math.sqrt((node.x - finish.x)**2 + (node.y - finish.y)**2)
        # save in node a reference to the (depot, node) edge (arc)
        node.dnEdge = snEdge
        node.ndEdge = nfEdge

    efficiencyList = []
    for i in range(1, len(nodes) - 2): # excludes the start and finish depots
        iNode = nodes[i]
        for j in range(i + 1, len(nodes) - 1):
            jNode = nodes[j]
            ijEdge = Edge(iNode, jNode) # creates the (i, j) edge
            jiEdge = Edge(jNode, iNode)
            ijEdge.invEdge = jiEdge # sets the inverse edge (arc)
            jiEdge.invEdge = ijEdge
            # compute the Euclidean distance as cost
            ijEdge.cost = math.sqrt((jNode.x - iNode.x)**2 + (jNode.y - iNode.y)**2)
            jiEdge.cost = ijEdge.cost # assume symmetric costs
            # compute efficiency as proposed by Panadero et al.(2020)
            ijSavings = iNode.ndEdge.cost + jNode.dnEdge.cost - ijEdge.cost
            edgeReward = iNode.reward + jNode.reward
            ijEdge.savings = ijSavings
            ijEdge.efficiency = alpha * ijSavings + (1 - alpha) * edgeReward
            jiSavings = jNode.ndEdge.cost + iNode.dnEdge.cost - jiEdge.cost
            jiEdge.savings = jiSavings
            jiEdge.efficiency = alpha * jiSavings + (1 - alpha) * edgeReward
            # save both edges in the efficiency list
            efficiencyList.append(ijEdge)
            efficiencyList.append(jiEdge)

    # sort the list of edges from higher to lower efficiency
    efficiencyList.sort(key = operator.attrgetter("efficiency"), reverse = True)
    return efficiencyList

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            MERGING PROCESS IN THE PJ'S HEURISTIC
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" Perform the BR edge-selection & routing-merging iterative process """
def merging(useBR, test, fleetSize, routeMaxCost, nodes, eff_list, random_numbers):
    sol = dummySolution(routeMaxCost, nodes) # compute the dummy solution
    effList = copy.copy(eff_list) # make a shallow copy of the effList since it will be modified
    while len(effList) > 0: # list is not empty
        position = 0
        if useBR == True:
            position = getRandomPosition(test, test.firstParam, test.secondParam, len(effList), random_numbers)
        else:
            position = 0  # greedy behavior
        ijEdge = effList.pop(position) # select the next edge from the list
        # determine the nodes i < j that define the edge
        iNode = ijEdge.origin
        jNode = ijEdge.end
        # determine the routes associated with each node
        iRoute = iNode.inRoute
        jRoute = jNode.inRoute
        # check if merge is possible
        isMergeFeasible = checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge, routeMaxCost)
        # if all necessary conditions are satisfied, merge and delete edge (j, i)
        if isMergeFeasible == True:
        # if still in list, delete edge (j, i) since it will not be used
            jiEdge = ijEdge.invEdge
            if jiEdge in effList:
                effList.remove(jiEdge)
            # iRoute will contain edge (i, finish)
            iEdge = iRoute.edges[-1] # iEdge is (i, finish)
            # remove iEdge from iRoute and update iRoute cost
            iRoute.edges.remove(iEdge)
            iRoute.cost -= iEdge.cost
            # node i will not be linked to finish depot anymore
            iNode.isLinkedToFinish = False
            # jRoute will contain edge (start, j)
            jEdge = jRoute.edges[0]
            # remove jEdge from jRoute and update jRoute cost
            jRoute.edges.remove(jEdge)
            jRoute.cost -= jEdge.cost
            # node j will not be linked to start depot anymore
            jNode.isLinkedToStart = False
            # add ijEdge to iRoute
            iRoute.edges.append(ijEdge)
            iRoute.cost += ijEdge.cost
            iRoute.reward += jNode.reward
            jNode.inRoute = iRoute
            # add jRoute to new iRoute
            for edge in jRoute.edges:
                iRoute.edges.append(edge)
                iRoute.cost += edge.cost
                iRoute.reward += edge.end.reward
                edge.end.inRoute = iRoute
            # delete jRoute from emerging solution
            sol.cost -= ijEdge.savings
            sol.routes.remove(jRoute)

    # sort the list of routes in sol by reward (reward) and delete extra routes
    sol.routes.sort(key = operator.attrgetter("reward"), reverse = True)
    for route in sol.routes[fleetSize:]:
        sol.reward -= route.reward # update reward
        sol.cost -= route.cost # update cost
        sol.routes.remove(route) # delete extra route
    return sol


#get random number from the text file
def getRand(test, random_numbers):
    # index is within the range of random numbers
    a = random_numbers[test.index1]
    test.index1 += 1
    if test.index1 >= len(random_numbers):
        test.index1 = 0

    # Return the random number at the specified index
    return a

""" Gets a random position according to a Gemetric(beta) """
def getRandomPositionOld(beta1, beta2, size):
    # randomly select a beta value between beta1 and beta2
    beta = beta1 + random.random() * (beta2 - beta1)
    index = int(math.log(random.random())/math.log(1 - beta))
    index = index % size
    return index

def getRandomPosition(test, beta1, beta2, size, random_numbers):
    # Calculate beta using the random_value and the specified range (beta1, beta2)
    beta = beta1 + getRand(test, random_numbers) * (beta2 - beta1)
    # Calculate index based on beta
    index = int(math.log(getRand(test, random_numbers))/math.log(1 - beta))
    index = index % size

    return index

""" Check if merging conditions are met """
def checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge, routeMaxCost):
    # condition 1: iRoute and jRoure are not the same route object
    if iRoute == jRoute: return False
    # condition 2: jNode has to be linked to start and i node to finish
    if iNode.isLinkedToFinish == False or jNode.isLinkedToStart == False: return False
    # condition 3: cost after merging does not exceed maxTime (or maxCost)
    if iRoute.cost + jRoute.cost - ijEdge.savings > routeMaxCost: return False
    # else, merging is feasible
    return True
