''' Reviewed by Angel A. Juan 2023.06 for the TOP with stochastic / dynamic travel times '''

import math
import random
import numpy as np

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    REVIEW THE SETTINGS (DET/STOCH/DYN) OF EACH EDGE (ARC)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# For experimental purposes, set the type of each edge in a given sol
# where: 0 = deterministic (default), 1 = stoch, and 2 = dynamic
def setEdgesType1(sol):
    for route in sol.routes:
        for e in route.edges:
            if e.end.ID % 2 == 0: # if ID of end node is even
                e.type = 1 # stochastic
            elif e.end.ID % 3 == 0: # if ID of end node is divisible by 3
                e.type = 2 # dynamic
            else:
                e.type = 0 # default




###STOCK/Dynamic EDGE####
def setEdgesType(sol):
    for route in sol.routes:
        for e in route.edges:
            if e.end.ID % 2 == 0:
                e.type = 2
            else:
                e.type = 0  # deterministic





"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    MONTE CARLO SIMULATION OF STOCHASTIC/DYNAMIC VALUES IN A SOL
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# This code assumes deterministic rewards on each node but random / dynamic travel times (cost),
# which might imply losing the accumulated reward in routes that exceed the max cost allowed
def simulation(sol, nRuns, routeMaxCost, varLevel):
    setEdgesType(sol) # for experiments, set the type of each edge (det/stoch/dyn)
    #weather = random.random() # daily weather adversity level, a random value between 0 (low) and 1 (high)
    #weather = np.random.random()
    accumRewardsInSol = 0 # accumulated sol rewards after multiple runs
    for i in range(0, nRuns):
        weather = np.random.random()
        rewardInSol = 0 # sol reward in this run
        for route in sol.routes:
            routeReward = 0 # route reward in this run
            routeCost = 0 # time- or distance-based cost
            for e in route.edges:
                node = e.end # end node of the edge
                routeReward += node.reward
                if e.type == 0: 
                    edgeCost = e.cost
                elif e.type == 1: # edge e has a stochastic travel time
                    edgeCost = getStochasticValue(mean=e.cost, varLevel=varLevel)
                elif e.type == 2: # edge e has a dynamic travel time depending upon weather and traffic
                    #traffic = random.random() # edge traffic adversity level, between 0 (low) and 1 (high)
                    traffic = np.random.random()
                    edgeCost = getDynamicValue(e, weather, traffic) 
                routeCost += edgeCost
            
            if routeCost > routeMaxCost: # violates constraint on max cost

                #penalized = True
                routeReward = 0 # penalty for violating the max time allowed per route
            rewardInSol += routeReward

            #print(f"Run: {i+1} - Route: {route} - Cost: {routeCost} - Penalized: {penalized}")

        accumRewardsInSol += rewardInSol
    sol.reward_sim = accumRewardsInSol / nRuns # reward refers to reward

''' Generates a random cost from a lognormal distribution '''
def getStochasticValue(mean=None, varLevel=None, scale=None, location=None):
    if scale==None and location==None:
         var = varLevel * mean
         mu = math.log(mean**2 / math.sqrt(var + mean**2))
         sigma = math.sqrt(math.log(1 + var / mean**2))
         stochCost = np.random.lognormal(mean=mu, sigma=sigma)
    elif mean==None and varLevel==None:
        stochCost = np.random.lognormal(mean=scale, sigma=location)
    else:
        print("Error using lognormal distribution!!")
    return stochCost

''' Generates a dynamic cost using a machine learning (regression) model '''
def getDynamicValue(edge, weather, traffic):
    # A multiple regression model that returns the standard cost if weather and 
    # traffic adversity levels are 0, while increasing the cost as they approach to 1
    # It is designed so the dynamic cost varies between edge.cost and 1.5 * edge.cost
    b0 = 0 # independent term in a regression model, 0 so that cost in good conditions is the standard one
    b_e = 1 # coefficient for edge standard cost
    b_w = 0.2 * edge.cost * 0.25 # coefficient for weather conditions (less influencial factor)
    b_t = 0.3 * edge.cost * 0.25 # coefficient for traffic conditions (more influencial factor)
    dynamicCost = b0 + b_e*edge.cost + b_w*weather + b_t*traffic
    return dynamicCost



