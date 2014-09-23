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
    DEFAULT = {
    'color':        '#DDD',         # main font color
    'color2':       '#AAA',         # secondary font color
    'color3':       '#222222',      # tertiary font color
    'background':   '#444444',      # main background color
    'background2':  '#2F2F2F',      # secondary background color
    'background3':  '#777777',      # tertiary background color
    'border':       '#5a5e5d',      # main border color
    'shadow':       '#000000',      # main shadow color
    'theme':        'dark',

    'table_border': '#494949',
    'side_bar_title': '#3C76C2',
    }
    DARK = DEFAULT


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
    'background':   '#FFFFFF',      # main background color
    'background2':  '#BBBBBB',      # secondary background color
    'background3':  '#D1D7E2',      # tertiary background color
    'border':       '#AAA',       # main border color

    'side_bar_title': '#3C76C2',
    'side_bar_title_color': '#FFF',
    'tab_background': '#3C76C2',
    'table_border': '#FFF',
    'theme':        'default',
    'shadow':       'rgba(0,0,0,0.4)',
    }




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



    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.colors = my.kwargs.get("colors")
        palette = my.kwargs.get("palette")
        if palette:
            my.set_palette(palette)
        else:
            # look at the project
            from pyasm.biz import Project
            project = Project.get()
            if project:
                value = project.get_value("palette")
                my.set_palette(value)


        # otherwise look at the user
        if not my.colors:
            from pyasm.biz import PrefSetting
            value = PrefSetting.get_value_by_key("palette")
            my.set_palette(value)


        # look in the config
        if not my.colors:
            value = Config.get_value("look", "palette")
            my.set_palette(value)


        if not my.colors:
            my.colors = my.COLORS

        # make sure all of the colors are defined
        for name, value in my.DEFAULT.items():
            # make a special provision for theme!
            if name == 'theme':
                continue

            if not my.colors.get(name):
                my.colors[name] = value


    def set_palette(my, palette):
        value = palette
        if not value:
            return

        try:
            my.colors = eval(value)

            # make sure all of the colors are defined
            for name, value in my.DEFAULT.items():
                # make a special provision for theme!
                if name == 'theme':
                    continue

                if not my.colors.get(name):
                    my.colors[name] = value

        except:
            try:
                value = value.upper()
                value = value.replace(" ", "_")
                my.colors = eval("my.%s" % value)
            except:
                print "WARNING: palette [%s] does not exist.  Using default" % value

               

    def get_theme(my):
        theme = my.colors.get("theme")
        if not theme:
            theme = "default"
        return theme


    def get_keys(my):
        return my.colors.keys()


    def get_colors(my):
        return my.colors


    def color(my, category, modifier=0, default=None):

        if not category:
            category = 'background'


        # make default adjustments
        if category.startswith("#"):
            color = category
            category = "color"
        else:
            color = my.colors.get(category)

        if not color:
            color = my.colors.get(default)
        if not color:
            color = category


        if category == 'background2' and not color:
            category = 'background'
            modifier += 10
            color = my.colors.get(category)
        if category == 'color2' and not color:
            category = 'color'
            modifier += 10
            color = my.colors.get(category)

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


    def gradient(my, palette_key, modifier=0, range=-20, reverse=False, default=None):

        if modifier == None:
            modifier = 0
        if range == None:
            range = -20

        from web_container import WebContainer
        web = WebContainer.get_web()
        palette = Palette.get()
        if web.is_IE():
            color = my.color(palette_key, (modifier+range)/2, default=default)
            return color
        else: 
            if not reverse:
                color1 = my.color(palette_key, modifier, default=default)
                color2 = my.color(palette_key, modifier+range, default=default)
            else:
                color2 = my.color(palette_key, modifier, default=default)
                color1 = my.color(palette_key, modifier+range, default=default)


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


