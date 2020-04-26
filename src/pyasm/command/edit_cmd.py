##########################################################
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

#__all__ = ["EditCmdException", "EditCmd", "EditAllCmd", "InsertMultiCmd"]
__all__ = []


import string, sys

from command import *

from pyasm.common import *
from pyasm.search import *

class EditCmdException(Exception):
    pass

  
# DEPRECATED        
class EditCmd(Command):

    def __init__(self, **kwargs):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        # get the view
        self.view = kwargs.get("view")
        if not self.view:
            self.view = web.get_form_value("view")
        if not self.view:
            self.view = "edit"

        self.search_key = kwargs.get("search_key")
        self.element_names = kwargs.get("element_names")
        self.input_prefix = kwargs.get('input_prefix')
        if not self.input_prefix:
            self.input_prefix = "edit"
        elif self.input_prefix == "__NONE__":
            self.input_prefix = ""
        


        super(EditCmd,self).__init__()
        self.search_type = None
        self.sobject = None


    def get_title(self):
        return "Insert/Edit Asset"


    def get_default_action_handler(self):
        return "DatabaseAction"


    def check(self):
        '''this should return True by default now since it is not run
           by default'''
        return True

       
       
    def execute(self):
        # for now just do an execute single
        self._execute_single()


    def _get_action_handlers(self):

        # get all of the element names for this asset
        search_type_obj = SearchType.get(self.search_type)

        # if element names are not specified, then get it from the view
        from pyasm.widget.widget_config import WidgetConfigView, WidgetConfig
        if not self.element_names:
            config = WidgetConfigView.get_by_search_type(search_type_obj, self.view)
            self.element_names = config.get_element_names()

        else:
            # FIXME: do we just a WidgetConfig here????
            base_view = self.view
            config = WidgetConfigView.get_by_element_names(self.search_type, self.element_names, base_view=base_view)


        assert self.element_names
        assert config


        # create all of the handlers
        action_handlers = []

        for element_name in (self.element_names):
            action_handler_class = \
                config.get_action_handler(element_name)
            if action_handler_class == "":
                action_handler_class = self.get_default_action_handler()


            action_handler = WidgetConfig.create_widget( action_handler_class )
            action_handler.set_name(element_name)
            action_handler.set_input_prefix(self.input_prefix)
            action_options = config.get_action_options(element_name)
            for key,value in action_options.items():
                action_handler.set_option(key, value)



            action_handlers.append(action_handler)

        return action_handlers
 




    def _execute_single(self):
        #  only do actions if the edit button has been pressed
        
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        #if web.get_form_value("do_edit") == "":
        #    return

       
        no_commit = (web.get_form_value("sobject_commit") == 'false')


        sobject = None
        if self.search_key:
            sobject = SearchKey.get_by_search_key(self.search_key)
            # this is needed for action handler below
            self.search_type = sobject.get_search_type()
            #search_id = sobject.get_id()

        else:
            # get the search type and search id
            self.search_type = web.get_form_value("search_type")
            if self.search_type == "":
                raise EditCmdException( "Search type not found" )
            search_id = web.get_form_value("search_id")
            if search_id == "":
                raise EditCmdException( "Search id not found" )
     

            # get the search object based on these parameters
            if search_id == "" or search_id == "-1":
                sobject = SObjectFactory.create(self.search_type)
            
            else:
                search = Search(self.search_type)
                search.add_id_filter( search_id )
                sobject = search.get_sobject()

                # there has to be an sobject to edit
                if sobject == None:
                    raise EditCmdException("No sobject found with search type [%s] and id [%s]" % (self.search_type, search_id) )


        action_handlers = self._get_action_handlers()

        # set the sobject foreach action handler
        for action_handler in action_handlers:
            action_handler.set_sobject(sobject)
            if action_handler.check():
                action_handler.execute()


        if sobject.is_insert():
            action = "Inserted"
        else:
            action = "Updated"

        # before we commit, we set what got changed in the info
        update_data = sobject.update_data
        for key, value in update_data.items():
            # don't include None
            if value != None:
                self.info[key] = value
            


        # commit the changes unless told not to
        if not no_commit:
            sobject.commit()
            # ask the sobject for the description
            self.add_description( sobject.get_update_description() )
        self.sobject = sobject
        # post process each action handers, post commit
        for action_handler in action_handlers:
            action_handler.postprocess()
            action_desc = action_handler.get_description()
            if action_desc:
                self.add_description(action_desc)


        

        # add the necessary date for triggers
        self.sobjects.append(sobject)
        self.info['action'] = action




