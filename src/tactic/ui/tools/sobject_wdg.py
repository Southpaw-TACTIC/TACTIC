###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ['SObjectDetailWdg', 'SObjectDetailInfoWdg', 'RelatedSObjectWdg', 'SnapshotDetailWdg', 'TaskDetailWdg', 'SObjectSingleProcessDetailWdg','SObjectRelatedNotesWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment, SPTDate, Common, FormatValue
from pyasm.biz import Snapshot, Pipeline
from pyasm.web import DivWdg, WebContainer, Table, WebState
from pyasm.search import Search, SearchType, SearchKey
from tactic.ui.panel import TableLayoutWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg, ThumbWdg
from pyasm.widget import WidgetConfig, WidgetConfigView

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import TabWdg, Menu, MenuItem
from tactic.ui.tools import PipelineCanvasWdg
from tactic.ui.widget import SingleButtonWdg, IconButtonWdg, ActionButtonWdg


class SObjectDetailWdg(BaseRefreshWdg):
    '''Single SObject Widget'''

    ARGS_KEYS = {
    'tab_element_names': {
        "description": "List of element names that will be in the tab",
        'category': 'Options',
        'type': 'TextWdg',
        'order': 1
    },
    'show_task_process': {
        'description': 'Determine if Add Note widget only shows the processes of existing tasks',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 2
    },

    'title_view': {
        'description': 'Determine the "title" view (top part of the detail view)',
        'category': 'Options',
        'type': 'TextWdg',
        'order': 3
    },


    }


    def init(self):
        self.show_task_process = self.kwargs.get('show_task_process')

    def get_title_wdg(self):



        title_view = self.kwargs.get("title_view")
        if title_view:
            from tactic.ui.panel import CustomLayoutWdg
            widget = CustomLayoutWdg(view=title_view)
            widget.kwargs['parent'] = self.parent
            widget.kwargs['sobject'] = self.sobject
            widget.kwargs['search_key'] = self.sobject.get_search_key()
            return widget



        search = Search("config/widget_config")
        search.add_filter("view", "detail_title")
        search.add_filter("search_type", self.search_type)
        config = search.get_sobject()
        if config:
            element_names = config.get_element_names()
            if "title" in element_names:
                widget = config.get_display_widget("title")
                if widget:
                    widget.kwargs['parent'] = self.parent
                    widget.kwargs['sobject'] = self.sobject
                    widget.kwargs['search_key'] = self.sobject.get_search_key()
                    return widget

        if self.parent:
            code = self.parent.get_value("code", no_exception=True)
            name = self.parent.get_value("name", no_exception=True)
            desc = self.parent.get_value("description", no_exception=True)
            status = self.parent.get_value("status", no_exception=True)
            search_type_obj = self.parent.get_search_type_obj()
        else:
            code = self.sobject.get_value("code", no_exception=True)
            name = self.sobject.get_value("name", no_exception=True)
            desc = self.sobject.get_value("description", no_exception=True)
            status = self.sobject.get_value("status", no_exception=True)
            search_type_obj = self.sobject.get_search_type_obj()


        # show a default title
        div = DivWdg()
        div.add_style("padding: 10px 15px")


        title = DivWdg()
        div.add(title)
        title.add_style("text-overflow: ellipsis")
        title.add_style("overflow-x: hidden")
        title.add_style("white-space: nowrap")



        search = Search("sthpw/snapshot")
        search.add_filter("search_type", "sthpw/search_type")
        search.add_filter("search_code", search_type_obj.get_value("code"))
        if search.get_sobject():
            thumb = ThumbWdg()
            title.add(thumb)
            thumb.set_icon_size(30)
            thumb.set_sobject(search_type_obj)
            thumb.add_style("float: right")


        title.add_style("font-size: 25px")
        title.add_style("margin-bottom: 5px")


        stype_title = search_type_obj.get_value("title")
        if stype_title:
            stype_title = _(stype_title)
            title.add("%s: " % stype_title)

        if name:
            title.add("%s" % name)
            if code:
                title.add(" <i style='font-size: 0.8; opacity: 0.7'>(%s)</i>" % code)
        elif code:
            title.add("%s" % code)
        else:
            title.add("(No name)")


        if desc:
            desc_div = DivWdg()
            desc_div.add(desc)
            desc_div.add_color("color", "color", 30)
            desc_div.add_style("font-size: 1.2em")
            div.add(desc_div)


        if status:
            status_div = DivWdg()
            div.add(status_div)
            status_div.add(status)
            status_div.add_style("padding: 3px 10px")
            status_div.add_style("margin: 8px 0px 3px 0px")
            status_div.add_style("border-radius: 5px")

            from pyasm.biz import Task
            color = Task.get_default_color(status)
            if not color:
                color = "#DDD"
            status_div.add_style("background: %s" % color)
            status_div.add_style("display: inline-block")



        return div




    def get_display(self):

        self.sobject = self.get_sobject()

        if not self.sobject:
            widget = DivWdg()
            widget.add("SObject does not exist or no longer exists")
            widget.add_style("margin: 100px auto")
            widget.add_style("width: 300px")
            widget.add_style("height: 60px")
            widget.add_style("padding: 60px")
            widget.add_style("text-align: center")
            widget.add_border()
            return widget

        if not self.__class__.__name__ == "SnapshotDetailWdg" and self.sobject.get_base_search_type() == "sthpw/snapshot":
            widget = SnapshotDetailWdg(**self.kwargs)
            return widget



        top = self.top
        top.add_class("spt_detail_top")
        #top.add_color("background", "background")
        #top.add_color("color", "color")


        if not self.sobject:
            top.add("No SObject defined for this widget")
            return top


        if self.parent:
            self.search_type = self.parent.get_base_search_type()
            self.search_key = SearchKey.get_by_sobject(self.parent)
            top.add_attr("spt_parent_key", self.search_key) 
            self.pipeline_code = self.parent.get_value("pipeline_code", no_exception=True)
            self.full_search_type = self.parent.get_search_type()
        else:
            self.pipeline_code = self.sobject.get_value("pipeline_code", no_exception=True)
            self.search_type = self.sobject.get_base_search_type()
            self.search_key = SearchKey.get_by_sobject(self.sobject)
            self.full_search_type = self.sobject.get_search_type()

        if not self.pipeline_code:
            self.pipeline_code = 'default'


        self.set_as_panel(top)



        # look for a custom view for the sobject detail
        custom_view = self.kwargs.get("view")
        use_default = self.kwargs.get("use_default")
        if use_default not in ['true', True] and not custom_view:
            from pyasm.biz import ProjectSetting
            key = "sobject_detail_view"
            custom_view = ProjectSetting.get_value_by_key(key, search_type=self.sobject.get_base_search_type())

        if custom_view:
            from tactic.ui.panel import CustomLayoutWdg
            selected = self.kwargs.get("selected") or ""
            layout = CustomLayoutWdg(
                    view=custom_view,
                    search_type = self.search_type,
                    search_key = self.search_key,
                    pipeline_code = self.pipeline_code,
                    selected = selected
            )
            top.add(layout)
            return layout



        title_wdg = self.get_title_wdg()
        title_wdg.add_class("spt_detail_title")
        top.add(title_wdg)
        title_wdg.add_style("display: inline-block")
        title_wdg.add_style("vertical-align: top")
        title_wdg.add_style("width: 500px")

        """
        title_wdg.add_style("background: #FFF")
        title_wdg.add_style("margin: 10px")
        title_wdg.add_style("border-radius: 10px")
        title_wdg.add_style("border: solid 1px #DDD")
        top.add_style("background: #F9F9F9")
        """



        panel_wdg = DivWdg()
        top.add(panel_wdg)
        panel_wdg.add_class("spt_detail_panel")
        panel_wdg.add_style("display: inline-block")
        panel_wdg.add_style("vertical-align: top")




        show_thumb = self.kwargs.get("show_thumb")
        if show_thumb not in ['false', False]:

            from tactic.ui.panel import ThumbWdg2
            thumb_div = DivWdg()
            panel_wdg.add(thumb_div)

            thumb = ThumbWdg2()
            thumb_div.add(thumb)
            thumb_div.add_style("width: 200px")
            thumb_div.add_style("height: 125px")
            thumb_div.add_style("padding: 5px")
            thumb_div.add_style("margin-left: 20px")
            thumb_div.add_style("margin-top: 20px")
            thumb_div.add_style("display: inline-block")
            thumb_div.add_style("vertical-align: top")
            thumb_div.add_style("overflow-y: hidden")
            # use a larger version for clearer display
            #thumb.set_icon_type('web')



            if self.parent:
                thumb.set_sobject(self.parent)
                search_key = self.parent.get_search_key()
            else:
                thumb.set_sobject(self.sobject)
                search_key = self.sobject.get_search_key()

            gallery_div = DivWdg()
            top.add( gallery_div )
            gallery_div.add_class("spt_tile_gallery")
     
            thumb_div.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_sobject_detail_top");
                    var gallery_el = top.getElement(".spt_tile_gallery");

                    var class_name = 'tactic.ui.widget.gallery_wdg.GalleryWdg';
                    var kwargs = {
                        search_key: bvr.search_key,
                        search_keys: [bvr.search_key],
                    };
                    spt.panel.load(gallery_el, class_name, kwargs);
                ''' } )
     

            # prefer to see the original image, then web
            #thumb.set_option('image_link_order', 'main|web|icon')
            #thumb.set_option("detail", "false")
            #thumb.set_option("icon_size", "100%")

        #top.add("<hr/>")


        top.add("<br clear='all'/>")

        top.add( self.get_tab_wdg() )

        return top









    def get_tab_wdg(self):

        div = DivWdg()


        # get the process
        if self.parent:
            process = self.sobject.get_value("process")
        else:
            process = ''


        # create a state for tab.  The tab only passes a search key
        # parent key
        search_key = SearchKey.get_by_sobject(self.sobject)
        parent_key = ""
        if search_key.startswith("sthpw/"):
            parent = self.sobject.get_parent()
            if parent:
                parent_key = parent.get_search_key()

        state = {
            'search_key': search_key,
            'parent_key': parent_key,
            'process': process,
        }
        WebState.get().push(state)


        config_xml = self.get_config_xml()
        config = WidgetConfig.get(view="tab", xml=config_xml)


        if process:
            custom_view = "tab_config_%s" % process
        else:
            custom_view = "tab_config"
        search = Search("config/widget_config")
        search.add_filter("category", "TabWdg")
        search.add_filter("search_type", self.search_type)
        search.add_filter("view", custom_view)
        custom_config_sobj = search.get_sobject()
        if custom_config_sobj:
            custom_config_xml = custom_config_sobj.get_value("config")
            custom_config = WidgetConfig.get(view=custom_view, xml=custom_config_xml)
            config = WidgetConfigView(search_type='TabWdg', view=custom_view, configs=[custom_config, config])

        selected = self.kwargs.get("selected")

        #menu = self.get_extra_menu()
        #tab = TabWdg(config=config, state=state, extra_menu=menu)
        tab = TabWdg(config=config, state=state, show_add=False, show_remove=False, tab_offset=10, selected=selected )
        tab.add_style("margin: 0px -1px -1px -1px")


        div.add(tab)
        div.add_style("padding-top: 10px")

        return div




    def get_extra_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Edit Tab Config')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var activator = spt.smenu.get_activator(bvr);
        spt.tab.top = activator.getParent(".spt_tab_top");
        var element_name = 'edit_tab_config';
        var title = 'Edit Tab Config';
        var class_name = 'tactic.ui.manager.ViewManagerWdg';
        var kwargs = {
            search_type: 'prod/asset',
            view: 'tab_config_model'
        }
        spt.tab.add_new(element_name, title, class_name, kwargs);

        '''
        } )
        menu.add(menu_item)


        return menu


    def get_default_tabs(self):
        tabs = ["info", "tasks","revisions","attachments","snapshots","checkin","edit"]
        return tabs



    def get_config_xml(self):
        if self.kwargs.get("use_parent") in [True, 'true']:
            search_key = self.sobject.get_search_key()
        else:
            search_key = self.kwargs.get("search_key")

            # convert to code=XYZ format

            sobject = Search.get_by_search_key(search_key)
            search_key = sobject.get_search_key()
        search_key = search_key.replace("&", "&amp;")

        title = self.search_type.split("/")[-1].title()

        detail_view = self.kwargs.get("detail_view")
        if not detail_view:
            detail_view = "table"

        show_default_elements = True
        if self.kwargs.get("show_default_elements") in [False, 'False', 'false']:
            show_default_elements = False

        values = {
                'search_key': search_key,
                'pipeline_code': self.pipeline_code,
                'search_type': self.search_type,
                'detail_view': detail_view,
                'show_default_elements': show_default_elements
        }

        config_xml = []

        config_xml.append('''
        <config>
        <tab>''')


        search_type_obj = SearchType.get(self.search_type)
        settings = search_type_obj.get_value("settings", no_exception=True)


        tabs = self.kwargs.get("tab_element_names")

        tab_view = self.kwargs.get("tab_view")
        if not tab_view:
            tab_view = "tab_element_names"


        config_search = Search("config/widget_config")
        config_search.add_filter("view", tab_view)
        config_search.add_filter("search_type", self.search_type)
        config_search.add_order_by("timestamp desc")
        configs = config_search.get_sobjects()

        from pyasm.search import WidgetDbConfig
        config = WidgetDbConfig.merge_configs(configs)

        if tabs:
            tabs = [x.strip() for x in tabs.split(',')] 
        elif config:
            tabs = config.get_element_names()
        else:
            tabs = self.get_default_tabs()
        
        if len(tabs) == 0:
            tabs.insert(0, "info")

        #if self.sobject.get_value("pipeline_code", no_exception=True):
        #    tabs.append("pipeline")
        #    values['pipeline_code'] = self.sobject.get_value("pipeline_code")
        if self.sobject.get_value("_is_collection", no_exception=True):
            tabs.append("collection")

            if "file_detail" in tabs:
                tabs.remove("file_detail")

            if "checkin_history" in tabs:
                tabs.remove("checkin_history")

        for tab in tabs:

            if tab == "tasks":
                config_xml.append('''
                <element name="tasks" title="Tasks">
                <display class='tactic.ui.panel.CustomLayoutWdg'>
                  <html>
                  <div style="padding: 20px">
                    <div style="font-size: 25px">Tasks</div>
                    <div>List of all of the tasks for this item</div>
                    <hr/>
                    <br/>
                    <element name="tasks">
                      <display class='tactic.ui.panel.ViewPanelWdg'>
                        <search_type>sthpw/task</search_type>
                        <view>detail</view>
                        <parent_key>%(search_key)s</parent_key>
                        <order_by>bid_start_date asc</order_by>
                        <width>100%%</width>
                        <show_shelf>false</show_shelf>
                      </display>
                    </element>
                  </div>
                  </html>
                </display>
                </element>
                ''' % values)


            elif tab == "info":
                config_xml.append('''
                <element name="info">
                  <display class='tactic.ui.tools.SObjectDetailInfoWdg'>
                    <search_key>%(search_key)s</search_key>
                    <detail_view>%(detail_view)s</detail_view>
                    <show_default_elements>%(show_default_elements)s</show_default_elements>
                  </display>
                </element>
                ''' % values)




            elif tab == "revisions":
                config_xml.append('''
                <element name="revisions" title="Revisions">
                  <display class='tactic.ui.panel.TileLayoutWdg'>
                    <search_type>sthpw/snapshot</search_type>
                    <parent_key>%(search_key)s</parent_key>
                    <process>review</process>
                    <layout>tile</layout>
                    <title_expr>@SUBSTITUTE('%%s - %%s', @GET(.login), @FORMAT(@GET(.timestamp), 'DATETIME'))</title_expr>
                    <bottom_expr>@GET(.description)</bottom_expr>
                    <width>100%%</width>
                    <show_shelf>false</show_shelf>
                    <group_elements>context</group_elements>
                  </display>
                </element>
                ''' % values)



            elif tab == "attachments":
                config_xml.append('''
                <element name="attachments" title="Attachments">
                  <display class='tactic.ui.panel.ViewPanelWdg'>
                    <search_type>sthpw/snapshot</search_type>
                    <parent_key>%(search_key)s</parent_key>
                    <process>attachment</process>
                    <layout>tile</layout>
                    <filter>
                      [
                        {"prefix":"main_body","main_body_enabled":"on","main_body_column":"is_latest","main_body_relation":"is","main_body_value":"true"},
                        {"prefix":"main_body","main_body_enabled":"on","main_body_column":"version","main_body_relation":"is greater than","main_body_value":"-1"},
                        {"prefix":"main_body","main_body_enabled":"on","main_body_column":"process","main_body_relation":"is","main_body_value":"attachment"}
                      ]
                      </filter>

                    <title_expr>@REPLACE(@GET(.context), 'attachment/', '')</title_expr>
                    <width>100%%</width>
                    <show_shelf>false</show_shelf>
                    <upload_mode>both</upload_mode>
                    <expand_mode>plain</expand_mode>
                    <no_results_msg>Drag and drop file here to upload.</no_results_msg>
                  </display>
                </element>
                ''' % values)

            elif tab == "related":
                config_xml.append('''
                <element name="related" title="Related">
                  <display class='tactic.ui.tools.RelatedSObjectWdg'>
                    <search_key>%(search_key)s</search_key>
                  </display>
                </element>
                ''' % values)

            elif tab == "file_detail":
                config_xml.append('''
                <element name="file_detail" title="File Metadata">
                  <display class='tactic.ui.tools.FileDetailWdg'>
                    <search_key>%(search_key)s</search_key>
                  </display>
                </element>
                ''' % values)



            elif tab == "snapshots" or tab == "checkin_history":
                config_xml.append('''
                <element name="snapshots" title="Check-in History">
                  <display class='tactic.ui.panel.CustomLayoutWdg'>
                  <html>
                    <div style="padding: 20px">
                    <div style="font-size: 25px">Check-in History</div>
                    <div>List of all of the check-ins for this item</div>
                    <hr/>
                    <br/>
                    <element>
                      <display class='tactic.ui.panel.ViewPanelWdg'>
                        <search_type>sthpw/snapshot</search_type>
                        <view>table</view>
                        <parent_key>%(search_key)s</parent_key>
                        <show_shelf>false</show_shelf>
                        <width>100%%</width>
                        <use_last_search>false</use_last_search>
                      </display>
                    </element>
                    </div>
                  </html>
                  </display>
                </element>
                ''' % values)



            elif tab == "checkin":
                config_xml.append('''
                <element name="checkin" title="Check-in">
                  <display class='tactic.ui.widget.CheckinWdg'>
                    <search_key>%(search_key)s</search_key>
                    <use_applet>false</use_applet>
                    <show_header>false</show_header>
                  </display>
                </element>
                ''' % values)

            elif tab == "edit":
                config_xml.append('''
                <element name="edit" title="Edit">
                  <display class='tactic.ui.panel.CustomLayoutWdg'>
                      <html>
                      <div style="padding: 20px">
                      <div style="font-size: 25px">Edit Metadata</div>
                      <div>Edit the data associated with this item</div>
                      <hr/>
                      <br/>
                      <element name="content" style="margin: 0px auto; width: 800px">
                      <display class='tactic.ui.panel.EditWdg'>
                        <search_key>%(search_key)s</search_key>
                        <num_columns>2</num_columns>
                        <view>edit</view>
                        <show_header>false</show_header>
                      </display>
                      </element>
                      </div>
                      </html>
                  </display>
                </element>
                ''' % values)

            elif tab == "pipeline":
                config_xml.append('''
                <element name="pipeline" title="Workflow">
                  <display class='tactic.ui.tools.TaskDetailPipelineWrapperWdg'>
                    <search_key>%(search_key)s</search_key>
                    <pipeline>%(pipeline_code)s</pipeline>
                  </display>
                </element>
                ''' % values)


            elif tab == "collection":
                search_type = values['search_type']
                parts = search_type.split("/")
                values['collection_type'] = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])
                values['expression'] = "@SOBJECT(collection:%(collection_type)s.%(search_type)s)" % values

                config_xml.append('''
                <element name="collection" title="Collection">
                  <display class='tactic.ui.panel.TileLayoutWdg'>
                    <layout>tile</layout>
                    <show_shelf>false</show_shelf>
                    <width>100%%</width>
                    <search_key>%(search_key)s</search_key>
                    <search_type>%(search_type)s</search_type>
                    <expression>%(expression)s</expression>
                  </display>
                </element>
                ''' % values)



            elif tab == "notes":
                config_xml.append('''
                <element name="notes" title="Notes" count="@COUNT(sthpw/note)">
                  <display class='tactic.ui.panel.CustomLayoutWdg'>
                  <html>
                    <div style="padding: 20px">
                    <div style="font-size: 25px">Notes</div>
                    <div>List of all of the notes for this item</div>
                    <hr/>
                    <br/>
                    <div style="min-height: 200px">
                    <element>
                      <display class='tactic.ui.widget.DiscussionWdg'>
                        <search_key>%(search_key)s</search_key>
                        <width>100%%</width>
                      </display>
                    </element>
                    </div>
                    </div>
                  </html>
                  </display>
                </element>
                ''' % values)






            elif tab.find("/") != -1:
                parts = tab.split("/")
                name = parts[-1]
                title = parts[-1].title().replace("_", " ")
                tab_values = {}
                tab_values['title'] = title
                tab_values['search_type'] = tab
                tab_values['search_key'] = self.search_key

                config_xml.append('''
                <element name="%(search_type)s" title="%(title)s">
                  <display class='tactic.ui.panel.ViewPanelWdg'>
                    <search_type>%(search_type)s</search_type>
                    <view>table</view>
                    <parent_key>%(search_key)s</parent_key>
                    <width>100%%</width>
                    <show_shelf>false</show_shelf>
                  </display>
                </element>
                ''' % tab_values)


            else:

                if config:
                    attrs = config.get_element_attributes(tab)
                else:
                    attrs = {}

                view = attrs.get("view")
                if view:
                    name = tab
                else:
                    view = tab
                    parts = tab.split(".")
                    name = parts[-1]

                title = None
                if config:
                    title = config.get_element_title(tab)

                count = attrs.get("count") or ""
                count_color = attrs.get("count_color") or ""
                
                if not title:
                    title = name.title().replace("_", " ")
                tab_values = {
                        'title': title,
                        'name': name,
                        'parent_key': search_key,
                        'view': view,
                        'count': count,
                        'count_color': count_color
                }

                attr_config = []
                for attr, value in attrs.items():
                    attr_config.append("<%s>%s</%s>" % (attr, value, attr) )
                attr_str = "\n".join(attr_config)
                tab_values['attrs'] = attr_str



                config_xml.append('''
                <element name="%(name)s" title="%(title)s" count="%(count)s" count_color="%(count_color)s">
                  <display class='tactic.ui.panel.CustomLayoutWdg'>
                    <view>%(view)s</view>
                    <parent_key>%(parent_key)s</parent_key>
                    <width>100%%</width>
                    %(attrs)s
                  </display>
                </element>
                ''' % tab_values)



        self.append_to_config(config_xml)

        config_xml.append('''
        </tab>
        </config>
        ''')

        config_xml = "".join(config_xml)
        config_xml = config_xml.replace("&", "&amp;")


        return config_xml


    def append_to_config(self, config_xml):
        return


    def get_sobject(self):

        search_key = self.kwargs.get("search_key")
        child_key = self.kwargs.get("child_key")

        if child_key:
            child = Search.get_by_search_key(child_key)
            sobject = child.get_parent()
            self.kwargs["search_key"] = sobject.get_search_key()
        else:
            sobject = Search.get_by_search_key(search_key)

        use_parent = self.kwargs.get("use_parent")
        if use_parent in [True, 'true']:
            sobject = sobject.get_parent()

        self.parent = None

        return sobject


    def get_sobject_info(self):
        titles = ['Code', 'Name', 'Description']
        exprs = []
        exprs.append( "@GET(.code)")
        exprs.append( "@GET(.name)")

        return titles, exprs


    def get_sobject_info_wdg(self):
        div = DivWdg()
        return div

        attr_table = Table()
        div.add(attr_table)

        attr_table.add_color("color", "color")

        sobject = self.get_sobject()

        titles, exprs = self.get_sobject_info()
        for title, expr in zip(titles, exprs):
            try:
                value = Search.eval(expr, sobject)
            except Exception as e:
                print "WARNING: ", e.message
                continue


            if value == '':
                value = '<i>none</i>'
            if len(value) > 100:
                value = "%s..." % value[:100]

            attr_table.add_row()
            th = attr_table.add_header("%s: " % title)
            th.add_style("text-align: left")
            td = attr_table.add_cell(value)

        #return attr_table
        return div


    def get_sobject_detail_wdg(self):
        div = DivWdg()
        #div.add_style("float: right")
        div.add_style("width: 100%")
        div.add_style("height: 100%")
        div.add_style("padding-top: 5px")


        info_div = DivWdg()
        div.add( info_div )
        #info_div.add_style("display: none")
        info_div.add_class("spt_sobject_detail")
        #info_div.add_style("width: 300px")
        info_div.add_style("padding: 30px 0px 20px 0px")

        info_table = Table()
        info_table.add_color("color", "color")
        info_div.add(info_table)


        edit_div = DivWdg()
        info_div.add(edit_div)
        edit_div.add_style("margin-top: -36px")
        edit_div.add_style("margin-left: 1px")
        edit_div.add_style("margin-right: -2px")
        #edit_div.add_style("overflow: scroll")
        #edit_div.add_style("height: 100%")
        edit_div.add_style("max-height: 300px")
        edit_div.add_style("overflow-y: auto")

        ignore = ["preview", "notes", "files"]

        from tactic.ui.panel.edit_layout_wdg import EditLayoutWdg
        if self.parent:
            sobject = self.get_sobject()
            search_type = sobject.get_search_type()
            search_key = sobject.get_search_key()

            # get the element names from the edit view
            config = WidgetConfigView.get_by_search_type(search_type=search_type, view="edit")
            element_names = config.get_element_names()


            edit = EditLayoutWdg(search_type=search_type, mode='view', view="detail", search_key=search_key, width=400, title=' ', ignore=ignore, element_names=element_names)

            edit_div.add(edit)

        else:

            view = self.kwargs.get("detail_view")
            if not view:
                view = "edit"

            element_names = ['code', 'name','description']

            # Make element_names empty if user desides to hide the default elements
            show_default_elements = self.kwargs.get("show_default_elements")
            
            if show_default_elements in ['false', 'False', False]:
                element_names = []

            config = WidgetConfigView.get_by_search_type(search_type=self.full_search_type, view=view)
            config_element_names = config.get_element_names()
            for x in config_element_names:
                if x in ignore:
                    continue
                if x not in element_names:
                    element_names.append(x)



            edit = EditLayoutWdg(search_type=self.full_search_type, mode='view', view="detail", search_key=self.search_key, width=400, title=' ', ignore=ignore, element_names=element_names)
            edit_div.add(edit)


        return div



