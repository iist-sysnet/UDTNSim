''' Creation of simulation timer '''
from __future__ import division
import geocalc


# Function to convert hours in HH:MM:SS format
def convert_HMS(hours):
    seconds = hours * 3600
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    txt_timer = '%02d:%02d:%02d' % (hours, minutes, seconds)

    return txt_timer


# Function for creating the simulation timer/clock
def create_sim_timer(bounds, global_params):
    # Calculation of the geographical distance corresponding to a
    # pixel (pix_unit)

    geo_pt1 = (float(bounds['minlat']), float(bounds['minlon']))
    geo_pt2 = (float(bounds['maxlat']), float(bounds['minlon']))

    pix_pt1 = geocalc.geo_to_cart(geo_pt1, global_params.gui_params)
    pix_pt2 = geocalc.geo_to_cart(geo_pt2, global_params.gui_params)

    geo_distance = geocalc.calculate_distance(geo_pt1, geo_pt2)
    pix_distance = round(pix_pt2[0]) - round(pix_pt1[0]) + 1

    pix_unit = geo_distance / pix_distance

    # Calculation of pixel multiplier for each group. For each group
    # the pixel multiplier will be maximum speed among the
    # groups / speed of the group
    speed_dict = {}
    mvmt_obj_groups = global_params.envt_params.groups
    max_speed = 0
    for group_id in mvmt_obj_groups:
        try:
            group_speed = mvmt_obj_groups[group_id]['Speed']
        except KeyError:
            group_speed = 0
        speed_dict[group_id] = group_speed
        max_speed = max(max_speed, group_speed)

    pix_multiplier = {}
    for group_id in speed_dict:
        try:
            pix_multiplier[group_id] = max_speed / speed_dict[group_id]
        except ZeroDivisionError:
            pix_multiplier[group_id] = 0

    # Simulator clock tick will be the pix_unit / maximum speed
    sim_tick = pix_unit / max_speed

    return sim_tick, pix_unit, pix_multiplier
