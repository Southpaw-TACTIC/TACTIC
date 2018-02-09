###########################################################
#
# Copyright (c) 2005, Southpaw Teciiihnology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# SObjectPlanner serves to replace ShotInstanceAdderWdg.  It is a general
# class that will make many to many relationships between any two sobject
# types.


# DEPRECATED

__all__ = []
#__all__ = [ 'SObjectPlannerWdg', 'NumSObjectInstancesWdg', 'SObjectInstanceAdderCbk', 'SObjectInstanceRemoverCbk', 'SObjectInstanceListWdg' ] 

from pyasm.search import Search, SearchType, SObjectFactory
from pyasm.command import Command
from pyasm.web import WebContainer, Widget, DivWdg, SpanWdg, WebState, HtmlElement
from pyasm.widget import FunctionalTableElement, TableWdg, HiddenWdg, IconSubmitWdg, IconButtonWdg, IconWdg

from shot_instance_adder_wdg import ShotInstanceAdderWdg


class SObjectPlannerWdg(ShotInstanceAdderWdg):
    '''Planner that can be configured by options.  Note that this should
    probably incorporated into the base class'''

    ADD_BUTTON = "Add Instance"


    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(SObjectPlannerWdg,self).__init__()

    def init(self):
        self.options = self.kwargs
        super(SObjectPlannerWdg,self).init()


    def get_search_type(self):
        search_type = self.options.get("search_type")
        return search_type

    def get_left_search_type(self):
        search_type = self.options.get("left_search_type")
        return search_type

    def get_left_view(self):
        view = self.options.get("left_view")
        if not view:
            view = "planner_left"
        return view


    def get_right_search_type(self):
        search_type = self.options.get("right_search_type")
        return search_type

    def get_right_view(self):
        view = self.options.get("right_view")
        if not view:
            view = "planner_right"
        return view


    def get_left_filter(self, search):
        return None

    def get_right_filter(self, search):
        return None


    def get_action_cbk(self):
        return ["pyasm.prod.web.SObjectInstanceAdderCbk", \
                "pyasm.prod.web.SObjectInstanceRemoverCbk" ]


    def get_action_wdg(self):
       
        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        main_div.add(self.get_view_select())
        main_div.add(div)
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')

        search_type = self.get_search_type()
         
        div.add(HtmlElement.b("Action: "))
        add_button = IconButtonWdg(self.ADD_BUTTON, IconWdg.ADD, long=True)
        behavior = {
            'type': 'click_up',
            'mouse_btn': 'LMB',
            'cbfn_action': 'spt.sobject_planner.action',
            'action': 'add',
            'search_type': search_type
        }
        add_button.add_behavior(behavior)


        retire_button = IconButtonWdg("Retire Instance",\
            IconWdg.RETIRE, long=True)
        behavior = {
            'type': 'click_up',
            'mouse_btn': 'LMB',
            'cbfn_action': 'spt.sobject_planner.action',
            'action': 'retire',
            'search_type': search_type
        }
        retire_button.add_behavior(behavior)


        delete_button = IconButtonWdg("Delete Instance",\
            IconWdg.DELETE, long=True)
        behavior = {
            'type': 'click_up',
            'mouse_btn': 'LMB',
            'cbfn_action': 'spt.sobject_planner.action',
            'action': 'delete',
            'search_type': search_type
        }
        delete_button.add_behavior(behavior)






        div.add(add_button)
        div.add(retire_button)
        div.add(delete_button)

        '''
        # add test popup
        from tactic.ui.container import PopupWdg
        from tactic.ui.panel import TableLayoutWdg
        popup = PopupWdg(id="planner", allow_page_activity=True)

        content = DivWdg()
        #content.add_style("height: 500px")
        #content.add_style("overflow: scroll")
        search_type = self.get_search_type()
        layout = TableLayoutWdg(search_type=search_type, view="planner_left")
        search = Search(search_type)
        layout.set_sobjects( search.get_sobjects() )
        content.add(layout)

        popup.add("Assets", "title")
        popup.add(content, "content")

        popup_button = IconButtonWdg("Popup",\
            IconWdg.DELETE, long=True)
        popup_button.add_event("onclick", "$('planner').setStyle('display','')")

        main_div.add(popup)
        main_div.add(popup_button)
        '''




        return main_div




