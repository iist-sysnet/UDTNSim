""" Module for Map related functions """
import math


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
