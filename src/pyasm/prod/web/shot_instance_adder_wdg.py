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

__all__ = ['ShotInstanceAdderWdg', 'ShotInstanceListWdg', 
'ShotInstanceAdderCbk', 'ShotInstanceRemoverCbk',
'LayerInstanceListWdg', 'LayerInstanceAdderCbk', 'LayerInstanceRemoverCbk',
'ShotParentWdg', 'ShotParentCbk', 'ShotParentDependencyWdg',
'NumShotInstancesWdg', 'TaskPlannerWdg', 'TaskPlannerCbk', 'TaskRetireCbk' , 'NumTasksWdg',
'TaskListWdg', 'SequencePlannerWdg', 'SequenceInstanceListWdg', 'SequencePlannerCbk', 'NumSequenceInstanceWdg', 'MultiPlannerWdg']


from pyasm.command import Command, CommandException
from pyasm.search import *
from pyasm.web import *
from pyasm.biz import Project
from pyasm.widget import BaseTableElementWdg, FunctionalTableElement, CheckboxWdg, TableWdg, SubmitWdg, ThumbWdg, IconSubmitWdg, IconWdg, SearchLimitWdg, HelpItemWdg, CheckboxColWdg, InsertLinkWdg, HiddenWdg, FilterSelectWdg


from shot_navigator_wdg import *
from asset_filter_wdg import *
from prod_context import *
from prod_input_wdg import *



class ShotInstanceAdderWdg(Widget):
    '''interface that allows instances to be added to shots'''
    CONTAINER_NAME = 'Shots'
    ADD_BUTTON = "Add Assets to Shots"
    
    def __init__(my, name="", view_select=""):
        my.view_select = view_select
        super(ShotInstanceAdderWdg, my).__init__(name)
    
    def get_search_type(my):
        return "prod/shot_instance"
    
    def get_left_search_type(my):
        return "prod/asset"

    def get_right_search_type(my):
        return "prod/shot"


    def get_left_view(my):
        return "layout"

    def get_right_view(my):
        return "layout"


    def get_left_filter(my, search=None):
        widget = Widget()
        asset_filter = AssetFilterWdg()
        asset_filter.alter_search(search)
        widget.add(asset_filter)

        widget.add( HtmlElement.br(2) )

        instance_filter = SequenceInstanceFilterWdg("asset_sequence_filter")
        instance_filter.alter_search(search)
        widget.add(instance_filter)

        return widget


    def get_right_filter(my, search=None):
        filter = SequenceFilterWdg('sequence_filter')
        filter.add_none_option()
        return filter

    def get_action_cbk(my):
        return ["pyasm.prod.web.ShotInstanceAdderCbk", \
                "pyasm.prod.web.ShotInstanceRemoverCbk" ]

    def get_view_select(my):
        div = FloatDivWdg(my.view_select)
        return div

    def get_action_wdg(my):
       
        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        main_div.add(my.get_view_select())
        main_div.add(div)
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')
         
        div.add(HtmlElement.b("Action: "))
        add_button = IconSubmitWdg(my.ADD_BUTTON, IconWdg.ADD, long=True)
        div.add(add_button)
        remove_button = IconSubmitWdg("Remove from %s" % my.CONTAINER_NAME,\
            IconWdg.DELETE, long=True)
        div.add(remove_button)
        for cbk in my.get_action_cbk():
            WebContainer.register_cmd(cbk)

        return main_div



    def get_left_wdg(my, view="layout"):

        search_type = my.get_left_search_type()
        search = Search(search_type)
        
        left_div = DivWdg()
        left_div.add_style("margin: 10px")

        title = DivWdg(css="maq_search_bar")
        title.add(search.get_search_type_obj().get_title())
        left_div.add(title)

        asset_filter = my.get_left_filter(search)
        if asset_filter:
            filter_box = DivWdg(asset_filter, css='filter_box')
            left_div.add(filter_box)
            asset_filter.alter_search(search)

        #assets_table = TableWdg(search_type, view)
        from tactic.ui.panel import TableLayoutWdg
        assets_table = TableLayoutWdg(table_id='table_left', search_type=search_type, view=view)
        assets_table.set_sobjects(search.get_sobjects(), search)
        
        left_div.add(assets_table)

        return left_div
        

    def get_right_wdg(my, view="layout"):
        search_type = my.get_right_search_type()
        search = Search(search_type)
        
        right_div = DivWdg()

        right_div.add_style("margin: 10px")

        title = DivWdg(css="maq_search_bar")
        title.add(search.get_search_type_obj().get_title())
        right_div.add(title)

        shot_filter = my.get_right_filter(search)
        if shot_filter:
            shot_filter.alter_search(search) 
        filter_wdg = DivWdg(css="filter_box")
        if shot_filter:
            filter_wdg.add(shot_filter)
       
        right_div.add(filter_wdg)

        from tactic.ui.panel import TableLayoutWdg
        shots_table = TableLayoutWdg(table_id='table_right', search_type=search_type, view=view)
        #shots_table = TableWdg(my.get_right_search_type(), view)
        shots_table.set_sobjects(search.get_sobjects(), search)

        right_div.add(shots_table)

        return right_div

    


    def init(my):

        #info_div = DivWdg()
        #info_div.add_attr("spt_class_name", "pyasm.prod.web.SObjectPlannerWdg")
        #my.add(info_div)


        help = HelpItemWdg('Shot Planner tab', 'The Shot Planner tab lets you search through your asset library and assign them to one or more shots. On assignment, asset instances are created which can be accessed in the 3D App area. The blue arrows lets you drill down to the assigned instances and shot details information respectively.')
        my.add(help)
        my.add( my.get_action_wdg() )

        table = Table()
        table.add_style("width: 100%")
        table.add_row()

        hidden = HiddenWdg("search_type", my.get_search_type() )
        my.add(hidden)
        WebState.get().add_state("planner_search_type", my.get_search_type() )


        # add the left widget
        left_view = my.get_left_view()
        left_wdg = my.get_left_wdg(left_view)
        td = table.add_cell(left_wdg)
        td.add_style("vertical-align: top")
        td.add_style("width: 50%")


        # add the right widget
        right_view = my.get_right_view()
        right_wdg = my.get_right_wdg(right_view)
        td = table.add_cell(right_wdg)
        td.add_style("width: 50%")
        td.add_style("vertical-align: top")

        my.add(table)

        #return super(ShotInstanceAdderWdg,my).get_display()



