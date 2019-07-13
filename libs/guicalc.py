''' Functions for calculations for GUI '''
from __future__ import division


# Function to find out the translation factor for the GUI from
# the lower and upper bound of location's geographical coordinates
def translation_factor(bounds):
    """ Return the translation factor for making the geographical
        co-ordinate to cartesian coordinate."""

    lon_trans = -bounds['minlon']
    lat_trans = -bounds['minlat']

    return (lat_trans, lon_trans)


# Function to find out the scale factor for the GUI. It depends on
# the geographical bound and the dimension of GUI
def scale_factor(bounds, height, width):
    """ Return the scale factor for the map. Height and width of
        x, y canvas should be given as the parameters. """

    tf = translation_factor(bounds)

    lat_min = bounds['minlat'] + tf[0]
    lon_min = bounds['minlon'] + tf[1]

    lat_max = bounds['maxlat'] + tf[0]
    lon_max = bounds['maxlon'] + tf[1]

    alpha = (height - 20) / (lat_max - lat_min)
    beta = (width - 20) / (lon_max - lon_min)

    return (alpha, beta)


# Function to compute delay points. One pixel corresponds to a geographical
# distance which is calculated as 'pix_unit'. The distance that the
# movement object travel in that distance / pix_unit will give the number
# of dummy movement points that should be added at junctions. The number
# is inversely proportional to the speed of the movement object. For each
# movement object the number is multiplied with its corresponding multiplier.
def compute_delay_pixels(global_params):
    delay_pixels = {}
    groups = global_params.envt_params.groups

    for group_id in groups:
        try:
            # Delay time in hours
            delay_time = groups[group_id]['Junction_Delay'] / 3600

            # Calculating the corresponding distance travelled by an object in
            # the group
            delay_dist = delay_time * groups[group_id]['Speed']
        except KeyError:
            # Occur for stationary objects (Speed and Junction_Delay will not
            # be there
            delay_pixels[group_id] = 0
            continue

        # Computing number of delay points required for the group
        pixel_multiplier = global_params.gui_params['pix_multiplier'][group_id]
        no_of_pixels = int(round(delay_dist / global_params.gui_params['pix_unit']) * pixel_multiplier)
        delay_pixels[group_id] = no_of_pixels

    return delay_pixels
