###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['Palette']

from pyasm.common import Container, Config, Common
from pyasm.search import Search

import colorsys, types

class Palette(object):


    # default color palette
    DARK = {
    'color':        '#CCC',         # main font color
    'color2':       '#BBB',         # secondary font color
    'color3':       '#222222',      # tertiary font color
    'background':   '#444444',      # main background color
    'background2':  '#2F2F2F',      # secondary background color
    'background3':  '#888888',      # tertiary background color
    'border':       '#737b79',      # main border color
    'theme':        'dark',

    'table_border': '#494949',
    'side_bar_title_color': '#EEEEEE',

    'shadow':       'rgba(0,0,0,0.8)',

    #'md_primary_dark': '#c7c7c7', 
    #'md_primary':   '#fafafa',
    #'md_primary_light': '#ffffff',
    #'md_secondary_dark': '#00675b',
    #'md_secondary': '#009688',
    #'md_secondary_light': '#52c7b8'

 
    "md_primary_dark": "#000a12",
    "md_primary": "#263238",
    "md_primary_light": "#4f5b62",
    "md_secondary_dark": "#00628b",
    "md_secondary": "#1d90bb",
    "md_secondary_light": "#61c0ee"
    
    }
    DEFAULT = DARK


    BLACK = {
    'color':        '#AAA',         # main font color
    'color2':       '#AAA',         # secondary font color
    'color3':       '#AAA',      # tertiary font color
    'background':   '#101010',      # main background color
    'background2':  '#100000',      # secondary background color
    'background3':  '#000000',      # tertiary background color
    'border':       '#202020',      # main border color
    'shadow':       '#202020',      # main shadow color
    'theme':        'dark',

    'table_border': '#202020',
    'side_bar_title': '#3C76C2',
    }


    AQUA = {
    'color':        '#000',         # main font color
    'color2':       '#333',         # secondary font color
    'color3':       '#333',         # tertiary font color
    'background':   '#F5F5F6',      # main background color
    'background2':  '#E1E2E1',      # secondary background color
    'background3':  '#D1D7E2',      # tertiary background color
    'border':       '#BBB',         # main border color

    'side_bar_title': '#3C76C2',
    'side_bar_title_color': '#000000',
    #'tab_background': '#3C76C2',
    'table_border': '#E0E0E0',
    'theme':        'default',
    'shadow':       'rgba(0,0,0,0.1)',
    'md_primary_dark': '#c7c7c7', 
    'md_primary': '#fafafa',
    'md_primary_light': '#ffffff',
    'md_secondary_dark': '#00675b',
    'md_secondary': '#009688',
    'md_secondary_light': '#52c7b8'
    }
    LIGHT = AQUA


    # silver theme
    SILVER = {
    'color':        '#000',         # main font color
    'color2':       '#333',         # secondary font color
    'color3':       '#333',         # tertiary font color
    'background':   '#DDDDDD',      # main background color
    'background2':  '#777777',      # secondary background color
    'background3':  '#999999',      # tertiary background color
    'border':       '#888888',         # main border color
    'table_border': '#DDD',
    'theme':        'default',
    'shadow':       'rgba(0,0,0,0.6)',

    'side_bar_title': '#3C76C2',
    }

    # silver theme
    BRIGHT = {
    'color':        '#000',         # main font color
    'color2':       '#333',         # secondary font color
    'color3':       '#333',         # tertiary font color
    'background':   '#FFFFFF',      # main background color
    'background2':  '#AAAAAA',      # secondary background color
    'background3':  '#EEEEEE',      # tertiary background color
    'border':       '#BBBBBB',         # main border color
    'table_border': '#E0E0E0',
    'theme':        'default',
    'shadow':       'rgba(0,0,0,0.6)',

    'side_bar_title': '#3C76C2',
    }


    # bon noche theme
    BON_NOCHE = {
    'color':        '#FFF',         # main font color
    'color2':       '#FFF',         # secondary font color
    'color3':       '#FFF',         # tertiary font color
    'background':   '#060719',      # main background color
    'background2':  '#4C1B2F',         # secondary background color
    'background3':  '#9E332E',      # tertiary background color
    'border':       '#444',         # main border color
    'table_border': '#060719',
    'theme': 'dark'
    }



    # origami theme
    ORIGAMI = {
    'color':        '#000',         # main font color
    'color2':       '#FFF',         # secondary font color
    'color3':       '#000',         # tertiary font color
    'background':   '#E8FAC8',      # main background color
    'background2':  '#8C8015',         # secondary background color
    'background3':  '#BAB966',      # tertiary background color
    'border':       '#888888',         # main border color
    'table_border': '#E8FAC8',
    'shadow':       'rgba(0,0,0,0.6)',
    'theme': 'default'
    }



    MMS = {
    'color':        '#FFF',         # main font color
    'color2':       '#000',         # secondary font color
    'color3':       '#000',         # tertiary font color
    'background':   '#00539F',      # main background color
    'background2':  '#CCCCCC',      # secondary background color
    'background3':  '#AAAAAA',      # tertiary background color
    'border':       '#999999',         # main border color
    'table_border': '#00539F',
    'theme': 'default'
    }



    AVIATOR = {
    'color':        '#000000',         # main font color
    'color2':       '#FFFFFF',         # secondary font color
    'color3':       '#FFFFFF',         # tertiary font color
    'background':   '#E6D595',      # main background color
    'background2':  '#1A9481',      # secondary background color
    'background3':  '#003D5c',      # tertiary background color
    'border':       '#666666',         # main border color
    'table_border': '#E6D595',
    'theme': 'dark'
    }





    #COLORS = DEFAULT
    #COLORS = SILVER
    #COLORS = ORIGAMI
    COLORS = AQUA
    #COLORS = BRIGHT
    #COLORS = BON_NOCHE
    #COLORS = MMS
    #COLORS = AVIATOR


    TABLE = {
    'table_hilite':         '#F00',
    'table_select':         '#FF0',
    'table_changed':        '#FFF',
    'header_background':    '#FFF'
    }



    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.colors = self.kwargs.get("colors")
        if not self.colors:
            self._init_palette()

        if not self.colors:
            self.colors = self.COLORS

        # make sure all of the colors are defined
        for name, value in self.DEFAULT.items():
            # make a special provision for theme!
            if name == 'theme':
                continue

            if not self.colors.get(name):
                self.colors[name] = value


    def _init_palette(self):
        value = self.kwargs.get("palette")
        if value:
            self.set_palette(value)
            if self.colors:
                return

        from pyasm.biz import ProjectSetting
        value = ProjectSetting.get_value_by_key("palette")
        if value:
            self.set_palette(value)
            if self.colors:
                return

        value = ProjectSetting.get_json_value_by_key("palette/colors")
        if value:
            self.set_palette(palette=None, colors=value)
            if self.colors:
                return

        
        from pyasm.biz import Project
        project = Project.get(no_exception=True)
        if project:
            value = project.get_value("palette")
            self.set_palette(value)
            if self.colors:
                return

        # otherwise look at the user
        from pyasm.biz import PrefSetting
        value = PrefSetting.get_value_by_key("palette")
        if value:
            self.set_palette(value)
            if self.colors:
                return
        
        value = Config.get_value("look", "palette")
        if value:
            self.set_palette(value)
            if self.colors:
                return
        

        value = self.COLORS
        if value:
            self.set_palette(palette=None, colors=value)
            return



    def set_palette(self, palette=None, colors=None):
        
        if not palette and not colors:
            return 

        try:
            if palette:
                value = palette
                self.colors = eval(value)
            elif colors:
                self.colors = colors

            # make sure all of the colors are defined
            for name, value in self.DEFAULT.items():
                # make a special provision for theme!
                if name == 'theme':
                    continue

                if not self.colors.get(name):
                    self.colors[name] = value

        except Exception as e:
            try:
                value = value.upper()
                value = value.replace(" ", "_")
                self.colors = eval("self.%s" % value)
            except:
                print("WARNING: palette [%s] does not exist.  Using default" % value)
                self.colors = self.DEFAULT
                self.colors = eval("self.%s" % value)


    def get_theme(self):
        theme = self.colors.get("theme")
        if not theme:
            theme = "default"
        return theme


    def get_keys(self):
        return self.colors.keys()


    def get_colors(self):
        return self.colors


    def color(self, category, modifier=0, default=None):

        if not category:
            category = 'background'


        # make default adjustments
        if category.startswith("#"):
            color = category
            category = "color"
        else:
            color = self.colors.get(category)

        if not color:
            color = self.colors.get(default)
        if not color:
            color = category


        if category == 'background2' and not color:
            category = 'background'
            modifier += 10
            color = self.colors.get(category)
        if category == 'color2' and not color:
            category = 'color'
            modifier += 10
            color = self.colors.get(category)

        return Common.modify_color(color, modifier)




    def modify_color(color, modifier):
        return Common.modify_color(color, modifier)
    modify_color = staticmethod(modify_color)

    """
        if not modifier:
            return color
            
        if not color:
            return None

        color = color.replace("#", '')

        if len(color) == 3:
            first = "%s%s" % (color[0], color[0])
            second = "%s%s" % (color[1], color[1])
            third = "%s%s" % (color[2], color[2])
        elif len(color) == 6:
            first = "%s" % color[0:2]
            second = "%s" % color[2:4]
            third = "%s" % color[4:6]

        first =  float(int(first, 16) ) / 256
        second = float(int(second, 16) ) / 256
        third =  float(int(third, 16) ) / 256

        if type(modifier) == types.ListType:
            rgb = []
            rgb.append( 0.01*modifier[0] + first )
            rgb.append( 0.01*modifier[1] + second )
            rgb.append( 0.01*modifier[2] + third )
        else:

            hsv = colorsys.rgb_to_hsv(first, second, third)
            value = 0.01*modifier + hsv[2]
            if value < 0:
                value = 0
            if value > 1:
                value = 1
            hsv = (hsv[0], hsv[1], value )
            rgb = colorsys.hsv_to_rgb(*hsv)


        first =  hex(int(rgb[0]*256))[2:]
        if len(first) == 1:
            first = "0%s" % first
        second = hex(int(rgb[1]*256))[2:]
        if len(second) == 1:
            second = "0%s" % second
        third =  hex(int(rgb[2]*256))[2:]
        if len(third) == 1:
            third = "0%s" % third

        if len(first) == 3:
            first = "FF"
        if len(second) == 3:
            second = "FF"
        if len(third) == 3:
            third = "FF"

        color = "#%s%s%s" % (first, second, third)
        return color

    modify_color = staticmethod(modify_color)

    """


    def gradient(self, palette_key, modifier=0, range=-20, reverse=False, default=None):

        if modifier == None:
            modifier = 0
        if range == None:
            range = -20

        from .web_container import WebContainer
        web = WebContainer.get_web()
        palette = Palette.get()
        if web.is_IE():
            color = self.color(palette_key, (modifier+range)/2, default=default)
            return color
        else: 
            if not reverse:
                color1 = self.color(palette_key, modifier, default=default)
                color2 = self.color(palette_key, modifier+range, default=default)
            else:
                color2 = self.color(palette_key, modifier, default=default)
                color1 = self.color(palette_key, modifier+range, default=default)


            if web.get_browser() == 'Mozilla':
                return "-moz-linear-gradient(top, %s, %s)" % (color1, color2)
            else:
                return "-webkit-gradient(linear, 0%% 0%%, 0%% 100%%, from(%s), to(%s))" % (color1, color2)



    def push_palette(cls, palette):
        palettes = Container.get("Palette:palettes")
        if palettes == None:
            palettes = []
            Container.put("Palette:palettes", palettes)
        palette = Palette(palette=palette)
        palettes.append(palette)
    push_palette = classmethod(push_palette)
 
    def pop_palette(cls):
        palettes = Container.get("Palette:palettes")
        if palettes == None:
            palettes = []
            Container.put("Palette:palettes", palettes)
        if len(palettes) == 0:
            return palettes[0]
        return palettes.pop()
    pop_palette = classmethod(pop_palette)
  
    def num_palettes(cls):
        palettes = Container.get("Palette:palettes")
        if palettes == None:
            palettes = []
            Container.put("Palette:palettes", palettes)
        return len(palettes)
    num_palettes = classmethod(num_palettes)
        
       
       
       

    def get(cls):
        palettes = Container.get("Palette:palettes")
        if palettes == None:
            palettes = []
            Container.put("Palette:palettes", palettes)
        if not palettes:
            palette = Palette()
            palettes.append(palette)
        else:
            palette = palettes[-1]
        return palette
    get = classmethod(get)
        
    def set(cls, palette):
        Container.put("Palette:palette", palette)
    set = classmethod(set)



