
using Random
using Distributions

# Define a function to set the type of each edge in a given solution
# where: 0 = deterministic (default), 1 = stochastic, and 2 = dynamic
function setEdgesType1(sol)
    for route in sol.routes
        for e in route.edges
            if e.finish.ID % 2 == 0  # if ID of the end node is even
                e.type = 1  # stochastic
            elseif e.finish.ID % 3 == 0  # if ID of the end node is divisible by 3
                e.type = 2  # dynamic
            else
                e.type = 0  # default
            end
        end
    end
end

#This function use for generating Stochastic scenario and Dynamic scenario seperatly
function setEdgesType(sol)
    for route in sol.routes
        for e in route.edges
            if e.finish.ID % 2 == 0  # If ID of the end node is even
                e.type = 1  # Stochastic = 1, Dynamic = 2
            else
                e.type = 0  # Deterministic
            end
        end
    end
end

# Define a function to simulate stochastic/dynamic values in a solution using Monte Carlo
function simulation(sol, nRuns, routeMaxCost, varLevel)
    setEdgesType(sol)  # Set the type of each edge (det/stoch/dyn) for experiments
    accumRewardsInSol = 0.0  # Accumulated solution rewards after multiple runs

    for i in 1:nRuns
        weather = rand()  # Daily weather adversity level, a random value between 0 (low) and 1 (high)
        rewardInSol = 0.0  # Solution reward in this run

        for route in sol.routes
            routeReward = 0.0  # Route reward in this run
            routeCost = 0.0  # Time- or distance-based cost

            for e in route.edges
                node = e.finish  # End node of the edge
                routeReward += node.reward

                if e.type == 0
                    edgeCost = e.cost
                elseif e.type == 1  # Edge e has a stochastic travel time
                    edgeCost = getStochasticValue(e.cost, varLevel)
                elseif e.type == 2  # Edge e has a dynamic travel time depending on weather and traffic
                    traffic = rand()  # Edge traffic adversity level, between 0 (low) and 1 (high)
                    edgeCost = getDynamicValue(e, weather, traffic)
                end

                routeCost += edgeCost
            end

            if routeCost > routeMaxCost  # Violates constraint on max cost
                routeReward = 0.0  # Penalty for violating the max time allowed per route
            end

            rewardInSol += routeReward
        end

        accumRewardsInSol += rewardInSol
    end

    sol.reward_sim = accumRewardsInSol / nRuns  # Average reward over multiple runs
end

# Define a function to generate a random cost from a lognormal distribution

function getStochasticValue(mean, varLevel)
    var = varLevel * mean
    mu = log(mean^2 / sqrt(var + mean^2))
    sigma = sqrt(log(1 + var / mean^2))
    stochCost = rand(LogNormal(mu, sigma))
    return stochCost
end

function getDynamicValue(edge, weather, traffic)
    # A multiple regression model that returns the standard cost if weather and traffic adversity levels are 0,
    # while increasing the cost as they approach 1. It is designed so the dynamic cost varies between edge.cost
    # and 1.5 * edge.cost.

    b0 = 0.0  # Independent term in a regression model, 0 so that cost in good conditions is the standard one
    b_e = 1.0  # Coefficient for edge standard cost
    b_w = 0.2 * edge.cost * 0.25  # Coefficient for weather conditions (less influential factor)
    b_t = 0.3 * edge.cost * 0.25  # Coefficient for traffic conditions (more influential factor)

    dynamicCost = b0 + b_e * edge.cost + b_w * weather + b_t * traffic

    return dynamicCost
end
