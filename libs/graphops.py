''' Module for graph theoretic operations '''
import networkx as nx
import geocalc


# Compute the length of a road segment
def compute_way_length(nodes, node_dict):
    length = 0.0
    u = nodes[0]
    for v in nodes[1:]:
        u_cord = node_dict[u]['cord']
        v_cord = node_dict[v]['cord']
        length += geocalc.calculate_distance(u_cord, v_cord)
        u = v

    return length


# Create graph from the node_dict and way_dict and select the
# largest connected component
def create_graph(node_dict, way_dict):
    way_type_dict = {}
    fp = open('libs/types.txt')
    for line in fp:
        comps = line.split()
        way_type_dict[comps[0]] = (int(comps[2]), comps[1])
    fp.close()

    available_types = set([])
    G = nx.Graph()

    for way_id in way_dict:
        u = way_dict[way_id]['nodes'][0]
        v = way_dict[way_id]['nodes'][-1]
        if G.has_edge(u, v):
            continue
        try:
            way_type = way_dict[way_id]['highway']
            if way_type not in way_type_dict:
                continue
        except KeyError:
            continue
        way_len = compute_way_length(way_dict[way_id]['nodes'], node_dict)
        G.add_edge(u, v, e_type=way_type_dict[way_type], e_len=way_len,
                   way_id=way_id)
        available_types.add(way_type_dict[way_type])

    components = list(nx.connected_component_subgraphs(G))
    road_graph = components[0]
    for H in components[1:]:
        if H.number_of_edges() > road_graph.number_of_edges():
            road_graph = H

    return road_graph, available_types