class ShotInstanceListWdg(Widget):

    def get_search_type(my):
        return "prod/shot_instance"
  
    
    def get_display(my):

        args = WebContainer.get_web().get_form_args()

        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']

        sobject = Search.get_by_search_key("%s|%s" % (search_type,search_id) )

        #instances = sobject.get_all_children("prod/instance")

        all_instances = []

        # get parent instances first
        parent_code = ""
        if sobject.has_value("parent_code"):
            parent_code = sobject.get_value("parent_code")
        if parent_code != "":
            parent = sobject.get_by_code(parent_code)

            search = Search(my.get_search_type())
            search.add_filter(sobject.get_foreign_key(), parent.get_code())
            search.add_filter("type", "asset")
            instances = search.get_sobjects()

            all_instances.extend(instances)


        search = Search(my.get_search_type())
        search.add_filter(sobject.get_foreign_key(), sobject.get_code())
        search.add_filter("type", "asset")
        instances = search.get_sobjects()
        all_instances.extend(instances)

        widget = DivWdg()
        
        widget.add_style("width: 95%")
        
        widget.add_style("float: right")
        table = TableWdg(my.get_search_type(),"layout", css='simple')
        table.set_sobjects(all_instances)
        table.set_show_property(False)

        aux_data = ShotInstance.get_aux_data(all_instances)
        table.set_aux_data(aux_data)
        widget.add(table)
        return widget





