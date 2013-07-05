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

__all__ = ['SchemaToolWdg', 'SchemaToolCanvasWdg', 'SchemaConnectorWdg', 'SchemaPropertyWdg','SchemaConnectorCbk']

from tactic.ui.common import BaseRefreshWdg

from pyasm.biz import Project, Schema
from pyasm.web import DivWdg, WebContainer, Table
from pyasm.command import Command
from pyasm.search import Search, SearchType, SearchException, WidgetDbConfig, SqlException
from tactic.ui.panel import TableLayoutWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg, SelectWdg, HiddenWdg, CheckboxWdg
from tactic.ui.container import MenuItem, Menu, ResizableTableWdg, TabWdg, DialogWdg, SmartMenu
from tactic.ui.app import SearchTypeCreatorWdg
from tactic.ui.widget import ActionButtonWdg

from pipeline_canvas_wdg import *
from pipeline_wdg import *

from tactic_client_lib import TacticServerStub

class SchemaToolWdg(PipelineToolWdg, PipelineEditorWdg):
    '''Schema Widget'''

    def get_group_type(my):
        return "schema"

    def get_node_type(my):
        return "search_type"


    def get_display(my):
        top = DivWdg()
        top.add_class("spt_schema_tool_top")
        top.add_class("spt_pipeline_editor_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        my.properties_dialog = DialogWdg(display=False, offset={'x': 0,'y':0})
        #inner.add( my.properties_dialog )
        my.properties_dialog_id = my.properties_dialog.get_id()
        my.properties_dialog.add_title("Edit Properties")

        connector_wdg = DivWdg()
        my.properties_dialog.add(connector_wdg)
        connector_wdg.add_class("spt_schema_connector_info")
        connector_wdg.add_style("padding: 10px")
        connector_wdg.add("Please select a node or connector.")
        connector_wdg.add_color("color", "color")
        connector_wdg.add_color("background", "background")
        connector_wdg.add_border()



        inner.add_color("background", "background")
        inner.add_border()

        dialog = my.get_create_dialog()
        inner.add( my.get_shelf_wdg() )

        inner.add(dialog)

        table = ResizableTableWdg()
        #table = Table()
        inner.add(table)
        table.add_row()

        canvas_wrapper = DivWdg()
        td = table.add_cell(canvas_wrapper)
        canvas_wrapper.add_class("spt_pipeline_wrapper")
        canvas = my.get_canvas()
        my.unique_id = canvas.get_unique_id()
        canvas_wrapper.add( canvas )

        table.add_row()
        td = table.add_cell()
        td.add(my.get_tab_wdg() )

        project = Project.get()
        current_project =project
        project_code = project.get_code()

        # go through all of the schema items and see if there is a search
        # type defined for this.
        exists = {}
        not_exists = {}
        not_has_tables = {}
        sthpw_types = {}
        sthpw_project = Project.get_by_code('sthpw')
        schema = Schema.get()
        search_types = schema.get_search_types(hierarchy=False)
        for search_type in search_types:
            project = current_project
            try:
                if search_type.startswith("sthpw/") or search_type.startswith("config/"):
                    sthpw_types[search_type] = True
                    project = sthpw_project
                    
                search_type_sobj = SearchType.get(search_type)

                # have to set project=sthpw_project above where applicable, 
                # otherwise this will automatically reports sthpw tables do not exist
                has_table = project.has_table(search_type)
                if not has_table:
                    not_has_tables[search_type] = True
                    raise SearchException("No table")

                exists[search_type] = True
            except SearchException, e:
                not_exists[search_type] = True

        div = DivWdg()
        inner.add(div)
        div.add_behavior( {
        'type': 'load',
        'exists': exists,
        'not_exists': not_exists,
        'not_has_tables': not_has_tables,
        'sthpw_types': sthpw_types,
        'project_code': project_code,
        'cbjs_action': '''
        var top = bvr.src_el.getParent('.spt_schema_tool_top');
        spt.pipeline.init_cbk(top);
        spt.pipeline.import_schema( bvr.project_code );

        for (search_type in bvr.exists) {
            var node = spt.pipeline.get_node_by_name(search_type);
            node.spt_registered = true;
            spt.pipeline.enable_node(node);
            //spt.pipeline.set_color(node, "#7A7");
        }

        for (search_type in bvr.not_exists) {
            var node = spt.pipeline.get_node_by_name(search_type);
            spt.pipeline.disable_node(node);
            node.spt_registered = false;
        }


        for (search_type in bvr.sthpw_types) {
            var node = spt.pipeline.get_node_by_name(search_type);
            spt.pipeline.set_color(node, "#AA7");
            spt.pipeline.enable_node(node);
        }


        for (search_type in bvr.not_has_tables) {
            var node = spt.pipeline.get_node_by_name(search_type);
            spt.pipeline.set_color(node, "#A33");
        }


        '''
        } )




        # open connection dialog everytime a connection is made

        event_name = "%s|connector_create" % my.unique_id

        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'dialog_id': my.properties_dialog_id,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var class_name = "tactic.ui.tools.SchemaConnectorWdg";
        var dialog = $(bvr.dialog_id);
        spt.show(dialog);

        var selected = spt.pipeline.get_selected();
        var item = selected[selected.length-1];
        spt.pipeline.clear_selected();
        spt.pipeline.add_to_selected(item);

        var from_node = item.get_from_node();
        var to_node = item.get_to_node();

        var connector = spt.pipeline.get_selected_connector();

        var kwargs = {
            from_search_type: spt.pipeline.get_node_name(from_node),
            to_search_type: spt.pipeline.get_node_name(to_node),
            from_col: connector.get_attr("from_col"),
            to_col: connector.get_attr("to_col")
        };
        var content = dialog.getElement(".spt_dialog_content");
        spt.panel.load(content, class_name, kwargs);
        
        '''
        } )


        project = Project.get()
        project_type = project.get_value("type")

        # open connection dialog everytime a connection is made
        event_name = "%s|node_create" % my.unique_id

        # Note this goes through every node, every time?
        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'project_type': project_type,
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);
        var node = bvr.firing_element;

        // add the prefix
        node.setAttribute("spt_prefix", bvr.project_type);

        if (typeof(node.spt_registered) == 'undefined' || node.spt_registered == false) {
            node.spt_registered = false;
            spt.pipeline.disable_node(node);
        }
        '''
        } )


        # listen to the stype|create event and refresh
        # IS THIS BEING USED? 
        # boris: yes

        event_name = 'stype|create'
        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'cbjs_action': '''
        var data = bvr.firing_data;

        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var group_name = spt.pipeline.get_current_group();
        var server = TacticServerStub.get();
        var project_code = server.get_project();

        var search_type = data.search_type;
        var parts = search_type.split("/");
        var prefix = parts[0];
        var name = parts[1];
        var node = spt.pipeline.get_node_by_name(name);
        if (!node) {
            node = spt.pipeline.get_node_by_name(search_type);
        }
        if (!node) {
            spt.info("Node [" + search_type + "] does not exist on canvas");
            // this happens if we are in Manage Search Types page
            return
        }
        else {
            node.setAttribute("spt_prefix", prefix);
            spt.pipeline.select_node(node);
        }

        
        var xml = ''
        try {
            xml = spt.pipeline.export_group(group_name); 
        }
        catch(e) {
            spt.alert(e);
            return;
        }
            
        var search_key = "sthpw/schema?code="+group_name;

        var data = {
            'schema': xml,
            'description': 'Schema for project ['+project_code+']',
        }
        server.insert_update(search_key, data );

        spt.panel.refresh(top);
        '''
        } )

        # listen to the stype|select event
        bgcolor = my.top.get_color("background")
        event_name = 'stype|select'
        div.add_behavior( {
        'type': 'listen',
        'bgcolor': bgcolor,
        'event_name': event_name,
        'cbjs_action': '''

        var top = bvr.firing_element.getParent(".spt_schema_tool_top");
        var dialog_top = top.getElement(".spt_dialog_top");
        var dialog = top.getElement(".spt_dialog_content");

        var node = spt.pipeline.get_selected_node();
        var group_name = spt.pipeline.get_group_by_node(node).get_name();
        var name = spt.pipeline.get_node_name(node);

        var class_name ='tactic.ui.tools.SchemaPropertyWdg'
        var kwargs = {
            'search_type': name,
            'schema_code': group_name
        }

        // FIXME: setTimeout is used to mitigate the drag bvr turning on when a node is selected. but the drag bvr needs to be fixed so it doesn't turn on when spt.panel.load() is called
        if (spt.is_shown(dialog_top)) {
            setTimeout(function(){spt.panel.load(dialog, class_name, kwargs);}, 200);
        }
        //spt.show(dialog);

        
        //connector_wdg.innerHTML = "<div style='padding: 10px; background: "+bvr.bgcolor+"'>No Connectors selected</div>";
        '''
        } )


        if my.kwargs.get("is_refresh") == "true":
            return inner
        else:
            return top




    def get_shelf_wdg(my):
 
        shelf_wdg = DivWdg()
        shelf_wdg.add_style("padding: 5px 5px 0px 5px")
        shelf_wdg.add_style("margin-bottom: -3px")
        shelf_wdg.add_color("background", "background", -10)
        shelf_wdg.add_border()


        spacing_divs = []
        for i in range(0, 3):
            spacing_div = DivWdg()
            spacing_divs.append(spacing_div)
            spacing_div.add_style("height: 36px")
            spacing_div.add_style("width: 2px")
            spacing_div.add_style("margin: 0 10 0 20")
            spacing_div.add_style("border-style: solid")
            spacing_div.add_style("border-width: 0 0 0 1")
            spacing_div.add_style("border-color: %s" % spacing_div.get_color("border"))
            spacing_div.add_style("float: left")



        #my.properties_dialog = DialogWdg(display=False)
        #my.properties_dialog.add_title("Properties")
        props_div = DivWdg()
        my.properties_dialog.add(props_div)
        properties_wdg = SchemaPropertyWdg()
        my.properties_dialog.add(properties_wdg )


        save_action = ''' 
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);
        var group_name = spt.pipeline.get_current_group();
        var server = TacticServerStub.get();
        var project_code = server.get_project();
        
        spt.app_busy.show("Saving schema ["+group_name+"]",null);
        var xml = '';
        try {
            xml = spt.pipeline.export_group(group_name);

        } catch(e) {
            spt.alert(e);
            spt.app_busy.hide();
            return;
        }
        var search_key = "sthpw/schema?code="+group_name;

        var data = {
            'schema': xml,
            'description': 'Schema for project ['+project_code+']',
        }
        server.insert_update(search_key, data );


        spt.panel.refresh(top);


        spt.app_busy.hide();
        '''

        shelf_wdg.add_named_listener('schema|save', save_action)
        button_div = my.get_buttons_wdg();
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)

        shelf_wdg.add(spacing_divs[0])

        zoom_div = DivWdg()
        shelf_wdg.add(zoom_div)
        zoom_div.add_style("float: left")
        zoom_div.add_style("height: 34px")
        zoom_div.add_style("margin-left: 15px")
        zoom_div.add_style("margin-right: 10px")
        zoom_div.add_style("padding-left: 5px")
        zoom_div.add_style("padding-right: 15px")

        button_div = my.get_zoom_buttons_wdg();
        zoom_div.add(button_div)
        button_div.add_style("margin-left: 10px")

        shelf_wdg.add(spacing_divs[1])

        button_div = my.get_action_buttons_wdg();
        button_div.add_style("margin-left: 10px")
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)
        button_div.add_style("margin-right: 20px")

        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias="project-schema|stype-connect|stype-register|tactic-anatomy-lesson|project-workflow-introduction", description="Show Schema Editor Help")
        shelf_wdg.add(help_button)

        shelf_wdg.add("<br clear='all'/>")

        return shelf_wdg


    def get_buttons_wdg(my):
        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg

        button_row = ButtonRowWdg(show_title=True)


        button = ButtonNewWdg(title="Refresh Schema", icon=IconWdg.REFRESH)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.app_busy.show("Refreshing Canvas");
        var top = bvr.src_el.getParent(".spt_schema_tool_top");
        spt.panel.refresh(top);
        spt.app_busy.hide();
        '''
        } )
 

        button = ButtonNewWdg(title="Save Schema on Canvas", icon=IconWdg.SAVE)
        icon = button.get_icon_wdg()
      
        """
        glow_action = '''var canvas = spt.get_cousin(bvr.src_el, '.spt_button_top', '.spt_button_canvas');
            var context = canvas.getContext("2d");
            var top = bvr.src_el.getParent('.spt_button_top');
            var image = bvr.src_el.getParent('.spt_button_top').getElement('img');
	   
               var click = top.getElement(".spt_button_icon");
            click.setStyle('display','none');
           
            canvas.setStyle('display','');

            var imgd = context.getImageData(0, 0, 500, 300);
	    var pix = imgd.data;
	    for (var i = 0, n = pix.length; i < n; i += 4) {
	    var grayscale = pix[i  ] * .3 + pix[i+1] * .59 + pix[i+2] * .11;
	    pix[i  ] = grayscale;   // red
	    pix[i+1] = grayscale;   // green
	    pix[i+2] = grayscale;   // blue
	   
	    }

	    //context.putImageData(imgd, 0, 0);
            context.drawImage(image, 0, 0);
           
            
          

                        
         '''
        """
     
        # makes it glow
        glow_action = ''' 
        bvr.src_el.setStyles(
        {'outline': 'none', 
        'border-color': '#CF7e1B', 
        'box-shadow': '0 0 8px #CF7e1b'});
        '''

        icon.add_named_listener('schema|change', glow_action)
        
        button_row.add(button)

       
            
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var ok = function(bvr) {spt.named_events.fire_event('schema|save', bvr);}
        var cancel = null;
        spt.confirm("Are you sure you wish to save the current schema?", ok, cancel);
       
        
        '''
        } )

        




        button = ButtonNewWdg(title="Add sType Node", icon=IconWdg.ADD)
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);
        var node = spt.pipeline.add_node();
        spt.pipeline.disable_node(node);
        spt.pipeline.unselect_all_nodes();

        top.addClass("spt_has_changes");
        '''
        } )


        button = ButtonNewWdg(title="Delete Selected", icon=IconWdg.DELETE)
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        spt.pipeline.delete_selected();

        var nodes = spt.pipeline.get_selected_nodes();
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].spt_registered) {
                var node_name = spt.pipeline.get_node_name(nodes[i]);
                spt.alert("Cannot delete a node ["+node_name+"] that is already registered");
                return;
            }
            spt.pipeline.remove_node(nodes[i]);
        }
        '''
        } )


        return button_row





    def get_create_dialog(my):

        dialog = DialogWdg(display=False, offset={'x':-100,'y':0})
        dialog.add_title("Register a new sType")
        my.dialog_id = dialog.get_id()

        div = DivWdg()
        dialog.add( div )
        return dialog




    def get_tab_wdg(my):
        project = Project.get()
        project_code = project.get_code()
        project_type = project.get_value("type")
        config_xml = '''
        <config>
        <tab>
          <element name='stype_list' title='sType List'>
            <display class='tactic.ui.panel.FastTableLayoutWdg'>
                <search_type>sthpw/search_type</search_type>
                <view>table</view>
                <show_search>false</show_search>
                <expression>@SOBJECT(sthpw/search_type['namespace','in','%s|%s'])</expression>
                <insert>false</insert>
            </display>
          </element>
          <element name='schema' title='Schema Details'>
            <display class='tactic.ui.panel.FastTableLayoutWdg'>
                <search_type>sthpw/schema</search_type>
                <view>table</view>
                <show_search>false</show_search>
                <expression>@SOBJECT(sthpw/schema['code', $PROJECT])</expression>
                <insert>false</insert>
            </display>
          </element>
        </tab>
        </config>
        ''' % (project_code, project_type)
        tab = TabWdg(config_xml=config_xml)

        return tab


    def get_canvas(my):
        my.height = my.kwargs.get("height")
        if not my.height:
            my.height = 300
        my.width = my.kwargs.get("width")
        return SchemaToolCanvasWdg(height=my.height, width=my.width, dialog_id=my.dialog_id, nob_mode="dynamic", line_mode='line', has_prefix=True, filter_node_name=True)



    def get_action_buttons_wdg(my):
        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg

        button_row = ButtonRowWdg(show_title=True)

        button = ButtonNewWdg(title="Register Selected sType", icon=IconWdg.REGISTER)
        button_row.add(button)

        # Note this is a copy of the context menu
        button.add_behavior( {
        'type': 'click_up',
        'dialog_id': my.dialog_id,
        'cbjs_action': '''
        var nodes = spt.pipeline.get_selected_nodes();
        if (nodes.length == 0) {
            spt.alert("Please select a node to register");
            return;
        }

        // use the first one
        var node = nodes[0];


        var registered = node.spt_registered;
        if (registered) {
            spt.alert("sType ["+spt.pipeline.get_node_name(node)+"] is already registered");
            //return;
        }

        var search_type = spt.pipeline.get_node_name(node);
        var dialog = $(bvr.dialog_id);

        var pos = node.getPosition();
        dialog.setStyle("top", pos.y + 50);
        dialog.setStyle("left", pos.x - 100);


        var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';
        var content = dialog.getElement(".spt_dialog_content");

        var kwargs = {
            'search_type': search_type,
        }

        spt.show(dialog);
        spt.panel.load(content, class_name, kwargs);

        //spt.pipeline.enable_node(node);
        '''
        } )

        
        button = ButtonNewWdg(title="Edit Pipelines", icon=IconWdg.PIPELINE)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var nodes = spt.pipeline.get_selected_nodes();
        if (nodes.length == 0) {
            spt.alert("Please select a node");
            return;
        }
        var node = nodes[nodes.length-1];

        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet registered. Please register this search type first." );
            return;
        }

        var class_name = 'tactic.ui.tools.PipelineToolWdg';

        var kwargs = {
            'search_type': search_type,
        }

        var element_name = "project_worflow";
        var title = "Project Workflows";

        var top = node.getParent(".spt_schema_tool_top");
        //var tab_top = top.getElement(".spt_tab_top");
        //spt.tab.set_tab_top(tab_top);
        spt.tab.set_main_body_tab();
        spt.tab.add_new(element_name, title, class_name, kwargs);
        '''
        } )


        project_code = Project.get_project_code()
        button = ButtonNewWdg(title="Edit Properties", icon=IconWdg.INFO)
        button.add_dialog(my.properties_dialog)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'project_code': project_code,
        'dialog_id': my.properties_dialog_id,
        'offset': { 'x': 0, 'y': 0 },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var group = spt.pipeline.get_group(bvr.project_code);
        //var connectors = group.get_connectors();
        //var connector = connectors[0];
        var connector = spt.pipeline.get_selected_connector();

        var class_name = "tactic.ui.tools.SchemaConnectorWdg";
        var dialog = $(bvr.dialog_id);
        
        /*
        var pos = bvr.src_el.getPosition();
        var size = bvr.src_el.getSize();
        dialog.setStyle("left", pos.x+bvr.offset.x);
        dialog.setStyle("top", pos.y+size.y+bvr.offset.y+5);
        spt.toggle_show_hide(dialog);

        */

        var selected = spt.pipeline.get_selected();
        if (selected.length == 0) {
            return;
        }
        var item = selected[selected.length-1];

        var from_node = item.get_from_node();
        var to_node = item.get_to_node();
        var kwargs = {
            from_search_type: spt.pipeline.get_node_name(from_node),
            to_search_type: spt.pipeline.get_node_name(to_node),
            from_col: connector.get_attr("from_col"),
            to_col: connector.get_attr("to_col")
        };
        var content = dialog.getElement(".spt_dialog_content");
        spt.panel.load(content, class_name, kwargs);

        '''
        } )




        #button = ButtonNewWdg(title="Table Manager", icon=IconWdg.DB)
        #button_row.add(button)

        #button = ButtonNewWdg(title="View Manager", icon=IconWdg.VIEW)
        #button_row.add(button)





        return button_row