class SObjectDetailInfoWdg(SObjectDetailWdg):

    def get_display(self):

        search_key = self.kwargs.get("search_key")
        self.sobject = Search.get_by_search_key(search_key)
        if self.sobject.get_base_search_type() == "sthpw/task":
            self.parent = self.sobject
        else:
            self.parent = None


        top = self.top

        if not self.sobject:
            top.add("No SObject defined for this widget")
            return top

        if self.parent:
            self.search_type = self.parent.get_base_search_type()
            self.search_key = SearchKey.get_by_sobject(self.parent)
            top.add_attr("spt_parent_key", self.search_key) 
            self.pipeline_code = self.parent.get_value("pipeline_code", no_exception=True)
            self.full_search_type = self.parent.get_search_type()
        else:
            self.pipeline_code = self.sobject.get_value("pipeline_code", no_exception=True)
            self.search_type = self.sobject.get_base_search_type()
            self.search_key = SearchKey.get_by_sobject(self.sobject)
            self.full_search_type = self.sobject.get_search_type()

        if not self.pipeline_code:
            self.pipeline_code = 'default'


        table = Table()
        top.add(table)
        table.set_max_width()

        table.add_row()

        td = table.add_cell()
        td.add_style("padding: 20px")
        td.add_style("width: 50%")

        #sobject_info_wdg = self.get_sobject_info_wdg()
        #sobject_info_wdg.add_style("width: 100%")
        #td.add(sobject_info_wdg)


        edit_wdg = ActionButtonWdg(title="Edit")
        edit_wdg.add_class("spt_details_edit_button")
        td.add(edit_wdg)
        edit_wdg.add_behavior( {
            'type': 'click',
            'search_key': search_key,
            'cbjs_action': '''
            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_key: bvr.search_key
            }

            spt.panel.load_popup("Edit", class_name, kwargs);

            '''
        } )

        edit_wdg.add_style("float: right")


        title_wdg = DivWdg()
        td.add(title_wdg)
        title_wdg.add("Summary")
        title_wdg.add_style("font-size: 1.4em")
        title_wdg.add_style("margin-bottom: 5px")

        desc_wdg = DivWdg()
        td.add(desc_wdg)
        desc_wdg.add("Detailed information about this item.")
        td.add("<hr/>")



        if self.search_type == 'sthpw/task' and not self.parent:
            pass
        else:
            sobject_info_wdg = self.get_sobject_detail_wdg()
            td.add(sobject_info_wdg)
            td.add_style("vertical-align: top")
            td.add_style("overflow: hidden")
            td.add_style("width: 50vw")


        td = table.add_cell()
        spacer_div = DivWdg()
        td.add(spacer_div)
        td.add_style("height: 1px")
        td.add_style("padding: 20px 0px 20px 20px")
        spacer_div.add_style("border-style: solid")
        spacer_div.add_style("border-width: 0px 0px 0px 1px")
        spacer_div.add_style("border-color: #DDD")
        spacer_div.add(" ")
        spacer_div.add_style("height: 100%")



        # right
        td = table.add_cell()
        td.add_style("text-align: left")
        td.add_style("vertical-align: top")
        td.add_class("spt_notes_wrapper")
        td.add_style("padding: 20px")

        title_wdg = DivWdg()
        td.add(title_wdg)
        title_wdg.add_style("width: 100%")
        title_wdg.add("Notes")
        title_wdg.add_style("font-size: 1.4em")
        title_wdg.add_style("margin-bottom: 5px")

        desc_wdg = DivWdg()
        td.add(desc_wdg)
        desc_wdg.add("List of all the notes for this item.")
        td.add("<hr/>")


        # write out all the notes totals
        search_type = self.sobject.get_base_search_type()

        parts = search_type.split("/")


        from pyasm.biz import ProjectSetting
        related_types = ProjectSetting.get_value_by_key("notes/%s/related_types" % parts[1])
        if related_types:
            related_types = related_types.split(",")
        else:
            related_types = []



        # hard code some built in stypes
        if search_type in ['sthpw/snapshot']:
            parent = self.sobject.get_parent()
            related_types = [parent.get_base_search_type()]

        elif search_type.startswith("sthpw/"):
            related_types = []


        # This is too broad
        """
        else:
            if related_types:
                related_types = related_types.split(",")

            else:
                from pyasm.biz import Schema
                schema = Schema.get()
                related_types = schema.get_related_search_types(self.sobject.get_base_search_type())
                related_types = list(set(related_types))
        """



        sobjects = []
        for related_type in related_types:
            related_sobjects = Search.eval("@SOBJECT(%s)" % related_type, self.sobject)
            sobjects.extend(related_sobjects)

        sobjects.insert(0, self.sobject)

        from tactic.ui.widget.discussion_wdg import DiscussionWdg
        for sobject in sobjects:
            search_key = sobject.get_search_key()

            if len(sobjects) > 1:
                name = sobject.get_value("name", no_exception=True)
                if name:
                    td.add("<b>%s</b> - %s" % (sobject.get_code(), name))
                else:
                    td.add("<b>%s</b>" % sobject.get_code())

            notes_div = DivWdg()
            td.add(notes_div)


            discussion_wdg = DiscussionWdg(search_key=search_key,
                    context_hidden=False, show_note_expand=False,
                    show_task_process=self.show_task_process)
            
            notes_div.add(discussion_wdg)
            #menu = discussion_wdg.get_menu_wdg(notes_div)
            #notes_div.add(menu)

            notes_div.add_style("min-width: 300px")
            notes_div.add_style("height: auto")
            notes_div.add_style("min-height: 20")
            notes_div.add_style("overflow-y: auto")
            notes_div.add_class("spt_resizable")

            if len(sobjects) > 1:
                notes_div.add_style("margin: 10px 10px")
                td.add("<hr/>")

        return top




class RelatedSObjectWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_class("spt_related_top")

        from pyasm.biz import Schema
        schema = Schema.get()

        search_key = self.kwargs.get("search_key")
        sobject = Search.get_by_search_key(search_key)

        search_type = sobject.get_base_search_type()
        related_types = Schema.get().get_related_search_types(search_type)


        table = Table()
        top.add(table)

        table.add_row()
        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("padding: 10px")
        left.add_style("width: 200px")
        left.add_style("min-width: 200px")

        left.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_related_item',
            'search_type': search_type,
            'search_key': search_key,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_related_top");
            var content = top.getElement(".spt_related_content");
            var related_type = bvr.src_el.getAttribute("spt_related_type");
            var class_name = "tactic.ui.panel.ViewPanelWdg";
            var kwargs = {
                search_type: related_type,
                parent_key: bvr.search_key,
            };
            var name = "Related: " + related_type;
            var title = name
            //spt.tab.add_new(name, title, class_name, kwargs);
            spt.panel.load(content, class_name, kwargs);
            '''
        } )

        left.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_related_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "#EEE");
            '''
        } )


        left.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_related_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )




        for related_type in related_types:
            attrs = schema.get_relationship_attrs(search_type, related_type)

            related_sobj = SearchType.get(related_type)
            name = related_sobj.get_title()


            related_div = DivWdg()
            left.add(related_div)
            related_div.add("<b>%s</b> <i style='opacity: 0.5'>(%s)</i>" % (name, related_type))
            related_div.add_style("padding: 3px")
            related_div.add_class("spt_related_item")
            related_div.add_attr("spt_related_type", related_type)

            left.add("<hr/>")

        right = table.add_cell()
        right.add_class("spt_related_content")
        right.add_style("vertical-align: top")



        return top




