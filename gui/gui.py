""" Module for class and functions related to GUI."""

from Tkinter import *
import tkMessageBox
import time
import os

import initsim
import geocalc
import shared

# Function for defining the simulation variables for the GUI
def set_sim_ctrl_variables(global_params):
    shared.Controls.sim_speed = 5
    shared.Controls.sim_pause_status = True
    shared.Controls.sim_stop_status = False
    shared.Controls.graph_mode = False

class Gui:
    ''' GUI '''

    available_way_types = ['highway', 'twowheeler', 'pedestrian',\
                           'trunk', 'railway', 'residential']
    color_dict = {"highway":"light slate gray", "twowheeler":"LightPink1", \
                  "pedestrian":"SkyBlue1", 'trunk': 'LightSalmon2', \
                  'railway': 'wheat2', "residential": "light green"}
    
    def __init__(self, title, global_params):
        self.top_widget = Tk() # Main widget for the GUI
        self.top_widget.protocol('WM_DELETE_WINDOW', \
                                 lambda:self.exit_simulator(global_params))
        self.top_widget.bind('<<Alt_F4>>', \
                             lambda:self.exit_simulator(global_params))
        self.top_widget.title(title)

        """ Frame for canvas where the simulation takes place """
        self.frm_can = Frame(self.top_widget)
        self.frm_can.pack(side=LEFT, padx=5, pady=5)

        # Canvas for showing map and movement objects
        self.main_canvas = Canvas(self.frm_can, width=650, height=600, \
                             background='white', bd=1, relief='ridge', \
                            highlightthickness=2)
                            
        self.main_canvas.create_polygon(620, 580, 630, 580, 625, 590,
                                        fill='green', outline='black')
        self.main_canvas.create_text(625, 596, text="N")
        self.txt_timer = self.main_canvas.create_text(575, 596, text='')
        self.txt_simno = self.main_canvas.create_text(325, 594, text='')
                            
        
        self.main_canvas.pack()

        self.frm_msg = Frame(self.top_widget)
        self.frm_msg.pack(side=LEFT)

        self.frm_simmsg = Frame(self.frm_msg)
        self.frm_simmsg.pack(pady=10)

        """ Statistics-1 """
        self.frm_msg1 = Frame(self.frm_simmsg)
        self.frm_msg1.pack(side=LEFT)
        self.lbl_msg1 = Label(self.frm_msg1, text='Statistic-1')
        self.lbl_msg1.pack(side=TOP)        
        self.txt_msg1 = Text(self.frm_msg1, height=15, width=30, \
                            background='light gray', foreground='navy')
        self.txt_msg1.tag_configure('txt_msg', justify=CENTER)
        self.txt_msg1.tag_add('txt_msg', 1.0, END)
        self.txt_msg1.pack(side=LEFT)
        self.scr_msg1 = Scrollbar(self.frm_msg1)
        self.scr_msg1.pack(side=LEFT, fill='y')
        self.scr_msg1.config(command=self.txt_msg1.yview)
        self.txt_msg1.config(yscrollcommand=self.scr_msg1.set)

        """ Statistics-2 """
        self.frm_msg2 = Frame(self.frm_simmsg)
        self.frm_msg2.pack(side=LEFT)
        self.lbl_msg2 = Label(self.frm_msg2, text='Statistic-2')
        self.lbl_msg2.pack(side=TOP)
        self.txt_msg2 = Text(self.frm_msg2, height=15, width=30, \
                             background='light gray', \
                             foreground='dark green')
        self.txt_msg2.pack(side=LEFT)
        self.scr_msg2 = Scrollbar(self.frm_msg2)
        self.scr_msg2.pack(side=LEFT, fill='y')
        self.scr_msg2.config(command=self.txt_msg2.yview)
        self.txt_msg2.config(yscrollcommand=self.scr_msg2.set)

        """ Statistics-3 """
        self.frm_msg3 = Frame(self.frm_msg)
        self.frm_msg3.pack(padx=10, pady=20)
        self.lbl_msg3 = Label(self.frm_msg3, text='Statistic-3')
        self.lbl_msg3.pack(side=TOP)
        self.txt_msg3 = Text(self.frm_msg3, height=15, width=64, \
                             background='light gray')
        self.txt_msg3.pack(side=LEFT)
        self.scr_msg3 = Scrollbar(self.frm_msg3)
        self.scr_msg3.pack(side=LEFT, fill='y')
        self.scr_msg3.config(command=self.txt_msg3.yview)
        self.txt_msg3.config(yscrollcommand=self.scr_msg3.set)

        """ Control buttons """
        self.frm_ctl = Frame(self.frm_msg)
        self.frm_ctl.pack(pady=10)

        self.btn_start = Button(self.frm_ctl, text='>', \
                    command=lambda:self.set_sim_pause_resume(False))
        self.btn_start.pack(side=LEFT)
        self.btn_pause = Button(self.frm_ctl, text='||', \
                    command=lambda:self.set_sim_pause_resume(True))
        self.btn_pause.pack(side=LEFT)
        self.btn_stop = Button(self.frm_ctl, text='O', \
                    command=lambda:self.stop_simulation(global_params))
        self.btn_stop.pack(side=LEFT)
        self.btn_rw = Button(self.frm_ctl, text='<<', \
                    command=lambda:self.set_sim_speed(False))
        self.btn_rw.pack(side=LEFT)
        self.btn_fw = Button(self.frm_ctl, text='>>', \
                    command=lambda:self.set_sim_speed(True))
        self.btn_fw.pack(side=LEFT)
        self.btn_close = Button(self.frm_ctl, text='X', \
                    command=lambda:self.exit_simulator(global_params))
        self.btn_close.pack(side=RIGHT, padx=20)

        self.mnu_bar = Menu(self.top_widget)
        self.top_widget.config(menu=self.mnu_bar)

        self.mnu_file = Menu(self.mnu_bar, tearoff=1)        
        self.mnu_bar.add_cascade(label='File', menu=self.mnu_file)
        self.mnu_file.add_command(label='Exit', \
                    command=lambda:self.exit_simulator(global_params))

        self.graph_mode = False
        self.mnu_graph = Menu(self.mnu_bar, tearoff=1)
        self.mnu_bar.add_cascade(label='Graph', menu=self.mnu_graph)
        self.mnu_graph.add_checkbutton(label='Graph Mode', \
                command=lambda:self.toggle_graph_mode(global_params), \
                variable=self.graph_mode, \
                onvalue=True, offvalue=False)
        # self.mnu_graph.add_command(label='Components << - >>', \
        #                            command=self.move_component)


    ## Function to draw the map and movement objects
    def draw_canvas(self, global_params):
        self.main_canvas.delete('all')

        # Drawing the map
        self.create_map(global_params.node_dict, global_params.way_dict)

        # Drawing movement objects
        for mvmt_ob in global_params.mvmt_obj_list:
            self.create_node(mvmt_ob, global_params)
        
        self.update_sim_timer(global_params)


    ## Function to toggle the simulator to graph mode
    def toggle_graph_mode(self, global_params):
        if self.graph_mode:
            self.graph_mode = False
            shared.Controls.graph_mode = False
            self.draw_canvas(global_params) # Draw map
        else:
            self.graph_mode = True
            shared.Controls.graph_mode = True
            self.draw_graph(global_params) # Draw graph


    ## Function for drawin the graph
    def draw_graph(self, global_params):
        self.main_canvas.delete('all')    

        road_graph = global_params.road_graph

        # Drawing all the vertices
        nodes = road_graph.nodes()
        for node in nodes:
            pix_pt = global_params.node_dict[node][1]
            self.main_canvas.create_oval(pix_pt[1] - 2,pix_pt[0] - 2, \
            pix_pt[1] + 2, pix_pt[0] + 2, fill='black', width=0)

        # Drawing all the edges
        edges = road_graph.edges()
        for edge in edges:
            pix_pt1 = global_params.node_dict[edge[0]][1]
            pix_pt2 = global_params.node_dict[edge[1]][1]
            color = Gui.color_dict[road_graph[edge[0]][edge[1]]['e_type']]
            self.main_canvas.create_line(pix_pt1[1], pix_pt1[0], \
                    pix_pt2[1], pix_pt2[0], fill=color)                

    ## Function to exit from the simulator
    def exit_simulator(self, global_params):
        # In case of an incomplete simulation, it ask user to confirm the exit
        if global_params.sim_time < global_params.envt_params.envt\
          ['Simulation_Time'] and not shared.Controls.sim_stop_status \
          and shared.Controls.no_of_simulation < \
          global_params.envt_params.envt['No_of_Simulations']:
            tkMessageBox.showinfo('Warning', 'Stop the simulation first to '
                                  'log the current status of simulation')
        else:
            self.top_widget.destroy()
            

    ## Function to stop the simulation
    def stop_simulation(self, global_params):
        if global_params.sim_time < global_params.envt_params.envt\
          ['Simulation_Time']:
            ans = tkMessageBox.askquestion('Warning', 'Simulation not yet '
                        'completed. You want to stop the simulation?', \
                                           icon='warning')
            if ans == 'yes':
                shared.Controls.sim_stop_status = True
        else:
            return True
            

    ## Function to toggle the simulator in pause/resume mode
    def set_sim_pause_resume(self, val):
        shared.Controls.sim_pause_status = val
        

    ## Function to control the speed of the movement of objects
    def set_sim_speed(self, up_flag):
        if up_flag:
            if shared.Controls.sim_speed <> 0:
                shared.Controls.sim_speed -= 1
        else:
            if shared.Controls.sim_speed <> 50:
                shared.Controls.sim_speed += 1
                
    ## Function to update the simulation time displayed in the GUI
    def update_sim_timer(self, global_params):
        self.main_canvas.delete(self.txt_timer)
        minutes, seconds = divmod(global_params.sim_time * 3600, 60)
        hours, minutes = divmod(minutes, 60)
        txt_timer = '%02d:%02d:%02d' % (hours, minutes, seconds)
        self.txt_timer = self.main_canvas.create_text(575, 596, text=txt_timer)
        self.main_canvas.itemconfig(self.txt_timer, text=txt_timer)
        

    ## Function to draw the map in the canvas
    def create_map(self, node_dict, way_dict):
        for item in way_dict:
            if way_dict[item][1] not in Gui.available_way_types:
                continue
            line_color = Gui.color_dict[way_dict[item][1]]
            for i in range(1, len(way_dict[item][0])):
                node_key0 = way_dict[item][0][i - 1]
                node_key1 = way_dict[item][0][i]
                point0 = node_dict[node_key0][1]
                point1 = node_dict[node_key1][1]
                self.main_canvas.create_line(point0[1], point0[0],\
                                             point1[1], point1[0],\
                                             fill=line_color, width=1)
        return True
        

    ## Function to draw a movement object
    def create_node(self, mvmt_ob, global_params):        
        ob_label = mvmt_ob.obj_id

        start_pt = mvmt_ob.curr_pix_pos
        color = global_params.envt_params.groups[mvmt_ob.group_id]['Color']

        # Mobile objects are drawn as filled circles
        if global_params.envt_params.groups[mvmt_ob.group_id]['Mobile']:
            self.main_canvas.create_oval(start_pt[1] - 3, start_pt[0] - 3, \
                                    start_pt[1] + 3, start_pt[0] + 3, \
                                    fill=color, tags=ob_label)

        # Objects which are immobile are drawn as triangles
        else:
            self.main_canvas.create_polygon(start_pt[1], start_pt[0] - 4,
                            start_pt[1] + 4, start_pt[0] + 4, \
                            start_pt[1] - 4, start_pt[0] + 4, \
                            fill=color, tags=ob_label, \
                            outline='grey')
                            
        # Creating the label for the object
        self.main_canvas.create_text(start_pt[1], start_pt[0] - 7, \
                                    text=ob_label, fill='brown', \
                                tags='txt_'+ob_label)


    ## Function to redraw the node. After each movement position updation
    ## each movement is redrawn
    def redraw_node(self, mvmt_ob, global_params):
        
        self.main_canvas.delete(mvmt_ob.obj_id)
        self.main_canvas.delete('txt_' + mvmt_ob.obj_id)
        
        ob_label = mvmt_ob.obj_id
        color = global_params.envt_params.groups[mvmt_ob.group_id]['Color']
        start_pt = mvmt_ob.curr_pix_pos
        self.main_canvas.create_oval(start_pt[1] - 3, start_pt[0] - 3, \
                                    start_pt[1] + 3, start_pt[0] + 3, \
                                    fill=color, tags=ob_label)                    
        self.main_canvas.create_text(start_pt[1], start_pt[0] - 7, \
                                    text=ob_label, fill='brown', \
                                tags='txt_'+ob_label)

        
    ## Function for updating simulator parameters displayed in the canvas
    def update_sim(self, global_params):
        self.main_canvas.after(shared.Controls.sim_speed)
        self.update_sim_timer(global_params)
        self.main_canvas.update()
        self.print_msg('SIMLN', 'Simulation - %d' % \
                       (shared.Controls.no_of_simulation))

    ## Function to update simulator during the 'pause' state
    def pause_update_sim(self):
        self.main_canvas.update()

    ## Function to delete an object from the canvas
    def delete_object(self, mvmt_ob):
        self.main_canvas.delete(mvmt_ob.mvmt_obj.uid)
        self.main_canvas.delete('txt_' + mvmt_ob.mvmt_obj.uid)
        

    ## Function to display messages in the three message boxes
    ## provided in the simulator
    def print_msg(self, msg_type, msg):
        msg = ' ' + msg + '\n'
        if msg_type == 'STAT1':
            self.txt_msg1.insert(END, msg)
        elif msg_type == 'STAT2':            
            self.txt_msg2.insert(END, msg)
        elif msg_type == 'STAT3':
            self.txt_msg3.insert(END, msg)            
        elif msg_type == 'SIMLN':
            self.main_canvas.delete(self.txt_simno)
            self.txt_simno = self.main_canvas.create_text(325, 594, text='SIMULATION - %d' % (shared.Controls.no_of_simulation))
            # self.main_canvas.itemconfig(self.txt_simno, text='SIMULATION - %d' % (shared.Controls.no_of_simulation))
            
        self.txt_msg1.see(END)
        self.txt_msg2.see(END)
        self.txt_msg3.see(END)
        
    ### Function for a common yes/no question box
    def ask_yes_or_no(self, title, txt_msg, icon_type):
        ans = tkMessageBox.askquestion(title, txt_msg, icon=icon_type)

        return ans
