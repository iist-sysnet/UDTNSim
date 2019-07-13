""" Class for reading the environment settings for the DTN environment.
    It contains the attributes for each of the group of nodes
    (mobile/stationary)."""
from __future__ import division
import textformat


class Settings:
    """ ENVIRONMENT SETTINGS """

    envt_params = {}
    hosts_group_params = {}

    txt_format_obj = textformat.Colors()

    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.envt = {}
        self.groups = {}

        # Read the environment parameters and their required type
        file_ptr = open('parser/envt_params.in', 'r')
        for line in file_ptr:
            comps = line.split(':')
            Settings.envt_params[comps[0]] = comps[1].strip()
        file_ptr.close()

        # Read the group parameters and their required type
        file_ptr = open('parser/group_params.in', 'r')
        for line in file_ptr:
            comps = line.split(':')
            Settings.hosts_group_params[comps[0]] = comps[1].strip()
        file_ptr.close()

    def print_error(self, line_no, error_msg):
        print ('Error: Line No. %d: %s' % (line_no, error_msg))
        return

    def type_check(self, attribute, value, in_group):
        """ Checking the type of an environment attribute. """

        if in_group:
            required_type = Settings.hosts_group_params[attribute]
        else:
            required_type = Settings.envt_params[attribute]

        # Checking for values given for parameters are valid or not
        if required_type == 'int':
            try:
                val = int(value)
                return True, val
            except ValueError:
                return False, None

        elif required_type == 'float':
            try:
                val = float(value)
                return True, val
            except ValueError:
                return False, None

        elif required_type == 'bool':
            if value == 'True':
                return True, True
            elif value == 'False':
                return True, False
            else:
                return False, None

        elif required_type == 'dict':
            value_str = value[1: -1]
            comps = value_str.split(',')
            local_dict = {}
            for comp in comps:
                key_val = comp.split(':')
                try:
                    local_dict[key_val[0]] = key_val[1]
                except ValueError:
                    return False, None
            return True, local_dict

        elif required_type == 'list':
            if value == 'None':
                return True, []
            if not value.startswith('[') or not value.endswith(']'):
                return False, None
            val_str = value[1: -1]
            val_str = val_str.split(',')
            temp = []
            for val in val_str:
                try:
                    temp.append(val)
                except ValueError:
                    return False, None
            return True, temp
        else:
            return True, value

    # Function for reading the 'settings.dtn' file
    def read_settings(self):
        """ Start and read all the attributes from settings file """

        self.txt_format_obj.print_msg('BLUE', 'Reading settings.')
        file_ptr = open(self.settings_file, 'r')
        in_group = False
        line_no = 0
        group_count = 0

        while True:
            line = file_ptr.readline()
            if not line:
                break
            line_no += 1
            line = line.replace(' ', '')
            line = line.strip('\n')

            if line.startswith('#'):  # Discarding comments
                continue

            # Environment specific parameter
            elif line.find('=') + 1 and not in_group:
                components = line.split('=')
                if len(components) < 2:
                    self.print_error(line_no, 'Attribute or value missing.')
                    return False
                elif components[0] not in Settings.envt_params:
                    self.print_error(line_no, 'Invalid attribute %s.' % (components[0]))
                    return False
                elif components[0] == 'Path_Types':
                    list_str = components[1]
                    if components[1][-1] != ']':
                        list_line = file_ptr.readline()
                        print (list_line)
                        while list_line and list_line[-2] != ']' and not (list_line.find(':') + 1) and not (list_line.find('[') + 1):
                            list_str += list_line
                            list_line = file_ptr.readline()
                            print (list_line)
                        if list_line[-2] == ']':
                            list_str += list_line
                            list_str = list_str.replace(' ', '')
                            list_str = list_str.replace('\n', '')
                            components[1] = list_str
                        else:
                            return False

                status, value = self.type_check(components[0], components[1],
                                                in_group)
                if status:
                    self.envt[components[0]] = value
                else:
                    self.print_error(line_no, 'Invalid attribute type - %s' % (components[1]))
                    return False

            # Group specific parameter
            elif line.find('=') + 1 and in_group:
                components = line.split('=')
                if len(components) < 2:
                    self.print_error(line_no, 'Attribute or value missing.')
                    return False
                elif components[0] not in Settings.hosts_group_params:
                    self.print_error(line_no, 'Invalid node attribute %s.' % (components[1]))
                    return False
                elif components[0] == 'TX_Range':
                    unit = components[1][-1]
                    if unit not in ['m', 'M', 'k', 'K']:
                        self.print_error(line_no, 'Invalid unit for %s.' % (components[0]))
                        return False
                    else:
                        if unit in ['m', 'M']:
                            components[1] = float(components[1][:-1]) / 1000
                        else:
                            components[1] = float(components[1][: -1])
                elif components[0] == 'Buffer_Size':
                    unit = components[1][-1]
                    if unit not in ['K', 'M', 'G']:
                        self.print_error(line_no, 'Invalid unit for %s.' % (components[1]))
                        return False
                    else:
                        components[1] = components[1][: -1]
                elif components[0] == 'Group_ID':
                    group_ID = components[1]
                    continue

                status, value = self.type_check(components[0],
                                                components[1], in_group)
                if status:
                    if components[0] == 'Paths':
                        for val in value:
                            if val not in self.envt['Path_Types'].values():
                                self.print_error(line_no, 'Invalid path IDs')
                                return False

                if status:
                    group_attrs[components[0]] = value
                else:
                    self.print_error(line_no, 'Invalid attribute type, %s.'\
                                     % (components[1]))
                    return False

            # Starting of '{' means starting of group parameter description
            elif line == '{':
                in_group = True
                group_attrs = {}

            # Ending of group paramter description
            elif line == '}':
                in_group = False
                self.groups[group_ID] = group_attrs
                group_count += 1

            elif line == '':
                continue

            else:
                self.print_error(line_no, 'Invalid text.')
                return False

        if group_count < self.envt['No_of_Hosts_Groups']:
            self.print_error(line_no, 'No. of hosts group defined is less than specified.')
            return False

        self.txt_format_obj.print_msg('GREEN', 'Done')

        return True