class SchemaConnectorWdg(BaseRefreshWdg):

    def get_display(my):

        project_code = Project.get_project_code()
        project = Project.get()
        project_type = project.get_value("type")

        # default should be project_type (just like SearchTypeCreatorWdg)
        if project_type:
            namespace = project_type
        else:
            namespace = project_code

        my.relationship = my.kwargs.get("relationship")


        left_search_type = my.kwargs.get("from_search_type")
        right_search_type = my.kwargs.get("to_search_type")
        if left_search_type.find("/") == -1:
            left_search_type = "%s/%s" % ( namespace, left_search_type)
        if right_search_type.find("/") == -1:
            right_search_type = "%s/%s" % ( namespace, right_search_type)

        web = WebContainer.get_web()
        orig_left_search_type = web.get_form_value('left_search_type')
        orig_right_search_type = web.get_form_value('right_search_type')

      
         
        my.left_search_type = left_search_type
        my.right_search_type = right_search_type

        left_selected = my.kwargs.get("from_col")
        right_selected = my.kwargs.get("to_col")

        namespace, left_table = left_search_type.split("/")
        namespace, right_table = right_search_type.split("/")
        if not left_selected:
            left_selected = "%s_code" % right_table
        if not right_selected:
            right_selected = "code"


        try:
            left_search_type_sobj = SearchType.get(left_search_type)
            left_columns = SearchType.get_columns(left_search_type)
        except Exception, e:
            left_search_type_sobj = SearchType.create("sthpw/search_type")
            left_search_type_sobj.set_value("search_type", left_search_type)
            left_columns = []

        try:
            right_search_type_sobj = SearchType.get(right_search_type)
            right_columns = SearchType.get_columns(right_search_type)
        except Exception, e:
            right_search_type_sobj = SearchType.create("sthpw/search_type")
            right_search_type_sobj.set_value("search_type", right_search_type)
            right_columns = []


        div = DivWdg()

       

        my.set_as_panel(div)
        div.add_class("spt_connect_top")
        div.add_color("background", "background")
        div.add_color("color", "color")
        div.add_style("width: 320px")
        div.add_style("padding: 10px")



        inner = DivWdg()

        # reversed, redraw the connector
        if orig_left_search_type == right_search_type and orig_right_search_type == left_search_type:

            new_from_col = web.get_form_value('right')
            new_to_col = web.get_form_value('left')
            inner.add_behavior({'type':'load',
            'cbjs_action': '''
            var connector = spt.pipeline.get_selected_connector();
            var f_node = connector.get_from_node();
            var t_node = connector.get_to_node();
            connector.set_from_node(t_node);
            connector.set_to_node(f_node);
            connector.set_attr('from_col', '%s');
            connector.set_attr('to_col', '%s');
            spt.pipeline.redraw_canvas();
            connector.draw_line(true);
       


            '''%(new_from_col, new_to_col)})
        else:
            # just draw the line with attribute names
             inner.add_behavior({'type':'load',
            'cbjs_action': '''
            var connector = spt.pipeline.get_selected_connector();
            connector.draw_line(true);
            '''})
        div.add(inner)

        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='stype-connect|tactic-anatomy-lesson')
        inner.add( help_button )
        help_button.add_style("float: right")
        help_button.add_style("margin-top: -8px")
        help_button.add_style("margin-right: -5px")

        info_div = DivWdg()
        inner.add(info_div)




        info_div.add("<b>Connection Editor</b><hr/>")
        #info_div.add("From sType: [%s]<br/>" % left_search_type )
        #info_div.add("To sType: [%s]<br/>" % right_search_type )
        #info_div.add("Connected from [%s] to [%s]<br/>" % (left_selected, right_selected) )


        relationship_select = SelectWdg("relationship")
        inner.add("Relationship Type: ")
        inner.add(relationship_select)
        #relationship_select.set_option("values", "code")
        relationship_select.set_option("values", "code|many_to_many")
        if my.relationship:
            relationship_select.set_value(my.relationship)


        relationship_select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_connect_top");
            var value = bvr.src_el.value;
            var code_el = top.getElement(".spt_code");
            var many_to_many_el = top.getElement(".spt_many_to_many");
            if (value == 'code') {
                code_el.setStyle("display", "");
                many_to_many_el.setStyle("display", "none");
            }
            else {
                code_el.setStyle("display", "none");
                many_to_many_el.setStyle("display", "");
            }
            '''
        } )


        inner.add("<br/><br/>")

        code_wdg = my.get_code_options(left_search_type_sobj, right_search_type_sobj, left_table, right_table, left_selected, right_selected, left_columns, right_columns)
        inner.add( code_wdg)

        many_wdg = my.get_many_to_many_options(left_search_type_sobj, right_search_type_sobj, left_table, right_table, left_selected, right_selected, left_columns, right_columns)
        inner.add( many_wdg)

        if my.relationship == "many_to_many":
            code_wdg.add_style("display: none")
        else:
            many_wdg.add_style("display: none")



        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return div

        return div




    """

    def xxget_code_options(my, left_search_type_sobj, right_search_type_sobj, left_table, right_table, left_selected, right_selected, left_columns, right_columns):

        div = DivWdg()
        div.add_class("spt_code");

        div.add("Connect the left sType to the right sType.  You can either select one of the columns displayed or type in manually.  The column does not need to exist yet.")

        div.add("<hr/>")

        save = ActionButtonWdg(title='OK', tip='Remember to save the whole schema at the end.')
        div.add(save)
        save.add_style("float: right")
        save.add_style("margin: -6px 30px 0 0")

        project_code = Project.get_project_code()
        save.add_behavior( {
        'type': 'click_up',
        'project': project_code,
        'cbjs_action': '''

        spt.app_busy.show("Saving Connections");

        var connect_top = bvr.src_el.getParent(".spt_connect_top");
        var values = spt.api.get_input_values(connect_top, null, false);

        var top = connect_top.getParent(".spt_schema_tool_top");

        spt.pipeline.init_cbk(top);
        var groups = spt.pipeline.get_groups();
        var group = groups[bvr.project];

        var left_search_type = values.left_search_type;
        var left_node = spt.pipeline.get_node_by_name(left_search_type);
        var right_search_type = values.right_search_type;
        var right_node = spt.pipeline.get_node_by_name(right_search_type);


        if (left_node == null) {
            var parts = left_search_type.split("/");
            var name = parts[1];
            left_node = spt.pipeline.get_node_by_name(name);
        }
        if (right_node == null) {
            var parts = right_search_type.split("/");
            var name = parts[1];
            right_node = spt.pipeline.get_node_by_name(name);
        }


        var server = TacticServerStub.get();

        // get the selected connector
        var connector = spt.pipeline.get_selected_connector();

        connector.set_from_node(left_node);
        connector.set_to_node(right_node);

        connector.set_color("#00f");
        spt.pipeline.redraw_canvas();

        var relationship = values.relationship;
        connector.set_attr("relationship", relationship)
        connector.set_attr("from_col", values.left);
        connector.set_attr("to_col", values.right);
        if (values.register_stypes == "on") {

            spt.app_busy.show("Registering sTypes using defaults");

            var class_name = 'tactic.ui.tools.SchemaSaveCmd';
            var kwargs = {
                'from_search_type': values.left_search_type,
                'to_search_type': values.right_search_type
            };
            server.execute_cmd(class_name, kwargs);
            //spt.panel.refresh(top);
            // just do a schema save so that new stypes are displayed properly
            spt.named_events.fire_event('schema|save', bvr);
        }

        if (values.create_columns == "on") {
            spt.app_busy.show("Creating columns");
            var cmd = 'tactic.ui.tools.SchemaConnectorCbk';
            try {
                server.execute_cmd(cmd, values);
            } catch (e) {
                var msg = spt.exception.handler(e);
                if (msg.test(/not registered/)) 
                    msg += '. You can try to turn on the option "Register sType with defaults"';
                spt.alert(msg);
            }
        }

        spt.app_busy.show("Firing events");
        var dialog = bvr.src_el.getParent(".spt_dialog_top");
        var dialog_id = dialog.getAttribute("spt_dialog_id"); 
        var event = dialog_id + "|dialog_close";
        spt.named_events.fire_event(event, {});
        spt.named_events.fire_event('schema|change', {});

        spt.app_busy.hide();

        '''
        } )


        hidden = HiddenWdg("left_search_type")
        div.add(hidden)
        hidden.set_value(my.left_search_type)

        hidden = HiddenWdg("right_search_type")
        div.add(hidden)
        hidden.set_value(my.right_search_type)


    """

    def get_code_options(my, left_search_type_sobj, right_search_type_sobj, left_table, right_table, left_selected, right_selected, left_columns, right_columns):

        div = DivWdg()
        div.add_class("spt_code");


        # check to see if 1) the stypes are registered and 2) the columns exist
        # if not, then provide a button to "auto-register" and create the
        # columns

        if not left_search_type_sobj or not right_search_type_sobj:
            div.add("Register sTypes with defaults ")
            checkbox = CheckboxWdg("register_stypes")
            div.add(checkbox)
            div.add("<br clear='all'/>")

        div.add("Create Columns ")
        checkbox = CheckboxWdg("create_columns")
        checkbox.set_checked()
        div.add(checkbox)

        # add save button
        save = ActionButtonWdg(title='OK', tip='Remember to save the whole schema at the end.')
        div.add(save)
        save.add_style("float: right")
        save.add_style("margin: -25px -3 0 0")

        project_code = Project.get_project_code()
        save.add_behavior( {
        'type': 'click_up',
        'project': project_code,
        'cbjs_action': '''

        spt.app_busy.show("Confirming Connections");

        var connect_top = bvr.src_el.getParent(".spt_connect_top");
        var values = spt.api.get_input_values(connect_top, null, false);
        var top = connect_top.getParent(".spt_schema_tool_top");

        spt.pipeline.init_cbk(top);
        var groups = spt.pipeline.get_groups();
        var group = groups[bvr.project];

        var left_search_type = values.left_search_type;
        //var left_node = spt.pipeline.get_node_by_name(left_search_type);
        var right_search_type = values.right_search_type;
        //var right_node = spt.pipeline.get_node_by_name(right_search_type);


        var server = TacticServerStub.get();

        // get the selected connector
        var connector = spt.pipeline.get_selected_connector();
        var left_node = connector.get_from_node();
        var right_node = connector.get_to_node();

        connector.set_from_node(left_node);
        connector.set_to_node(right_node);

        connector.set_color("#00f");
        spt.pipeline.redraw_canvas();

        var relationship = values.relationship;
        connector.set_attr("relationship", relationship)
        connector.set_attr("from_col", values.left);
        connector.set_attr("to_col", values.right);
        if (values.register_stypes == "on") {

            spt.app_busy.show("Registering sTypes using defaults");

            var class_name = 'tactic.ui.tools.SchemaSaveCmd';
            var kwargs = {
                'from_search_type': values.left_search_type,
                'to_search_type': values.right_search_type
            };
            server.execute_cmd(class_name, kwargs);
            //spt.panel.refresh(top);
            // just do a schema save so that new stypes are displayed properly
            spt.named_events.fire_event('schema|save', bvr);
        }

        if (values.create_columns == "on") {
            spt.app_busy.show("Creating columns");
            var cmd = 'tactic.ui.tools.SchemaConnectorCbk';
            try {
                server.execute_cmd(cmd, values);
            } catch (e) {
                var msg = spt.exception.handler(e);
                if (msg.test(/not registered/)) 
                    msg += '. You can try to turn on the option "Register sType with defaults"';
                spt.alert(msg);
            }
        }

        //spt.app_busy.show("Firing events");
        var dialog = bvr.src_el.getParent(".spt_dialog_top");
        var dialog_id = dialog.getAttribute("spt_dialog_id"); 
        var event = dialog_id + "|dialog_close";
        spt.named_events.fire_event(event, {});
        spt.named_events.fire_event('schema|change', {});

        spt.app_busy.hide();

        '''
        } )


        hidden = HiddenWdg("left_search_type")
        div.add(hidden)
        hidden.set_value(my.left_search_type)

        hidden = HiddenWdg("right_search_type")
        div.add(hidden)
        hidden.set_value(my.right_search_type)



        div.add("<br clear='all'/><br/>")

        from tactic.ui.widget import SingleButtonWdg
        switch = SingleButtonWdg(title="Switch", icon=IconWdg.UNDO)
        switch.add_behavior( {
            'type': 'click_up',
            'left_search_type': my.left_search_type,
            'right_search_type': my.right_search_type,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_connect_top");

            var kwargs = {
              left_search_type: bvr.left_search_type,
              right_search_type: bvr.right_search_type
            };

            top.setAttribute("spt_from_search_type", bvr.right_search_type);
            top.setAttribute("spt_to_search_type", bvr.left_search_type);

            var connector = spt.pipeline.get_selected_connector();
            var from_col = '';
            var to_col = '';

            //reverse it
            if (connector) {
                to_col = connector.get_attr('from_col') ?  connector.get_attr('from_col'): '';
                from_col = connector.get_attr('to_col') ?  connector.get_attr('to_col') : '';
            }
            top.setAttribute("spt_from_col", from_col);
            top.setAttribute("spt_to_col", to_col);

            spt.panel.refresh(top);

            '''
        } )

        table = Table()
        div.add(table)
        table.add_color("color", "color")

        table.add_row()
        table.add_cell("From (child):")
        table.add_cell()
        table.add_cell("To (parent):")


        tr = table.add_row()
        tr.add_gradient("background", "background", -10)
        tr.add_style("height: 30px")

        # left title
        td = table.add_cell(left_table)
        td.add_style("padding-left: 5px")
        td.add_border()

        switch_div = DivWdg(switch)
        td = table.add_cell(switch_div)
        td.add_border()
        switch_div.add_style("margin: 3 1 7 3")

        # right title
        td = table.add_cell(right_table)
        td.add_style("padding-left: 5px")
        td.add_border()


        tr, td = table.add_row_cell()
        td.add("<br/>Using columns:")


        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 150px")
        left.add_class("spt_connect_column_top")
        left.add_class("spt_dts")
        left.add_style("padding: 5px")
        #left.add_color("background", "background3")


        hidden = TextWdg("left")
        left.add(hidden)
        hidden.add_class("spt_input")
        if left_selected:
            hidden.set_value(left_selected)

        left.add("<br/>")
        left.add("<hr/>")

        for column in left_columns:
            selected = False
            if column == left_selected:
                selected = True
            column_div = my.get_column_wdg(column, selected)
            left.add(column_div)

        if not left_search_type_sobj:
            widget = DivWdg()
            left.add(widget)
            widget.add_style("padding: 5px")
            widget.add("<i>-- Not Registered --</i>")

        table.add_cell()

        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add_style("width: 150px")
        right.add_class("spt_connect_column_top")
        right.add_class("spt_dts")
        right.add_style("padding: 5px")
        #right.add_color("background", "background3")

        hidden = TextWdg("right")
        right.add(hidden);
        hidden.add_class("spt_input")
        if right_selected:
            hidden.set_value(right_selected)

        right.add("<br/>")
        right.add("<hr/>")

        for column in right_columns:
            selected = False
            if column == right_selected:
                selected = True
            column_div = my.get_column_wdg(column, selected)
            right.add(column_div)

        if not right_search_type_sobj:
            widget = DivWdg()
            widget.add_style("padding: 5px")
            right.add(widget)
            widget.add("<i>-- Not Registered --</i>")

        return div


    def get_column_wdg(my, column, selected=False):
        column_div = DivWdg()
        column_div.add_style("padding: 2px")
        column_div.add_class("spt_connect_column")
        column_div.add_class("hand")

        color = column_div.get_color("background")
        if selected:
            column_div.add_color("background", "background", -20)


        column_div.add_behavior( {
        'type': 'hover',
        'color': color,
        #'cb_set_prefix': 'spt.mouse.table_layout_hover',
        #'add_color_modifier': 10,
        #'cbjs_action_over': '''
        #var color = spt.css.modify_color_value(bvr.color, -10);
        #bvr.src_el.setstyle("background", color);
        #''',
        #'cbjs_action_out': '''
        #bvr.src_el.setstyle("background", bvr.color);
        #'''
        } )


        column_div.add_behavior( {
        'type': 'click_up',
        'color': color,
        'cbjs_action': '''
        var column_top = bvr.src_el.getParent(".spt_connect_column_top");
        var connects = column_top.getElements(".spt_connect_column");
        for (var i = 0; i < connects.length; i++) {
            connects[i].setStyle("background", bvr.color);
        }

        var value = bvr.src_el.innerHTML;

        var color = spt.css.modify_color_value(bvr.color, -10);
        bvr.src_el.setStyle("background", color);

        var input = column_top.getElement(".spt_input");
        input.value = value;
        

        '''
        } )


        column_div.add(column)
        return column_div



    def get_many_to_many_options(my, left_search_type_sobj, right_search_type_sobj, left_table, right_table, left_selected, right_selected, left_columns, right_columns):

        div = DivWdg()
        div.add_class("spt_many_to_many");

        new_search_type = "%s_in_%s" % (left_table, right_table)
        left_search_type = left_search_type_sobj.get_base_key()
        right_search_type = right_search_type_sobj.get_base_key()

        msg_div = DivWdg()
        div.add(msg_div)
        msg_div.add("This will create a new intermediate sType called which will relate the two sTypes.<br/>")
        msg_div.add_style("margin: 15px")
        msg_div.add_style("padding: 15px")
        msg_div.add_border()
        msg_div.add_color("color", "color")
        msg_div.add_color("background", "background3")

        div.add("<br/>")

        div.add("Create: &nbsp;")

        text = TextWdg("new_search_type")
        text.add_class("spt_instance")
        div.add(text)
        text.set_value(new_search_type)
        div.add("<br/>"*2)


        div.add("Between: ")
        div.add("<b>%s</b>" % left_search_type)
        div.add(" and ")
        div.add("<b>%s</b>" % right_search_type)
        div.add("<br/><br/>")

        button = ActionButtonWdg(title="Create >>")
        div.add(button)
        button.add_style("float: right")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var dialog = bvr.src_el.getParent(".spt_dialog_top");
            spt.app_busy.show("Creating Many to Many relationship");
            spt.hide(dialog);
            var top = bvr.src_el.getParent(".spt_many_to_many");
            var instance_el = top.getElement(".spt_instance");
            var instance = instance_el.value;
            spt.relationship.create_many_to_many(instance);
            spt.named_events.fire_event('schema|save', {});
            spt.app_busy.hide();
            '''
        } )

        div.add("<br clear='all'/>")


        div.add_behavior( {
            'type': 'load',
            'from': left_search_type_sobj.get_base_key(),
            'to': right_search_type_sobj.get_base_key(),
            'from_table': left_table,
            'to_table': right_table,
            'cbjs_action': '''

