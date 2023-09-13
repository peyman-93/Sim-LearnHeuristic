
using Random
using LinearAlgebra: norm
using Statistics: mean

include("aux_objects.jl")   
include("simulation.jl")  



# Define the generateEfficiencyList function
function generateEfficiencyList(nodes, alpha)
    start = nodes[1]
    fin = nodes[end]
    efficiencyList = Edge[]

    for i in 2:length(nodes) - 1 # excludes the start and finish depots
        node_i = nodes[i]
        snEdge = Edge(origin = start, finish = node_i) # creates the (start, node_i) edge (arc)
        nfEdge = Edge(origin = node_i, finish = fin) # creates the (node_i, finish) edge (arc)

        # Compute the Euclidean distance as cost
        snEdge.cost = sqrt((node_i.x - start.x)^2 + (node_i.y - start.y)^2)
        nfEdge.cost = sqrt((node_i.x - fin.x)^2 + (node_i.y - fin.y)^2)

        # Save references to the (depot, node_i) edge (arc) in node_i
        node_i.dnEdge = snEdge
        node_i.ndEdge = nfEdge
    end

    for i in 2:length(nodes) - 1 # excludes the start and finish depots
        node_i = nodes[i]
        for j in i+1:length(nodes) - 1
            node_j = nodes[j]
            ijEdge = Edge(origin = node_i, finish = node_j) # creates the (node_i, node_j) edge
            jiEdge = Edge(origin = node_j, finish = node_i) # creates the (node_j, node_i) edge

            # Sets the inverse edge (arc)
            ijEdge.invEdge = jiEdge
            jiEdge.invEdge = ijEdge

            # Compute the Euclidean distance as cost (assume symmetric costs)
            ijEdge.cost = sqrt((node_j.x - node_i.x)^2 + (node_j.y - node_i.y)^2)
            jiEdge.cost = ijEdge.cost

            # Compute efficiency as proposed by Panadero et al. (2020)
            ijSavings = node_i.ndEdge.cost + node_j.dnEdge.cost - ijEdge.cost
            edgeReward = node_i.reward + node_j.reward

            ijEdge.savings = ijSavings
            ijEdge.efficiency = alpha * ijSavings + (1 - alpha) * edgeReward

            jiSavings = node_j.ndEdge.cost + node_i.dnEdge.cost - jiEdge.cost
            jiEdge.savings = jiSavings
            jiEdge.efficiency = alpha * jiSavings + (1 - alpha) * edgeReward

            # Save both edges in the efficiency list
            push!(efficiencyList, ijEdge)
            push!(efficiencyList, jiEdge)
        end
    end

    # Sort the list of edges from higher to lower efficiency
    sort!(efficiencyList, by = x -> x.efficiency, rev = true)
    return efficiencyList
end


# Define the getRandomPosition function
function getRandomPosition(beta1, beta2, size, rng)
    # Randomly select a beta value between beta1 and beta2
    beta = beta1 + rand(rng) * (beta2 - beta1)
    index = trunc(Int64, (log(rand(rng)) / log(1 - beta)))
    index = mod(index, size)
    return index + 1
end

# Define the checkMergingConditions function
function checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge, routeMaxCost)
    # Condition 1: iRoute and jRoute are not the same route object
    if iRoute === jRoute
        return false
    end
    
    # Condition 2: jNode has to be linked to start, and iNode to finish
    if !iNode.isLinkedToFinish || !jNode.isLinkedToStart
        return false
    end
    
    # Condition 3: Cost after merging does not exceed routeMaxCost
    if iRoute.cost + jRoute.cost - ijEdge.savings > routeMaxCost
        return false
    end
    
    # Merging is feasible
    return true
end


