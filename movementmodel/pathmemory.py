''' Path type based movment '''
import random

import pathtype as pt


# Class for Path-type based movement. It inherit the basic movement
# from SimpleRandomMovement except the initial and next_node computations.
class PathMemoryMovement(pt.PathTypeMovement):
    ''' Path-type based movement model'''

    def __init__(self, obj_label, group_id, group_params, global_params):
        pt.PathTypeMovement.__init__(self, obj_label, group_id,
                                     group_params, global_params)

    # Redefinition of compute_next_node from SimpleRandomMovement
    def compute_next_node(self, global_params):
        G = global_params.road_graph
        possible_nodes = self.find_possible_nodes(self.next_node,
                                                  global_params)
        try:
            possible_nodes.remove(self.curr_node)
        except ValueError:
            pass

        # Removing already traversed ways
        temp = possible_nodes[:]
        for v in possible_nodes:
            if G[self.next_node][v]['way_id'] in self.ways_visited:
                temp.remove(v)

        if temp:
            next_node = random.choice(temp)
        elif possible_nodes:
            next_node = random.choice(possible_nodes)
        else:
            next_node = self.curr_node  # Return to previous node

        return next_node