class EditAllCmd(Command):
    '''Edit one single element of all the sobjects displayed.''' 
    def __init__(self):
        from pyasm.web import WebContainer
        self.web = WebContainer.get_web()
        self.view = self.web.get_form_value("view")
        if self.view == "":
            self.view = "edit"

        super(EditAllCmd,self).__init__()
        self.search_type = None
        self.element_name = None
        self.sobject = None

    def get_title(self):
        return "Edit All Displayed Assets"


    def get_default_action_handler(self):
        return "DatabaseAction"

    def check(self):
        # only do actions if the edit_all button has been pressed
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        if web.get_form_value("edit_all"):
            return True

        return False

       
    def execute(self):
        # get the search type and search id
        self.search_type = self.web.get_form_value("search_type")
        
        if self.search_type == "":
            raise EditCmdException( "Search type not found" )
        search_type_base = SearchType.get(self.search_type).get_base_key()
        search_ids = self.web.get_form_value("%s_search_ids" %search_type_base)
        
        # selected key is used instead of the search_ids 
        from pyasm.widget import EditCheckboxWdg 
        selected_keys = self.web.get_form_value(EditCheckboxWdg.CB_NAME)

        # search_ids is not really used but it should exist
        if search_ids == "":
            raise EditCmdException( "Search ids not found" )


        if selected_keys: # e.g. 123|V|153 (just an id, search_type omitted) 
            # these values come from Elements.get_value() in Common.js
            # they should be delimited by |V| 
            search_ids = selected_keys.split("|V|")
        else:
            raise UserException('No [%s] were selected! Please close this '\
                'pop-up and select the checkboxes first.' \
                %SearchType.get(self.search_type).get_description())
        
        # get the search object based on these parameters
        sobjects = None
        search = Search(self.search_type)
        search.set_show_retired(True)
        search.add_filters('id', search_ids)
        sobjects = search.get_sobjects()
        
        # there has to be an sobject to edit
        if not sobjects:
            raise EditCmdException("No sobject found with search type [%s] and id [%s]" % (self.search_type, search_ids) )

        action_handlers = self._get_action_handlers()
        action = "Updated"
        
        for sobject in sobjects:
            for action_handler in action_handlers:
                action_handler.set_sobject(sobject)
                if action_handler.check():
                    action_handler.execute()
            
            # commit the changes
            sobject.commit()
            self.sobject = sobject
            # post process each action handlers, post commit
            for action_handler in action_handlers:
                action_handler.postprocess()

            # add a description to this command
        self.add_description( "%s search type: '%s', ids = %s" \
                % (action, self.search_type,  search_ids))
                
            


    def _get_action_handlers(self):
        from pyasm.widget.widget_config import WidgetConfig, WidgetConfigView

        
        # get all of the element names for this asset
        search_type_obj = SearchType.get(self.search_type)

        # get the sobject config
        default_config = WidgetConfig.get_default( \
            search_type_obj,self.view)

        config = WidgetConfigView.get_by_search_type(search_type_obj,self.view)
        
        from pyasm.widget import EditAllWdg
        from pyasm.web import WebContainer
        element_name = WebContainer.get_web().get_form_value(\
            EditAllWdg.ELEMENT_NAME)
        
        # store action handlers in a list, only getting one for now
        action_handlers = []

        action_handler_class = \
            config.get_action_handler(element_name)

        # else get it from the default handler
        if default_config != None and action_handler_class == "":
            action_handler_class = \
                default_config.get_action_handler(element_name)

        if action_handler_class == "":
            action_handler_class = self.get_default_action_handler()
        action_handler = WidgetConfig.create_widget( action_handler_class )
        action_handler.set_name(element_name)
        action_handler.set_input_prefix(self.input_prefix)

        action_handlers.append(action_handler)

        return action_handlers


class InsertMultiCmd(EditCmd):

    def check(self):
        # only do actions if the insert_all button has been pressed
        from pyasm.web import WebContainer
        from pyasm.widget import InsertMultiWdg
        web = WebContainer.get_web()
        if web.get_form_value(InsertMultiWdg.INSERT_MULTI):
            self.insert_elem = web.get_form_value(InsertMultiWdg.ELEMENT_NAME)
            if self.insert_elem:
                return True
        return False

    def execute(self):
        
        from pyasm.web import WebContainer
        from pyasm.widget import CreateSelectWdg
        web = WebContainer.get_web()
        if self.insert_elem:
            items_value = web.get_form_value('%s|%s' %(self.insert_elem, CreateSelectWdg.SELECT_ITEMS))
            values = items_value.split('||')
            for value in values:
                if not value:
                    continue
                self._execute_single(value)


    def _execute_single(self, value):
        #  only do actions if the edit button has been pressed
        
        from pyasm.web import WebContainer

        web = WebContainer.get_web()
       
        # get the search type and search id
        self.search_type = web.get_form_value("search_type")

        if self.search_type == "":
            raise EditCmdException( "Search type not found" )
        search_id = web.get_form_value("search_id")
        if search_id == "":
            raise EditCmdException( "Search id not found" )
        
        # get the search object based on these parameters
        sobject = None
        if search_id == "" or search_id == "-1":
            sobject = SObjectFactory.create(self.search_type)
        
        else:
            raise TacticException('Search id should be empty for multiple insertion ""') 

        action_handlers = self._get_action_handlers()

        # set the sobject foreach action handler
        for action_handler in action_handlers:
            action_handler.set_sobject(sobject)
            # preset the value externally
            if action_handler.get_name() == self.insert_elem:
                action_handler.set_value(value)
            if action_handler.check():
                action_handler.execute()

        action = "Inserted"
        
        # before we commit, we set what got changed in the info
        update_data = sobject.update_data
        for key, value in update_data.items():
            self.info[key] = value
       
        sobject.commit()
        # ask the sobject for the description
        self.add_description( sobject.get_update_description() )
        self.sobject = sobject
        # post process each action handers, post commit
        for action_handler in action_handlers:
            action_handler.postprocess()
            action_desc = action_handler.get_description()
            if action_desc:
                self.add_description(action_desc)


        # add the necessary date for triggers
        self.sobjects.append(sobject)
        self.info['action'] = action