class SObjectInstanceAdderCbk(Command):

    def check(self):
        web = WebContainer.get_web()
        if web.get_form_value(SObjectPlannerWdg.ADD_BUTTON) != "":
            return True

    def get_title(self):
        return "Add Instance"

    
    def get_checkbox_names(self):
        ''' returns the class of the left and right CheckboxColWdg'''
        return "left_search_key", "right_search_key"

    def get_search_type(self):
        web = WebContainer.get_web()
        search_type = web.get_form_value("search_type")
        return search_type
        
    def execute(self):

        left_cb_name , right_cb_name = self.get_checkbox_names()
        
        web = WebContainer.get_web()

        right_search_keys = web.get_form_values(right_cb_name)
        if not right_search_keys:
            return

        right_sobjects = []
        for right_search_key in right_search_keys:
            right_sobject = Search.get_by_search_key(right_search_key)
            right_sobjects.append(right_sobject)

        search_type = self.get_search_type()

        left_search_keys = web.get_form_values(left_cb_name)
        for left_search_key in left_search_keys:

            left_sobject = Search.get_by_search_key( left_search_key )
            for right_sobject in right_sobjects:
                #instance_name = "%s" % right_sobject.get_value("name")

                left_foreign_key = left_sobject.get_foreign_key()
                right_foreign_key = right_sobject.get_foreign_key()

                instance = SObjectFactory.create(search_type)
                instance.set_value(left_foreign_key, left_sobject.get_code() )
                instance.set_value(right_foreign_key, right_sobject.get_code() )

                name = left_sobject.get_code()
                instance.set_value("name", name)
                instance.commit()



class SObjectInstanceRemoverCbk(Command):

    def get_title(self):
        return "Retire/Delete Instance"

    def check(self):
        web = WebContainer.get_web()
        if web.get_form_value("Delete Instance") == "":
            self.mode = "delete"
        elif web.get_form_value("Retire Instance") == "":
            self.mode = "retire"
        else:
            return False

        return True


    def execute(self):

        web = WebContainer.get_web()

        select_keys = web.get_form_values("select_instance")
        for select_key in select_keys:
            sobject = Search.get_by_search_key( select_key )
            # NOTE: should probably check if there are any snapshots before
            # deleting

            if self.mode == "retire":
                sobject.retire()
                self.add_description("Retired [%s]" % sobject.get_code() )
            elif self.mode == "delete":
                sobject.delete()
                self.add_description("Deleted [%s]" % sobject.get_code() )





class NumSObjectInstancesWdg(FunctionalTableElement):
    '''Lists the number of instances in a shot'''
    def init(self):
        self.numbers = {}

    def get_title(self):
        return "#"

    def preprocess(self):

        sobjects = self.sobjects
        if not sobjects:
            return

        # find all of the instances in a shot
        sobject = sobjects[0]
        foreign_key = sobject.get_foreign_key()

        search_type = WebState.get().get_state("planner_search_type")
        search = Search( search_type )

        search.add_column(foreign_key)

        if len(sobjects) == 1:
            search.add_filter(foreign_key, sobject.get_code())
        else:
            search_codes = [x.get_code() for x in sobjects]
            search.add_filters(foreign_key, search_codes)

        search_type = sobject.get_search_type()
        search.add_order_by(foreign_key)
        children = search.get_sobjects()

        # convert to a dictionary
        for child in children:
            code = child.get_value(foreign_key)
            number = self.numbers.get(code)
            if not number:
                number = 0
           
            number += 1
            self.numbers[code] = number

        #print self.numbers
 


    def get_display(self):
        sobject = self.get_current_sobject()
        number = self.numbers.get(sobject.get_code())
        if not number:
            return "&nbsp;"
        return "(%d)" % number



class SObjectInstanceListWdg(Widget):
    def get_search_type(self):
        web = WebContainer.get_web()
        search_type = web.get_form_value("planner_search_type")
        assert( search_type )
        return search_type

    def get_display(self):

        web = WebContainer.get_web()
        args = web.get_form_args()

        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']

        sobject = Search.get_by_search_key("%s|%s" % (search_type,search_id) )

        planner_search_type = self.get_search_type()


        # get parent instances first
        '''
        all_instances = []
        parent_code = ""
        if sobject.has_value("parent_code"):
            parent_code = sobject.get_value("parent_code")
        if parent_code != "":
            parent = sobject.get_by_code(parent_code)

            search = Search(planner_search_type)
            search.add_filter(sobject.get_foreign_key(), parent.get_code())
            instances = search.get_sobjects()

            all_instances.extend(instances)
        '''


        search = Search(planner_search_type)
        search.add_filter(sobject.get_foreign_key(), sobject.get_code())
        instances = search.get_sobjects()
        #all_instances.extend(instances)

        widget = DivWdg()
        widget.add( HiddenWdg("planner_search_type", planner_search_type) )
        widget.add_style("width: 95%")
        widget.add_style("float: right")
        table = TableWdg(search_type, "layout", css='minimal')
        table.table.set_max_width(use_css=True)
        #table.set_sobjects(all_instances)
        table.set_search(search)
        table.do_search()
        table.set_show_property(False)

        #aux_data = ShotInstance.get_aux_data(all_instances)
        #table.set_aux_data(aux_data)
        widget.add(table)
        return widget


