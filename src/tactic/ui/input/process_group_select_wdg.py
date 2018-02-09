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
from pyasm.web import DivWdg, SpanWdg
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

    def init(self):
        pass

    def get_display(self):
        self.labels_attr =  self.get_option('label_attr')
        if self.labels_attr:
            self.labels_attr = self.labels_attr.split('|')
        else:
            self.labels_attr = ["display_name"]

        from tactic.ui.panel import EditWdg
        if hasattr(self, 'parent_wdg') and isinstance(self.get_parent_wdg(), EditWdg):
            sobject = self.get_current_sobject()
            parent = sobject.get_parent()
            group = None
            pipeline_code = None

            if parent:
                pipeline_code = parent.get_value('pipeline_code')
            pipeline = Pipeline.get_by_code(pipeline_code)
            
            labels_expr = None

            if pipeline:
                attrs = pipeline.get_process_attrs(sobject.get_value('process'))
                group = attrs.get('%s_login_group'%self.get_name())
            if group:
            
                values_expr = "@GET(sthpw/login_group['login_group', '%s'].sthpw/login_in_group.sthpw/login.login)"%group
                if self.labels_attr:
                    labels_expr = ["@GET(sthpw/login_group['login_group', '%s'].sthpw/login_in_group.sthpw/login.%s)"%(group, x.strip()) for x in self.labels_attr]
                    labels_expr =  ' + &nbsp + '.join(labels_expr)
            else:
                values_expr = "@GET(sthpw/login.login)"
                if self.labels_attr:
                    labels_expr = ["@GET(sthpw/login.%s)"%(x.strip()) for x in self.labels_attr]
                    labels_expr =  ' + &nbsp + '.join(labels_expr)
            select = SelectWdg(self.get_input_name())
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
            current_value = sobject.get_value(self.get_name())
            if current_value:
                select.set_value(current_value)
            return select


        #all_users = Search.eval("@GET(sthpw/login.login)")
        all_users = Search.eval("@SOBJECT(sthpw/login)")
        all_users_label =  []
        
        # don't use expression here since it's not as db-efficient as retrieving the sobjects
        """
        if self.labels_attr:
            labels_expr = ["@GET(sthpw/login.login.%s)"%x.strip() for x in self.labels_attr]
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


        top = DivWdg()
        
        top.add_class("spt_input_top")

        # HACK! This isn't very well constructed
        ### Tore: Not self code! Copied from ProcessContextInputWdg. Seems to work though.
        top.add_attr("spt_cbjs_get_input_key", "return cell_to_edit.getAttribute('spt_pipeline_code');")
        
        # Adding an "all users" select option in case it can't find a useful select widget.
        div = DivWdg()
        div.add_class("spt_input_option")
        #div.add_attr("spt_input_key", '__all__') #Not needed, since it defaults to the first one anyway.
        select = SelectWdg(self.get_name())
        select.add_empty_option("-- Select a User --")
        values = []
        labels = []
        labels_dict = {}
        for user in all_users:
            user_name = user.get_value('login')
            values.append(user_name)

            label = user.get_value("display_name")
            if not label:
                label = user_name

            if self.labels_attr:
                user_labels = [user.get_value(x) for x in self.labels_attr]
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
            
            select = SelectWdg(self.get_name())
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
    def handle_td(self, td):
        super(LoginTableElementWdg, self).handle_td(td)
        task = self.get_current_sobject()
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
                
                    td.add_attr('spt_pipeline_code', attrs.get('%s_login_group'%self.get_name()))
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

    def get_value(self, name=None):
        if not name:
            name = self.get_name()

        div = DivWdg()
        div.add_style("display: inline-block")

        value = super(LoginTableElementWdg, self).get_value(name)
        if value:
            user = Search.get_by_code("sthpw/login", value)
            if user:
                value = user.get_value("display_name") or value

        #return value

        self.sobject = self.get_current_sobject()

        if self.is_editable() and not value:
            empty = SpanWdg()
            div.add(empty)
            div.add_style("text-align: center")
            div.add_style("width: 100%")
            div.add_style("white-space: nowrap" )
            empty.add("--Select--")
            empty.add_style("opacity: 0.5")
            return div

        div.add(value)

        # display a link if specified
        link_expr = "@SOBJECT(sthpw/login)"
        if self.sobject and link_expr:
            # using direct behavior because new_tab isn't working consistently
            #div.add_class("tactic_new_tab")
            div.add_style("text-decoration", "underline")
            #div.add_class("tactic_new_tab")
            div.add_attr("search_key", self.sobject.get_search_key())
            div.add_attr("expression", link_expr)
            div.add_class("hand")

            search_type_sobj = self.sobject.get_search_type_obj()
            sobj_title = value

            #name = self.sobject.get_value("name", no_exception=True)
            name = None
            if not name:
                name = self.sobject.get_code()
            div.add_attr("name", value)

            # click up blocks any other behavior
            div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.table.open_link(bvr);
                '''
            } )



        return div

