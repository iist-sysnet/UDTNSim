""" Fuctions for parsing XML file in .osm format which is exported
    from www.openstreetmap.org
"""
import networkx
import geocalc
import guicalc
import time

## Function to reduce the map by splitting ways which form juctions
## with other ways at the middle of the road. Function also appends
## the length of each ways to the way_dict.

def normalize_map(node_dict, way_dict):
    
    dup_way_dict = {}    
    i = 0
    for way in way_dict:
        way_type = way_dict[way][1]
        
        way_nodes = way_dict[way][0] # Extracting the available nodes in the way
        if not way_nodes:
            continue

        # Traverse through the intermediate way to find out any junctions
        temp = [way_nodes[0]]
        way_distance = 0.0
        for j in xrange(1, len(way_nodes)):
            way_distance += geocalc.calculate_distance(\
                node_dict[way_nodes[j - 1]][0], node_dict[way_nodes[j]][0])

            # If number of ways connected to a point is > 1 indicates that
            # it is a junction. So the way is splitted.
            if len(node_dict[way_nodes[j]][2]) > 1 or j == len(way_nodes) - 1:
                temp.append(way_nodes[j])
                dup_way_dict[i] = [temp, way_type, way_distance]
                i += 1
                temp = [way_nodes[j]]
                way_distance = 0.0
            else:
                temp.append(way_nodes[j])

    # Updating node_dict and way_dict based on newly created ways
    dup_node_dict = {}
    for item in node_dict:
        dup_node_dict[item] = [node_dict[item][0], node_dict[item][1], []]
    
    for way in dup_way_dict:
        for item in dup_way_dict[way][0]:
            dup_node_dict[item][2].append(way)
    
    return dup_node_dict, dup_way_dict


## Function to extract way information from the openstreetmap file
def traverse_way(file_ptr, node_dict, way_id):
    """ Return the node information of a <way> tag """
    
    nodes_order = []
    way_classes = {'highway': ['v=\"unclassified\"', 'v=\"tertiary\"', \
                    'v=\"secondary\"', 'v=\"primary\"', 'v=\"primary_link\"', \
                    'v=\"trunk\"', 'v=\"trunk_link\"', \
                    'v=\"secondary_link\"', 'v=\"tertiary_link\"'], \
                   'twowheeler': ['v=\"footway\"', 'v=\"living_street\"', \
                                  'v=\"residential\"', 'v=\"service\"' ], \
                   'pedestrian': ['v=\"pedestrian\"', 'v=\"cycle_way\"'],
                   'railway': ['v=\"rail\"'], \
                   'residential': ['v=\"residential\"']\
                   }
                   
    way_type = None
    way_type_flag = False
    for line in file_ptr:
        if line.find("</way>") + 1:
            break
            
        elif line.find("<nd") + 1: # 'nd' tag is followed by a node id
            node_id = int(line.split("\"")[1])
            if node_id in node_dict:
                nodes_order.append(node_id)
                node_dict[node_id][2].append(way_id)

        # 'tag' tag gives the type of the way in their 'k' attribute
        elif (line.find("<tag") + 1) and (not way_type_flag):
            components = line.split()
            components[2] = components[2][: -2]
            if components[1].find('k=\"highway\"') + 1:
                if components[2] in way_classes['twowheeler']:
                    way_type = 'twowheeler'
                elif components[2] in way_classes['pedestrian']:
                    way_type = 'pedestrian'
                elif components[2] in way_classes['highway']:
                    way_type = 'highway'
                elif components[2] in way_classes['residential']:
                    way_type = 'residential'
                way_type_flag = True
            elif components[1].find('k=\"railway\"') + 1:
                if components[2] in way_classes['railway']:
                    way_type = 'railway'
                way_type_flag = True
                           
    return nodes_order, way_type, file_ptr
    

## Function to parse the openstreetmap file and create two dictionaries
## with the following format. (Here 'node' represents a geographical point).
## 1. node_dict = {node_id: [(lon, lat), (y, x), [way_ids]]
## (way_ids represent the ways connected to that particular node)
## 2. way_dict = {way_id: [[node_ids], type, length]
## (node_ids represent the nodes which make the way)
def parse_osm(osmfile, height, width):

    """ Main function for parsing the .osm file. It return two dictionaries in
        the form.
        1. node_dict = {node_id: [(lat, lon), (y, x), [way_ids]]}
        2. way_dict = {way_id: [[node_ids], 'way_type']
    """
    file_ptr = open(osmfile, "r")
    
    xml_header = file_ptr.readline()
    if xml_header.find("<?xml") < 0:
        return "Error: Invalid xml format"
        
    osm_header = file_ptr.readline()
    if osm_header.find("<osm") < 0:
        return "Error: Invalid osm format"

    bounds_header = file_ptr.readline()
    if bounds_header.find("<bounds") < 0:
        return "Error: No bounds defined"

    # Read the bounds of the geographical region in latitude and longitudes
    # bounds = [lon1, lat1, lon2, lat2]
    bounds = []
    components = bounds_header.split()
    for i in range(1, 5):
        comps = components[i].split('"')
        # bounds.append(float(components[i][8:17]))
        bounds.append(float(comps[1]))
        

    gui_params = {}
    gui_params['trans_factor'] = guicalc.translation_factor(bounds)
    gui_params['scale_factor'] = guicalc.scale_factor(bounds, height, width)

    # Initializing the dictionaries for storing node and way information
    node_dict = {}
    way_dict = {}
    for line in file_ptr:
        if line.find("<node") + 1: # Represents a node tag
            components = line.split()

            for i in range(len(components)):
                if components[i].find("lat=") + 1: # Reading latitude
                    lat_index = i
            for i in range(len(components)):
                if components[i].find("lon=") + 1: # Reading longitude
                    lon_index = i
            
            node_id = int(components[1].split("\"")[1])
            lat = float(components[lat_index].split("\"")[1])
            lon = float(components[lon_index].split("\"")[1])
            
            if lat >= bounds[0] and lat <= bounds[2] and lon >= bounds[1] \
               and lon <= bounds[3]:
                geo_coord = (lat, lon)
                cart_coord = geocalc.geo_to_cart(geo_coord, gui_params)
                node_dict[node_id] = [geo_coord, cart_coord, []]                

        # Detected a 'way' tag. The function 'traverse_way' is called to
        # retrieve the way information
        elif line.find("<way") + 1: 
            components = line.split()
            way_id = int(components[1].split("\"")[1])
            node_order, way_type, file_ptr = traverse_way(file_ptr, node_dict, way_id)
            if way_type:
                way_dict[way_id] = [node_order, way_type]
        else:
            continue

    file_ptr.close()

    node_dict, way_dict = normalize_map(node_dict, way_dict)

    return node_dict, way_dict, bounds, gui_params
        