spt.relationship = {};

spt.relationship.create_many_to_many = function(instance) {

    var server = TacticServerStub.get();
    var project_code = server.get_project();

    var from = bvr.from;
    var to = bvr.to;

    var group_name = spt.pipeline.get_current_group();

    var from_parts = from.split("/");
    var to_parts = to.split("/");

    if (!instance) {
        instance = group_name + "/" + from_parts[1] + "_in_" + to_parts[1];
    }
    else {
        instance = group_name + "/" + instance;
    }

    var connector = spt.pipeline.get_selected_connector();
    connector.set_attr("relationship", "many_to_many");
    connector.set_attr("node_type", "instance");
    spt.pipeline.delete_selected(connector);

    var instance_node = spt.pipeline.add_node(instance)
    spt.pipeline.clear_selected();

    var from_node = spt.pipeline.get_node_by_name(from);
    var to_node = spt.pipeline.get_node_by_name(to);
    var group = spt.pipeline.get_group(project_code);

    var from_pos = spt.pipeline.get_position(from_node);
    var to_pos = spt.pipeline.get_position(to_node);

    // calculate the position of the node
    var tl_pos = {};
    var br_pos = {};
    if (to_pos.x > from_pos.x) {
        tl_pos.x = from_pos.x;
        br_pos.x = to_pos.x;
    }
    else {
        tl_pos.x = to_pos.x;
        br_pos.x = from_pos.x;
    }
    if (to_pos.y > from_pos.y) {
        tl_pos.y = from_pos.y;
        br_pos.y = to_pos.y;
    }
    else {
        tl_pos.y = to_pos.y;
        br_pos.y = from_pos.y;
    }

    var pos = {
                x: (br_pos.x - tl_pos.x) / 2 + tl_pos.x,
                y: (br_pos.y - tl_pos.y) / 2 + tl_pos.y
              }
    spt.pipeline.move_to(instance_node, pos.x, pos.y);

    var connector = spt.pipeline.add_connector();
    connector.set_from_node(instance_node);
    connector.set_to_node(from_node);
    connector.set_attr("relationship", "code");
    connector.draw();
    group.add_connector(connector);

    var connector2 = spt.pipeline.add_connector();
    connector2.set_from_node(instance_node);
    connector2.set_to_node(to_node);
    connector2.set_attr("relationship", "code");
    connector2.draw();
    group.add_connector(connector2)

    server.start();


    try  {
        var cmd = 'tactic.ui.app.SearchTypeCreatorCmd';
        var kwargs = {
            search_type_name: instance,
            namespace: group_name,
            title: 'Instance sType',
            description: 'Connection from ['+from+'] to ['+to+']',
            column_name: [bvr.from_table+'_code', bvr.to_table+'_code'],
            column_type: ['varchar', 'varchar']

        }
        server.execute_cmd(cmd, kwargs);

        var schema = spt.pipeline.export_group(project_code);

        // update the schema
        var search_key = 'sthpw/schema?code=' + project_code;
        var data = {
            schema: schema
        };
        server.update(search_key, data);

        server.finish();


    }
    catch(e) {
        server.abort();
        throw(e);
    }

}
        '''
        } )

        return div



class SchemaPropertyWdg(BaseRefreshWdg):

    def get_display(my):
        div = DivWdg()

        div.add_class("spt_schema_properties_top")

        search_type = my.kwargs.get("search_type")
        schema_code = my.kwargs.get("schema_code")

        schema = Schema.get_by_code(schema_code)
        if not schema:
            attrs = {}
        else:
            attrs = schema.get_attrs_by_search_type(search_type)


        div.add_color('background', 'background')

        #div.set_id("properties_editor")
        #div.add_style("display", "none")



        title_div = DivWdg()
        div.add(title_div)
        title_div.add_style("height: 20px")
        title_div.add_gradient("background", "background", -20)
        title_div.add_class("spt_property_title")
        if not search_type:
            title_div.add("sType: <i>--None--</i>")
        else:
            title_div.add("sType: %s" % search_type)
        title_div.add_style("font-weight: bold")
        title_div.add_style("margin-bottom: 5px")
        title_div.add_style("padding: 5px")


        # add a no process message
        """
        no_process_wdg = DivWdg()
        no_process_wdg.add_class("spt_pipeline_properties_no_process")
        div.add(no_process_wdg)
        no_process_wdg.add( "No sType node or connector selected")
        no_process_wdg.add_style("padding: 30px")
        """


        # get a list of known properties
        properties = ['display']


        # show other properties
        table = Table()
        table.add_class("spt_schema_properties_content")
        table.add_style("margin: 10px")
        table.add_color('color', 'color')
        table.add_row()
        #table.add_header("Property")
        #table.add_header("Value")

        if not search_type:
            table.add_style("display: none")

        table.add_behavior( {
        'type': 'load',
        'cbjs_action': my.get_onload_js()
        } )

        
        # Making invisible to ensure that it still gets recorded if there.
        tr = table.add_row()
        td = table.add_cell('Display: ')
        td.add_style("width: 100px")
        td.add_attr("title", "display name of the sType when instantiated. e.g. @GET(prod/asset.code)")
        text_name = "spt_property_display"
        text = TextWdg(text_name)
        if attrs.get('display'):
            text.set_value(attrs.get('display'))

        text.set_option('size','35')
        text.add_class(text_name)
        text.add_event("onBlur", "spt.schema_properties.set_properties()")

        th = table.add_cell(text)
        
   

        tr, td = table.add_row_cell()

        button = ActionButtonWdg(title="OK", tip="Remember to save the schema at the end.")
        td.add("<hr/>")
        td.add(button)
        button.add_style("float: right")
        button.add_style("margin-right: 20px")
        td.add("<br clear='all'/>")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.schema_properties.set_properties();
        var top = bvr.src_el.getParent(".spt_dialog_top");
         
        spt.named_events.fire_event('schema|change', {});
        spt.hide(top);
        '''
        } )


        div.add(table)

        return div

    def get_onload_js(my):
        return r'''

spt.schema_properties = {};
spt.schema_properties.set_properties = function() {

    var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
    var wrapper = top.getElement(".spt_pipeline_wrapper");
    spt.pipeline.init_cbk(wrapper);

    var prop_top = spt.get_element(top, ".spt_schema_properties_top");
    var connector_top = spt.get_element(top, ".spt_connector_properties_top");

    var selected_nodes = spt.pipeline.get_selected_nodes();
    var selected = spt.pipeline.get_selected();
    if (selected_nodes.length > 1) {
        spt.alert('Please select only 1 node or connector to set property');
        return;
    }
        
    if (selected_nodes.length==1) {
        /*var title_el = spt.get_element(top, ".spt_property_title");
        var node_name = title_el.node_name;*/
        var node = selected_nodes[0];
        if (node)
        {
            var properties = ['display'];

            for ( var i = 0; i < properties.length; i++ ) {
                var el = prop_top.getElement(".spt_property_" + properties[i]);
                spt.pipeline.set_node_property( node, properties[i], el.value );
            }
        }
    }
  
            
}

        '''


