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

__all__ = ['ShotCreatorWdg', 'ShotCreatorCmd']


from pyasm.search import SObjectFactory, Search
from pyasm.web import DivWdg, SpanWdg, Widget, WebContainer
from pyasm.widget import TextWdg
from pyasm.biz import Task
from pyasm.prod.web import SequenceFilterWdg, SubmitWdg, TableWdg
from pyasm.command import Command


class ShotCreatorWdg(Widget):
    '''Widget to quickly create a large number of shots'''
    def get_display(my):
        WebContainer.register_cmd("pyasm.alpha.shot_creator_wdg.ShotCreatorCmd")

        widget = Widget()

        div = DivWdg(css="filter_box")

        span = SpanWdg(css="med")
        span.add(SequenceFilterWdg())
        div.add(span)

        span = SpanWdg(css="med")
        span.add("Number of Shots: ")
        span.add( TextWdg("num_shots") )
        div.add(span)

        span = SpanWdg(css="med")
        span.add("Pipeline: ")
        div.add(span)

        button = SubmitWdg("Create Shots")
        div.add(button)

        widget.add(div)


        search = Search("prod/shot")
        sobjects = search.get_sobjects()

        table = TableWdg("prod/shot", "manage")
        table.set_sobjects(sobjects)
        widget.add(table)

        return widget


class ShotCreatorCmd(Command):

    def execute(my):
        web = WebContainer.get_web()
        if not web.get_form_value("Create Shots"):
            return

        sequence_filter = SequenceFilterWdg()
        sequence_code = sequence_filter.get_value()

        num_shots = web.get_form_value("num_shots")
        if num_shots:
            num_shots = int(num_shots)
        else:
            return

        start = 1

        pipeline_code = "shot"


        for i in range(start, num_shots+1):
            shot = SObjectFactory.create("prod/shot")
            shot.set_value("code", "%s%0.3d" % (sequence_code, i) )
            shot.set_value("sequence_code", sequence_code )
            shot.set_value("pipeline_code", pipeline_code)

            shot.commit()

            Task.add_initial_tasks(shot)


