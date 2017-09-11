""" Module for report related functions and classes """

from __future__ import division
import os
import shutil

import initsim
import textformat
import maps
import shared
import simtimer


def create_report_directory(global_params):
    dir_name = global_params.envt_params.envt['Report_Directory']
    if os.path.isdir(dir_name):
        txt_writer = textformat.Colors()
        if not global_params.gui_ob:
            txt_writer.print_msg('RED', 'Warning.')
        txt_msg = "The directory '%s' already exists. " % (dir_name)
        if not shared.Controls.no_of_simulation:
            if global_params.gui_ob:
                ans = global_params.gui_ob.ask_yes_or_no('Warning', txt_msg + 'Do you want to replace it?', 'warning')
            else:
                ans = ' '

        ans = 'yes'
        if ans == 'no':
            return False
        else:
            cwd = os.getcwd() + '/' + dir_name
            shutil.rmtree(cwd)
            os.makedirs(dir_name)
    else:
         os.makedirs(dir_name)

    return True
            

class MovementReport:
    ''' REPORT FOR MOVEMENT OBJECTS '''
    
    def __init__(self, mvmt_ob, global_params):
        """ Initialize with a specific directory to the mvmt_ob """
        self.report_dir = global_params.envt_params.envt['Report_Directory'] + \
                          mvmt_ob.obj_id + '/'
        if not os.path.isdir(self.report_dir):
            os.makedirs(self.report_dir)

    ## Function to create the log files related to the simulations
    def create_log(self, mvmt_ob, global_params):
	# Log the finalized messages
 	file_ptr = open('%smsgs_finalized_%d.dat' % (self.report_dir, \
                                    shared.Controls.no_of_simulation), 'w')
        for ev in mvmt_ob.finalized_msgs:
            event_id = ev.e_id
            file_ptr.write('%s\n' % (event_id))
        file_ptr.close()
                
        # Log the messages collected by the movement object
        file_ptr = open('%smsgs_collected_%d.dat' % (self.report_dir, \
                                    shared.Controls.no_of_simulation), 'w')
        for msg_tuple in mvmt_ob.buffer:
            event_id = msg_tuple[0].e_id
            from_ob = msg_tuple[1]
            file_ptr.write('%s %s\n' % (event_id, from_ob))
        file_ptr.close()        

        # Write the movement objects who meets with the movement objects
        file_ptr = open('%scontacts_%d.dat' % (self.report_dir,\
                                    shared.Controls.no_of_simulation), 'w')
        for contact in mvmt_ob.protocol_obj.contact_objs:
            obj_id = contact[0]
            start_time = contact[1]
            if contact[2]:
                end_time = contact[2]
            else:
                end_time = simtimer.convert_HMS(global_params.sim_time)
            file_ptr.write('%s %s %s\n' % (obj_id, start_time, end_time))
        file_ptr.close()

	if mvmt_ob.group_id == 'Depot':
		return

        # Write the summary of the simulation
        file_ptr = open('%ssummary_%d.dat' % (self.report_dir,\
                                    shared.Controls.no_of_simulation), 'w')
        dist_traveled = mvmt_ob.time_traveled * mvmt_ob.speed
        file_ptr.write('Distance: %f\nTime: %s\n' % (dist_traveled, \
                            simtimer.convert_HMS(mvmt_ob.time_traveled)))
        file_ptr.close()

	# Write the ways visited
        file_ptr = open('%sways_visited_%d.dat' % (self.report_dir, \
                                    shared.Controls.no_of_simulation), 'w')
        for way_id in mvmt_ob.ways_visited:
            file_ptr.write('%d\n' % (way_id))
        file_ptr.close()


	# Log the waiting time of the movement object
	file_ptr = open('%swait_time_%d.dat' % (self.report_dir, \
                                    shared.Controls.no_of_simulation), 'w')
	for item in mvmt_ob.wait_times:
		if item[0] and item[1]:
			text = '%s %s\n' % (simtimer.convert_HMS(item[0]), simtimer.convert_HMS(item[1]))
			file_ptr.write(text)
	try:
            if mvmt_ob.wait_flag:
                    text = '%s %s\n' % (simtimer.convert_HMS(mvmt_ob.wait_start), simtimer.convert_HMS(global_params.sim_time))
        except:
            pass
        
	file_ptr.close()

class EventReport:
    ''' REPORT FOR EVENT OBJECTS '''
    
    def __init__(self, event_ob, global_params):
        """ Initialize with a specific directory to the mvmt_ob """
        self.report_dir = global_params.envt_params.envt['Report_Directory'] + \
                          'events' + '/'
        if not os.path.isdir(self.report_dir):
            os.makedirs(self.report_dir)

        self.event_id = event_ob.e_id

    ## Function to create log of events
    def create_log(self, event_ob):
        f_ptr = open('%s%s_%d.dat' % (self.report_dir, self.event_id, \
                                    shared.Controls.no_of_simulation), 'a')
        txt = 'EID: %s\nTime: %s\nDuration: %s\nExpiry: %s\nExpired: %s\nData: %s\nBuffer: %s' % \
          (self.event_id, simtimer.convert_HMS(event_ob.time), \
                     simtimer.convert_HMS(event_ob.duration), \
                     simtimer.convert_HMS(event_ob.expiry), \
                     str(event_ob.expired_status), event_ob.data, \
                     str(event_ob.buffer))

        f_ptr.write(txt)
        f_ptr.close()
        
