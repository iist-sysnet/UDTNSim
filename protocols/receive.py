''' module of Superior-Peer data transfer '''
import geocalc
import simtimer

import epidemic
import superiorpeer

class ReceiveHandoff(superiorpeer.SuperiorPeerHandoff):
    ''' Superior-Only Handoff '''

    def __init__(self, group_id, global_params):
        superiorpeer.SuperiorPeerHandoff.__init__(self, group_id, global_params)
        
    ## Function for exchanging data with all the neighbors
    def exchange_data(self, mvmt_ob, global_params):

        return


    def execute_protocol(self, mvmt_ob, global_params):
        # Find the neighbors
        self.find_neighbors(mvmt_ob, global_params)
        self.print_neighbors(mvmt_ob, global_params.gui_ob)
        self.exchange_data(mvmt_ob, global_params)
        

    def print_neighbors(self, mvmt_ob, gui_ob):
        if not gui_ob:
            return 

        for node in self.neighbor_dict:
            distance = self.neighbor_dict[node][0]
            already_neighbor = self.neighbor_dict[node][1]
            if not already_neighbor:                
                # gui_ob.print_msg('STAT1', '%s -> %s (%.4f)' % (mvmt_ob.obj_id, node.obj_id, distance))
                gui_ob.print_msg('STAT2', '%s -> %s (%d)' % (mvmt_ob.obj_id, node.obj_id, distance * 1000))

        return 
                
        
