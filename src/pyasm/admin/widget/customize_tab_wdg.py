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

__all__ = ["CustomizeTabWdg", 'CustomizeTabCbk', 'TabSecurityTableElementWdg', \
'TabSecurityLinkWdg','TabSecurityWdg', 'TabSecurityCbk']

from pyasm.search import Search, SearchType, SObjectFactory
from pyasm.web import WebContainer, Widget, DivWdg, SpanWdg, Table, HtmlElement
from pyasm.widget import *
from pyasm.prod.web import ProdSetting, ProdIconSubmitWdg
from pyasm.common import Container

class CustomizeTabWdg(Widget):

    DEFAULT_ACTION = "invisible"
    APP_TAB = "Maya/Houdini/XSI"
    def init(my):
        my.main_invisible_dict = {}

        my.register_cmd_handler()
        my.add(HelpItemWdg('Customize Tabs', 'You can customize the visibility of the Tabs for this particular project. Check the box beside tabs you want to hide.', False))

    def register_cmd_handler(my):
        WebContainer.register_cmd("pyasm.admin.widget.CustomizeTabCbk")

    def get_display(my):

        widget = Widget()
        main_div = DivWdg()
        main_div.add_class("filter_box")
        
        main_div.add_style('-moz-border-radius','10px')
        div = DivWdg()
        div.add_style('padding-left','10px')
        div.add_style('width','420px')
        main_div.add(my.get_mode_wdg())
        main_div.add(div)
        instructions = "By default, all tabs are made visible. Check the checkboxes for those tabs you want to hide for the current project. Click on the tab group title below to view the checkboxes."
        span = SpanWdg(instructions)
        div.add(span)
        my.invisible_list = my.get_tab_list()

        my.handle_tabs(div)
        div.add(HtmlElement.br(2))
        button = DivWdg(my.get_update_button())
        button.add_style('float','right')
        div.add(button)
        div.add(HtmlElement.br(2))
        widget.add(main_div)
        widget.add(HiddenWdg('update_tab_key'))
        
        return widget

    def get_tab_list(my):
        tab_list = ProdSetting.get_seq_by_key('invisible_tabs')
        return tab_list

        
    def handle_tabs(my, div):
        from pyasm.prod.site import MainTabWdg, MayaTabWdg
        TabWdg.set_mode("check")
        tab_wdg = MainTabWdg()
        div.add( my.get_tab_wdg(tab_wdg, "Main", is_main=True) )

        tabs = tab_wdg.get_widget("tab")
        main_tab_names = tabs.get_tab_names()

        for tab_name in main_tab_names:
            widget = tabs.wdg_dict.get(tab_name)
            widget = tabs.init_widget(widget)
            div.add( my.get_tab_wdg(widget, tab_name))

        tab_wdg = MayaTabWdg()
        div.add( my.get_tab_wdg(tab_wdg, my.APP_TAB, is_main=True) )
        TabWdg.set_mode("normal")
       
        

    def get_update_button(my):
        submit = ProdIconSubmitWdg("Update")
       
        submit.add_event('onclick', "document.form.elements['update_tab_key'].value ='true'")
        #span.add(SpanWdg('&nbsp;', css='med'))
        submit.add_class('small')
        return submit

    

    def get_mode_wdg(my):
        div = DivWdg()
        div.add("<h3>Customize Project Tabs</h3>")
        return div

    """
    def hide_selected(my):
        '''Determines whether to hide the selected subtabs or not'''
        return True
    """ 


    def get_tab_wdg(my, tab_wdg, title, is_main=False):

        tab = tab_wdg.get_widget("tab")
        div = DivWdg(id='tab_group_%s' %title)
        # hide it if it has been set as invisible in the Main Tab
        stored_tab = my.main_invisible_dict.get(title)
        if is_main:
            div.add_style('display','block')
        elif (stored_tab and stored_tab == 'invisible'):
            div.add_style('display','none')
        else:
            div.add_style('display','block')
        

        div.add_style('margin', '8px')
        if not tab:
            return div
        tab_names = tab.get_tab_names()
        table_class='table'
        if is_main:
            table_class='table main_tab_head'
        table = Table(css=table_class)
        table.add_style("width: 400px")
        div.add(table)

        span = SpanWdg(title, css='small')
        
        
        tr = table.add_row()
        tr.add_style('line-height','2em')
        swap = SwapDisplayWdg()
        title_span = SpanWdg(title, css='small')

        swap_th = table.add_header(swap)
        swap_th.add_style('width: 10px')
        th = table.add_header(title_span, css='hand')
        th.add_style("width: 300px")
       
        tbody = table.add_tbody()
        unique_id = tbody.set_unique_id()
        SwapDisplayWdg.create_swap_title(th, swap, tbody)
        
        num_checked = 0
        for tab_name in tab_names:
            if title in ["Main", my.APP_TAB]:
                full_tab_name = tab_name
            else:
                full_tab_name = "%s/%s" % (title, tab_name)

            table.add_row()
            #checkbox = CheckboxWdg("invisible_tabs/%s" %tab.get_tab_key() )
            checkbox = CheckboxWdg("invisible_tabs" )
            if my.invisible_list and full_tab_name in my.invisible_list:
                checkbox.set_checked()
                num_checked += 1
                if is_main:
                    my.main_invisible_dict[tab_name] =  my.DEFAULT_ACTION 
            elif is_main:
                #TODO: this line seems redundant
                my.main_invisible_dict[tab_name] = 'visible'

            checkbox.set_option("value", full_tab_name)
            if is_main:
                my.process_tabgroup_visibility(checkbox, tab_name)
            else:
                my.process_tab_visibility(checkbox)
            checkbox.set_persist_on_submit()
            table.add_cell(checkbox)
            table.add_data(SpanWdg(tab_name, css='small'))

        if num_checked:
            title_span.add("&nbsp;&nbsp;( %s )" % num_checked)

        
        return div

    def process_tabgroup_visibility(my, checkbox, tab_name):
        '''process the tab group visibility in this particular UI thru javascript'''
        tab_group_name = 'tab_group_%s' % tab_name

        # this has to be first
        checkbox.add_event('onclick', \
            "if (this.value=='Admin' && this.checked) {if (!confirm('Hiding the Admin tab will hide a lot of admin functions. Are you sure?')) this.checked=false;}")
        checkbox.add_event('onclick', \
            "if (!$('%s')) return; if (this.checked) set_display_off('%s'); else set_display_on('%s')" %(tab_group_name, tab_group_name, tab_group_name))
       

    def process_tab_visibility(my, checkbox):
        '''process the tab visibility in this particular UI thru javascript'''
        checkbox.add_event('onclick', \
            "if (this.value=='Admin/Customize Tabs' && this.checked) {if (!confirm('You are trying to hide the tab that you are viewing now. Are you sure?')) this.checked=false;}")
       

