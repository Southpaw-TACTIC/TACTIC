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

__all__ = ['OverlayStatsWdg']

from pyasm.common import SetupException
from pyasm.search import *
from pyasm.web import *
from pyasm.biz import *

from tactic.ui.common import BaseTableElementWdg




class OverlayStatsWdg(BaseTableElementWdg):
    '''Display stats as an overlay on other widgets like the tile in TileLayoutWdg'''
    
    ARGS_KEYS = {

        "expr": {
            'description': "expression to retrieve a list of figures to display",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Display'
        },
        "bg_color": {
            'description': "background color for each of the stats to display",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Display'
        },
        "sobject": {
            'description': "input sobject for the expr",
            'type': 'TextWdg',
            'order': 3,
            'category': 'internal'
        }



    }

    def get_display(self):
        expr = self.kwargs.get('expr')
        sobject = self.kwargs.get('sobject')
        bg_color = self.kwargs.get('bg_color')
        bg_colors = bg_color.split(',')
        bg_colors = [ x.strip() for x in bg_colors ]


        js_exprs = []
        rtn = Search.eval(expr, sobjects=[sobject])
        if isinstance(rtn, dict):
            stats = rtn.get('label')
            js_exprs = rtn.get('click_expr')
            if len(js_exprs) != len(stats):
                raise SetupException('the number of stats and js_expr returned from the PYTHON script must be the same.')
        else:
            stats = rtn
        if len(bg_color) < len(stats):
            raise SetupException('bg_color provided should not be less than the list returned from expression')
        
        stat_div = DivWdg()
        stat_div.add_styles('bottom: 4px; right: 5px; position: absolute')
        for i, stat in enumerate(stats): 
            span = SpanWdg(css='badge')
            span.add_style('margin-left','2px')
            span.add_style('background', bg_colors[i])
            span.add_style('box-shadow','1px 1px 2px #AAAAAA')
            span.add(stat)
            if js_exprs:
                # change mouse pointer to hand
                span.add_class('hand')

                js_expr = js_exprs[i]
                parser = ExpressionParser() 
                related = parser.get_plain_related_types(js_expr)
                search_type = related[-1]

                search_key = sobject.get_search_key()
                search_code = sobject.get_name()
                if len(search_code) > 13:
                    search_code = '%s..'%search_code[0:12]
                span.add_behavior({'type': 'click_up',
                'js_expr' : js_expr,
                'search_type': search_type,
                'search_key': search_key,
                'search_code': search_code,
                'cbjs_action': '''var kwargs = {
                    expression: bvr.js_expr,
                    search_type: bvr.search_type,
                    search_key: bvr.search_key
                    };
                spt.tab.set_tab_top_from_child(bvr.src_el);    
                spt.tab.add_new(bvr.search_key  + '- %d', bvr.search_code + '- %d', 'tactic.ui.panel.TableLayoutWdg', kwargs);
                '''% (i+1, i+1)
                })

            stat_div.add(span)

        return stat_div




