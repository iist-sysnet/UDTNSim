""" Module for Map related functions """
import math


def calculate_distance(coord1, coord2):
    """ Return the distance between two geographical points. """

    deg2rad = math.pi / 180
    phi1 = (90.0 - coord1[0]) * deg2rad
    phi2 = (90.0 - coord2[0]) * deg2rad

    th1 = coord1[1] * deg2rad
    th2 = coord2[1] * deg2rad

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(th1 - th2) + \
           math.cos(phi1) * math.cos(phi2))
    # cos = (math.sin(phi1) * math.sin(phi2) + math.cos(th1 - th2) * \
    #        math.cos(phi1) * math.cos(phi2))

    if cos > 1:
       cos = 1

    distance = math.acos(cos) * 6373

    return distance    

''' Function which convert map to graph. It returns
    a list of all edges with weights.
'''
def map_to_graph(node_dict, way_dict):
    edge_dict = {}
    for way in way_dict:
        way_nodes = way_dict[way][0]
        way_distance = 0.0
        for i in range(1, len(way_nodes)):
            way_distance += calculate_distance(node_dict[way_nodes[i-1]][1], \
                                               node_dict[way_nodes[i]][1])

        edge_dict[(way_nodes[0], way_nodes[i])] = (way_distance, way_dict[way][1])

    return edge_dict
            

''' Function to reduce complexity of graph by giving small values for
    way IDs and node IDs. Also the function will split the ways, 
    which has an intersection with another way, into two or more paths 
    so that the movemets can be make simple.
'''
def normalize_map(node_dict, way_dict):
    """ Reduce the map by splitting ways which form juctions with other
        ways at the middle of the road. Fuction also appends the length of
        each ways to the way_dict. """
    
    dup_way_dict = {}    
    i = 0
    for way in way_dict:
        way_type = way_dict[way][1]
        way_nodes = way_dict[way][0]
        if not way_nodes:
            continue
        temp = [way_nodes[0]]
        way_distance = 0.0
        for j in xrange(1, len(way_nodes)):
            way_distance += calculate_distance(node_dict[way_nodes[j - 1]][0], \
                                                   node_dict[way_nodes[j]][0])
            if len(node_dict[way_nodes[j]][2]) > 1 or j == len(way_nodes) - 1:
                temp.append(way_nodes[j])
                dup_way_dict[i] = [temp, way_type, way_distance]
                i += 1
                temp = [way_nodes[j]]
                way_distance = 0.0
            else:
                temp.append(way_nodes[j])
   
    dup_node_dict = {}
    for item in node_dict:
        dup_node_dict[item] = [node_dict[item][0], node_dict[item][1], []]

    for way in dup_way_dict:
        for item in dup_way_dict[way][0]:
            dup_node_dict[item][2].append(way)
    
    return dup_node_dict, dup_way_dict



def normalize_map2(node_dict, way_dict):
    for way in way_dict:
        way_nodes = way_dict[way][0]
        way_dist = 0.0
        
        v1 = way_nodes[0]
        for v2 in way_nodes[1:]:
            v1_pt = node_dict[v1][0]
            v2_pt = node_dict[v2][0]
            
            dist = calculate_distance(v1_pt, v2_pt)
            way_dist += dist
            
            v1 = v2
        way_dict[way].append(way_dist)

    return node_dict, way_dict
    
        
