''' Path type based movment '''
import random

import simplerandom as sr


# Class for Path-type based movement. It inherit the basic movement
# from SimpleRandomMovement except the initial and next_node computations.
class PathTypeMovement(sr.SimpleRandomMovement):
    ''' Path-type based movement model'''

    def __init__(self, obj_label, group_id, group_params, global_params):
        sr.SimpleRandomMovement.__init__(self, obj_label, group_id,
                                         group_params, global_params)

    # Re-definition of initial node computation
    def compute_initial_node(self, global_params):
        # Read possible paths for the object given in the 'settings.dtn' file
        G = global_params.road_graph
        possible_nodes = []
        for u in G.nodes():
            if self.find_possible_nodes(u, global_params):
                possible_nodes.append(u)

        initial_node = random.choice(possible_nodes)

        return initial_node

    # Redefinition of compute_next_node from SimpleRandomMovement
    def compute_next_node(self, global_params):
        possible_nodes = self.find_possible_nodes(self.next_node,
                                                  global_params)
        try:
            possible_nodes.remove(self.curr_node)
        except ValueError:
            pass
        if possible_nodes:
            return random.choice(possible_nodes)
        else:
            return self.curr_node  # Return to previous node

    # Function to find possible neighbors with permitted types
    def find_possible_nodes(self, u, global_params):
        G = global_params.road_graph
        possible_types = [int(x) for x in global_params.envt_params.groups[self.group_id]['Paths']]
        possible_nodes = []
        for v in G.neighbors(u):
            if G[u][v]['e_type'][0] in possible_types:
                possible_nodes.append(v)

        return possible_nodes
