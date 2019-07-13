''' Class with text formatting capabilities '''


class Colors:
    color_dict = {'BOLD': 1, 'ITALIC': 3, 'UNDERLINE': 4, 'BLINK': 5,
                  'BGWHITE': 7, 'DARKRED': 31, 'DARKGREEN': 32,
                  'DARKORANGE': 33, 'DARKBLUE': 34, 'DARKPINK': 35,
                  'DARKSKYBLUE': 36, 'BGRED': 41, 'BGGREEN': 42,
                  'BGORANGE': 43, 'BGBLUE': 44, 'BGPINK': 45,
                  'BGSKYBLUE': 46, 'BLACK': 90, 'RED': 91,
                  'GREEN': 92, 'YELLOW': 93, 'BLUE': 94,
                  'PINK': 95, 'SKYBLUE': 96, 'WHITE': 97,
                  'END': '\033[0m'
                  }

    def print_msg(self, color, msg):
        print ('\033[' +  str(Colors.color_dict[color]) + 'm' + msg + \
               Colors.color_dict['END'])

        return