class SnapshotDetailWdg(SObjectDetailWdg):

    def get_title_wdg(self):

        title_wdg = DivWdg()
        title_wdg.add_style("margin: 20px")
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("opacity: 0.7")


        self.sobject = self.get_sobject()

        parent = self.sobject.get_parent()

        snapshot_div = DivWdg()
        title_wdg.add(snapshot_div)
        snapshot_div.add_style("font-size: 25px")
        snapshot_div.add(self.sobject.get_code())


 
        context = self.sobject.get_value("context", no_exception=True)
        process = self.sobject.get_value("process", no_exception=True)
        version = self.sobject.get_value("version", no_exception=True)
        login = self.sobject.get_value("login", no_exception=True)
        timestamp = self.sobject.get_datetime_value("timestamp")
        timestamp = SPTDate.convert_to_local(timestamp)
        time_ago = SPTDate.get_time_ago(timestamp)

        context_wdg = DivWdg()
        title_wdg.add(context_wdg)
        context_wdg.add("Process: %s" % process)
        context_wdg.add_style("margin: 5px 0px")


        context_wdg = DivWdg()
        title_wdg.add(context_wdg)
        context_wdg.add("User: %s" % login)
        context_wdg.add_style("margin: 5px 0px")


        context_wdg = DivWdg()
        title_wdg.add(context_wdg)
        context_wdg.add("Created: %s" % time_ago)
        context_wdg.add_style("margin: 5px 0px")




        version_wdg = DivWdg()
        title_wdg.add(version_wdg)
        version_wdg.add("Latest Version: %0.3d" % version)
        version_wdg.add_style("margin: 5px 0px")


        lib_path = self.sobject.get_lib_path_by_type()
        lib_path_info = Common.get_dir_info(lib_path)
        if lib_path_info.get("file_type") == "file":
            size = lib_path_info.get("size")
            size_str = FormatValue().get_format_value(size, "KB")

            size_wdg = DivWdg()
            title_wdg.add(size_wdg)
            size_wdg.add("File Size: %s" % size_str)
            size_wdg.add_style("margin: 5px 0px")

            media_type = "image"





        # only show the client path if it is defined in the config file
        from pyasm.biz import ProdSetting
        from pyasm.common import Config
        client_os = Environment.get_env_object().get_client_os()
        if client_os == 'nt':
            prefix = "win32"
        else:
            prefix = "linux"

        key = '%s_client_repo_dir' % prefix
        base_dir = Config.get_value("checkin", key)
        if base_dir:
            lib_dir_wdg = DivWdg()
            title_wdg.add(lib_dir_wdg)

            lib_dir = self.sobject.get_lib_dir()
            client_lib_dir = self.sobject.get_client_lib_dir()


            lib_dir_wdg.add_style("margin: 5px 0px")
            lib_dir_wdg.add("Client Path:")

            from tactic.ui.input import TextInputWdg
            #text.add(client_lib_dir)
            text = TextInputWdg()
            text.set_value(client_lib_dir)
            text.add_style("width", "100%")
            text.add_class("form-control")
            lib_dir_wdg.add(text)
            text.add_behavior({
                'type': 'click',
                'cbjs_action': '''
                bvr.src_el.select();
                try {
                    document.execCommand('copy');
                } catch(err) {
                    alert("Cannot copy");
                }
                '''
            } )




        return title_wdg


    def get_default_tabs(self):
        #tabs = ["checkin_history"]
        tabs = []
        return tabs


    def append_to_config(self, config_xml):

        values = {}

        process = self.sobject.get_value("process")
        context = self.sobject.get_value("context")
        parent = self.sobject.get_parent()
        #values['search_key'] = parent.get_search_key()
        values['search_key'] = ''
        values['process'] = process

        values['expression'] = "@SEARCH(sthpw/snapshot['context','%s']['search_code','%s']['search_type','%s'])" % (context, self.sobject.get("search_code"), self.sobject.get("search_type"))

        config_xml.append('''
        <element name="snapshot_history" title="Check-in History">
          <display class='tactic.ui.panel.CustomLayoutWdg'>
          <html>
            <div style="padding: 20px">
            <div style="font-size: 25px">Check-in History</div>
            <div>List of all of the check-ins for this item</div>
            <hr/>
            <br/>
            <element>
              <display class='tactic.ui.panel.ViewPanelWdg'>
                <search_type>sthpw/snapshot</search_type>
                <view>table</view>
                <parent_key>%(search_key)s</parent_key>
                <expression>%(expression)s</expression>
                <show_shelf>false</show_shelf>
                <width>100%%</width>
                <use_last_search>false</use_last_search>
              </display>
            </element>
            </div>
          </html>
          </display>
        </element>
        ''' % values)


        values['expression2'] = "@SEARCH(sthpw/snapshot['process','%s/review']['search_code','%s']['search_type','%s'])" % (process, self.sobject.get("search_code"), self.sobject.get("search_type"))


        config_xml.append('''
        <element name="review" title="Review Feedback">
          <display class='tactic.ui.panel.CustomLayoutWdg'>
          <html>
            <div style="padding: 20px">
            <div style="font-size: 25px">Review Feedback</div>
            <div>List of all of the Reviews for this item</div>
            <hr/>
            <br/>
            <element>
              <display class='tactic.ui.panel.ViewPanelWdg'>
                <layout>tile</layout>
                <search_type>sthpw/snapshot</search_type>
                <view>table</view>
                <width>100%%</width>
                <show_shelf>false</show_shelf>
                <expression>%(expression2)s</expression>
              </display>
            </element>
            </div>
          </html>
          </display>
        </element>
        ''' % values)







