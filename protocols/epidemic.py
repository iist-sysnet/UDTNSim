''' module of Epidemic data transfer '''
import geocalc
import simtimer

class EpidemicHandoff:
    ''' Epidemic Data Handoff '''

    def __init__(self):
        self.neighbor_dict = {}
        self.contact_objs = []

    ## Function to find neighbors
    def find_neighbors(self, mvmt_ob, global_params):
        mvmt_obj_list = global_params.mvmt_obj_list
        group_params = global_params.envt_params.groups[mvmt_ob.group_id]

        tx_range = group_params['TX_Range']

        # print '\n---------%s (%f)---------\n' % (mvmt_ob.obj_id, tx_range)
        for obj in mvmt_obj_list:
            if obj.obj_id == mvmt_ob.obj_id:
                continue

            # Calculate the geographical distance between mvmt_ob and obj
            mvmt_ob_geo = mvmt_ob.curr_geo_pos
            obj_geo = obj.curr_geo_pos
            dist = geocalc.calculate_distance(mvmt_ob_geo, obj_geo)

            # If distance < transmission range both are in range
            if dist <= tx_range:
                if obj in self.neighbor_dict:
                    self.neighbor_dict[obj][0] = dist
                    self.neighbor_dict[obj][1] = True
                else:
                    time_stamp = simtimer.convert_HMS(global_params.sim_time)
                    self.neighbor_dict[obj] = [dist, False, time_stamp, None]
            else:
                if obj in self.neighbor_dict:
                    obj_infn = self.neighbor_dict[obj]
                    time_stamp = simtimer.convert_HMS(global_params.sim_time)
                    self.contact_objs.append((obj.obj_id, obj_infn[2], time_stamp))
                    self.neighbor_dict.pop(obj)

    ## Function for exchanging data with all the neighbors
    def exchange_data(self, mvmt_ob, global_params):
        msgs = mvmt_ob.buffer[:]

        # Extract all messages from the buffer of movement object
        src_msg_data = []
        for msg_tuple in msgs:
            src_msg_data.append(msg_tuple[0])
            

        # Copy the messages to neighbor nodes
        for node in self.neighbor_dict:
            mobile_status = global_params.envt_params.groups[node.group_id]['Mobile']
            if not mobile_status:
                continue
            dst_msg_data = []
            for msg_tuple in node.buffer[:]:
                dst_msg_data.append(msg_tuple[0])

            msgs_not_in_node = set(src_msg_data) - set(dst_msg_data)
            if global_params.gui_ob:
                msg_ids = []
                for msg in msgs_not_in_node:
                    msg_ids.append(msg.e_id)
                    if msg_ids:
                        global_params.gui_ob.print_msg('STAT3', '%s -> %s: %s' \
                                                       % (mvmt_ob.obj_id, node.obj_id, \
                                                          str(msg_ids)))
            for msg in msgs_not_in_node:
                node.buffer.append([msg, mvmt_ob.obj_id])


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
                
        
