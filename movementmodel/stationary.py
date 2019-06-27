''' Module for a stationary object '''
from __future__ import division
import random

import geocalc
import report

class Stationary:
    ''' Stationary object '''

    def __init__(self, obj_label, group_id, group_params, global_params):

        self.obj_id = obj_label # Unique label for the movement object
        
        self.group_id = group_id # Group ID given in the 'settings.dtn' file

        # If a node moves from node A to node B, then A will be the
        # prev_node and B will be the next_node
        self.prev_node = self.compute_initial_node(global_params)
        #print '%s: %d' % (self.obj_id, self.prev_node)
        self.next_node = self.prev_node

        # The current geographical position in (lat, lon) and pixel
        # position in (y, x)
        self.curr_geo_pos = global_params.node_dict[self.prev_node][0]
        self.curr_pix_pos = global_params.node_dict[self.prev_node][1]

        # Buffer for storing data
        self.buffer = []

        # Object to log the information regarding simulation
        self.report_obj = report.MovementReport(self, global_params)

        # Objects for handoff protocol
        self.protocol_obj = None

	# Addition
	self.finalized_msgs = set([])
	self.init_node = self.prev_node # This will be the depot id
	self.depot_ob = None
	self.wait_times = []
	self.wait_start = None	


    ## Function to compute initial node for the simulation
    def compute_initial_node(self, global_params):
        nodes = list(global_params.road_graph.nodes())

        # Choose a random node from the graph
        initial_node = random.choice(nodes)

        return initial_node
