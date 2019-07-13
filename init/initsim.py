from __future__ import division
import numpy

# Import libraries
import xmlparser
import settings
import textformat
import graphops
import gui
import guicalc
import geocalc
import shared
import simtimer
import report

# Import mobility models
import stationary
import simplerandom
import pathtype
import pathmemory

# Import routing protocols
import epidemic


# Function to create a Data Handoff object
def create_handoff_object(group_id, global_params):
    group_params = global_params.envt_params.groups[group_id]
    protocol_type = group_params['Protocol']
    if protocol_type == 'EpidemicHandoff':
        return epidemic.EpidemicHandoff()

    return None


# Function for creating a movement object. If you add a new movement
# model, please append one more elif condtion to this function so that
# no other change is further required in this code.
def create_mvmt_object(obj_label, group_id, group_params, global_params):
    obj_type = group_params['Movement']
    if obj_type == 'Stationary':
        return stationary.Stationary(obj_label, group_id,
                                     group_params, global_params)
    elif obj_type == 'SimpleRandomMovement':
        return simplerandom.SimpleRandomMovement(obj_label, group_id,
                                                 group_params, global_params)
    elif obj_type == 'PathTypeMovement':
        return pathtype.PathTypeMovement(obj_label, group_id,
                                         group_params, global_params)
    elif obj_type == 'PathMemoryMovement':
        return pathmemory.PathMemoryMovement(obj_label, group_id,
                                             group_params, global_params)


# Function for setting up the simulation environment. Since the
# simulation environment is same, this function will be executed
# only once.
def init_sim_envt():
    print ('Initializing simulation environment.')

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
    node_dict, way_dict, bounds = xmlparser.parse_osm(envt_params.envt['Map'])

    # GUI parameters, i.e., translation and scaling factors
    global_params.gui_params['trans_factor'] = guicalc.translation_factor(bounds)
    global_params.gui_params['scale_factor'] = guicalc.scale_factor(bounds,
                                                                    600, 600)
    
    # Create the simulator timer
    global_params.sim_tick, pix_unit, pix_multiplier = simtimer.create_sim_timer(bounds, global_params)
    global_params.gui_params['pix_unit'] = pix_unit
    global_params.gui_params['pix_multiplier'] = pix_multiplier

    # Compute junction delay points
    global_params.gui_params['delay_pixels'] = guicalc.compute_delay_pixels(global_params)

    # Compute pixel coordinates of nodes
    for node in node_dict:
        pix_cord = geocalc.geo_to_cart(node_dict[node]['cord'], global_params.gui_params)
        node_dict[node]['pixcord'] = pix_cord

    global_params.way_dict = way_dict
    global_params.node_dict = node_dict

    # Create the graph
    global_params.road_graph, available_road_types = graphops.create_graph(node_dict, way_dict)

    available_types = [u for u, v in available_road_types]
    for group_id in global_params.envt_params.groups:
        try:
            road_types = [int(x) for x in global_params.envt_params.groups[group_id]['Paths']]
        except KeyError:
            continue
        for road_type in road_types:
            if road_type not in available_types:
                writer_obj.print_msg('RED', 'Invalid paths given for %s in \'sim.config\'.' % (group_id))
                writer_obj.print_msg('WHITE', 'Available path types: %s.' % (str(available_road_types)))
                return False, None

    # Create GUI if 'GUI_Enabled' is set to True in 'sim.config'
    if envt_params.envt['GUI_Enabled']:
        gui_ob = gui.Gui('UDTN Simulator', global_params)
        global_params.gui_ob = gui_ob
        gui.set_sim_ctrl_variables(global_params)
        gui_ob.create_map(global_params)

    # Create a report directory
    report_status = report.create_report_directory(global_params)
    if not report_status:
        return False, None

    return True, global_params


# Function for initializing all the movmemnt objects. This function is
# executed for each simulation.
def init_mvmt_objects(global_params):
    global_params.writer_obj.print_msg('ITALIC',
                                       'Initializing the movment objects.')

    # Create movement objects
    envt_params = global_params.envt_params

    for group_id in envt_params.groups:
        group = envt_params.groups[group_id]
        global_params.mvmt_obj_dict[group_id] = []
        for i in range(group['No_of_Hosts']):
            obj_label = group['Label'][0] + str(i)

            # Creation of a movement object
            mvmt_obj = create_mvmt_object(obj_label, group_id, group,
                                          global_params)
            global_params.mvmt_obj_dict[group_id].append(mvmt_obj)

            # Addition of Handoff object
            if group['Protocol'] != 'None':
                mvmt_obj.protocol_obj = create_handoff_object(group_id,
                                                              global_params)

    # Draw graphical objects for corresponding movement objects
    if global_params.gui_ob:
        for group_id in global_params.mvmt_obj_dict:
            mvmt_obj_list = global_params.mvmt_obj_dict[group_id]
            for mvmt_obj in mvmt_obj_list:
                global_params.gui_ob.create_node(mvmt_obj, global_params)

    global_params.writer_obj.print_msg('GREEN', 'Done.')

    return True


# Function to initialize settings for event generation in nodes
def init_events(global_params):
    for group_id in global_params.mvmt_obj_dict:
        try:
            msg_rate = global_params.envt_params.groups[group_id]['Events']
        except KeyError:
            continue
        simulation_time = global_params.envt_params.envt['Simulation_Time']
        no_of_event_points = int(simulation_time * msg_rate)
        event_interval = 1.0 / msg_rate

        # Creating message generation timestamps for each object
        for mvmt_obj in global_params.mvmt_obj_dict[group_id]:
            event_times = numpy.random.exponential(event_interval,
                                                   no_of_event_points)
            t = 0
            for tm in event_times:
                t += tm
                mvmt_obj.event_times.append(t)

    return True
