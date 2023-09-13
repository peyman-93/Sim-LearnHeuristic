
using CSV
using Random
using Printf
using Plots
using Parameters

include("aux_functions.jl")  
include("simheu.jl")  

# Read the tests2run.txt file and build the list of instances (tests) to run
file_name = "tests/tests2run.txt"
tests = readTests(file_name)

# Create a list to store the results
results = []

# For each instance (test), read inputs, create nodes, and execute it
for test in tests
    # Set the seed in the RNG for reproducibility purposes
    rng = Xoshiro(test.seed)
    Random.seed!(test.seed)  # used during simulation

    # Print basic instance info
    println("\nInstance: ", test.instanceName)
    println("Var level (k in Var = k*mean):", test.varLevel)

    # Read input data from instance file
    file_name = "data/$(test.instanceName).txt"
    fleetSize, routeMaxCost, nodes = read_instance(file_name)
    
    # Execute the algorithm and obtain the different Our Best solutions, where
    # OBD = Our Best Deterministic sol
    # OBS = Our Best Stochastic sol

    OBD, OBS = algorithm(test, fleetSize, routeMaxCost, nodes, rng)

    # Append the results to the list
    push!(results, Dict(
        "Instance" => test.instanceName,
        "Seed" => test.seed,
        "OBD" => OBD.reward,
        "OBD-S" => OBD.reward_sim,
        "OBS" => OBS.reward_sim,
        "OBD_T" => OBD.time,
        "OBS_T" => OBS.time
    ))

    # Print summary results
    println("Reward for OBD sol in a Det. env. =", OBD.reward)
    println("Reward for OBD sol in a Stoch. env. =", OBD.reward_sim)
    println("Reward for OBS sol in a Stoch. env. =", OBS.reward_sim)
    println("Routes for OBD sol")
    printRoutes(OBD)
    println("Routes for OBS sol")
    printRoutes(OBS)
end

# Define the output CSV file path
output_file = "results.csv"

# Write the results to the CSV file
CSV.write(output_file, results)

println("Results saved to", output_file)

