''' Module for graph theoretic operations '''
import networkx as nx

## Function to create the graph, with vertices and edges, from
## the given road network. End point of each way will be taken
## as vertices and road will be represented as an edge between
## them
def create_minimal_graph(way_dict):
    # Create a Graph object
    road_graph = nx.Graph()

    # Add vertices and edges
    for way in way_dict:
        v1 = way_dict[way][0][0]
        v2 = way_dict[way][0][-1]
        weight = way_dict[way][2] # Distance
        edge_type = way_dict[way][1] # Road type

        road_graph.add_edge(v1, v2, weight=weight, e_type=edge_type, \
                            way_id=way)

    return road_graph