class ShotInstanceAdderCbk(Command):

    
    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value(ShotInstanceAdderWdg.ADD_BUTTON) != "":
            return True

    def get_title(my):
        return "Add Instance"

    def get_checkbox_cols(my):
        ''' returns the class of the left and right CheckboxColWdg'''
        return AssetCheckboxWdg, ShotCheckboxWdg

    def get_instance_cls(my):
        return ShotInstance
        
    def execute(my):

        left_cb , right_cb = my.get_checkbox_cols()
        
        web = WebContainer.get_web()

        select_shots = web.get_form_values(right_cb.CB_NAME)
        if not select_shots:
            return

        shots = []
        
        for select_shot in select_shots:
            shot = Search.get_by_search_key(select_shot)
            shots.append(shot)


        select_assets = web.get_form_values(left_cb.CB_NAME)
        for select_asset in select_assets:

            sobject = Search.get_by_search_key( select_asset )
            for shot in shots:
                instance_name = "%s" % sobject.get_value("name")
                eval('my.get_instance_cls().create(shot, sobject, instance_name)')
        my.add_description('Add asset to shots [%s]'% ', '.join(SObject.get_values(shots,'code')))
 
class ShotInstanceRemoverCbk(Command):

    CONTAINER_NAME = 'Shots'
    
    def get_title(my):
        return "Remove Shot Instance"

    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value("Remove from %s" % my.CONTAINER_NAME) != "":
            return True


    def execute(my):

        web = WebContainer.get_web()

        select_keys = web.get_form_values("select_instance")
        for select_key in select_keys:
            sobject = Search.get_by_search_key( select_key )
            # NOTE: should probably check if there are any snapshots before
            # deleting
            sobject.delete()

            my.add_description("Removed %s" % sobject.get_code() )


class LayerInstanceListWdg(ShotInstanceListWdg):
    
    def get_search_type(my):
        return "prod/layer_instance"
    
class LayerInstanceAdderCbk(ShotInstanceAdderCbk):
   
    def get_checkbox_cols(my):
        return AssetCheckboxWdg, LayerCheckboxWdg

    def get_instance_cls(my):
        return LayerInstance

class LayerInstanceRemoverCbk(ShotInstanceRemoverCbk):

    CONTAINER_NAME = 'Layers'


class ShotParentWdg(ShotInstanceAdderWdg):

    def get_left_search_type(my):
        return "prod/shot"

    def get_left_filter(my, search=None):
        filter = ShotFilterWdg()
        return filter

    def get_left_wdg(my, view="layout_left"):
        return super(ShotParentWdg,my).get_left_wdg(view=view)

    def get_right_wdg(my, view="layout_right"):
        return super(ShotParentWdg,my).get_left_wdg(view=view)

    #def get_right_filter(my, search=None):
    #    filter = ShotFilterWdg()
    #    return filter



    def get_action_wdg(my):

        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        main_div.add(div)
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')
        div.add(HtmlElement.b("Action: "))
        add_button = IconSubmitWdg("Add to Parent", IconWdg.ADD, long=True)
        div.add(add_button)
        remove_button = IconSubmitWdg("Remove Parent", IconWdg.DELETE, long=True)
        div.add(remove_button)

        WebContainer.register_cmd("pyasm.prod.web.ShotParentCbk")

        return main_div


class ShotParentCbk(Command):

    def get_title(my):
        return "Shot parent"

    def execute(my):

        web = WebContainer.get_web()

        if web.get_form_value("Add to Parent") != "":

            select_parent = web.get_form_value("select_parent")
            if select_parent == "":
                raise CommandException("No parents selected")
            parent = Search.get_by_search_key( select_parent )

            parent_code = parent.get_code()
            

            select_shots = web.get_form_values("select_shot")
            if not select_shots:
                raise CommandException("No shots selected")

            for select_key in select_shots:
                sobject = Search.get_by_search_key( select_key )
                code = sobject.get_code()

                # you cannot parent to yourself
                if code == parent_code:
                    raise CommandException("Cannot parent shot '%s' to itself" \
                        % code)

                sobject.set_value("parent_code", parent_code)
                sobject.commit()

                my.description = "Parented '%s' to '%s'" % (code, parent_code)

        elif web.get_form_value("Remove Parent") != "":
    
            select_shots = []
            select_shots.extend( web.get_form_values("select_shot") )
            select_shots.extend( web.get_form_values("select_parent") )
            if not select_shots:
                raise CommandException("No shots selected")

            for select_key in select_shots:
                sobject = Search.get_by_search_key( select_key )
                code = sobject.get_code()
                parent_code = sobject.get_value("parent_code")

                my.description = "Removed parent '%s' from '%s'" % \
                    (parent_code, code)

                sobject.set_value("parent_code", "")
                sobject.commit()


