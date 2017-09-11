''' The main execution file '''
from __future__ import division
import sys
library_list = ['init/', 'parser/', 'settings/', 'movementmodel/', 'gui/', \
                'libs/', 'report/', 'protocols/', 'event/']
sys.path += library_list

import initsim
import shared
import eventops
import simtimer

# Function for executing a simulation
def execute_simulation(global_params):
    """ Function for Simulation """

    mvmt_obj_list = global_params.mvmt_obj_list
    global_params.sim_time = 0.0 

    # Loop will work till the sim_time reaches the 'Simulation_Time' specified in
    # the 'settings.dtn' file
    while global_params.sim_time < global_params.envt_params.envt['Simulation_Time']:
        if shared.Controls.sim_stop_status: # Work only when there is a 
            break # 'stop-button' click on the simulator

        for mvmt_obj in mvmt_obj_list:
            mobility_status = global_params.envt_params.groups[mvmt_obj.group_id]['Mobile']
            if not mobility_status:
                continue
            mvmt_obj.update_position(global_params) # A unit movement of mobile node
            if global_params.gui_ob: # Redraw the node's position
                global_params.gui_ob.redraw_node(mvmt_obj, global_params)

        for mvmt_ob in mvmt_obj_list:
            mvmt_ob.protocol_obj.execute_protocol(mvmt_ob, global_params)

        if global_params.gui_ob:
            global_params.gui_ob.update_sim(global_params) # Update simultion parameters
            while shared.Controls.sim_pause_status:
                if shared.Controls.sim_stop_status:
                    return
                global_params.gui_ob.pause_update_sim()
                continue # Loop will work when the simulator is in paused state
	else:
	    timetxt = simtimer.convert_HMS(global_params.sim_time)
	    sys.stdout.write('\r%s' % (timetxt))
	    sys.stdout.flush()

        # Updating the simulation clock timer
        global_params.sim_time += global_params.sim_tick

        # Random message generation
        event_creation_status = eventops.create_event(global_params)

        for event_ob in global_params.events_list:
            if not event_ob.expired_status:
                event_ob.check_expiry(global_params.sim_time)

    # Generating the log of the nodes' movement in the simulation
    for mvmt_ob in global_params.mvmt_obj_list:
        mobility_status = global_params.envt_params.groups[mvmt_ob.group_id]['Mobile']
        if not mobility_status and mvmt_ob.group_id != 'Depot':
            continue
        else:
            mvmt_ob.report_obj.create_log(mvmt_ob, global_params)

    # Generating the log of the events
    for event_ob in global_params.events_list:
        event_ob.report_obj.create_log(event_ob)


# Main function for the simulator
def main():
    shared.Controls.no_of_simulation = 0 # For controlling the number of simulations

    # Initializing simulation environment. Required only once
    init_status, global_params = initsim.init_sim_envt()
    if not init_status:
        return

    # print 'Entered in before execn'
    while True:
        global_params.writer_obj.print_msg('WHITE', '\nSimulation %d running' \
                                           % (shared.Controls.no_of_simulation))
        # Initialize all movement objects
        mvmt_obj_status = initsim.init_mvmt_objects(global_params)

        # Initialize events
        event_init_status = initsim.init_events(global_params)
        if not event_init_status:
            return 1
        
        execute_simulation(global_params) # Execute simulation
        shared.Controls.no_of_simulation += 1 

        # Loop continue until the number of simulations reaches the
        # 'No_of_Simulations' parameter given in the 'settings.dtn' file
        if shared.Controls.no_of_simulation == global_params.envt_params.envt['No_of_Simulations'] \
          or shared.Controls.sim_stop_status:
            break

    # Displaying the GUI
    if global_params.gui_ob:
        global_params.gui_ob.top_widget.mainloop()

if __name__ == '__main__':
    main()
