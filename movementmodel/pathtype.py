''' Path type based movment '''
import random

import simplerandom as sr

## Class for Path-type based movement. It inherit the basic movement
## from SimpleRandomMovement except the initial and next_node computations.
class PathTypeMovement(sr.SimpleRandomMovement):
    ''' Path-type based movement model'''

    def __init__(self, obj_label, group_id, group_params, global_params):
        sr.SimpleRandomMovement.__init__(self, obj_label, group_id, \
                                         group_params, global_params)

    ## Re-definition of initial node computation
    def compute_initial_node(self, global_params):
	#return 103214114	# Manhattan
	#return 103174015 # Newyork
	#return 1365948969 #Dharavi

        # Read possible paths for the object given in the 'settings.dtn' file
        possible_paths = global_params.envt_params.groups[self.group_id]\
          ['Paths']

        # Nodes (junctions) of the road network
        nodes = global_params.road_graph.nodes()

        # Choose a node (junction) at random which is connected to
        # at least one path which has the type in which the object can move
        type_flag = True
        while type_flag:
            initial_node = random.choice(nodes) # Selecting a node at random

            # Collecting its neighbors
            neighbors = global_params.road_graph.neighbors(initial_node)

            # Among neighbors, check for at least one path with required type
            for node in neighbors:
                way_type = global_params.road_graph[initial_node][node]\
                  ['e_type']
                try:
                    way_type_id = global_params.envt_params.envt\
                      ['Path_Types'][way_type]
                    if way_type_id in possible_paths:
                        type_flag = False
                        break
                except KeyError:
                    pass

        return initial_node

    ## Redefinition of compute_next_node from SimpleRandomMovement
    def compute_next_node(self, global_params):
        road_graph = global_params.road_graph

        # Collect neighbors of current node
        neighbor_nodes = road_graph.neighbors(self.next_node)
        possible_nodes = []

        # Collect the possbile path types the object can move
        possible_types = global_params.envt_params.groups[self.group_id]['Paths']

        # Select all the neighbor nodes which have a way with specified type
        for node in neighbor_nodes:
            way_type = road_graph[self.next_node][node]['e_type']
            try:
                way_type_id = global_params.envt_params.envt['Path_Types'][way_type]
                if way_type_id in possible_types:
                    possible_nodes.append(node)
            except KeyError:
                pass

        try:
            # Removing the previous node from which the movement object came
            possible_nodes.remove(self.prev_node)
        except:
            pass # Happens only at start where prev_node = next_node

        if possible_nodes:
            # If at least one neighbor is available, choose one at random
            next_node = random.choice(possible_nodes)
        else:
            # If no possible neighbor nodes, return to prev_node
            next_node = self.prev_node

        return next_node
    