function merging(useBR, test, fleetSize, routeMaxCost, nodes, eff_list, rng)
    sol = dummySolution(routeMaxCost, nodes)
    effList = copy(eff_list)

    while !isempty(effList)
        position = 1
        if useBR
            position = getRandomPosition(test.firstParam, test.secondParam, length(effList), rng)
   
        end

        ijEdge = popat!(effList, position)
        iNode = ijEdge.origin
        jNode = ijEdge.finish
        iRoute = iNode.inRoute
        jRoute = jNode.inRoute
        isMergeFeasible = checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge, routeMaxCost)

        if isMergeFeasible
            jiEdge = ijEdge.invEdge
            if jiEdge in effList
                splice!(effList, findall(x -> x === jiEdge, effList))
            end

            iEdge = iRoute.edges[end]
            deleteat!(iRoute.edges, length(iRoute.edges))
            iRoute.cost -= iEdge.cost
            iNode.isLinkedToFinish = false

            jEdge = jRoute.edges[1]
            deleteat!(jRoute.edges, 1)
            jRoute.cost -= jEdge.cost
            jNode.isLinkedToStart = false

            push!(iRoute.edges, ijEdge)
            iRoute.cost += ijEdge.cost
            iRoute.reward += jNode.reward
            jNode.inRoute = iRoute

            for edge in jRoute.edges
                push!(iRoute.edges, edge)
                iRoute.cost += edge.cost
                iRoute.reward += edge.finish.reward
                edge.finish.inRoute = iRoute
            end

            sol.cost -= ijEdge.savings
            deleteat!(sol.routes, findall(x -> x === jRoute, sol.routes))
        end
    end

    sort!(sol.routes, by = x -> x.reward, rev = true)

    if length(sol.routes) > fleetSize
        for route in sol.routes[fleetSize+1:end]
            sol.reward -= route.reward
            sol.cost -= route.cost
            deleteat!(sol.routes, findall(x -> x === route, sol.routes))
        end
    end

    return sol
end


# Define the genInitSol function
function genInitSol(test, fleetSize, routeMaxCost, nodes, rng)
    best_reward = 0
    eff_list = []
    init_sol = Solution()
    
    for new_alpha in range(0, stop=1, length=11)
        new_effList = generateEfficiencyList(nodes, new_alpha)
        sol = merging(false, test, fleetSize, routeMaxCost, nodes, new_effList, rng)
        
        if sol.reward > best_reward
            best_reward = sol.reward
            eff_list = new_effList
            init_sol = sol
        end
    end

    return init_sol, eff_list
end

# Define the dummySolution function
function dummySolution(routeMaxCost, nodes)
    sol = Solution()
    for node in nodes[2:end-1]  # Excludes the start and finish depots
        snEdge = node.dnEdge
        nfEdge = node.ndEdge
        snfRoute = Route()
        push!(snfRoute.edges, snEdge)
        snfRoute.reward += node.reward
        snfRoute.cost += snEdge.cost
        push!(snfRoute.edges, nfEdge)
        snfRoute.cost += nfEdge.cost
        node.inRoute = snfRoute
        node.isLinkedToStart = true
        node.isLinkedToFinish = true
        if snfRoute.cost <= routeMaxCost
            push!(sol.routes, snfRoute)
            sol.cost += snfRoute.cost
            sol.reward += snfRoute.reward
        end
    end
    return sol
end



# Define the algorithm function
function algorithm(test, fleetSize, routeMaxCost, nodes, rng)
    # Select the best alpha value and efficiency list for computing enhanced savings
    # and generate an initial solution using the selected alpha value and efficiency list
    init_sol, eff_list = genInitSol(test, fleetSize, routeMaxCost, nodes, rng)
    
    # Set initial solution as the Our Best Det sol in a Det environment
    OBD = init_sol
    simulation(OBD, test.shortSim, routeMaxCost, test.varLevel)
    list_OBS = []  # Initialize a list to store solutions
    push!(list_OBS, OBD)
    
    # Stage 1: Start the main loop searching for better det and stoch sols
    elapsed = 0
    start_time = time()
    while elapsed < test.maxTime
        # Use the merging process of the PJs heuristic to generate a new det sol
        new_detSol = merging(true, test, fleetSize, routeMaxCost, nodes, eff_list, rng)
        
        # If new_detSol is promising, update best det and stoch sols if appropriate
        epsilon = 0  # Epsilon can be modified to select a higher/lower number of promising solutions
        if new_detSol.reward >= OBD.reward + epsilon
            OBD = new_detSol

            #define computational time for OBD
            OBD.time = time() - start_time

            simulation(OBD, test.shortSim, routeMaxCost, test.varLevel)
            push!(list_OBS, OBD)
        end
        
        elapsed = time() - start_time
    end
    
    # Stage 2: Refinement of the best k stoch sols
    sort!(list_OBS, rev=true, by=sol -> sol.reward_sim)
    OBS = list_OBS[1]
    simulation(OBD, test.longSim, routeMaxCost, test.varLevel)  # Guarantee that the OBD keeps an accurate estimate
    simulation(OBS, test.longSim, routeMaxCost, test.varLevel)  # Guarantee that the OBS keeps an accurate estimate
    
    max_elite = 10  # Max number of elite sols to consider
    k = min(max_elite, length(list_OBS))  # Number of elite stochastic solutions to consider
    for i in 1:k
        new_OBS = list_OBS[i]
        simulation(new_OBS, test.longSim, routeMaxCost, test.varLevel)
        if new_OBS.reward_sim > OBS.reward_sim
            OBS = new_OBS
        end
    end
    
    return OBD, OBS
end
