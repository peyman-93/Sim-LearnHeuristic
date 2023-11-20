''' Reviewed by Angel A. Juan 2023.06 for the TOP with stochastic / dynamic travel times '''
import csv
import os
import random
import numpy as np
import matplotlib.pyplot as plt

from aux_functions import read_tests, read_instance, printRoutes
from simheu1 import detExcecution, simExcecution

# Read the tests2run.txt file and build the list of instances (tests) to run
file_name = "tests" + os.sep + "tests2run.txt"
tests = read_tests(file_name)

# Create a list to store the results
results = []

# Initialize an index to keep track of the current random number
#random_index = 0
#maxIterations = 100.000
# For each instance (test), read inputs, create nodes, and execute it
for test in tests:

    # set the seed in the RNG for reproducibility purposes
    random.seed(test.seed) # Python default RNG, used during BR
    np.random.seed(test.seed) # Numpy RNG, used during simulation
    # print basic instance info
    print('\nInstance: ', test.instanceName)
    print('Var level (k in Var = k*mean):', test.varLevel)
    # read input data from instance file
    file_name = "data" + os.sep + test.instanceName + ".txt"
    fleetSize, routeMaxCost, nodes = read_instance(file_name)
    # execute the algorithm and obtain the different Our Best solutions, where
    # OBD = Our Best Deterministic sol
    # OBS = Our Best Stochastic sol

    OBD = detExcecution(test, fleetSize, routeMaxCost, nodes)
    # OBS = simExcecution(test, fleetSize, routeMaxCost, nodes)


    # Append the results to the list
    results.append({
        'Instance': test.instanceName,
        "Seed": test.seed,
        'OBD': OBD.reward,
        #'OBD-S': OBD.reward_sim,
        #'OBS': OBS.reward_sim,
        "OBD_T": OBD.time,
        #"OBS_T": OBS.time
    })

    # Print summary results
    print('Reward for OBD sol in a Det. env. =', OBD.reward)
    #print('Reward for OBD sol in a Stoch. env. =', OBD.reward_sim)
    #print('Reward for OBS sol in a Stoch. env. =', OBS.reward_sim)
    print('Routes for OBD sol')
    printRoutes(OBD)
    #print('Routes for OBS sol')
    #printRoutes(OBS)

# Define the output CSV file path
output_file = 'results_Python_TimeHeu.csv'

# Write the results to the CSV file
fieldnames = ['Instance', "Seed", 'OBD', "OBD_T"]

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("Results saved to", output_file)