class ShotParentDependencyWdg(Widget):
    '''Widget which displays a shots relationship with parent and children.
    Used in shot parenting tab'''

    def get_display(my):

        args = WebContainer.get_web().get_form_args()

        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']

        shot = Search.get_by_search_key("%s|%s" % (search_type,search_id) )


        # get all of the parents
        all_shots = []
        current = shot

        count = 0
        while count < 20:
            parent_code = current.get_value("parent_code")
            if parent_code == "":
                break
            parent = Shot.get_by_code(parent_code)
            all_shots.insert(0, parent)
            current = parent

            count += 1

        widget = DivWdg()
        widget.add_style("width: 90%")
        widget.add_style("float: right")

        # diplay parents
        level = 0
        for current in all_shots:
            my.display_shot(current, widget, level)
            level += 1

        # display current
        my.display_shot(shot, widget, level, True)

        # display children
        my.handle_children(shot, widget, level+1)

        return widget


    def handle_children(my, shot, widget, count):

        code = shot.get_code()
        search = Search("prod/shot")
        search.add_filter("parent_code", code)

        children = search.get_sobjects()
        if not children:
            return

        # display all of the children
        for child in children:
            my.display_shot(child, widget, count)
            my.handle_children(child, widget, count+1)



    def display_shot(my, shot, widget, count, is_current=False):
        thumb = ThumbWdg()
        thumb.set_sobject(shot)
        thumb.set_icon_size(45)

        widget.add( "&nbsp;" * 5 * count + "L ")
        widget.add(thumb)
        widget.add(" ")
        span = SpanWdg()
        if is_current:
            span.add_style("background: #eee")
            span.add_style("font-weight: bold")
            span.add_style("font-size: 1.1em")
        span.add(shot.get_code())
        span.add(" ")
        span.add(shot.get_value("description"))
        widget.add(span)
        widget.add("<br/>")



class NumShotInstancesWdg(FunctionalTableElement):
    '''Lists the number of instances in a shot'''

    def get_title(my):
        return "#"

    def preprocess(my):

        # TODO: this does not take shot parenting into account
        sobjects = my.sobjects
        if not sobjects:
            return

        # find all of the instances in a shot
        sobject = sobjects[0]
        foreign_key = sobject.get_foreign_key()

        search = Search( ShotInstance )
        search.add_column(foreign_key)
        #search.add_filter("type", 'asset')

        if len(sobjects) == 1:
            search.add_filter(foreign_key, sobject.get_code())
        else:
            search_codes = [x.get_code() for x in sobjects]
            search.add_filters(foreign_key, search_codes)

        search_type = sobject.get_search_type()
        search.add_order_by(foreign_key)
        children = search.get_sobjects()

        # convert to a dictionary
        my.numbers = {}
        for child in children:
            code = child.get_value(foreign_key)
            number = my.numbers.get(code)
            if not number:
                number = 0
           
            number += 1
            my.numbers[code] = number

        #print my.numbers
 


    def get_display(my):
        sobject = my.get_current_sobject()
        number = my.numbers.get(sobject.get_code())
        if not number:
            return "&nbsp;"
        return "(%d)" % number