class TaskDetailWdg(SObjectDetailWdg):


    def get_title_wdg(self):

        title = DivWdg()

        title.add_style("height: 20px")
        title.add_style("padding: 6px")
        title.add_style("font-weight: bold")
        title.add_style("font-size: 1.4em")

        if not self.parent:
            title.add("Parent not found")
            return title

        code = self.parent.get_value("code", no_exception=True)
        name = self.parent.get_value("name", no_exception=True)

        process = self.sobject.get("process")
        task_code = self.sobject.get("code")
        status = self.sobject.get("status")
        description = self.sobject.get("description")
        start_date = self.sobject.get("bid_start_date")
        end_date = self.sobject.get("bid_end_date")

        bgcolor = title.get_color("background")
        title.add("<span style='font-size: 1.2em; padding: 4px; margin: 0px 20px 0px 0px;'>%s</span>  Task <i>(%s)</i>" % (process, code))


        # Test adding this ... need to find a place for it
        #notes_div = DivWdg()
        #title.add(notes_div)
        #from tactic.ui.widget.discussion_wdg import DiscussionWdg
        #discussion_wdg = DiscussionWdg(search_key=self.parent.get_search_key(), process=process, context_hidden=True, show_note_expand=True)
        #notes_div.add(discussion_wdg)

        title.add("<hr/>")


        table = Table()
        title.add(table)
        table.add_style("width: 100%")
        table.add_style("margin-right: 30px")

        if description:
            table.add_row()
            table.add_cell("Description:")
            table.add_cell(description)



        if start_date:
            table.add_row()
            table.add_cell("Start Date:")
            table.add_cell(start_date)

        if end_date:
            table.add_row()
            table.add_cell("End Date:")
            table.add_cell(end_date)

        table.add_row()
        table.add_cell("Status:")
        table.add_cell(status)

        return title



    def get_sobject(self):
        search_key = self.kwargs.get("search_key")
        self.sobject = Search.get_by_search_key(search_key)
        self.parent = self.sobject.get_parent()
        return self.sobject


    def get_sobject_info(self):

        titles = ['Description']
        exprs = []
        exprs.append( "@GET(parent.description)")
        return titles, exprs


 

    def get_config_xml(self):

        process = self.sobject.get_value("process")
        context = self.sobject.get_value("context")
        process_title = "Process - %s" % (process)
        process_name = "process_%s" % process
        parent_key = ''
        if self.parent:
            parent_key = SearchKey.get_by_sobject(self.parent).replace("&","&amp;")
        search_key = SearchKey.get_by_sobject(self.sobject).replace("&","&amp;")

        config_xml = []

        config_xml.append( '''
        <config>
        <tab>''' )


        if self.parent:
            parent_type = self.parent.get_base_search_type()
            config_xml.append( '''
            <element name="info" title="Info">
              <display class='tactic.ui.panel.CustomLayoutWdg'>
              <html>
                <div style="margin: 20px">
                  <div style="font-size: 16px">Detailed Info</div>
                  <hr/>
                  <element name="content">
                    <display class='tactic.ui.panel.edit_layout_wdg.EditLayoutWdg'>
                      <search_type>%s</search_type>
                      <search_key>%s</search_key>
                      <width>600px</width>
                      <mode>view</mode>
                      <view>detail</view>
                    </display>
                  </element>
                  </div>
              </html>
              </display>
            </element>
            ''' % (parent_type, parent_key) )


        """
        config_xml.append( '''
        <element name="edit" title="Edit">
          <display class='tactic.ui.panel.EditWdg'>
            <search_key>%s</search_key>
          </display>
        </element>
        ''' % (search_key) )
        """

        config_xml.append('''
        <element name="edit" title="Edit">
          <display class='tactic.ui.container.ContentBoxWdg'>
              <title>Edit</title>
              <content_height>auto</content_height>
              <config>
              <element name="content" style="margin: 0px auto; width: 800px">
              <display class='tactic.ui.panel.EditWdg'>
                <search_key>%s</search_key>
                <num_columns>2</num_columns>
                <view>edit</view>
                <show_header>false</show_header>
                <width>90%%</width>
              </display>
              </element>
              </config>
          </display>
        </element>
        ''' % search_key)






        #from tactic.ui.panel.edit_layout_wdg import EditLayoutWdg
        #edit = EditLayoutWdg(search_type=self.full_search_type, mode='view', view="detail", search_key=self.search_key, width=400, title=' ', ignore=ignore, element_names=element_names)
           

        
        if not self.parent:
            config_xml.append( '''
            </tab>
            </config>
            ''' )

            config_xml = "".join(config_xml)
            return config_xml

        values = self.parent.get_data()
        values['search_key'] = self.parent.get_search_key().replace("&", "&amp;")
        values['process'] = process



        config_xml.append('''
        <element name="revisions" title="Revisions">
          <display class='tactic.ui.panel.TileLayoutWdg'>
            <search_type>sthpw/snapshot</search_type>
            <parent_key>%(search_key)s</parent_key>
            <context>review/%(process)s</context>
            <layout>tile</layout>
            <title_expr>@SUBSTITUTE('%%s - %%s', @GET(.login), @FORMAT(@GET(.timestamp), 'DATETIME'))</title_expr>
            <bottom_expr>@GET(.description)</bottom_expr>
            <width>100%%</width>
            <show_shelf>false</show_shelf>
          </display>
        </element>
        ''' % values)


        config_xml.append('''
        <element name="snapshots" title="Check-in History">
          <display class='tactic.ui.panel.TableLayoutWdg'>
            <search_type>sthpw/snapshot</search_type>
            <view>table</view>
            <parent_key>%(search_key)s</parent_key>
            <width>100%%</width>
            <show_shelf>false</show_shelf>
            <op_filters>[["process","%(process)s"],["is_latest","true"]]</op_filters>
          </display>
        </element>
        ''' % values)





        display_options = self.kwargs
        options_list = []
        for key, value in display_options.items():
            if key in ['search_key','process', 'parent_key','checkin_ui_options','checkin_script_path','checkin_script','checkin_relative_dir']:
                continue
            options_list.append('<%(key)s>%(value)s</%(key)s>'%({'key':key, 'value': value}))

        display_options = self.kwargs
        options_list = []
        for key, value in display_options.items():
            if key in ['search_key','process','show_versionless_folder']:
                continue
            options_list.append('<%(key)s>%(value)s</%(key)s>'%({'key':key, 'value': value}))

        wdg_xml = '''
        <element name="checkin_%s" title="Checkin">
          <display class='tactic.ui.widget.CheckinWdg'>
            <search_key>%s</search_key>
            <process>%s</process>
            <use_applet>false</use_applet>
            <context>%s</context>
            <show_header>false</show_header>
            %s
          </display>
        </element>
        
        ''' % (process_name, parent_key, process, context, '\n'.join(options_list))

        config_xml.append( wdg_xml)

        config_xml.append('''
        <element name="status_log" title="Status Log">
          <display class='tactic.ui.panel.TableLayoutWdg'>
            <search_type>sthpw/status_log</search_type>
            <view>table</view>
            <parent_key>%(search_key)s</parent_key>
            <width>100%%</width>
            <show_shelf>false</show_shelf>
            <expand_on_load>true</expand_on_load>
          </display>
        </element>
        ''' % {"search_key": search_key} )


    

        config_xml.append( '''
        </tab>
        </config>
        ''' )

        config_xml = "".join(config_xml)

        return config_xml



