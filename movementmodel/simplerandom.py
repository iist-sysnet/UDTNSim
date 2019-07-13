''' Module for simple random movement '''
from __future__ import division
import random
import numpy

import stationary
import geocalc


class SimpleRandomMovement(stationary.Stationary):
    """ Simple Random Movement Model """

    def __init__(self, obj_label, group_id, group_params, global_params):
        stationary.Stationary.__init__(self, obj_label, group_id,
                                       group_params, global_params)

        # next_node represents the next junction toward the object is moving
        self.next_node = self.curr_node

        self.curr_way = None  # The way ID in which the node is moving.

        # Speed of the object given in the 'som.config' file
        self.speed = group_params['Speed']

        self.ways_visited = []  # List to keep the ways traversed

        self.time_traveled = 0.0  # Time of movement (does not include delays)

        # List to create the movement points between two nodes. i.e.,
        # when a movement object chooses a path, say A->B, all the
        # points between A and B will be generated in 'mvmt_points' list
        self.mvmt_points = []

        # To keep track of the instantaneous point of movement
        self.mvmt_pt_index = 0

    # Function to select next node when the movement object
    # reaches a junction or the end of a road
    def compute_next_node(self, global_params):
        road_graph = global_params.road_graph

        # Collect all possible nodes available from the junction
        possible_nodes = list(road_graph.neighbors(self.next_node))
        try:
            # Remove the junction from which the object came
            possible_nodes.remove(self.curr_node)
        except ValueError:
            pass  # Happens only at start where curr_node = next_node

        if possible_nodes:
            # Select a random node from the possible nodes
            next_node = random.choice(possible_nodes)
        else:
            # Situation of end of road. So object has only one option
            # to return to the previous node
            next_node = self.curr_node

        return next_node

    # Function to generate all the movement points between a way
    def populate_way_points(self, global_params):
        way_dict = global_params.way_dict
        node_dict = global_params.node_dict

        way_id = global_params.road_graph[self.curr_node][self.next_node]['way_id']

        # Available node points between curr_node and next_node
        way_nodes = way_dict[way_id]['nodes']
        if self.curr_node != way_nodes[0]:
            way_nodes.reverse()

        self.mvmt_points = []

        # Parse through each node points and generate required number
        # of points between each nodes
        i_node = way_nodes[0]
        for j_node in way_nodes[1:]:
            # Pixel points of end vertices
            i_pix_pt = node_dict[i_node]['pixcord']
            j_pix_pt = node_dict[j_node]['pixcord']

            # Geographical points of end vertices
            i_geo_pt = node_dict[i_node]['cord']
            j_geo_pt = node_dict[j_node]['cord']

            # Calculating the geographical distance between two points
            i_j_distance = geocalc.calculate_distance(i_geo_pt, j_geo_pt)

            # Calculating the number of intermediate points required. It
            # depends on the distance corresponding to one pixel and speed
            # of the movement object.
            no_of_points = int(round(i_j_distance / global_params.gui_params['pix_unit']) *
                               global_params.gui_params['pix_multiplier'][self.group_id])

            # Generating the required pixel points and geographical points
            # using linear interpolation
            pix_xs = numpy.linspace(i_pix_pt[0], j_pix_pt[0], no_of_points)
            pix_ys = numpy.linspace(i_pix_pt[1], j_pix_pt[1], no_of_points)

            lons = numpy.linspace(i_geo_pt[0], j_geo_pt[0], no_of_points)
            lats = numpy.linspace(i_geo_pt[1], j_geo_pt[1], no_of_points)

            # Appending the generated points to 'mvmt_points' list. Each item
            # will be in the format [(y, x), (lon, lat)]
            for i in range(1, no_of_points):
                self.mvmt_points.append([(pix_xs[i], pix_ys[i]),
                                         (lons[i], lats[i])])

            i_node = j_node

        # Adding dummy movement points corresponding to the 'Junction_Delay'
        # parameter given in 'sim.config' file.
        no_of_delay_pixels = global_params.gui_params['delay_pixels'][self.group_id]
        for i in range(no_of_delay_pixels):
            self.mvmt_points.append([None, None])

        # Reset the index to point to the beginning position of movement points
        self.mvmt_pt_index = 0

        return

    ## Function to make a unit movement for the movement object
    def update_position(self, global_params):

        if self.mvmt_pt_index == len(self.mvmt_points):
            # Indicates the movement through the current way completed.
            # Need to select the next node
            while True:
                # In case the nodes are so closer there won't be sufficient
                # distance to make at least one pixel for the way_points.
                # In such case compute_next_node needs to be recalled.
                next_node = self.compute_next_node(global_params)

                if next_node == self.next_node:
                    return

                # Updating the prev_node and next_node
                self.curr_node = self.next_node
                self.next_node = next_node

                # Setting the current way as newly selected way
                self.curr_way = global_params.road_graph[self.curr_node][self.next_node]['way_id']

                # Append the new way to ways_visited list
                self.ways_visited.append(self.curr_way)

                # Generate movement points for the selected way
                self.populate_way_points(global_params)

                # If at least one movement point gets generated,
                # break from the loop
                if self.mvmt_points:
                    break

        # If the movement point is a dummy point (a junction delay
        # point), the movement will not be counted, i.e., the movement
        # object is at rest
        if self.mvmt_points[self.mvmt_pt_index][0]:
            self.curr_pix_pos = self.mvmt_points[self.mvmt_pt_index][0]
            self.curr_geo_pos = self.mvmt_points[self.mvmt_pt_index][1]
            self.time_traveled += global_params.sim_tick

        # Make a movement. i.e., update the movement_point index
        self.mvmt_pt_index += 1

        return