class SchemaConnectorCbk(Command):

    def execute(my):
        right_search_type = my.kwargs.get('right_search_type')
        right = my.kwargs.get('right')
        left_search_type = my.kwargs.get('left_search_type')
        left = my.kwargs.get('left')
        col_type = 'varchar(256)'

        server = TacticServerStub.get() 
        server.add_column_to_search_type(right_search_type, right, col_type)
        server.add_column_to_search_type(left_search_type, left, col_type)


        namespace, left_table = left_search_type.split("/")
        namespace, right_table = right_search_type.split("/")


        element_name = left
        if element_name.endswith("_code"):
            element_name2 = left.replace("_code", "")
        elif element_name.endswith("_id"):
            element_name2 = left.replace("_id", "")
        else:
            element_name2 = ""


        # create a view definition
        element_xml = '''
        <element name='%s'/>
        ''' % (element_name)
        config = WidgetDbConfig.get_by_search_type(left_search_type, "definition")
        if config:
            config.append_xml_element(element_name, element_xml)

            # create a view definition
            if element_name2:
                element_xml = '''
                <element name='%s' edit="true">
                  <display widget='expression'>
                    <expression>@GET(%s.name)</expression>
                    <calc_mode>fast</calc_mode>
                  </display>
                </element>
                ''' % (element_name2, right_search_type)
                print "element: ", element_xml
                config.append_xml_element(element_name2, element_xml)
            config.commit_config()




        # create an edit definition for the code
        element_xml = '''
        <element name='%s'>
          <display class='SelectWdg'>
            <empty>-- Select --</empty>
            <query>%s|code|code</query>
          </display>
        </element>
        ''' % (element_name, right_search_type)

        config = WidgetDbConfig.get_by_search_type(left_search_type, "edit_definition")
        if not config:
            config = SearchType.create("config/widget_config")
            config.set_value("search_type", left_search_type)
            config.set_value("view", "edit_definition")
            config._init()

        config.append_xml_element(element_name, element_xml)

        if element_name2:
            element_xml = '''
            <element name='%s'>
              <display class='SelectWdg'>
                <empty>-- Select --</empty>
                <query>%s|code|name</query>
              </display>
              <action class='DatabaseAction'>
                <column>%s</column>
              </action>
            </element>
            ''' % (element_name2, right_search_type, element_name)

            config.append_xml_element(element_name2, element_xml)

        config.commit_config()



        # create an edit definition for the code
        if element_name2:
            element_xml = '''
            <element name='%s'/>
            ''' % (element_name2)
            config = WidgetDbConfig.get_by_search_type(left_search_type, "edit")
            config.append_xml_element(element_name2, element_xml)

            config.commit_config()

        else:
            element_xml = '''
            <element name='%s'/>
            ''' % (element_name)
            config = WidgetDbConfig.get_by_search_type(left_search_type, "edit")
            config.append_xml_element(element_name, element_xml)

            config.commit_config()







        # create a view definition for the parent
        element_name = left_table
        element_xml = '''
        <element name='%s'>
          <display widget='hidden_row'>
            <dynamic_class>tactic.ui.panel.FastTableLayoutWdg</dynamic_class>
            <search_type>%s</search_type>
            <view>table</view>
            <show_shelf>true</show_shelf>
          </display>
        </element>
        ''' % (element_name, left_search_type)

        config = WidgetDbConfig.get_by_search_type(right_search_type, "definition")
        if config:
            config.append_xml_element(element_name, element_xml)
            config.commit_config()