__all__.append("SObjectTaskStatusDetailWdg")
class SObjectTaskStatusDetailWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top

        top.add_class("spt_tasks_status_detail_top")

        search_key = self.kwargs.get("search_key")

        from tactic.ui.table import TaskElementWdg
        from pyasm.search import Search
        self.sobject = Search.get_by_search_key(search_key)


        if self.sobject.get_base_search_type() == "sthpw/task":
            self.parent = self.sobject.get_parent()
        else:
            self.parent = None

        if self.parent:
            code = self.parent.get_value("code", no_exception=True)
            name = self.parent.get_value("name", no_exception=True)
            search_type_obj = self.parent.get_search_type_obj()
        else:
            code = self.sobject.get_value("code", no_exception=True)
            name = self.sobject.get_value("name", no_exception=True)
            search_type_obj = self.sobject.get_search_type_obj()



        title = DivWdg()
        top.add(title)
        top.add_style("min-width: 500px")


        from tactic.ui.panel import ThumbWdg2
        from tactic.ui.widget import ActionButtonWdg
        from tactic.ui.panel import TableLayoutWdg

        search_key = self.sobject.get_search_key()



        thumb = ThumbWdg2()
        title.add(thumb)
        thumb.set_sobject(self.sobject)
        thumb.add_style("width: px")
        thumb.add_style("float: left")
        thumb.add_style("margin: 0px 15px")



        title.add_color("background", "background", -5)
        title.add_style("padding: 10px")
        title.add_style("font-weight: bold")
        title.add_style("font-size: 1.4em")
        title.add_border(color="#DDD")

        title.add_style("margin-bottom: 20px")



        code = self.sobject.get("code")
        name = self.sobject.get("name")
        description = self.sobject.get("description")

        info_div = DivWdg()
        title.add(info_div)
        info_div.add("%s<br/>" % code)
        if name != code:
            info_div.add("%s<br/>" % name)
        else:
            info_div.add("<br/>")
        info_div.add("<span style='font-size: 0.8em'>%s</span><br/>" % description)
        info_div.add_style("margin-left: 15px")




        shelf_wdg = DivWdg()
        top.add(shelf_wdg)
        shelf_wdg.add_style("margin: 10px 0px")
        """
        button = ActionButtonWdg(title="Add")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")
        """
        
        button = ActionButtonWdg(title="Save")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_tasks_status_detail_top");
            var layout = top.getElement(".spt_layout");
            spt.table.set_layout(layout);
            spt.table.save_changes();

            '''
        } )
 
        button = ActionButtonWdg(title="Details")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")
        button.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.tools.SObjectDetailWdg';
            var kwargs = {
                search_key: bvr.search_key
            }

            var server = TacticServerStub.get();
            var sobject = server.get_by_search_key(bvr.search_key);
            var name = sobject.name;
            if (!name) {
                name = sobject.code;
            }

            var title = "Detail ["+name+"]";
            spt.tab.add_new(title, title, class_name, kwargs);
            '''
        } )



        # TODO: can't use this for now because the action class is not passed through
        # the table layout to the EditMultipleCmd
        """
        config = '''
        <config>
        <test>
        <element name='tasks' title='Tasks'>
           <display class='tactic.ui.table.TaskElementWdg'>
            <layout>vertical</layout>
            <status_color>status</status_color>
            <show_assigned>true</show_assigned>
            <show_dates>true</show_dates>
            <edit>true</edit>
            <edit_status>true</edit_status>
            <edit_assigned>true</edit_assigned>
            <show_filler_tasks>true</show_filler_tasks>
            <show_task_edit>true</show_task_edit>
          </display>
          <action class='tactic.ui.table.TaskElementCbk'/>
        </element>
        </test>
        </config>
        '''

        from pyasm.common import Xml
        xml = Xml()
        xml.read_string(config)
        """

        element = TableLayoutWdg(
                search_type=self.sobject.get_base_search_type(),
                view="test",
                show_shelf="false",
                search_key=self.sobject.get_search_key(),
                element_names=['task_pipeline_vertical'],
                show_select="false",
                show_search_limit="false",
                show_row_highlight="false"
        )
        top.add(element)




        """
        element = TableLayoutWdg(
                search_type="sthpw/task",
                show_shelf=False,
                parent_key=self.sobject.get_search_key(),
                element_names=['process','description','status','assigned','priority'],
                show_select=False,
                init_load_num=-1,
                show_search_limit=False,
        )
        top.add(element)
        """


        return top





