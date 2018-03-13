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

__all__ = ["EditCmdException", "EditCmd", "EditMultipleCmd"]


import string, sys, types


from pyasm.common import *
from pyasm.search import Search, SearchType, SearchKey, SqlException
from pyasm.command import Command
from pyasm.common import TacticException

class EditCmdException(Exception):
    pass

  
        
class EditCmd(Command):

    def __init__(self, **kwargs):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        # get the view
        self.view = kwargs.get("view")
        if not self.view:
            self.view = "edit"

        self.search_key = kwargs.get("search_key")




        self.trigger_mode = kwargs.get("trigger_mode")
        if self.trigger_mode == None:
            self.trigger_mode = True


        # if data is passed in, then use this as the form values
        self.data = kwargs.get("data")
        if self.data != None:
            self.element_names = self.data.keys()
        else:
            self.element_names = kwargs.get("element_names")


        # a special variable can be passed through called __data__.  This
        # comes from the EditWdg form
        form_data = web.get_form_value("__data__")
        if form_data:
            form_data = jsonloads(form_data)
            self.config_xml = form_data.get("config_xml")
            if not self.config_xml:
                self.config_xml = None
            else:
                self.config_xml = self.config_xml.replace("&", "&amp;")
        else:
            form_data = {}
            self.config_xml = None


        self.multiplier = 1
        self.multiplier_str = kwargs.get("multiplier")
        if not self.multiplier_str:
            self.multiplier_str = web.get_form_value("multiplier")
            if self.multiplier_str:
                try:
                    self.multiplier = int(self.multiplier_str)
                except:
                    pass



        self.parent_key = kwargs.get("parent_key")
        self.connect_key = kwargs.get("connect_key")
        self.input_prefix = kwargs.get('input_prefix')
        if not self.input_prefix:
            self.input_prefix = "edit"
        elif self.input_prefix == "__NONE__":
            self.input_prefix = ""

        self.extra_data = kwargs.get("extra_data") or {}
        if isinstance(self.extra_data, basestring):
            self.extra_data = jsonloads(self.extra_data)

        self.extra_action = kwargs.get("extra_action") or {}

        super(EditCmd,self).__init__()
        self.search_type = None
        self.sobject = kwargs.get("sobject")


    def get_sobject(self):
        return self.sobject


    def is_api_executable(self):
        return True


    def get_title(self):
        return "Insert/Edit Item"


    def get_default_action_handler(self):
        return "DatabaseAction"


    def check(self):
        '''this should return True by default now since it is not run
           by default'''
        return True

       
       
    def execute(self):
        last_sobject = None
        last_code = None
        last_name = None
        for index in range(0,self.multiplier):
            if last_code:
                code = Common.get_next_code(last_code)
            else:
                code = None
            if last_name:
                name = Common.get_next_code(last_name)
            else:
                name = None
            last_sobject = self._execute_single(code, name=name)
            last_code = last_sobject.get_value("code", no_exception=True)
            last_name = last_sobject.get_value("name", no_exception=True)





    def _get_action_handlers(self):

        # get all of the element names for this asset
        search_type_obj = SearchType.get(self.search_type)

        # discover any default handlers
        default_elements = []


        from pyasm.widget.widget_config import WidgetConfigView, WidgetConfig
        tmp_config = WidgetConfigView.get_by_search_type(self.search_type, self.view)

        tmp_element_names = tmp_config.get_element_names()

        for element_name in tmp_element_names:
            action_handler = tmp_config.get_action_handler(element_name)
            if action_handler == 'DefaultValueDatabaseAction':
                default_elements.append(element_name)




        # if element names are not specified, then get it from the view
        if not self.element_names:
            config = WidgetConfigView.get_by_search_type(search_type_obj, self.view)
            self.element_names = config.get_element_names()


        elif self.config_xml:
            config = WidgetConfigView.get_by_search_type(search_type_obj, self.view)
            extra_config = WidgetConfig.get(view="tab", xml=self.config_xml)
            config.get_configs().insert(0, extra_config)

        else:
            base_view = self.view
            config = WidgetConfigView.get_by_element_names(self.search_type, self.element_names, base_view=base_view)


        # as a back up look up the definition in the view
        display_view = "table"
        display_config = WidgetConfigView.get_by_search_type(search_type_obj, display_view)


        # add the default elements
        for element_name in default_elements:
            if element_name not in self.element_names:
                self.element_names.append(element_name)


        assert self.element_names
        assert config

        # create all of the handlers
        action_handlers = []

        for element_name in self.element_names:

            action_handler_class = \
                    config.get_action_handler(element_name)

            # Try to get it from the display view
            if not action_handler_class:
                display_class = \
                        display_config.get_display_handler(element_name)
                try:
                    stmt = Common.get_import_from_class_path(display_class)
                    exec(stmt)
                    action_handler_class = eval("%s.get_default_action()" % display_class)
                except Exception as e:
                    #print("WARNING: ", e)
                    action_handler_class = ""

            if action_handler_class == "":
                action_handler_class = self.get_default_action_handler()

            action_handler = WidgetConfig.create_widget( action_handler_class )
            action_handler.set_name(element_name)
            action_handler.set_input_prefix(self.input_prefix)
            action_options = config.get_action_options(element_name)

            if self.data != None:

                element_data = self.data.get(element_name)
                action_handler.set_data(element_data)

            for key, value in action_options.items():
                action_handler.set_option(key, value)


            action_handlers.append(action_handler)





        # handle extra_actions
        for action_handler_class, data in self.extra_action.items():

            element_name = action_handler_class

            action_handler = Common.create_from_class_path(action_handler_class)
            action_handler.set_name(element_name)
            action_handler.set_input_prefix(self.input_prefix)

            if self.data != None:
                element_data = self.data.get(element_name)
                action_handler.set_data(element_data)

            for key, value in data.items():
                action_handler.set_option(key, value)

            action_handlers.append(action_handler)





        return action_handlers
 




    def _execute_single(self, code, name=None):
        #  only do actions if the edit button has been pressed
        
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

       
        no_commit = (web.get_form_value("sobject_commit") == 'false')


        sobject = None
        if self.search_key:
            sobject = SearchKey.get_by_search_key(self.search_key)
            if not sobject:
                raise TacticException('This search key [%s] no longer exists.'%self.search_key)
            # this is needed for action handler below
            self.search_type = sobject.get_search_type()

        elif self.sobject:
            sobject = self.sobject
            self.search_type = sobject.get_search_type()

        else:
            # get the search type and search id
            self.search_type = web.get_form_value("search_type")
            if self.search_type == "":
                raise EditCmdException( "Search type not found" )
            search_id = web.get_form_value("search_id")
     
            # get the search object based on these parameters
            if search_id == "" or search_id == "-1":
                sobject = SearchType.create(self.search_type)
            
            else:
                search = Search(self.search_type)
                search.add_id_filter( search_id )
                sobject = search.get_sobject()

                # there has to be an sobject to edit
                if sobject == None:
                    raise EditCmdException("No sobject found with search type [%s] and id [%s]" % (self.search_type, search_id) )

        action_handlers = self._get_action_handlers()

        # set the sobject for each action handler
        for action_handler in action_handlers:

            action_handler.set_sobject(sobject)
            if action_handler.check():
                if self.parent_key:
                    action_handler.set_option('parent_key', self.parent_key)
                if self.connect_key:
                    action_handler.set_option('connect_key', self.connect_key)
                action_handler.execute()
                

        # set the parent, if there is one and it's in insert
        if sobject.is_insert() and self.parent_key:
            sobject.add_relationship(self.parent_key)


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


        if code:
            sobject.set_value("code", code)

        # only fill in a new with the passed in name if it has been
        # specified
        if name:
            sobject.set_value("name", name)


        for key, value in self.extra_data.items():
            sobject.set_value(key, value)


        # commit the changes unless told not to.
        # NOTE: this prevents any connections to be made
        if not no_commit:
            try:
                if sobject.is_insert():
                    is_insert = True
                else:
                    is_insert = False

                sobject.commit(triggers=self.trigger_mode)
         

                # only connect on insert
                if is_insert and self.connect_key and self.connect_key != "__NONE__":
                    sobject.connect(self.connect_key, "task")

            except SqlException as e:
                msg = "An error was encountered adding this item.  The error reported was [%s]" % e
                raise SqlException(msg)


            # ask the sobject for the description
            self.add_description( sobject.get_update_description() )



        # do a post action
        for action_handler in action_handlers:
            try:
                action_handler.post_execute()
            except Exception as e:
                print "WARNING: ", e




        self.sobject = sobject
        # post process each action handers, post commit
        for action_handler in action_handlers:
            action_handler.postprocess()
            action_desc = action_handler.get_description()
            if action_desc:
                self.add_description(action_desc)


        # add the necessary data for triggers
        self.sobjects.append(sobject)
        self.info['action'] = action
        self.info['search_key'] = SearchKey.get_by_sobject(sobject, use_id=True)
        self.info['sobject'] = sobject.get_sobject_dict()

        return sobject