class SchemaManyToManyCbk(Command):

    def execute(my):
        right_search_type = my.kwargs.get('right_search_type')
        right = my.kwargs.get('right')
        left_search_type = my.kwargs.get('left_search_type')
        left = my.kwargs.get('left')

        instance_type = "xxx/xxx"

        # register this search type
        cmd = SearchTypeCreatorCbk()

        # add the connectors

        # do this in javascript???

        cbjs_action = '''
        spt.pipeline.add_new(bvr.instance_type);

        // remove the two connectors and add
        var from_node = spt.pipeline.get_node_by_name("project/blah");
        var to_node = spt.pipeline.get_node_by_name("project/blah2");
        connector.set_from_node(from_node);
        connector.set_to_node(to_node);
        connector.draw();

        '''

 


class SchemaToolCanvasWdg(PipelineToolCanvasWdg):

    def get_node_size(my):
        width = 100
        height = 50
        return width, height


    def get_extra_node_content_wdg(my):
        icon = IconWdg("Expand", IconWdg.CONTENTS)
        icon.add_style("position: absolute")
        icon.add_style("top: 2px")
        icon.add_style("left: 3px")
        icon.add_class("hand")
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = bvr.src_el.getParent(".spt_pipeline_node");
        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet created. Please create this sType first" );
            return;
        }

        var class_name = 'tactic.ui.panel.TableLayoutWdg';

        var kwargs = {
            'search_type': search_type,
            'view': 'table',
        }

        var parts = search_type.split("/");
        var element_name = search_type + "_raw_data";
        var title = parts[parts.length-1]+" [data]";

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);
        spt.tab.add_new(element_name, title, class_name, kwargs);




        '''
        } )

        return icon


    def get_node_behaviors(my):
        return []

    def get_canvas_behaviors(my):
        bgcolor = my.top.get_color("background")
        return [
        {
        'type': 'click_up',
        'bgcolor': bgcolor,
        'cbjs_action': '''
        spt.pipeline.init(bvr);

        var top = bvr.src_el.getParent(".spt_schema_tool_top");
        var connector_wdg = top.getElement(".spt_dialog_content");

        var connector = spt.pipeline.hit_test_mouse(mouse_411);
        
        //var connector = spt.pipeline.get_selected();
        if (connector == null) {
            spt.pipeline.clear_selected();
            connector_wdg.innerHTML = "<div style='padding: 10px; background: "+bvr.bgcolor+"'>No sType or Connectors selected</div>";
            return;
        }


        var from_node = connector.get_from_node();
        var from_search_type = spt.pipeline.get_node_name(from_node);
        var to_node = connector.get_to_node();
        var to_search_type = spt.pipeline.get_node_name(to_node);

        var attrs = connector.get_attrs();

        var class_name = 'tactic.ui.tools.SchemaConnectorWdg';
        var kwargs = {
            from_search_type: from_search_type,
            to_search_type: to_search_type,
            from_col: connector.get_attr("from_col"),
            to_col: connector.get_attr("to_col"),
            relationship: attrs.relationship
        };
        spt.panel.load(connector_wdg, class_name, kwargs);

        '''
        }
        ]

        """
        {
        'type': 'double_click',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var top = bvr.src_el.getParent(".spt_schema_tool_top");
        var connector_wdg = top.getElement(".spt_schema_connector_info");
        var dialog = connector_wdg.getParent(".spt_dialog_top");
        dialog.setStyle("display", "");
        '''
        }
        """


    def get_node_context_menu(my):

        dialog_id = my.kwargs.get('dialog_id')

        #menu = super(PipelineToolCanvasWdg, my).get_node_context_menu()

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.dg_table.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Rename sType')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            var registered = node.spt_registered;
            if (registered) {
                spt.alert("Cannot rename a registered sType");
                return;
            }
            spt.pipeline.set_rename_mode(node);
            '''
        } )
        menu.add(menu_item)

        menu_item = MenuItem(type='separator', label='Actions')
        menu.add(menu_item)

      




      



        menu_item = MenuItem(type='action', label='Register sType')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'dialog_id': dialog_id,
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);

        var registered = node.spt_registered;
        if (registered) {
            spt.alert("sType ["+spt.pipeline.get_node_name(node)+"] is already registered");
            return;
        }

        var search_type = spt.pipeline.get_node_name(node);
        var dialog = $(bvr.dialog_id);

        var pos = node.getPosition();
        dialog.setStyle("top", pos.y + 50);
        dialog.setStyle("left", pos.x - 100);


        var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';
        var content = dialog.getElement(".spt_dialog_content");

        var kwargs = {
            'search_type': search_type,
        }

        spt.show(dialog);
        spt.panel.load(content, class_name, kwargs);

        //spt.pipeline.enable_node(node);

        '''
        } )

    

        menu_item = MenuItem(type='separator', label='Actions')
        menu.add(menu_item)




        menu_item = MenuItem(type='action', label='Delete sType')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);

            var registered = node.spt_registered;
            if (!registered) {
                spt.pipeline.init( { src_el: node } );

                if (node.spt_registered) {
                    spt.alert("Cannot remove registered sType");
                    return;
                }

                spt.pipeline.remove_node(node);
            }
            else {
                var node_name = spt.pipeline.get_node_name(node);

                var class_name = 'tactic.ui.tools.DeleteSearchTypeToolWdg';
                var kwargs = {
                    search_type: node_name
                };
                var popup = spt.panel.load_popup("Delete", class_name, kwargs);
                // store it for deletion later
                popup.stype_node = node;
            }
            '''
        } )
        menu.add(menu_item)




        menu_item = MenuItem(type='title', label='Details')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Edit Properties')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);
        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet registered. Please register this search type first" );
            return;
        }
        var class_name = 'tactic.ui.panel.EditWdg';
        var kwargs = {
            search_key: 'sthpw/search_object?code='+search_type
        }
        spt.panel.load_popup("Edit sType", class_name, kwargs);

        '''
        } )

 
        menu_item = MenuItem(type='action', label='Import Data')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);
        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet registered. Please register this search type first" );
            return;
        }
        var class_name = 'tactic.ui.widget.CsvImportWdg';
        var kwargs = {
            search_type: search_type,
        }
        spt.panel.load_popup("Import Data", class_name, kwargs);

        '''
        } )


        menu_item = MenuItem(type='action', label='Edit Pipeline(s)')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);

        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet registered. Please register this search type first" );
            return;
        }

        var class_name = 'tactic.ui.tools.PipelineToolWdg';

        var kwargs = {
            'search_type': search_type,
        }

        var element_name = "project_workflow";
        var title = "Project Workflow";

        var top = node.getParent(".spt_schema_tool_top");
        //var tab_top = top.getElement(".spt_tab_top");
        //spt.tab.set_tab_top(tab_top);
        spt.tab.set_main_body_tab();
        spt.tab.add_new(element_name, title, class_name, kwargs);

        '''
        } )

        menu_item = MenuItem(type='action', label='View Manager')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);

        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet created. Please create this search type first" );
            return;
        }

        var class_name = 'tactic.ui.manager.ViewManagerWdg';

        var kwargs = {
            'search_type': search_type
        }

        var element_name = "view_" + search_type;
        var title = "View ["+search_type+"]";

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);
        spt.tab.add_new(element_name, title, class_name, kwargs);


        '''
        } )



        menu_item = MenuItem(type='action', label='Show Triggers')
        #menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);

        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet created. Please create this search type first" );
            return;
        }

        var class_name = 'tactic.ui.panel.TableLayoutWdg';

        var kwargs = {
            'search_type': 'sthpw/trigger',
            'view': 'table',
            'expression': "@SOBJECT(sthpw/trigger['search_type','"+search_type+"'])"
        }

        var element_name = "trigger_" + search_type;
        var title = "Triggers ["+search_type+"]";

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);
        spt.tab.add_new(element_name, title, class_name, kwargs);

        '''
        } )


        menu_item = MenuItem(type='action', label='Show Naming Conventions')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);

        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet created. Please create this search type first" );
            return;
        }

        var class_name = 'tactic.ui.panel.TableLayoutWdg';

        var kwargs = {
            'search_type': 'config/naming',
            'view': 'table',
            'expression': "@SOBJECT(config/naming['search_type','"+search_type+"'])"
        }

        var element_name = "naming" + search_type;
        var title = "Naming ["+search_type+"]";

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);
        spt.tab.add_new(element_name, title, class_name, kwargs);

        '''
        } )



        menu_item = MenuItem(type='action', label='Show Triggers/Notifications')
        # FIXME: Disabling for now
        #menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);

            var top = node.getParent(".spt_schema_tool_top");
            spt.tab.top = top.getElement(".spt_tab_top");

            var search_type = node.getAttribute("spt_element_name");
            //var pipeline_code = node.spt_group;

            var class_name = 'tactic.ui.tools.trigger_wdg.TriggerToolWdg';
            var kwargs = {
                //pipeline_code: pipeline_code,
                search_type: search_type,
                mode: 'schema'
            }

            element_name = 'trigger_'+search_type;
            title = 'Triggers ['+search_type+']';
            spt.tab.add_new(element_name, title, class_name, kwargs);

            '''
        } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Show Raw Data')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);

        var search_type = spt.pipeline.get_node_name(node);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet created. Please create this search type first" );
            return;
        }

        var class_name = 'tactic.ui.panel.TableLayoutWdg';

        var kwargs = {
            'search_type': search_type,
            'view': 'table',
        }

        var parts = search_type.split("/");
        var element_name = search_type + "_raw_data";
        var title = parts[parts.length-1]+" [data]";

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);
        spt.tab.add_new(element_name, title, class_name, kwargs);

        '''
        } )


        

        menu_item = MenuItem(type='action', label='Edit Database Columns')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);
        var registered = node.spt_registered;
        if (!registered) {
            spt.alert("sType ["+search_type+"] is not yet created. Please create this search type first" );
            return;
        }

        var search_type = spt.pipeline.get_node_name(node);

        var class_name = "tactic.ui.app.SearchTypeToolWdg";
        var kwargs = {
            show_definition: 'true',
            search_type: search_type,
        };

        var element_name = "database_" + search_type;
        element_name = element_name.replace("/", "_");
        var title = "Columns ["+search_type+"]";

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);
        spt.tab.add_new(element_name, title, class_name, kwargs);
        '''
        } )






        """
        menu_item = MenuItem(type='action', label='Show Detail')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var node = spt.smenu.get_activator(bvr);
        spt.pipeline.init(node);

        var top = node.getParent(".spt_schema_tool_top");
        var tab_top = top.getElement(".spt_tab_top");
        spt.tab.set_tab_top(tab_top);

        var search_type = spt.pipeline.get_node_name(node);

        var element_name = 'detail_' + search_type;
        var title = 'Detail [' + search_type + ']';
        var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';
        spt.tab.add_new(element_name, title, class_name);
        '''
        } )
        """

        return menu



__all__.append('SchemaSaveCmd')
from pyasm.command import Command
class SchemaSaveCmd(Command):

    def get_title(my):
        return "SchemaSaveCmd"

    def execute(my):
        # save the schema

        # go through each connection and ensure that there are the following
        # elements
        project = Project.get()
        project_type = project.get_value("type")
        project_code = Project.get_project_code()

        if project_type:
            namespace = project_type
        else:
            namespace = project_code


        # foreign key
        # photos.store_code -> store.code

        from_search_type = my.kwargs.get("from_search_type")
        to_search_type = my.kwargs.get("to_search_type")
        if from_search_type.find("/") == -1:
            from_search_type = "%s/%s" % (namespace, from_search_type)
        if to_search_type.find("/") == -1:
            to_search_type = "%s/%s" % (namespace, to_search_type)

        namespace, from_table = from_search_type.split("/")
        namespace, to_table = to_search_type.split("/")

        print "from: ", from_search_type
        print "to: ", to_search_type
       
        from_search_type_obj = SearchType.get(from_search_type, no_exception=True)
        to_search_type_obj = SearchType.get(to_search_type, no_exception=True)
        print "FROM obj ", from_search_type_obj
        print "To obj ", to_search_type_obj


        # register the search types
        from tactic.ui.app import SearchTypeCreatorCmd
        if not from_search_type_obj:
            creator = SearchTypeCreatorCmd(search_type_name=from_search_type, sobject_parent=to_search_type)
            creator.execute()
            my.add_description('Saving Schema info with %s' %from_search_type)
        if not to_search_type_obj:
            creator = SearchTypeCreatorCmd(search_type_name=to_search_type)
            creator.execute()
            my.add_description('Saving Schema info with %s' %to_search_type)

        return

        # find edit for photo
        element_name = "%s_hidden" % from_table
        config = WidgetDbConfig.get_by_search_type(from_search_type, "definition")
        hidden_row_xml = '''
<element name="%s" edit="false" title="%s">
  <display widget="hidden_row">
    <search_type>%s</search_type>
    <show_gear>false</show_gear>
    <show_refresh>false</show_refresh>
    <dynamic_class>tactic.ui.panel.TableLayoutWdg</dynamic_class>
    <show_search_limit>false</show_search_limit>
    <view>table</view>
  </display>
</element>
        ''' % (element_name, from_table, from_search_type)

        config.append_xml_element(element_name, hidden_row_xml)


        # find edit for photo
        config = WidgetConfig.get_by_search_type(from_search_type, "edit")
        element_name = to_table
        drop_xml = '''
<element name="%s">
  <display class="tactic.ui.table.DropElementWdg">
    <css_background-color>#425952</css_background-color>
    <accepted_drop_type>%s</accepted_drop_type>
  </display>
</element>
        ''' % ( to_table, from_search_type )
        config.append_xml_element(to_table, hidden_row_xml)




