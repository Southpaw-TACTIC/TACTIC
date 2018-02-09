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
__all__ = ['CGAppLoaderWdg','IntrospectWdg']

from pyasm.common import Xml, Container
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, WebContainer, Table
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, HiddenWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg
#from connection_select_wdg import ConnectionSelectWdg


class CGAppLoaderWdg(BaseRefreshWdg):
    '''Main loader class for CG apps'''

    def get_args_keys(self):
        '''external settings which populate the widget'''
        return {
        'view': 'view that this widget is making use of',
        'search_type': 'search type',
        'load_options_class': 'custom load options class name', 
        'load_script': 'custom load script',
        'load_script_path': 'custom load script path',
        }

    def init(self):
        self.view = self.kwargs.get('view')
        self.search_type = self.kwargs.get('search_type')
        self.load_options_class = self.kwargs.get('load_options_class')
        self.load_script = self.kwargs.get('load_script')
        self.load_script_path = self.kwargs.get('load_script_path')

        self.state = Container.get_full_dict("global_state")

    
    def get_display(self):
        # specially made for "load" view
        if not self.view.endswith("load"):
            return DivWdg()



        widget = Widget()
        # first use
        filter_top = DivWdg(css="maq_search_bar")
        filter_top.add_color("background", "background2", -15)

        # so dg_table.search_cbk will obtain values from this widget
        filter_top.add_class('spt_table_search')
        filter_top.add_style("padding: 3px")

        # this is used by get_process() in LoaderWdg
        filter_top.add(HiddenWdg('prefix', 'view_action_option'))

        for name, value in self.kwargs.items():
            filter_top.set_attr("spt_%s" % name, value)


        from tactic.ui.cgapp import SObjectLoadWdg, LoaderButtonWdg, LoaderElementWdg, IntrospectWdg

        # this contains the process filter and load options
        sobject_load = SObjectLoadWdg(search_type=self.search_type, load_options_class = self.load_options_class)
        filter_top.add(sobject_load)

       

        # set the process
        #class foo:
        #    def get_value(self):
        #        return "texture"
        #Container.put("process_filter", foo())

        filter_top.add( HtmlElement.br() )

        table = Table()
        table.add_class('spt_action_wdg')

        table.set_max_width()
        td = table.add_cell()       
     
        # create the loader button
        button = LoaderButtonWdg()


        # -------------
        # test an event mechanism
        event_name = '%s|load_snapshot' % self.search_type
        #event_name = 'load_snapshot'

        # get triggers with this event
        from pyasm.search import Search
        search = Search("config/client_trigger")
        search.add_filter("event", event_name)
        triggers = search.get_sobjects()

        if triggers:
            for trigger in triggers:
                #callback = trigger.get_value("custom_script_code")
                callback = trigger.get_value("callback")

                event_script = '''
                spt.app_busy.show("Loading ...", "Loading selected [%s] in to session");
                var script = spt.CustomProject.get_script_by_path("%s");
                bvr['script'] = script;
                spt.CustomProject.exec_custom_script(evt, bvr);
                spt.app_busy.hide();
                ''' % (self.search_type, callback)

                loader_script = '''spt.named_events.fire_event('%s', {})''' % event_name
                table.add_behavior( {
                    'type': 'listen',
                    'event_name': event_name,
                    'cbjs_action': event_script
                } )

        # test a passed in script path
        elif self.load_script_path:

            # an event is called
            event_name = 'load_snapshot'
            event_script = '''var script = spt.CustomProject.get_script_by_path("%s");spt.CustomProject.exec_script(script)''' % self.load+script_path

            loader_script = '''spt.named_events.fire_event('%s', {})''' % event_name
            table.add_behavior( {
                'type': 'listen',
                'event_name': event_name,
                'cbjs_action': event_script
            } )

        # end test
        # ---------------



        elif self.load_script:
            loader_script = self.load_script
        else:
            loader_script = LoaderElementWdg.get_load_script(self.search_type)

        #print LoaderElementWdg.get_load_script(self.search_type)
        
        # add the introspect button
        introspect_button = IntrospectWdg()
        introspect_button.add_style('float: left')
        introspect_button.add_style('margin-bottom: 6px')
        td.add(introspect_button)

        # to be attached
        smart_menu = LoaderElementWdg.get_smart_menu(self.search_type)
        button.set_load_script(loader_script)
        button.set_smart_menu(smart_menu)

        td.add(button)
        td.add_style('text-align','right')
        td.add_style('padding-right', '40px') 
        widget.add(filter_top)
        widget.add( HtmlElement.br() )
        widget.add(table)

        return widget

class IntrospectWdg(ActionButtonWdg):
    '''a widget that does introspection to analyze/update what 
        assets(versions) are loaded in the session of the app'''

    def __init__(self):
        super(IntrospectWdg, self).__init__(title='Introspect', tip='Introspect the current session')
        self.add_behavior({'type': "click", 'cbjs_action': "introspect(bvr)"})

