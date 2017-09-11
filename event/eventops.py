''' Module with functions for event operations '''
from __future__ import division
import random
import string

import shared
import events

def create_random_data(size = 5):
    data = ''.join(random.choice(string.ascii_uppercase + \
                                 string.ascii_lowercase + \
                                 string.digits) for _ in range(size))
    return data


## Function for creating an event
def create_event(global_params):

    while  (events.Event.event_counter < len(events.Event.event_interval_list))\
      and (events.Event.event_interval_list[events.Event.event_counter] \
      < global_params.sim_time):

        event_id = 'E%d' % (events.Event.event_counter)
        event_duration = 1 / 6 # Event duration as 10 minutes
        event_data = create_random_data() # Creating radom text

        # Create the event object
        event_obj = events.Event(event_id, global_params.sim_time, \
                               event_duration, event_data, global_params)

        # Select a random static node from the objects
        stat_obj = random.choice(events.Event.stat_obj_list)
        event_obj.buffer.append(stat_obj.obj_id) # Add parent object to event
        stat_obj.buffer.append((event_obj, stat_obj.obj_id)) # Add event object 

        global_params.events_list.append(event_obj) # 


        gui_ob = global_params.gui_ob
        if gui_ob:
            gui_ob.print_msg('STAT1', '%s @ %s' % (event_id, stat_obj.obj_id))

        events.Event.event_counter += 1

    return True
