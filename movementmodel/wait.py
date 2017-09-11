''' Path type based movment '''
import random

import pathtype as pt

## Class for Path-type based movement. It inherit the basic movement
## from SimpleRandomMovement except the initial and next_node computations.
class WaitMovement(pt.PathTypeMovement):
    ''' Path-type based movement model'''

    def __init__(self, obj_label, group_id, group_params, global_params):
        pt.PathTypeMovement.__init__(self, obj_label, group_id, \
                                         group_params, global_params)
	self.wait_flag = False
	self.wait_start = None


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

	# Addition of Waiting Process Code
	av_nodes = []
	if self.buffer:
		#possible_nodes.append(self.prev_node)		
		for node in possible_nodes:
			e_type = road_graph[self.next_node][node]['e_type']
			if e_type == 'highway':
				av_nodes.append(node)
	if av_nodes:
		# print '%s in Highway Mode' % (self.obj_id)
		if not self.wait_flag:
			self.wait_start = global_params.sim_time
			self.wait_flag = True
		return self.next_node
	# End of Waiting Process Code

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
    