__all__.append("TaskDetailPipelineWrapperWdg")
__all__.append("TaskDetailPipelineWdg")
class TaskDetailPipelineWrapperWdg(BaseRefreshWdg):


    def get_display(self):
        search_key = self.kwargs.get("search_key")
        self.sobject = Search.get_by_search_key(search_key)
        if self.sobject:
            self.parent = self.sobject.get_parent()
        else:
            self.parent = None

        pipeline_code = self.kwargs.get("pipeline")

        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_pipeline_wrapper")

        pipeline = Pipeline.get_by_code(pipeline_code)
        if pipeline:

            update_wdg = DivWdg()
            top.add(update_wdg)
            update_wdg.add_update( {
                'search_key': pipeline.get_search_key(),
                'interval': 3,
                'value': True,
                'cbjs_action': '''spt.panel.refresh_element(bvr.src_el)'''
            } )



        # it's ok to not have a parent unless it's a task, then just exit early
        if not self.parent and self.sobject and self.sobject.get_base_search_type() == 'sthpw/task':
            top.add('Parent of this task cannot be found.')
            return top


        top.add(self.get_pipeline_wdg(pipeline_code) )


        return top


    def get_pipeline_wdg(self, pipeline_code):
        div = DivWdg()

        height = self.kwargs.get("height") or 500
        show_title = self.kwargs.get("show_title")

        show_title = self.kwargs.get("show_title")
        if show_title not in [False, 'false']:
            title = DivWdg()
            title.add_color("background", "background3", -5)
            title.add_style("height: 20px")
            title.add_style("font-weight: bold")
            title.add_style("padding: 4px")
            title.add_border()
            title.add("Workflow")
            div.add(title)

        kwargs = {
            'width': "auto",
            'height': height,
            'show_title': show_title,
            'pipeline': pipeline_code,
            'is_editable': False,
            'use_mouse_wheel': True,
            'show_border': False,
        }
        pipeline = TaskDetailPipelineWdg(**kwargs)
        div.add(pipeline)
        load_div = DivWdg()
        div.add(load_div)


        # This is only for tasks!!!!
        enabled_tasks = set()
        from pyasm.biz import Task
        process = ''
        
        if self.parent:
            tasks = Task.get_by_sobject(self.parent)
            if self.sobject.has_value("process"):
                process = self.sobject.get_value("process")
        elif self.sobject:
            tasks = Task.get_by_sobject(self.sobject)
        else:
            tasks = []

        for task in tasks:
            enabled_tasks.add(task.get_value("process"))

        enabled_tasks = list(enabled_tasks)

        if pipeline_code:
            load_div.add_behavior( { 
            'type': 'load',
            'process': process,
            'enabled_tasks': enabled_tasks,
            'pipeline': pipeline_code,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(top);

            /*
            var nodes = spt.pipeline.get_nodes_by_group(bvr.pipeline);
            for (var i = 0; i < nodes.length; i++) {
                var has_task = false;
                var node = nodes[i];
                var node_name = spt.pipeline.get_node_name(node);
                for (var j = 0; j < bvr.enabled_tasks.length; j++) {
                    if (node_name == bvr.enabled_tasks[j]) {
                        has_task = true;
                        break;
                    }
                }

                if (!has_task && node) {
                    spt.pipeline.disable_node(node);
                }
            }
            */

            spt.pipeline.unselect_all_nodes();

            var node = spt.pipeline.get_node_by_name(bvr.process);
            if (node) {
                node.setStyle("font-weight", "bold");
                spt.pipeline.select_node(node);
            }

            spt.pipeline.fit_to_canvas(bvr.pipeline);


            var top = spt.pipeline.top;
            var text = top.getElement(".spt_pipeline_editor_current2");
            if (!text) {
                return;
            }

            var server = TacticServerStub.get();
            var pipeline = server.get_by_code("sthpw/pipeline", bvr.pipeline);
            var html = "<span class='hand spt_pipeline_link' spt_pipeline_code='"+pipeline.code+"'>"+pipeline.name+"</span>";
            text.innerHTML = html;



            '''
            } )


        return div



class TaskDetailPipelineWdg(PipelineCanvasWdg):

    def get_node_context_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Load Detail Report')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            var name = node.getAttribute("spt_element_name");

            var top = node.getParent(".spt_detail_top");
            spt.tab.top = top.getElement(".spt_tab_top");

            var search_key = top.getAttribute("spt_parent_key");
            if (!search_key) {
                search_key = top.getAttribute("spt_search_key");
            }

            var class_name = 'tactic.ui.tools.sobject_wdg.SObjectSingleProcessDetailWdg';
            var kwargs = {
                search_key: search_key,
                process: name
            }

            var title = "Detail ["+name+"]";
            var element_name = "detail_"+name;
            spt.tab.add_new(element_name, title, class_name, kwargs);
            '''
        } )
        menu.add(menu_item)


        return menu




