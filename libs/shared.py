''' Module for the shared objects and variables '''

## Class for creating an  object with required global parameters
class Shared:
    def __init__(self):
        # Environment and group parameters read from the 'settings.dtn' file
        self.envt_params = None

        # Way dictionary created from the .osm file
        self.way_dict = None

        # Node dictionary created from the .osm file
        self.node_dict = None

        # The graph created from the road network
        self.road_graph = None

        # GUI object for the simulator
        self.gui_ob = None

        # The parameters required for GUI
        self.gui_params = None

        # Movement object list
        self.mvmt_obj_list = None

        # Simulator time
        self.sim_time = 0.0

        # Value of one simulator clock tick
        self.sim_tick = None

        # Object for printing messages such as errors, warnings etc.
        self.writer_obj = None

        # List for events
        self.events_list = []


## Class for simulation control variables. These are static variables
## which are required and modified from different modules
class Controls:
    # Flag for pause/resume status of the simulator
    sim_pause_status = True

    # Flag for stop status of the simulator. When the user clicks on
    # the stop button, the flag becomes 'True'
    sim_stop_status = False

    # The counter for the number of simulations. 
    no_of_simulation = 0

    # To make the GUI to a graph mode so that the road network will be
    # redrawn as a graph
    graph_mode = False
