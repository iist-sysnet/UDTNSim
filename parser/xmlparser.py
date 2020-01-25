from xml.etree import cElementTree as ET


def parse_node(tag_info, node_dict, bounds):
    root = ET.fromstring(tag_info)
    node_id = int(root.attrib['id'])
    lat = float(root.attrib['lat'])
    lon = float(root.attrib['lon'])
    node_info = {'cord': (lat, lon)}

    if (bounds['minlat'] <= lat <= bounds['maxlat']) and (bounds['minlon'] <= lon <= bounds['maxlon']):
        for child in root:
            tag = child.attrib['k']
            if tag in ['shop', 'cuisine', 'leisure']:
                node_info[tag] = child.attrib['v']

        node_dict[node_id] = node_info

    return


def parse_way(tag_info, node_dict, way_dict):
    root = ET.fromstring(tag_info)
    way_id = int(root.attrib['id'])
    way_info = {'nodes': []}
    for child in root:
        if child.tag == 'nd':
            node_id = int(child.attrib['ref'])
            if node_id in node_dict:
                way_info['nodes'].append(int(child.attrib['ref']))
            else:
                return
        elif child.tag == 'tag':
            tag = child.attrib['k']
            if tag in ['highway', 'name', 'landuse']:
                way_info[tag] = child.attrib['v']
    way_dict[way_id] = way_info


def normalize_way_dict(node_dict, way_dict):
    node_ways = {}
    for node in node_dict:
        node_ways[node] = set([])

    for way_id in way_dict:
        for node in way_dict[way_id]['nodes']:
            node_ways[node].add(way_id)

    new_way_dict = {}
    new_way_count = 0
    for way_id in way_dict:
        nodes = way_dict[way_id]['nodes']
        u = nodes[0]
        new_way_dict[new_way_count] = way_dict[way_id].copy()
        new_way_dict[new_way_count]['nodes'] = [u]
        for v in nodes[1:]:
            new_way_dict[new_way_count]['nodes'].append(v)
            if len(node_ways[v]) > 1:
                new_way_count += 1
                new_way_dict[new_way_count] = way_dict[way_id].copy()
                new_way_dict[new_way_count]['nodes'] = [v]
            u = v

    return new_way_dict


def parse_osm(filename):
    fp = open(filename)
    node_dict = {}
    way_dict = {}
    fp = open(filename, encoding='UTF-8')
    tag_info = ''
    in_tag_flag = False
    ready_to_parse = False
    for line in fp:
        if '<bounds' in line:
            root = ET.fromstring(line)
            bounds = root.attrib
            for key in bounds:
                bounds[key] = float(bounds[key])
        elif '<node' in line or '<way' in line:
            tag_info = line
            in_tag_flag = True
            ready_to_parse = False
            if '/>' in line:
                in_tag_flag = False
                ready_to_parse = True
        elif '</node>' in line or '</way>' in line:
            tag_info += line
            in_tag_flag = False
            ready_to_parse = True
        elif in_tag_flag is True:
            tag_info += line
        else:
            pass

        if ready_to_parse:
            if '<node' in tag_info:
                parse_node(tag_info, node_dict, bounds)
            elif '<way' in tag_info:
                parse_way(tag_info, node_dict, way_dict)
            ready_to_parse = False
    fp.close()

    way_dict = normalize_way_dict(node_dict, way_dict)

    return node_dict, way_dict, bounds
