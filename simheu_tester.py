''' Reviewed by Angel A. Juan 2023.06 for the TOP with stochastic / dynamic travel times '''
import csv
import os
import random
import numpy as np
import matplotlib.pyplot as plt

from aux_functions import read_tests, read_instance, printRoutes
from simheu import detExcecution, simExcecution, getRand

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

    # Use the getRand function to obtain a random number at the current index
    #test.random_value, test.index1 = getRand(index1, random_file)
    # Define the path to the random data file
    random_file = "random_numbers.txt"

    # Initialize the index to 0
    test.index1 = 0

    # open and read the random numers from the text file:
    with open("random_numbers.txt", "r") as random_file:
        random_numbers = [float(line.strip()) for line in random_file]

    # set the seed in the RNG for reproducibility purposes
    #random.seed(test.seed) # Python default RNG, used during BR
    #np.random.seed(test.seed) # Numpy RNG, used during simulation
    # print basic instance info
    print('\nInstance: ', test.instanceName)
    print('Var level (k in Var = k*mean):', test.varLevel)
    # read input data from instance file
    file_name = "data" + os.sep + test.instanceName + ".txt"
    fleetSize, routeMaxCost, nodes = read_instance(file_name)
    # execute the algorithm and obtain the different Our Best solutions, where
    # OBD = Our Best Deterministic sol
    # OBS = Our Best Stochastic sol

    OBD = detExcecution(test, fleetSize, routeMaxCost, nodes, random_numbers)
    OBS = simExcecution(test, fleetSize, routeMaxCost, nodes, random_numbers)


    # Append the results to the list
    results.append({
        'Instance': test.instanceName,
        "Seed": test.seed,
        'OBD': OBD.reward,
        'OBD-S': OBD.reward_sim,
        'OBS': OBS.reward_sim,
        "OBD_T": OBD.time,
        "OBS_T": OBS.time
    })

    # Print summary results
    print('Reward for OBD sol in a Det. env. =', OBD.reward)
    print('Reward for OBD sol in a Stoch. env. =', OBD.reward_sim)
    print('Reward for OBS sol in a Stoch. env. =', OBS.reward_sim)
    print('Routes for OBD sol')
    printRoutes(OBD)
    print('Routes for OBS sol')
    printRoutes(OBS)

# Define the output CSV file path
output_file = 'results_Rand_PY.csv'

# Write the results to the CSV file
fieldnames = ['Instance', "Seed", 'OBD', 'OBD-S', 'OBS', "OBD_T", "OBS_T"]

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("Results saved to", output_file)