class TaskPlannerWdg(ShotInstanceAdderWdg):

    def get_left_search_type(my):
        return "sthpw/task"

    def get_left_view(my):
        return "layout_left"

    def get_right_view(my):
        return "task_planner"

    def get_left_filter(my, search=None):
        return Widget()

    def get_right_wdg(my,view="task_planner"):
        return super(TaskPlannerWdg,my).get_right_wdg(view=view)

    #def get_right_filter(my, search=None):
    #    filter = ShotFilterWdg()
    #    return filter



    def get_action_wdg(my):

        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')
       
        main_div.add(my.get_view_select())

        main_div.add(div)
        div.add(HtmlElement.b("Action: "))
        add_button = IconSubmitWdg("Add to Shot", IconWdg.ADD, long=True)
        div.add(add_button)
        remove_button = IconSubmitWdg("Retire from %s" %TaskRetireCbk.CONTAINER_NAME, IconWdg.DELETE, long=True)
        div.add(remove_button)

        WebContainer.register_cmd("pyasm.prod.web.TaskPlannerCbk")
        WebContainer.register_cmd("pyasm.prod.web.TaskRetireCbk")

        #FIXME: hardcode to shot for now
        search_type = 'prod/shot'
        WebState.get().add_state("ref_search_type", search_type )
        return main_div



    def get_left_wdg(my, view="layout_left"):

        search_type = my.get_left_search_type()
        search = Search(search_type)

        # filter by project
        #project_code = Project.get_project_code()
        #search.add_filter("project_code", project_code )
        # use a holding place for these "special"
        #parent_search_type = my.get_right_search_type()
        #search.add_filter("search_type", "%s?project=%s" % \
        #    (parent_search_type, project_code) )

        search.add_filter("s_status", "__TEMPLATE__")
        
        left_div = DivWdg()
        left_div.add_style("margin: 10px")
        left_div.add(HtmlElement.h3("Template Task") )


        asset_filter = my.get_left_filter(search)
        filter_box = DivWdg(asset_filter, css='filter_box')
        left_div.add(filter_box)
        asset_filter.alter_search(search)

        assets_table = TableWdg(search_type, view)
        assets_table.set_sobjects(search.get_sobjects(), search)
        left_div.add(assets_table)

        return left_div
 
class TaskPlannerCbk(Command):

    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value("Add to Shot") != "":
            return True
        return False

    def get_title(my):
        return "Task Planner"

    def get_checkbox_cols(my):
        ''' returns the class of the left and right CheckboxColWdg'''
        return CheckboxColWdg, ShotCheckboxWdg

    def execute(my):

        left_cb , right_cb = my.get_checkbox_cols()
        
        web = WebContainer.get_web()


        select_shots = web.get_form_values(right_cb.CB_NAME)
        if not select_shots:
            return

        select_tasks = web.get_form_values("sthpw_task")
        if not select_tasks:
            return

        # get all of the shots
        shots = []
        for shot_search_key in select_shots:
            shot = Search.get_by_search_key(shot_search_key)
            shots.append(shot)

        # get all of the tasks
        tasks = []
        for task_search_key in select_tasks:
            task = Search.get_by_search_key(task_search_key)
            tasks.append(task)


        # copy these tasks into the selected shots
        from pyasm.biz import Task
        for shot in shots:
            for task in tasks:
                # extract the properties of each task
                process = task.get_value("process")
                description = task.get_value("description")
                assigned = task.get_value("assigned")
                supe = task.get_value("supervisor")
                # create a new tasks
                new_task = Task.create(shot, process, description, assigned=assigned,\
                        supervisor=supe)
                my.sobjects.append(new_task)
        my.add_description("Added template tasks to shot(s)")

class TaskRetireCbk(Command):
    ''' retire all the selected tasks'''
    CONTAINER_NAME = 'Shots'
    
    def get_title(my):
        return "Retire tasks"

    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value("Retire from %s" % my.CONTAINER_NAME) != "":
            return True


    def execute(my):
        web = WebContainer.get_web()

        select_keys = web.get_form_values("select_instance")
        for select_key in select_keys:
            sobject = Search.get_by_search_key( select_key )
            # NOTE: should probably check if there are any snapshots before
            # deleting
            sobject.retire()

            my.add_description("Retired %s" % sobject.get_code() )

class NumTasksWdg(FunctionalTableElement):
    '''Lists the number of tasks in a sobject'''

    def get_title(my):
        return "#"

    def get_display(my):
        sobject = my.get_current_sobject()
        search = Search("sthpw/task")
        search.add_sobject_filter(sobject)
        count = search.get_count()

        return "(%s)" % count



class TaskListWdg(Widget):

    def get_display(my):

        args = WebContainer.get_web().get_form_args()

        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']

        sobject = Search.get_by_search_key("%s|%s" % (search_type,search_id) )

        widget = DivWdg()
        widget.add_style("width: 95%")
        widget.add_style("margin-left: 20px")
        table = TableWdg("sthpw/task", "layout_right")
        from pyasm.biz import Task
        tasks = Task.get_by_sobject(sobject)
        table.set_sobjects(tasks)
        table.set_show_property(False)
        widget.add(table)

        return widget



