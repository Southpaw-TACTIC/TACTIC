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

__all__ = ['SObjectLoadWdg']

from pyasm.common import Common, Container
from pyasm.biz import Pipeline, Project
from pyasm.web import Widget, DivWdg, SpanWdg, WebContainer
from pyasm.widget import HiddenWdg

from pyasm.prod.web import ProcessFilterWdg


from load_options_wdg import LoadOptionsWdg, AnimLoadOptionsWdg, ShotLoadOptionsWdg

from tactic.ui.panel import TableLayoutWdg
from tactic.ui.common import BaseRefreshWdg


class SObjectLoadWdg(BaseRefreshWdg):

    def get_display(my):

        widget = Widget()
        my.search_type = my.options.get("search_type")
        if not my.search_type:
            my.search_type = my.kwargs.get("search_type")

        assert my.search_type

        my.load_options_class = my.kwargs.get('load_options_class')

        
        state = Container.get("global_state")
        if state:
            my.process = state.get("process")
        else:
            my.process = None

        # the filter for searching assets
        div = DivWdg(css='filter_box')
        div.add_color("background", "background2", -35)


        from app_init_wdg import PyMayaInit, PyXSIInit, PyHoudiniInit
        if WebContainer.get_web().get_selected_app() == 'Maya':
            app = PyMayaInit()
        elif WebContainer.get_web().get_selected_app() == 'XSI':
            app = PyXSIInit()
        elif WebContainer.get_web().get_selected_app() == 'Houdini':
            app = PyHoudiniInit()
        div.add(app)


        # add the possibility of a custom callback
        callback = my.options.get('callback')
        if callback:
            hidden = HiddenWdg("callback", callback)
            div.add(hidden)


        # or add the possiblity of a switch mode
        pipeline_type = "load"
        hidden = HiddenWdg("pipeline_type", pipeline_type)

        if my.process:
            process_div = DivWdg()
            process_div.add_style("margin: 10px")
            process_div.add("PROCESS: %s" % my.process)
            process_div.add_style("font-size: 20px")
            widget.add(process_div)

            hidden_wdg = HiddenWdg("process_select_%s" %my.search_type)
            hidden_wdg.set_value(my.process)
            widget.add(hidden_wdg)
        else:
            search_type = my.search_type
            if search_type =='prod/shot_instance':
                search_type = 'prod/shot'

            process_filter = ProcessFilterWdg(my.get_context_data(search_type), search_type)
            span = SpanWdg(process_filter, css='med')
            div.add(span)
            widget.add(div)

        # load options for diff search type
        if my.load_options_class:
            load_options = Common.create_from_class_path(my.load_options_class)
        elif my.search_type=='prod/asset':
            load_options = LoadOptionsWdg()
        elif my.search_type == 'prod/shot':
            load_options = ShotLoadOptionsWdg()
        elif my.search_type == 'prod/shot_instance':
            load_options = AnimLoadOptionsWdg()
        else:
            load_options = LoadOptionsWdg()
        load_options.set_prefix(my.search_type)


        widget.add(load_options)

        return widget



    def get_context_data(my, search_type=None):
        '''get the list of contexts that can be checked in with this widget'''
        # usually there is no pipeline for prod/shot_instance
        #search_type = my.search_type
        labels, values = Pipeline.get_process_select_data(search_type, \
            project_code=Project.get_project_code())
        

        return labels, values