from pyasm.command import Command
class CustomizeTabCbk(Command):

    def get_title(my):
        return 'Customize Tab Visibility'

    def check(my):
        web = WebContainer.get_web()
        my.tab_key = web.get_form_value("update_tab_key")
        if not my.tab_key:
            return False
        else:
            return True

    def execute(my):
        web = WebContainer.get_web()
        key = "invisible_tabs"
        
        invisible_tabs = web.get_form_values(key)
        
        prod_setting = ProdSetting.get_by_key(key)
        if not prod_setting:
            prod_setting = SObjectFactory.create("prod/prod_setting")
            prod_setting.set_value("key", key)
            prod_setting.set_value("type", "sequence")
            prod_setting.set_value("description", "invisible tabs for %s" %my.tab_key)


        value = "|".join(invisible_tabs)
        prod_setting.set_value("value", value )
        prod_setting.commit()



class TabSecurityTableElementWdg(FunctionalTableElement):
    def get_display(my):
        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        link = TabSecurityLinkWdg(search_type, search_id)

        widget = Widget()
        xml_wdg = XmlWdg()
        xml_wdg.set_name(my.get_name())
        xml_wdg.set_sobject(sobject)
        widget.add(xml_wdg)
        widget.add(link)
        return widget


class TabSecurityWdg(CustomizeTabWdg):

    DEFAULT_ACTION = "visible"
    # FIXME: dummy constructor to with constructor to EditWdg
    def __init__(my, arg1, arg2):
        super(TabSecurityWdg, my).__init__()

    def is_error_free(my, web):
        ''' if it is intructed to close and is error-free , return True'''
        if web.get_form_value(EditWdg.CLOSE_WDG) and\
            not Container.get("cmd_report").get_errors():
            return True

        return False

    def get_display(my):
        web = WebContainer.get_web()
        event_container = WebContainer.get_event_container()
        refresh_script = "window.parent.%s" % event_container.get_refresh_caller()
        if my.is_error_free(web):
            return HtmlElement.script(refresh_script)

        widget = Widget()
        # for the is_error_free() check
        widget.add(HiddenWdg(EditWdg.CLOSE_WDG)) 
        
        div = DivWdg()
        div.center()
        div.add_class("filter_box")
        div.add_style('-moz-border-radius','10px')

        div.add(my.get_mode_wdg())

        instructions = "By default, all tabs are made invisible on update. Check the checkboxes for those tabs you want to show for this particular access rule. Click on the tab group title below to view the checkboxes."
        div.add(instructions)
        my.invisible_list = my.get_tab_list()

        my.handle_tabs(div)
        div.add(my.get_action_html())
        widget.add(div)
        widget.add(HiddenWdg('update_tab_key'))
        return widget

    def get_mode_wdg(my):
        div = DivWdg()
        div.add("<h3>Tab Security</h3>")
        help = HelpItemWdg("Tab Security", "Select the checkboxes of tabs you wish to give permission to view", True)
        div.add(help)
        return div
    """
    def hide_selected(my):
        return False
    """

    def register_cmd_handler(my):
        WebContainer.register_cmd("pyasm.admin.widget.TabSecurityCbk")

    def get_tab_list(my):
        web = WebContainer.get_web()
        search_type = web.get_form_value("search_type")
        search_id = web.get_form_value("search_id")

        # make sure this is remembered
        from pyasm.web import WebState
        state = WebState.get()
        state.add_state("search_type", search_type)
        state.add_state("search_id", search_id)

        access_rule = Search.get_by_id(search_type, search_id)

        if access_rule:
            xml = access_rule.get_xml_value("rule")
            tab_list = xml.get_values("rules/rule/@key")
        else:
            tab_list = []
        
        return tab_list

    def process_tabgroup_visibility(my, checkbox, tab_name):
        pass

    def process_tab_visibility(my, checkbox):
        pass

    def get_action_html(my):
       
        edit = SubmitWdg("do_edit", _("Update"))
        edit.add_event('onclick', "document.form.elements['update_tab_key'].value ='true'")
        
        # call an edit event
        event = WebContainer.get_event("sthpw:submit")
        edit.add_event("onclick", "document.form.%s.value='true'" %EditWdg.CLOSE_WDG)
        #edit_continue.add_event( "onclick", event.get_caller() )
        
        

        # create a cancel button to close the window
        cancel = ButtonWdg(_("Cancel"))
        layout = WebContainer.get_web().get_form_value('layout')
        my.iframe = WebContainer.get_iframe(layout)
        iframe_close_script = "window.parent.%s" % my.iframe.get_off_script() 
        cancel.add_event("onclick", iframe_close_script)

        div = DivWdg(css='centered')
        
        div.center()
        web = WebContainer.get_web()
        selected_keys = web.get_form_value(EditCheckboxWdg.CB_NAME)
        if not selected_keys:
            div.add(SpanWdg(edit, css='med'))
        div.add(SpanWdg(cancel, css='med'))

        return div

