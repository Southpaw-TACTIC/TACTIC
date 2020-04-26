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


__all__ = ['SObjectGroupWdg', 'SObjectGroupCmd', 'ItemInContainerWdg']

from pyasm.web import *
from pyasm.security import Login
from pyasm.search import Search, SObjectConfig, SearchType, SObjectFactory
from pyasm.command import Command
from pyasm.widget import CheckboxWdg, IconWdg, IconSubmitWdg, HiddenRowToggleWdg, HiddenWdg



class SObjectGroupWdg(Widget):
    GROUP_TABLE_NAME = 'group_tbl'
    ADD_LABEL = 'Add'

    def __init__(self, item_cls, container_cls, grouping_cls, name="SObjectGroupWdg"):
        self.item_cls = item_cls
        self.item_sobj = self.container_sobj = None 
        self.container_cls = container_cls
        self.grouping_cls  = grouping_cls
        super(SObjectGroupWdg, self).__init__()

        
    def init(self):
        
        
        # List the items
        search = Search(self.item_cls.SEARCH_TYPE)
        self._order_search(search)    
        
        items = search.get_sobjects()
        if items:
            self.item_sobj = items[0]
        #select = MultiSelectWdg("item_ids")
        #select.set_search_for_options(search,"login", "get_full_name()")

        user_span = SpanWdg(css='med')
        
        user_table = Table(css='table')
        user_table.add_style("margin-left: 6px")
        user_table.set_max_width()
        user_table.add_col(css='small')
        user_table.add_col()
        
        user_table.add_style("min-width: 14em")
        user_table.add_row_cell(search.get_search_type_obj()\
            .get_description(), "heading")

        for item in items:
            user_table.add_row()
            checkbox = CheckboxWdg("item_ids")
            checkbox.set_option("value", item.get_primary_key_value() )
            user_table.add_cell( checkbox )

            project_code = item.get_value("project_code", no_exception=True)
            if project_code:
                user_table.add_cell( "[ %s ]" % project_code )
            else:
                user_table.add_cell( "[ * ]" )

            user_table.add_cell( item.get_description() )
        user_span.add(user_table)

        # control widget in the middle
        control_div = DivWdg()
        control_div.add_style('padding: 100px 10px 0 10px')

        button = IconSubmitWdg(self.ADD_LABEL, IconWdg.INSERT, True)
        button.add_style('padding: 2px 30px 4px 30px')
        control_div.add(button)
        
        
        main_table = Table(css='collapse')
        main_table.set_max_width()
        main_table.add_row(css='plain_bg')
        main_table.add_cell(user_span, 'valign_top')
        td = main_table.add_cell(control_div, 'valign_top')
        td.add_style('width','12em')
        main_table.add_cell(self._get_target_span(), 'valign_top')

        self.add(main_table)
    
        # register command here
        if self.item_sobj and self.container_sobj:
            marshaller = WebContainer.register_cmd("pyasm.widget.SObjectGroupCmd")
            marshaller.set_option("grouping_search_type", self.grouping_cls.SEARCH_TYPE)
            marshaller.set_option("item_foreign_key", self.item_sobj.get_foreign_key())
            marshaller.set_option("container_foreign_key", self.container_sobj.get_foreign_key())
        
    def _order_search(self, search):
        config = SObjectConfig.get_by_search_type(search.get_search_type_obj())
        if config:
            search.add_order_by(config.get_order_by())
            
    def _get_target_span(self):
        # get the target span
        search = Search(self.container_cls.SEARCH_TYPE)
        self._order_search(search)
        groups = search.get_sobjects()
        if groups:
            self.container_sobj = groups[0]
        
        target_span = SpanWdg(css='med')
        group_table = Table(self.GROUP_TABLE_NAME, css='table')
        group_table.add_style('width','30em')
        group_table.add_col(css='small')
        group_table.add_col(css='small')    
        group_table.add_col()    
            
        target_span.add(group_table)
        group_table.add_row_cell(search.get_search_type_obj()\
            .get_description(), "heading")
        checkbox = CheckboxWdg()
        checkbox.set_option("onclick", \
            "a=new Elements('container_ids');a.toggle_all(this);")
        group_table.add_row()
        group_table.add_cell(checkbox)
        col_name = group_table.get_next_col_name() 
        
        toggle_control = HiddenRowToggleWdg(col_name, is_control=True, auto_index=True)
      
        group_table.add_cell(toggle_control)
        group_table.add_cell('MASTER CONTROL')
        
        remove_cmd = HiddenWdg(SObjectGroupCmd.REMOVE_CMD)
        self.add(remove_cmd)
        for group in groups:
            group_table.add_row()
            checkbox = CheckboxWdg("container_ids")
            checkbox.set_option("value", group.get_primary_key_value() )
            
            toggle = HiddenRowToggleWdg(col_name, auto_index=True)
            toggle.store_event()
         
            group_details = ItemInContainerWdg( group, self.item_sobj, self.item_cls, self.grouping_cls )
           
            # set the target content of the toggle
            toggle.set_static_content(group_details)
           
            group_table.add_cell( checkbox )
            group_table.add_cell( toggle, add_hidden_wdg=True )
            group_table.add_cell( group.get_description())
            num_items = group_details.get_num_items()
            if num_items:
                td = group_table.add_cell( "( %s )" % num_items, 'no_wrap')
                td.add_style('color: #777')
            else:
                group_table.add_blank_cell()
       
        
        return target_span