class EditMultipleCmd(Command):
    '''Do multiple edits in a single call'''

    def execute(self):
        """
        var kwargs = {
            search_keys: search_keys,
            view: 'edit_item',
            element_names: element_names,
            input_prefix: '__NONE__',
            update_data: update_data
        }
        """

        parent_key = self.kwargs.get("parent_key")
        connect_key = self.kwargs.get("connect_key")
        search_keys = self.kwargs.get("search_keys")
        view = self.kwargs.get("view")
        element_names = self.kwargs.get("element_names")
        input_prefix = self.kwargs.get("input_prefix")
        update_data = self.kwargs.get("update_data")
        update_data = jsonloads(update_data)

        trigger_mode = self.kwargs.get("trigger_mode")

        # add the extra data
        extra_data = self.kwargs.get("extra_data")
        extra_data = jsonloads(extra_data)

        # add the extra action
        extra_action = self.kwargs.get("extra_action")
        extra_action = jsonloads(extra_action)

        edit_search_keys = []   # includes inserted ones

        # set the list of web_data coming in usually from inline edit element
        # like gantt or work hours
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        web_data = web.get_form_value("web_data")
        web_data_list = None
        if web_data:
            web_data_list = jsonloads(web_data)


        sk_dict = {}
        search_types = set()
        for i, search_key in enumerate(search_keys):

            data = update_data[i]
            extra = extra_data[i]

            if extra:
                for name, value in extra.items():
                    if not data.has_key(name):
                        data[name] = value

            if web_data_list:
                single_web_data = web_data_list[i]
                web.set_form_value('web_data', single_web_data)

            cmd = EditCmd(
                parent_key = parent_key,
                connect_key = connect_key,
                search_key=search_key,
                view=view,
                data=data,
                input_prefix=input_prefix,
                extra_action=extra_action[i],
                trigger_mode=trigger_mode,
            )
            cmd.execute()

            sobject = cmd.get_sobject()
            search_key = sobject.get_search_key(use_id=True)

            edit_search_keys.append(search_key)

            base_search_type = sobject.get_base_search_type()
            search_types.add( base_search_type )
            sk_data_list = sk_dict.get( base_search_type)
            if not sk_data_list:
                sk_data_list = []
                sk_dict[base_search_type] = sk_data_list

            sk_data_list.append((search_key, data))
            
        self.info['search_keys'] = edit_search_keys

        search_types = list(search_types)
        search_types_label = ", ".join(search_types)

        self.add_description( "Updated [%s] item/s in types [%s]" % (len(search_keys), search_types_label ) )
        # call the done trigger for checkin
        from pyasm.command import Trigger

        prefix = 'update_multi'
        for search_type in search_types:
            sk_data_list = sk_dict.get(search_type)
            grouped_edit_search_keys, data_list = map(list, zip(*sk_data_list))
                
                
            output = {}
            output['search_keys'] = grouped_edit_search_keys
            output['update_data'] = data_list
            Trigger.call(self, "%s|%s" % (prefix, search_type), output)