class TabSecurityLinkWdg(EditLinkWdg):
    def __init__(my, search_type, search_id, text="Modify Tab Security", config_base="tab_config",\
           widget="pyasm.admin.widget.TabSecurityWdg"):
           
        my.long = False
        
        super(TabSecurityLinkWdg, my).__init__(search_type,search_id,text,config_base, widget)
        #EditLinkWdg.__init__(my, search_type,search_id,text,config_base, widget)


    def _set_iframe_width(my, iframe):
        if my.layout == 'default':
            iframe.set_width(74)
        else:
            iframe.set_width(56)

    def get_button(my):
        button = IconButtonWdg(my.text, IconWdg.ADD, my.long)
        return button

        


class TabSecurityCbk(Command):

    def get_title(my):
        return 'Tab Security'

    def check(my):
        web = WebContainer.get_web()
        my.tab_key = web.get_form_value("update_tab_key")
        if not my.tab_key:
            return False
        else:
            return True

    def execute(my):
        web = WebContainer.get_web()
        
        key = "invisible_tabs"
        tabs = web.get_form_values(key)

        search_type = web.get_form_value("search_type")
        search_id = web.get_form_value("search_id")
        assert search_type, search_id

        # set this value to the appropriate access rule
        
        tabs = web.get_form_values(key)

        # see if the access rule already exists
        access_rule = Search.get_by_id(search_type, search_id)
        if not access_rule:
            project_code = Project.get_project_code()
            access_rule = SearchType.create("sthpw/access_rule")
            access_rule.set_value("code", code)
            access_rule.set_value("project_code", project_code)

            xml = Xml()
            doc = xml.create_doc("rules")
        else:
            xml = access_rule.get_xml_value("rule", "rules")


        access = "allow"
        default = "deny"
        root = xml.get_root_node()

        # first remove all of the tab rules 
        rule_nodes = xml.get_nodes("rules/rule[@group='tab']")
        for rule_node in rule_nodes:
            root.removeChild(rule_node)

        rule_node = xml.create_element("rule")
        xml.set_attribute(rule_node, "group", "tab")
        xml.set_attribute(rule_node, "default", default)
        root.appendChild(rule_node)

        # for each rule
        for tab in tabs:
            rule_node = xml.create_element("rule")
            xml.set_attribute(rule_node, "group", "tab")
            xml.set_attribute(rule_node, "key", tab)
            root.appendChild(rule_node)

            xml.set_attribute(rule_node, "access", access)

        #print xml.to_string()

        access_rule.set_value("rule", xml.to_string())
        access_rule.commit()

        





