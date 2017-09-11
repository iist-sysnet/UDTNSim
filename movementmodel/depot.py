''' Module for simple random movement '''
from __future__ import division
import random
import numpy

import stationary
import geocalc
import report

class DepotMovement(stationary.Stationary):
    """ Simple Random Movement Model """

    def __init__(self, obj_label, group_id, group_params, global_params):
        stationary.Stationary.__init__(self, obj_label, group_id, group_params, global_params)

	self.ways_visited = []

	self.neigh_list = global_params.road_graph.neighbors(self.init_node)
	self.neigh_list.pop(1)
	self.neigh_index = 1

	for mvmt_ob in global_params.mvmt_obj_list:
		mvmt_ob.depot_ob = self

	print 'Depot initialized'
	
    def get_a_node(self):
	next_node = self.neigh_list[self.neigh_index]
	self.neigh_index += 1
	if self.neigh_index == len(self.neigh_list):
		self.neigh_index = 0

	return next_node

    def compute_initial_node(self, global_params):
	#return 103214114	# Manhattan
	return 103174015 # Newyork
	#return 1365948969 #Dharavi
	

   
