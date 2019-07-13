''' Module for a stationary object '''
from __future__ import division
import random

import report


class Stationary:
    ''' Stationary object '''

    def __init__(self, obj_label, group_id, group_params, global_params):

        self.obj_id = obj_label  # Unique label for the movement object

        self.group_id = group_id  # Group ID given in the 'sim.config' file

        # Current node id of the object
        self.curr_node = self.compute_initial_node(global_params)

        # The current geographical position in (lat, lon) and pixel
        # position in (y, x)
        self.curr_geo_pos = global_params.node_dict[self.curr_node]['cord']
        self.curr_pix_pos = global_params.node_dict[self.curr_node]['pixcord']

        # Buffer for storing data
        self.buffer = []

        # Object to log the information regarding simulation
        self.report_obj = report.MovementReport(self, global_params)

        # Objects for handoff protocol
        self.protocol_obj = None

        # Events configuration
        self.event_times = []  # Event generation timestamps
        self.events = []  # Event list

    # Function to compute initial node for the simulation
    def compute_initial_node(self, global_params):
        nodes = list(global_params.road_graph.nodes())

        # Choose a random node from the graph
        initial_node = random.choice(nodes)

        return initial_node
