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

__all__ = ['AggregateWdg','AggregateRegisterCmd', 'AggregateCmd']

from pyasm.common import Environment
from pyasm.biz import Project
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, Table
from pyasm.widget import WidgetConfigView, TextWdg, SelectWdg, IconButtonWdg, IconWdg


from tactic.ui.common import BaseRefreshWdg

from tactic.command import Scheduler, SchedulerTask


class AggregateWdg(BaseRefreshWdg):
    '''Widget to calculate aggregates'''


    ARGS_KEYS = {
        'search_type': 'The search type that will be recalculated',
        'view': 'The view to extract the definition from',
        'element_name': 'The element name to calculate'
    }



    def get_display(my):

        my.search_type = my.kwargs.get('search_type')
        my.element_name = my.kwargs.get('element_name')
        assert my.search_type
        assert my.element_name

        class_name = 'tactic.ui.app.aggregate_wdg.AggregateCmd'
        interval = 120
        priority = None

        if my.kwargs.get('is_refresh'):
            user = Environment.get_user_name()

            # these interval jobs need to have a specific code
            code = "aggregate|%s|%s" % (my.search_type, my.element_name)

            # check to see if the job exists
            #job = Search.get_by_code("sthpw/queue", code)
            job = None
            if not job:
                job = SearchType.create("sthpw/queue")
                #job.set_value("code", code)

                job.set_value("project_code", Project.get_project_code() )
                job.set_value("class_name", class_name)
                job.set_value("command", class_name)
                job.set_value("serialized", str(my.kwargs) )
                job.set_value("interval", 120)
                job.set_value("state", 'pending')
                job.set_value("queue", 'interval')
                job.set_value("priority", 9999)
                job.set_value("login", user) 
                job.commit()




        my.view = my.kwargs.get('view')
        if not my.view:
            my.view = 'definition'

        
        top = DivWdg()
        my.set_as_panel(top)

        action_div = DivWdg()
        top.add(action_div)

        refresh = IconButtonWdg("Refresh", IconWdg.REFRESH)
        refresh.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_panel");
        spt.panel.refresh(top);
        '''
        } )
        action_div.add(refresh)



        register_div = DivWdg()
        register_div.add_class("spt_queue_register")
        top.add(register_div)
        register_div.add_style("border: solid 1px black")
        register_div.add_style("padding: 20px")
        register_div.add("Register new interval aggregate")

        table = Table()
        table.add_style("margin: 15px")
        register_div.add(table)
        table.add_row()
        table.add_cell("command: ")
        table.add_cell(class_name)

        #table.add_row()
        #table.add_cell("priority: ")
        #table.add_cell(priority)

        table.add_row()
        table.add_cell("interval: ")
        td = table.add_cell("every ")
        td.set_attr("title", "Recalculation interval")
        text = TextWdg("interval")
        text.add_style("width: 30px")
        text.set_value(interval)
        td.add(text)

        unit_select = SelectWdg("unit")
        unit_select.set_value(interval)
        unit_select.set_option("values", "seconds|minutes|hours|days")
        td.add(" ")
        td.add(unit_select)

        table.add_row()
        table.add_cell("queue: ")
        table.add_cell("interval")


        from pyasm.widget import ProdIconButtonWdg
        button = ProdIconButtonWdg("Register")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_queue_register")
        var values = spt.api.get_input_values(top);
        var top = bvr.src_el.getParent(".spt_panel");
        spt.panel.refresh(top);
        '''
        } )
        register_div.add(button)


        from pyasm.widget import ProdIconButtonWdg
        button = ProdIconButtonWdg("Cancel")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        alert('cancel');
        '''
        } )
        register_div.add(button)


        '''
        cmd = AggregateCmd(**my.kwargs)

        print "registering scheduled task"
        scheduler = Scheduler.get()
        scheduler.start_thread()
        task = AggregateRefreshTask(name="cow", command=cmd)
        scheduler.add_interval_task(task, 10, mode='forked')
        scheduler.cancel_task("cow", delay=35)
        '''


        top.add("<br/>")
        top.add("<b>Current Job Queue</b>")
        top.add("<br/><br/>")
        from tactic.ui.panel import TableLayoutWdg
        table = TableLayoutWdg(search_type='sthpw/queue',view='test')
        top.add(table)

        return top


from pyasm.command import Command
class AggregateRegisterCmd(Command):

    def execute(my):
        my.search_type = my.kwargs.get("search_type")
        my.element_name = my.kwargs.get("element_name")
        assert my.search_type
        assert my.element_name

        interval = my.kwargs.get('interval')
        if not interval:
            interval = 120

        data_type = my.kwargs.get('data_type')
        if not data_type:
            data_type = 'float'

        class_name = 'tactic.ui.app.aggregate_wdg.AggregateCmd'
        priority = None

        user = Environment.get_user_name()

        # these interval jobs need to have a specific code
        code = "aggregate|%s|%s" % (my.search_type, my.element_name)

        # check to see if the job exists
        job = Search.get_by_code("sthpw/queue", code)
        if not job:
            job = SearchType.create("sthpw/queue")
            job.set_value("code", code)

            job.set_value("project_code", Project.get_project_code() )
            job.set_value("class_name", class_name)
            job.set_value("command", class_name)
            job.set_value("login", user) 
            job.set_value("queue", 'interval')

            # this is meaningless
            job.set_value("priority", 9999)

            # not sure what to do here if it already exists
            job.set_value("state", 'pending')



            # add a column to the table
            from pyasm.command import ColumnAddCmd
            from pyasm.search import AlterTable
            column_name = my.element_name
            cmd = ColumnAddCmd(my.search_type, column_name, data_type)
            cmd.execute()

            # modify the table
            #alter = AlterTable(my.search_type)
            #alter.modify(my.search_type, data_type)
            #print alter.get_statements()


        job.set_value("serialized", str(my.kwargs) )
        job.set_value("interval", interval)
        job.commit()



#class AggregateRefreshTask(SchedulerTask):
#    def execute(my):
#        cmd = my.kwargs.get("command")
#        Command.execute_cmd(cmd)




from pyasm.command import Command
class AggregateCmd(Command):

    ARGS_KEYS = {
        'search_type': 'The search type that will be recalculated',
        'view': 'The view to extract the definition from',
        'element_name': 'The element name to calculate'
    }


    def get_title(my):
        return "Aggregate Calculation"


    def execute(my):

        my.search_type = my.kwargs.get('search_type')
        my.element_name = my.kwargs.get('element_name')
        #print "Calculating aggregate: ", my.search_type, my.element_name

        my.view = my.kwargs.get('view')
        if not my.view:
            my.view = 'definition'

        config = WidgetConfigView.get_by_search_type(search_type=my.search_type, view=my.view)
        widget = config.get_display_widget(my.element_name)

        # calculate all of the values
        search = Search(my.search_type)
        sobjects = search.get_sobjects()
        widget.set_sobjects(sobjects)
        widget.kwargs['use_cache'] = "false"

        for i, sobject in enumerate(sobjects):
            widget.set_current_index(i)
            value = widget.get_text_value()

            print sobject.get_code(), "value [%s]: " %value

            # all cache columns need are named with a c_ preceeding it
            # s_status
            # c_element_name
            #
            # this_month -> c_this_month
            #column = "c_%s" % my.element_name
            #sobject.set_value(column, value)
            sobject.set_value(my.element_name, value)
            sobject.commit()



