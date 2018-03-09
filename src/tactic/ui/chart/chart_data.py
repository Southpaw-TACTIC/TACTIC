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
    def __init__(self):
        self.data = {}
        self.data['elements'] = []

        palette = Palette.get()
        background = palette.color("background")
        color = palette.color("background3")

        self.data['bg_colour'] = background

        self.data['y_axis'] = {
            'grid-colour': color,
            'grid-visible': True,
            'colour': color,
        }
        self.data['x_axis'] = {
            'grid-colour': color,
            'grid-visible': False,
            'colour': color,
        }


    def add_element(self, element):
        self.data['elements'].append(element.get_data())


    def set_value(self, key, value, override=False):
        '''manual override for any value'''

        if override:
            self.data[key] = value
        else:
            self.data[key].update(value)




    def get_data(self):
        return self.data


class ChartElement(object):
    def __init__(self, chart_type):
        self.data = {}
        assert(chart_type)
        
        self.data['type'] = chart_type

        default = self._get_defaults(chart_type)
        for key, value in default.items():
            self.data[key] = value


    def _get_defaults(self, chart_type):
        if chart_type in ['pie','bar','bar_3d']:
            return {
                'gradient-fill': 'true',
                'colours':   ["#d01f3c","#356aa0","#C79810"],
                'alpha': 1.0,
                'animate':  [ { "type": "fade" }],
            }
        else:
            return {}


    def set_values(self, values):
        self.data['values'] = values


    def set_param(self, key, value):
        self.data[key] = value
        

    def get_data(self):
        return self.data


