''' Path type based movment '''
import random
import networkx as nx

import pathtype as pt

## Class for Path-type based movement. It inherit the basic movement
## from SimpleRandomMovement except the initial and next_node computations.
class HighwayMovement(pt.PathTypeMovement):
    ''' Path-type based movement model'''

    def __init__(self, obj_label, group_id, group_params, global_params):
        pt.PathTypeMovement.__init__(self, obj_label, group_id, \
                                         group_params, global_params)

	self.mygraph = nx.Graph()
	self.path = []
	self.path_index = None

	self.node_seq_list = [self.init_node]


	self.return_to_depot_flag = False
	self.finalized_flag = False
	self.init_flag = True
	self.wait_flag = False
    	

    ## Redefinition of compute_next_node from SimpleRandomMovement
    def compute_next_node(self, global_params):
	# In case the journey is finalized
	if self.finalized_flag:
		self.path_index += 1
		if self.path_index == len(self.path):
			self.path_index = 1
		next_node = self.path[self.path_index]

		return next_node
	
	# If node reached depot after one journey
	if not self.init_flag and self.next_node == self.init_node:
		self.path = self.node_seq_list[:]
		self.path_index = 1
		self.finalized_flag = True
		# print '%s journey finalized :D' % (self.obj_id)

		next_node = self.path[self.path_index]

		return next_node


	# First journey
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
                if way_type_id in possible_types and not self.mygraph.has_edge(self.next_node, node):
                    possible_nodes.append(node)
            except KeyError:
                pass

        try:
            # Removing the previous node from which the movement object came
            possible_nodes.remove(self.prev_node)
        except:
            pass # Happens only at start where prev_node = next_node

        if possible_nodes: # and self.next_node != self.init_node) or self.init_flag:
            # If at least one neighbor is available, choose one at random
            next_node = random.choice(possible_nodes)
	    if self.return_to_depot_flag:
		    self.return_to_depot_flag = False
		    self.path = []
		    self.path_index = 0
		    #print '%s find unexplored path :)' % (self.obj_id)
			
        else:
	    if self.return_to_depot_flag:
		self.path_index += 1	
	    else:
            	# If no possible neighbor nodes, return to Depot
    		#print '%s returning to depot :(' % (self.obj_id)
	    	self.path = nx.shortest_path(self.mygraph, self.next_node, self.init_node, weight='weight')
	    	self.path_index = 1

	    	self.return_to_depot_flag = True
	
            next_node = self.path[self.path_index]
	   
	if self.init_flag:
		next_node = self.depot_ob.get_a_node()	

	wt = road_graph[self.next_node][next_node]['weight']
	
	self.mygraph.add_edge(self.next_node, next_node, weight=wt)

	self.node_seq_list.append(next_node)

	self.init_flag = False

        return next_node
    
