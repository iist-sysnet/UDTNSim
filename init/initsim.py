from __future__ import division
import os
import numpy

import xmlparser, settings, textformat, graphops, gui, guicalc, \
  shared, simtimer, report
import stationary, simplerandom, pathtype, depot, restricted, wait, highway, pathmemory
import epidemic
import events
import superioronly, superiorpeer, deposit, receive

## Function to create a Data Handoff object
def create_handoff_object(group_id, global_params):
    group_params = global_params.envt_params.groups[group_id]
    protocol_type = group_params['Protocol']
    if protocol_type == 'EpidemicHandoff':
        return epidemic.EpidemicHandoff()
    elif protocol_type == 'SuperiorOnlyHandoff':
        return superioronly.SuperiorOnlyHandoff(group_id, global_params)
    elif protocol_type == 'SuperiorPeerHandoff':
        return superiorpeer.SuperiorPeerHandoff(group_id, global_params)
    elif protocol_type == 'DepositHandoff':
	return deposit.DepositHandoff(group_id, global_params)
    elif protocol_type == 'ReceiveHandoff':
	return receive.ReceiveHandoff(group_id, global_params)

    return None
    

## Function for creating a movement object. If you add a new movement
## model, please append one more elif condtion to this function so that
## no other change is further required in this code.
def create_mvmt_object(obj_label, group_id, group_params, global_params):
    obj_type = group_params['Movement']
    if obj_type == 'Stationary':
        return stationary.Stationary(obj_label, group_id, group_params, global_params)
    if obj_type == 'SimpleRandomMovement':
        return simplerandom.SimpleRandomMovement(obj_label, group_id, group_params, global_params)
    elif obj_type == 'PathTypeMovement':
        return pathtype.PathTypeMovement(obj_label, group_id, group_params, global_params)
    elif obj_type == 'PathMemoryMovement':
        return pathmemory.PathMemoryMovement(obj_label, group_id, group_params, global_params)
    elif obj_type == 'DepotMovement':
	return depot.DepotMovement(obj_label, group_id, group_params, global_params)
    elif obj_type == 'RestrictedMovement':
	return restricted.RestrictedMovement(obj_label, group_id, group_params, global_params) 
    elif obj_type == 'WaitMovement':
	return wait.WaitMovement(obj_label, group_id, group_params, global_params)
    elif obj_type == 'HighwayMovement':
	return highway.HighwayMovement(obj_label, group_id, group_params, global_params)
    

## Function for setting up the simulation environment. Since the
## simulation environment is same, this function will be executed 
## only once. 
def init_sim_envt():
    print 'Initializing simulation environment.'
    
    # Create a shared object for sharing global information
    global_params = shared.Shared() 

    # Object for printing messages
    writer_obj = textformat.Colors()
    global_params.writer_obj = writer_obj

    # Reading the settings file
    envt_params = settings.Settings('sim.config')
    global_params.envt_params = envt_params
    read_settings_status = envt_params.read_settings()
    if not read_settings_status:
        writer_obj.print_msg('WHITE', 'Error in the settings file.')
        return False, None

    
    # Parse the openstreetmap file and make appropriate dictionaries
    # for node points and ways
    global_params.node_dict, global_params.way_dict, bounds, \
    global_params.gui_params, = xmlparser.parse_osm(envt_params.envt['Map'],
                                                    600, 600)

    # Create the simulator timer
    global_params.sim_tick, pix_unit, pix_multiplier = simtimer.create_sim_timer\
      (bounds, global_params)
    global_params.gui_params['pix_unit'] = pix_unit
    global_params.gui_params['pix_multiplier'] = pix_multiplier

    # Compute junction delay points
    global_params.gui_params['delay_pixels'] = guicalc.compute_delay_pixels\
      (global_params)

    # Create a graph of road network
    global_params.road_graph = graphops.create_minimal_graph\
      (global_params.way_dict)

    # Create GUI if 'GUI_Enabled' is set to True in 'settings.dtn'
    if envt_params.envt['GUI_Enabled']:
        gui_ob = gui.Gui('DTN Simulator', global_params)
        global_params.gui_ob = gui_ob
        gui.set_sim_ctrl_variables(global_params)
        gui_ob.create_map(global_params.node_dict, global_params.way_dict)

    # Create a report directory
    report_status = report.create_report_directory(global_params)
    if not report_status:
        return False, None

    return True, global_params


## Function for initializing all the movmemnt objects. This function will 
## be executed for each simulation.
def init_mvmt_objects(global_params):
    global_params.writer_obj.print_msg('ITALIC', 'Initializing the movment objects.')
    
    # Create movement objects
    global_params.mvmt_obj_list = [] # List for keeping all movement objects
    envt_params = global_params.envt_params


    for group_id in envt_params.groups:
        group = envt_params.groups[group_id]
        
        for i in range(group['No_of_Hosts']):
            obj_label = group['Label'][0] + str(i)

            # Creation of a movement object
            mvmt_obj = create_mvmt_object(obj_label, group_id, group, \
                                          global_params) 
            global_params.mvmt_obj_list.append(mvmt_obj)

            # Addition of Handoff object
            if group['Protocol'] <> 'None':
                mvmt_obj.protocol_obj = create_handoff_object(group_id, global_params)



    # Draw graphical objects for corresponding movement objects
    if global_params.gui_ob:
        for mvmt_obj in global_params.mvmt_obj_list:
            global_params.gui_ob.create_node(mvmt_obj, global_params)

    global_params.writer_obj.print_msg('GREEN', 'Done.')

    return True


## Function to initialize the settings for event generation
def init_events(global_params):

    rng_params = global_params.envt_params.envt['Random_Msg_Gen_Parameter']
    rng_params[0] = int(rng_params[0])
    rng_params[1] = float(rng_params[1])

    try:        
        event_interval = rng_params[1] / rng_params[0]
        no_of_event_points = global_params.envt_params.envt['Simulation_Time'] \
          * rng_params[0] / rng_params[1]
    except:
        global_params.writer_obj('WHITE', 'Error in \'Random_Msg_Gen_Parameter\' \
        in \'settings.dtn\'')
        return False

    event_interval_list = numpy.random.exponential(event_interval, \
                                                   no_of_event_points)

    i = 0
    for j in range(1, int(no_of_event_points)):
        event_interval_list[j] += event_interval_list[i]
        i = j

    events.Event.event_interval_list = event_interval_list
    
    events.Event.event_counter = 0

    events.Event.stat_obj_list = []
    for mvmt_obj in global_params.mvmt_obj_list:
        group_params = global_params.envt_params.groups[mvmt_obj.group_id]
        if not group_params['Mobile'] and mvmt_obj.group_id != 'Depot':
            events.Event.stat_obj_list.append(mvmt_obj)

    return True
      

