''' Module for definition of events '''
import report

class Event:
    ''' Event '''
    event_interval_list = []
    event_counter = 0
    stat_obj_list = []

    def __init__(self, event_id, event_time, event_duration, event_data, global_params):
        self.e_id = event_id # Unique event id
        self.time = event_time # Event occurrence time
        self.duration = event_duration # Duration of the event
        self.data = event_data # Data generated in the event
        self.expiry = event_time + event_duration # Event expiry time
        self.expired_status = False
        self.buffer = [] # To store miscellaneous information
        self.report_obj = report.EventReport(self, global_params)

    ## Function to check for event expiry
    def check_expiry(self, curr_time):
        if curr_time > self.expiry:
            self.expired_status = True
            return True
        else:
            return False
