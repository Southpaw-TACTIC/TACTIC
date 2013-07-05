###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#



__all__ = ['ChartData', 'ChartElement']

from pyasm.common import Environment, Common
from pyasm.web import Palette

# DEPRECATED


class ChartData(object):
    def __init__(my):
        my.data = {}
        my.data['elements'] = []

        palette = Palette.get()
        background = palette.color("background")
        color = palette.color("background3")

        my.data['bg_colour'] = background

        my.data['y_axis'] = {
            'grid-colour': color,
            'grid-visible': True,
            'colour': color,
        }
        my.data['x_axis'] = {
            'grid-colour': color,
            'grid-visible': False,
            'colour': color,
        }


    def add_element(my, element):
        my.data['elements'].append(element.get_data())


    def set_value(my, key, value, override=False):
        '''manual override for any value'''

        if override:
            my.data[key] = value
        else:
            my.data[key].update(value)




    def get_data(my):
        return my.data


class ChartElement(object):
    def __init__(my, chart_type):
        my.data = {}
        assert(chart_type)
        
        my.data['type'] = chart_type

        default = my._get_defaults(chart_type)
        for key, value in default.items():
            my.data[key] = value


    def _get_defaults(my, chart_type):
        if chart_type in ['pie','bar','bar_3d']:
            return {
                'gradient-fill': 'true',
                'colours':   ["#d01f3c","#356aa0","#C79810"],
                'alpha': 1.0,
                'animate':  [ { "type": "fade" }],
            }
        else:
            return {}


    def set_values(my, values):
        my.data['values'] = values


    def set_param(my, key, value):
        my.data[key] = value
        

    def get_data(my):
        return my.data