class SObjectSingleProcessDetailWdg(BaseRefreshWdg):
    '''Shows the task, snapshot and notes information for an sobject'''

    def get_sobject(self):
        search_key = self.kwargs.get("search_key")
        self.sobject = Search.get_by_search_key(search_key)
        self.parent = None
        if self.sobject:
            self.parent = self.sobject.get_parent()
        return self.sobject


    def get_display(self):
        top = DivWdg()

        sobject = self.get_sobject()
        if not sobject:
            return top
        process = self.kwargs.get("process")

        #from tactic.ui.table import TaskElementWdg
        #task_wdg = TaskElementWdg()
        #task_wdg.set_sobject(self.sobject)
        #top.add(task_wdg)

        search = Search('sthpw/task')
        search.add_parent_filter(sobject)
        search.add_filter("process", process)
        tasks = search.get_sobjects()

        tasks_div = DivWdg()
        top.add(tasks_div)
        #tasks_div.add_style("padding: 0px 0px 20px 0px")
        tasks_div.add_style("margin: 10px")
        tasks_div.set_box_shadow()

        title = DivWdg()
        title.add_color("background", "background3", 0, -5)
        title.add_color("color", "color3", -10)
        title.add_border()
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("All Tasks for process '%s':" % process)
        tasks_div.add(title)


        task_wdg = TableLayoutWdg(search_type="sthpw/task",view='single_process', show_row_select="false", show_insert="false", show_gear="false", show_search_limit="false", show_search=False, show_refresh="false", show_shelf="false")
        task_wdg.set_sobjects(tasks)
        tasks_div.add(task_wdg)


        #from tactic.ui.container import ResizableTableWdg
        #table = ResizableTableWdg()
        table = Table()
        top.add(table)
        table.add_style("width: 100%")
        table.add_row()


        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("width: 50%")

        notes_div = DivWdg()
        td.add(notes_div)
        notes_div.set_box_shadow()
        notes_div.add_style("margin: 10px")

        title = DivWdg()
        notes_div.add(title)
        title.add_color("background", "background3", 0, -5)
        title.add_color("color", "color3", -10)
        title.add_border()
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("Notes:")


        from tactic.ui.widget.discussion_wdg import DiscussionWdg
        discussion_wdg = DiscussionWdg(search_key=sobject.get_search_key(), process=process, context_hidden=True,\
            show_note_expand=True)
        notes_div.add(discussion_wdg)
        menu = discussion_wdg.get_menu_wdg(notes_div)
        notes_div.add(menu)

        search = Search('sthpw/snapshot')
        search.add_parent_filter(sobject)
        search.add_filter("process", process)
        snapshots = search.get_sobjects()

        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("width: 50%")
        td.add_style("padding: 0 0 0 0")

        snapshots_div = DivWdg()
        td.add(snapshots_div)
        snapshots_div.set_box_shadow()
        snapshots_div.add_style("margin: 10px")


        title = DivWdg()
        title.add_color("background", "background3", 0, -5)
        title.add_color("color", "color3", -10)
        title.add_border()
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("Snapshots:")
        snapshots_div.add(title)


        snapshot_wdg = TableLayoutWdg(search_type="sthpw/snapshot",view='table', mode='simple', show_row_select=False, width='100%', show_shelf="false")
        snapshot_wdg.set_sobjects(snapshots)
        snapshots_div.add(snapshot_wdg)



        return top



__all__.append("TaskDetailPanelWdg")
class TaskDetailPanelWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top

        top.add_class("spt_tasks_status_detail_top")

        search_key = self.kwargs.get("search_key")

        from tactic.ui.table import TaskElementWdg
        from pyasm.search import Search
        self.sobject = Search.get_by_search_key(search_key)


        if self.sobject.get_base_search_type() == "sthpw/task":
            self.parent = self.sobject.get_parent()
        else:
            self.parent = None

        if self.parent:
            code = self.parent.get_value("code", no_exception=True)
            search_type_obj = self.parent.get_search_type_obj()
        else:
            code = self.sobject.get_value("code", no_exception=True)
            search_type_obj = self.sobject.get_search_type_obj()



        title = DivWdg()
        top.add(title)
        top.add_style("min-width: 500px")


        from tactic.ui.panel import ThumbWdg2
        from tactic.ui.widget import ActionButtonWdg
        from tactic.ui.panel import TableLayoutWdg

        search_key = self.sobject.get_search_key()


        thumb = ThumbWdg2()
        title.add(thumb)
        if self.parent:
            thumb.set_sobject(self.parent)
        else:
            thumb.set_sobject(self.sobject)
        thumb.add_style("width: 80px")
        thumb.add_style("float: left")
        thumb.add_style("margin: 0px 15px")



        title.add_color("background", "background", -5)
        title.add_style("padding: 10px")
        title.add_style("font-weight: bold")
        title.add_style("font-size: 1.4em")
        title.add_border(color="#DDD")

        title.add_style("margin-bottom: 20px")



        code = self.sobject.get("code")
        description = self.sobject.get("description")

        info_div = DivWdg()
        title.add(info_div)
        info_div.add("%s<br/>" % code)
        info_div.add("<br/>")
        info_div.add("<span style='font-size: 0.8em'>%s</span><br/>" % description)
        info_div.add_style("margin-left: 15px")


        shelf_wdg = DivWdg()
        top.add(shelf_wdg)
        shelf_wdg.add_style("margin-bottom: 10px")
        shelf_wdg.add_style("text-align: center")

        
        button = ActionButtonWdg(title="Save")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_tasks_status_detail_top");
            var layout = top.getElement(".spt_layout");
            spt.table.set_layout(layout);
            spt.table.save_changes();

            '''
        } )
        button.add_style("display: inline-block")
 


        button = ActionButtonWdg(title="Submit")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")


        button = ActionButtonWdg(title="Check-in")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")


        button = ActionButtonWdg(title="Download")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")

        button = ActionButtonWdg(title="Detail")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")



        from tactic.ui.panel import EditWdg

        element = EditWdg(
                search_type=self.sobject.get_base_search_type(),
                search_key=self.sobject.get_search_key(),
                element_names=['status','days_due','priority'],
                show_header=False,
                show_action=False
        )
        top.add(element)


        element = TableLayoutWdg(
                search_type=self.sobject.get_base_search_type(),
                view="test",
                show_shelf="false",
                search_key=self.sobject.get_search_key(),
                element_names=['work_hours'],
                show_select="false",
                show_search_limit="false",
                show_row_highlight="false",
                height="50px",
        )
        top.add(element)


        element = TableLayoutWdg(
                search_type=self.sobject.get_base_search_type(),
                use_parent="true",
                view="test",
                show_shelf="false",
                search_key=self.sobject.get_search_key(),
                element_names=['notes'],
                show_select="false",
                show_search_limit="false",
                show_row_highlight="false",
                height="50px",
        )
        top.add(element)

        return top


class SObjectRelatedNotesWdg(BaseRefreshWdg):

    def get_display(self):
        search_key = self.kwargs.get("search_key")

        from pyasm.search import Search
        self.sobject = Search.get_by_search_key(search_key)
        self.show_task_process = self.kwargs.get('show_task_process')

        top = self.top
        td = DivWdg()
        top.add(td)
        td.add_style("text-align: left")
        td.add_style("vertical-align: top")
        td.add_class("spt_notes_wrapper")
        td.add_style("padding: 20px")

        title_wdg = DivWdg()
        td.add(title_wdg)
        title_wdg.add_style("width: 100%")
        title_wdg.add("Notes")
        title_wdg.add_style("font-size: 1.4em")
        title_wdg.add_style("margin-bottom: 5px")

        desc_wdg = DivWdg()
        td.add(desc_wdg)
        desc_wdg.add("List of all the notes for this item.")
        td.add("<hr/>")

        #write out all the notes totals
        search_type = self.sobject.get_base_search_type()

        parts = search_type.split("/")


        from pyasm.biz import ProjectSetting
        related_types = ProjectSetting.get_value_by_key("notes/%s/related_types" % parts[1])
        if related_types:
            related_types = related_types.split(",")
        else:
            related_types = []


        sobjects = []
        for related_type in related_types:
            related_sobjects = Search.eval("@SOBJECT(%s)" % related_type, self.sobject)
            sobjects.extend(related_sobjects)

        sobjects.insert(0, self.sobject)

        from tactic.ui.widget.discussion_wdg import DiscussionWdg
        for sobject in sobjects:
            search_key = sobject.get_search_key()

            if len(sobjects) > 1:
                name = sobject.get_value("name", no_exception=True)
                if name:
                    td.add("<b>%s</b> - %s" % (sobject.get_code(), name))
                else:
                    td.add("<b>%s</b>" % sobject.get_code())

            notes_div = DivWdg()
            td.add(notes_div)


            discussion_wdg = DiscussionWdg(search_key=search_key,
                    context_hidden=False, show_note_expand=False,
                    show_task_process=self.show_task_process)

            notes_div.add(discussion_wdg)
            #menu = discussion_wdg.get_menu_wdg(notes_div)
            #notes_div.add(menu)

            notes_div.add_style("min-width: 300px")
            notes_div.add_style("height: auto")
            notes_div.add_style("min-height: 20")
            notes_div.add_style("overflow-y: auto")
            notes_div.add_class("spt_resizable")

            if len(sobjects) > 1:
                notes_div.add_style("margin: 10px 10px")
                td.add("<hr/>")

        return top