# FIXME: is this being used??

__all__.append('RelatedDatabaseAction')
from pyasm.command import DatabaseAction
class RelatedDatabaseAction(DatabaseAction):

    def execute(self):
        sobject = self.sobject


        column = self.get_option('column')
        if not column:
            column = self.get_name()

        # much easier to use expression
        expr = self.get_option('expression')
        related_type = self.get_option('search_type')

        value = self.get_value()

        if expr:
            related = sobject.eval(expr)
            if not related:

                # FIXME: this requires an enormous number of variables to get
                # right. The expression know how to build the missing sobjects

                # the sobject needs to be committed in order to perform a
                # relational insert
                if sobject.is_insert():
                    related.commit()

                # create a new one dynamically
                related = SearchType.create(related_type)
                related.add_relationship(sobject)

                # add initial values
                data = self.get_option("data")
                if data:
                    data = jsonloads(str(data))
                    for name, value in data.items():
                        related.set_value(name, value)

                related.commit()

            else:
                # assume by taking the first one
                if type(related) == types.ListType:
                    related = related[0]



        elif related_type:
            related_types = related_type.split(".")

            related = sobject 
            for related_type in related_types:
                next_related = related.get_related_sobject(related_type)
                if not next_related:

                    # the sobject needs to be committed in order to perform a
                    # relational insert
                    if related.is_insert():
                        related.commit()

                    # create a new one dynamically
                    next_related = SearchType.create(related_type)
                    next_related.add_relationship(related)

                    # add initial values
                    data = self.get_option("data")
                    if data:
                        data = jsonloads(str(data))
                        for name, value in data.items():
                            next_related.set_value(name, value)

                    next_related.commit()

                related = next_related


        value = self.get_value()
        related.set_value(column, value)
        #print "setting: ", related.get_search_key(), column, value
        related.commit()