class ItemInContainerWdg(HtmlElement):
   
    def __init__(self, group, item_sobj, item_cls, grouping_cls):
        self.group = group
        self.item_cls = item_cls
        self.item_sobj = item_sobj
        self.grouping_cls = grouping_cls
        super(ItemInContainerWdg, self).__init__('div')


    def init(self):
        assert self.group != None
        self.items = self.get_items()


    def get_num_items(self):
        return len(self.items)


    def get_items(self):
        if not self.item_sobj:
            return []
        search = Search( self.item_cls.SEARCH_TYPE )
        query = "%s in (select %s from %s where \
            %s = '%s')" % (self.item_sobj.get_primary_key(), \
            self.item_sobj.get_foreign_key(), \
            SearchType.get(self.grouping_cls.SEARCH_TYPE).get_table(),\
            self.group.get_foreign_key(),\
            self.group.get_value(self.group.get_primary_key()))
        
        search.add_where(query)    
        return search.get_sobjects()
    
    def set_group_name(self, group_name):
        self.group_name = group_name
        
    def get_display(self): 
        #self.init()
        item_table = Table(css='minimal')
        item_table.add_style('margin-left','30px')
       
        for item in self.items:
            item_table.add_row()
            space_td = item_table.add_blank_cell()
            
            item_td = item_table.add_cell(item.get_description())
            item_td.set_attr("nowrap", "1")
            
            delete = IconSubmitWdg("Remove from group", \
                IconWdg.DELETE, add_hidden=False)
            delete.add_event("onclick","document.form.remove_cmd.value=\
                '%s|%s';document.form.submit();" \
                % (self.group.get_primary_key_value(), item.get_primary_key_value()) )
            del_span = SpanWdg(css='med')
            del_span.add(delete)
            item_table.add_cell(del_span)
        if not self.items:
            item_table.add_blank_cell()
       
        self.add(item_table)
        return super(ItemInContainerWdg, self).get_display()

class SObjectGroupCmd(Command):

    REMOVE_CMD = 'remove_cmd'
    def get_title(self):
        return "Associate sobjects by grouping"
        
    
    def check(self):
        self.add = WebContainer.get_web().get_form_value(\
            SObjectGroupWdg.ADD_LABEL) != ''
        self.remove = WebContainer.get_web().get_form_value(\
            SObjectGroupCmd.REMOVE_CMD) != ''
        if self.add or self.remove:
            if self.grouping_search_type and self.item_foreign_key and \
                    self.container_foreign_key:
                return True
        else:
            return False

    def set_grouping_search_type(self, search_type):
        self.grouping_search_type = search_type    
        
    def set_item_foreign_key(self, foreign_key):
        self.item_foreign_key = foreign_key

    def set_container_foreign_key(self, foreign_key):
        self.container_foreign_key = foreign_key

    def create_grouping(self, item_value, container_value):
        grouping = self._get_existing_grouping(item_value, container_value)
        if grouping:
            return grouping
        sobject = SObjectFactory.create( self.grouping_search_type )
        sobject.set_value( self.item_foreign_key, item_value)
        sobject.set_value( self.container_foreign_key, container_value)
        sobject.commit()
        return sobject

    def remove_grouping(self, item_value, container_value):
        grouping = self._get_existing_grouping(item_value, container_value)
        if grouping:
            grouping.delete()
            
    def _get_existing_grouping(self, item_value, container_value):
        search = Search( self.grouping_search_type )
        search.add_filter( self.item_foreign_key, item_value)
        search.add_filter( self.container_foreign_key, container_value)
        return search.get_sobject()
    
    def execute(self):
        web = WebContainer.get_web()
        if self.add:
            self.description = "Add items for [%s]" % self.grouping_search_type
            item_ids = web.get_form_values("item_ids")
            container_ids = web.get_form_values("container_ids")
            
            for item_id in item_ids:
                # add to all of the groups
                for container_id in container_ids:
                     self.create_grouping(item_id, container_id)

        elif self.remove:
            self.description = "Remove items for [%s]" % self.grouping_search_type
            remove_cmd = web.get_form_value(self.REMOVE_CMD)
            tmp = remove_cmd.split('|')
            if len(tmp) == 2:
                container_id = tmp[0]
                item_id = tmp[1]
                self.remove_grouping(item_id, container_id)
            