class SequencePlannerWdg(ShotInstanceAdderWdg):
 
    ADD_BUTTON = "Add Assets to Sequence"
    def get_right_search_type(my):
        return "prod/sequence"

    def get_right_filter(my, search=None):
        return Widget()

    def get_left_filter(my, search=None):
        widget = Widget()
        asset_filter = AssetFilterWdg()
        asset_filter.alter_search(search)
        widget.add(asset_filter)
        return widget



    def get_action_wdg(my):

        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')
        
        main_div.add(my.get_view_select())
        main_div.add(div)

        div.add(HtmlElement.b("Action: "))
        add_button = IconSubmitWdg(my.ADD_BUTTON, IconWdg.ADD, long=True)
        div.add(add_button)
        #remove_button = IconSubmitWdg("Remove from Sequence", IconWdg.DELETE, long=True)
        #div.add(remove_button)

        WebContainer.register_cmd("pyasm.prod.web.SequencePlannerCbk")

        return main_div



class SequenceInstanceListWdg(Widget):

    def get_display(my):

        args = WebContainer.get_web().get_form_args()

        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']

        sobject = Search.get_by_search_key("%s|%s" % (search_type,search_id) )

        search = Search("prod/sequence_instance")
        search.add_filter(sobject.get_foreign_key(), sobject.get_code())
        all_instances = search.get_sobjects()
        widget = DivWdg()
        widget.add_style("width: 95%")
        widget.add_style("margin-left: 20px")
        table = TableWdg("prod/sequence_instance", "layout", css="minimal")
        table.set_show_property(False)
        table.set_show_header(False)
        table.set_sobjects(all_instances)
        table.set_search(search)
        widget.add(table)

        aux_data = SequenceInstance.get_aux_data(all_instances)
        table.set_aux_data(aux_data)
        return widget

class SequencePlannerCbk(Command):
    
    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value(SequencePlannerWdg.ADD_BUTTON) != "":
            return True
        
        return False
    
    def get_title(my):
        return "Sequence Planner"


    def get_checkbox_cols(my):
        ''' returns the class of the left and right CheckboxColWdg'''
        return AssetCheckboxWdg, ShotCheckboxWdg



    def execute(my):

        left_cb , right_cb = my.get_checkbox_cols()
        
        web = WebContainer.get_web()

        left_selects = web.get_form_values(left_cb.CB_NAME)
        if not left_selects:
            return
        right_selects = web.get_form_values(right_cb.CB_NAME)
        if not right_selects:
            return

        # get all of the left sobjects
        left_sobjects = []
        for left_search_key in left_selects:
            left_sobject = Search.get_by_search_key(left_search_key)
            left_sobjects.append(left_sobject)


        # get all of the right sobjects
        right_sobjects = []
        for right_search_key in right_selects:
            right_sobject = Search.get_by_search_key(right_search_key)
            right_sobjects.append(right_sobject)

        my.handle_sobjects(left_sobjects, right_sobjects)


    def handle_sobjects(my, left_sobjects, right_sobjects):
        
        for left_sobject in left_sobjects:
            for right_sobject in right_sobjects:

                sobject = SearchType.create("prod/sequence_instance")
                sobject.set_value(left_sobject.get_foreign_key(), left_sobject.get_code() )
                sobject.set_value(right_sobject.get_foreign_key(), right_sobject.get_code() )
                sobject.commit()


class NumSequenceInstanceWdg(FunctionalTableElement):
    '''Lists the number of tasks in a sobject'''

    def get_title(my):
        return "#"

    def get_display(my):
        sobject = my.get_current_sobject()
        search = Search("prod/sequence_instance")
        search.add_filter(sobject.get_foreign_key(), sobject.get_code() )
        count = search.get_count()

        return "(%s)" % count

class MultiPlannerWdg(Widget):

    ''' A collection of Planners '''
    def get_display(my):
        select = FilterSelectWdg('planner_type', label='Planner: ', css='med')
        select.set_option('values', ['shot', 'task', 'sequence'])

        type = select.get_value()
        if type=='task':
            planner = TaskPlannerWdg(view_select=select)
        elif type=='sequence':
            planner = SequencePlannerWdg(view_select=select)
        else:
            planner = ShotInstanceAdderWdg(view_select=select)

        return planner


