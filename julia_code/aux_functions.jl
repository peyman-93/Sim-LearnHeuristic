include("aux_objects.jl")  

# Define a function to read tests from a file
function readTests(fileName :: String)
	tests = Vector{Test}()
	open(fileName, "r") do f
		_ = readline(f)
		for line in readlines(f)
			tokens = split(line, "\t")
			if !occursin("#", tokens[1])
				# Parse test line tokens
				instanceName = tokens[1]
				maxTime = parse(Int64, tokens[2])
                firstParam = parse(Float64, tokens[3])
                secondParam = parse(Float64, tokens[4])
				seed = parse(Int64, tokens[5])
				shortSim = parse(Int64, tokens[6])
				longSim = parse(Int64, tokens[7])
				variance = parse(Float64, tokens[8])
				# Add constructed test case to tests list
				test = Test(instanceName,  maxTime, firstParam, secondParam, seed, shortSim, longSim, variance)
				push!(tests, test)
			end
		end
	end
	return tests
end



# Define a function to read instance data from a file
function read_instance(file_name::String)
    fleetSize, routeMaxCost, nodes = 0, 0.0, []
    i = -3  # Start at -3 so that the first node is node 0
    open(file_name, "r") do instance
        for line in eachline(instance)
            if i == -3
                # Line 0 contains the number of nodes, not needed
            elseif i == -2
                fleetSize = parse(Int64, split(line, ';')[2])
            elseif i == -1
                routeMaxCost = parse(Float64, split(line, ';')[2])
            else
                # Array data with node data: x, y, reward
                data = parse.(Float64, split(line, ';'))
                # Create instance nodes
                aNode = Node(i, data[1], data[2], data[3], nothing, nothing, nothing, false, false)
                push!(nodes, aNode)
            end
            i += 1
        end
    end
    return fleetSize, routeMaxCost, nodes
end

# Define a function to print routes in a solution
function printRoutes(sol)
    for route in sol.routes
        print("0")
        for e in route.edges
            print("->", e.finish.ID)
        end
        println("\nRoute det reward:", route.reward, "; det cost:", route.cost)
    end
    println("Time: ", sol.time)
end
