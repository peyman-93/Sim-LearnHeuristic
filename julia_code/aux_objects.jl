
# Define an abstract type for Route
abstract type AbstractRoute end

# Define an abstract type for Node
abstract type AbstractNode end

# A struct defining Test objects
struct Test
    instanceName::String
    maxTime::Int64
    firstParam::Float64
    secondParam::Float64
    seed::Int64
    shortSim::Int64
    longSim::Int64
    varLevel::Float64
end

# A struct defining Edge objects
@with_kw mutable struct Edge
    origin::AbstractNode
    finish::AbstractNode
    cost::Float64 = 0
    savings::Float64 = 0
    invEdge::Union{Nothing, Edge} = nothing
    efficiency::Float64 = 0
    type::Int64 = 0
end

# A struct defining Node objects
@with_kw mutable struct Node <: AbstractNode
    ID::Int64
    x::Float64
    y::Float64
    reward::Float64
    inRoute::Union{Nothing, AbstractRoute} = nothing
    dnEdge::Union{Nothing, Edge} = nothing
    ndEdge::Union{Nothing, Edge} = nothing
    isLinkedToStart::Bool = false
    isLinkedToFinish::Bool = false
end

# A struct defining Route objects
@with_kw mutable struct Route <: AbstractRoute
    cost::Float64 = 0
    edges::Vector{Edge} = []
    reward::Float64 = 0
end

function reverse(route::Route)
    route.edges = reverse(route.edges)
end

# A struct defining Solution objects
@with_kw mutable struct Solution
    #last_ID::Int64
    ID::Int64 = 0
    routes::Vector{AbstractRoute} = []
    cost::Float64 = 0
    reward::Float64 = 0
    reward_sim::Float64 = 0
    time :: Float64 = 0.0
end
