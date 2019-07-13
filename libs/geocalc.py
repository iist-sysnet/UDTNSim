import math


# Function to calculate the geographical distance between two points
def calculate_distance(coord1, coord2):
    """ Return the distance between two geographical points. """

    deg2rad = math.pi / 180
    phi1 = (90.0 - coord1[0]) * deg2rad
    phi2 = (90.0 - coord2[0]) * deg2rad

    th1 = coord1[1] * deg2rad
    th2 = coord2[1] * deg2rad

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(th1 - th2) +
           math.cos(phi1) * math.cos(phi2))

    if cos > 1:
        cos = 1

    distance = math.acos(cos) * 6373

    return distance


# Function to convert a geographical coordinate to the Cartesian
# coordinate for the simulator GUI
def geo_to_cart(geo, gui_params):
    """ Return the cartesian coordinate corresponding to a geographical
        coordinate. """

    tf = gui_params['trans_factor']
    sf = gui_params['scale_factor']

    lat_cart = (geo[0] + tf[0]) * sf[0] + 10
    lon_cart = (geo[1] + tf[1]) * sf[1] + 30

    return (lat_cart, lon_cart)


# Function to convert a cartesian coordinate in the simulator GUI
# to the corresponding geographical coordinate
def cart_to_geo(cart, gui_params):
    """ Return geographical coordinate corresponding to a cartesian
        coordinate. """

    tf = gui_params['trans_factor']
    sf = gui_params['scale_factor']

    lat_geo = ((cart[0] - 10) / sf[0]) - tf[0]
    lon_geo = ((cart[1] - 30) / sf[1]) - tf[1]

    return (lat_geo, lon_geo)
