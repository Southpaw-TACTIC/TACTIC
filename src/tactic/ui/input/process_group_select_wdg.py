###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ProcessGroupSelectWdg', 'LoginTableElementWdg']

from pyasm.search import Search, SearchKey, SearchException
from pyasm.biz import Pipeline
from pyasm.web import DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg
from tactic.ui.common import SimpleTableElementWdg

class ProcessGroupSelectWdg(BaseInputWdg):
    '''This widget builds a select widget '''
    ARGS_KEYS = {

        "label_attr": {
            'description': "a list of | seperated login attributes to show in place of just the login attribute",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Display'
        }
     
        
    }

    def init(my):
        pass

    def get_display(my):
        my.labels_attr =  my.get_option('label_attr')
        if my.labels_attr:
            my.labels_attr = my.labels_attr.split('|')

        from tactic.ui.panel import EditWdg
        if hasattr(my, 'parent_wdg') and isinstance(my.get_parent_wdg(), EditWdg):
            sobject = my.get_current_sobject()
            parent = sobject.get_parent()
            group = None
            pipeline_code = None

            if parent:
                pipeline_code = parent.get_value('pipeline_code')
            pipeline = Pipeline.get_by_code(pipeline_code)
            
            labels_expr = None

            if pipeline:
                attrs = pipeline.get_process_attrs(sobject.get_value('process'))
                group = attrs.get('%s_login_group'%my.get_name())
            if group:
            
                values_expr = "@GET(sthpw/login_group['login_group', '%s'].sthpw/login_in_group.sthpw/login.login)"%group
                if my.labels_attr:
                    labels_expr = ["@GET(sthpw/login_group['login_group', '%s'].sthpw/login_in_group.sthpw/login.%s)"%(group, x.strip()) for x in my.labels_attr]
                    labels_expr =  ' + &nbsp + '.join(labels_expr)
            else:
                values_expr = "@GET(sthpw/login.login)"
                if my.labels_attr:
                    labels_expr = ["@GET(sthpw/login.%s)"%(x.strip()) for x in my.labels_attr]
                    labels_expr =  ' + &nbsp + '.join(labels_expr)
            select = SelectWdg(my.get_input_name())
            select.add_empty_option("-- Select a User --")
            """
            values = []
            labels = []
            for user in group_users:
                values.append(user)
                labels.append('  %s'%user)
            """
            select.set_option('values_expr', values_expr)
            if labels_expr:
                select.set_option('labels_expr', labels_expr)
            current_value = sobject.get_value(my.get_name())
            if current_value:
                select.set_value(current_value)
            return select


        #all_users = Search.eval("@GET(sthpw/login.login)")
        all_users = Search.eval("@SOBJECT(sthpw/login)")
        all_users_label =  []
        
        # don't use expression here since it's not as db-efficient as retrieving the sobjects
        """
        if my.labels_attr:
            labels_expr = ["@GET(sthpw/login.login.%s)"%x.strip() for x in my.labels_attr]
        """
        '''
        groups = Search.eval("@SOBJECT(sthpw/login_group)")
        group_dict = {}
        for group in groups:
            group_users =
Search.eval("@GET(sthpw/login_group['login_group',
'%s'].sthpw/login_in_group.sthpw/login.login)"%group.get_value('login_group'))
            group_dict[group.get_value('login_group')] = group_users
        '''

        logins_dict = {}
        for user in all_users:
            user_name = user.get_value('login')
            logins_dict[user_name] = {}
        group_dict = {}
        items = Search.eval("@SOBJECT(sthpw/login_in_group)")
        for item in items:
             item_login = item.get_value("login")
             if logins_dict.get(item_login) == None:
                 continue
             item_group = item.get_value("login_group")

             group_list = group_dict.get(item_group)
             if group_list == None:
                 group_list = []
                 group_dict[item_group] = group_list
             group_list.append(item_login)


        print "gggg: ", group_dict
            
        
        top = DivWdg()
        
        top.add_class("spt_input_top")

        # HACK! This isn't very well constructed
        ### Tore: Not my code! Copied from ProcessContextInputWdg. Seems to work though.
        top.add_attr("spt_cbjs_get_input_key", "return cell_to_edit.getAttribute('spt_pipeline_code');")
        
        # Adding an "all users" select option in case it can't find a useful select widget.
        div = DivWdg()
        div.add_class("spt_input_option")
        #div.add_attr("spt_input_key", '__all__') #Not needed, since it defaults to the first one anyway.
        select = SelectWdg(my.get_name())
        select.add_empty_option("-- Select a User --")
        values = []
        labels = []
        labels_dict = {}
        for user in all_users:
            user_name = user.get_value('login')
            values.append(user_name)
            label = user_name
            if my.labels_attr:
                user_labels = [user.get_value(x) for x in my.labels_attr]
                label = ' '.join(user_labels)

            labels_dict[user_name] = label
            
            labels.append('%s'%label)
            #print "select ", user_name

        # -- NOTE: leaving this commented out code here for reference. Not sure why this is the case but when
        # --       this click behavior is used instead of a 'change' behavior that forces a blur on select,
        # --       click selection only works for this widget in Firefox and does NOT work in IE
        #
        # select.add_behavior( { 'type': 'click',
        #    'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el );' } )


        # -- Replace previous 'click' behavior with a 'change' behavior to force blur() of select element ...
        # -- this works for both Firefox and IE
        #
        select.add_behavior( { 'type': 'change',
           'cbjs_action': 'bvr.src_el.blur();' } )


        #behavior = {
        #    'type': 'keyboard',
        #    'kbd_handler_name': 'DgTableSelectWidgetKeyInput',
        #}
        #select.add_behavior( behavior )


        select.set_option("values", values)
        select.set_option("labels", labels)
           
        div.add(select)
        top.add(div)
        
        #Building each of the select widgets per group here.
        for group in group_dict.keys():
            div = DivWdg()
            div.add_class("spt_input_option")
            div.add_attr("spt_input_key", group)
            
            select = SelectWdg(my.get_name())
            select.add_empty_option("-- Select a User --")
            values = ['']
            labels = ['<< %s >>'%group]
            for user in group_dict[group]:
                values.append(user)
                label = labels_dict.get(user)
                labels.append('  %s'%label)
            select.add_behavior( { 'type': 'click',
               'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el );' } )
            #behavior = {
            #    'type': 'keyboard',
            #    'kbd_handler_name': 'DgTableSelectWidgetKeyInput',
            #}
            #select.add_behavior( behavior )
            select.set_option("values", values)
            select.set_option("labels", labels)
            
            div.add(select)
            top.add(div)
        
        return top

class LoginTableElementWdg(SimpleTableElementWdg):
    '''This ElementWdg is used to add the group that the given task is looking
    for in ProcessGroupSelectWdg.'''
    def handle_td(my, td):
        super(LoginTableElementWdg, my).handle_td(td)
        task = my.get_current_sobject()
        if task:
            search_type = task.get_value('search_type')
            search_id = task.get_value('search_id')
            
            if not search_type or not search_id:
                return
            
            search_key = SearchKey.build_search_key(search_type, search_id, column='id')
            
            from pyasm.common import SObjectSecurityException
            try:
                parent = Search.get_by_search_key(search_key)
                pipeline = Pipeline.get_by_sobject(parent)
               
                if pipeline:
                    attrs = pipeline.get_process_attrs(task.get_value('process'))
                
                    td.add_attr('spt_pipeline_code', attrs.get('%s_login_group'%my.get_name()))
            except SObjectSecurityException, e:
                pass
            except SearchException, e:
                if e.__str__().find('not registered') != -1:
                    pass
                elif e.__str__().find('does not exist for database') != -1:
                    pass    
                elif e.__str__().find('Cannot find project') != -1:
                    pass
                else:
                    raise


