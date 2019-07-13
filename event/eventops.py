''' Module with functions for event operations '''
from __future__ import division
import random
import string

import events


def create_random_data(size=5):
    data = ''.join(random.choice(string.ascii_uppercase +
                                 string.ascii_lowercase +
                                 string.digits) for _ in range(size))
    return data


# Function to create event
def create_event(global_params):
    for group_id in global_params.mvmt_obj_dict:
        try:
            global_params.envt_params.groups[group_id]['Events']
        except KeyError:
            continue
        for mvmt_ob in global_params.mvmt_obj_dict[group_id]:
            ev_len = len(mvmt_ob.events)
            if ev_len == len(mvmt_ob.event_times):
                continue
            elif global_params.sim_time >= mvmt_ob.event_times[ev_len]:
                event_id = 'E%d' % (events.Event.event_counter)
                try:
                    event_duration = global_params.envt_params.groups[group_id]['Event_Life'] / 3600
                except KeyError:
                    event_duration = 1 / 3600
                event_data = mvmt_ob.obj_id + '_' + create_random_data()

                event_ob = events.Event(event_id, mvmt_ob.obj_id,
                                        global_params.sim_time,
                                        event_duration, event_data,
                                        global_params)
                mvmt_ob.events.append(event_ob)
                mvmt_ob.buffer.append((event_ob, mvmt_ob.obj_id,
                                       event_ob.time))
                global_params.events_list.append(event_ob)

                gui_ob = global_params.gui_ob
                if gui_ob:
                    gui_ob.print_msg('STAT1', '%s @ %s' % (event_id, mvmt_ob.obj_id))

                events.Event.event_counter += 1

    return True