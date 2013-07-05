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

__all__ = ['SObjectEditorWdg', 'SObjectAddAttrCmd']

from pyasm.search import SearchType, Search, SObject, WidgetDbConfig, WidgetDbConfigCache, Sql

from pyasm.common import *

from pyasm.web import *
from pyasm.widget import *
from pyasm.command import *
from pyasm.common import Xml
from pyasm.search import DbContainer, AlterTableUndo

import re


class SObjectEditorWdg(Widget):

    REORDER = "Reorder_View"
    
    
    def __init__(my, database, schema):
        my.database = database
        my.schema = schema
        my.search_type = None
        my.script_div = Widget()
        my.row_ids = []
        my.view_list = []
        super(SObjectEditorWdg,my).__init__()

    def init(my):
        
        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)

        WebContainer.register_cmd("pyasm.admin.creator.SObjectAddAttrCmd")


        script = HtmlElement.script("""
        function remove_attr(view) {
            var msg = "This will remove the element from the config."
            if (view == 'definition')
                msg = "This will also REMOVE THE COLUMN in the database."
            var agree = confirm( msg + " Are you sure?")
            if (agree)
                return true
            else
                return false
        }

        function remove_view(view_name) {
            var msg = "This will remove the view [" + view_name + "]."
            
            var agree = confirm( msg + " Are you sure?")
            if (agree)
                return true
            else
                return false
        }
        """)
        my.add(script)



        my.add( my._get_title_wdg() )


        # get all of the configs
        my.configs = WidgetDbConfig.get_all_by_search_type(\
            my.search_type)
        div = DivWdg()
        div.set_class("admin_section")
        div.add(HtmlElement.h3("Elements"))
        div.add( my._get_create_attr_wdg() )

        div.add(HiddenWdg(my.REORDER)) 
        
        div.add(HtmlElement.br())
        div.add(HtmlElement.h3("Definition"))
        div.add( my._get_views_attr_wdg(my.configs, "definition") )
       

        if not my.configs:
            my.add(div)
            my.init_script()
            return
        
        div.add( my._get_current_view_wdg() )

        my.add(div)


        div = DivWdg()
        div.set_class("admin_section")
        
        div.add(HtmlElement.h3("Views"))
        control_div = DivWdg( css='filter_box')
        control_div.add_style('height: 2em')
        div.add(control_div)
        div.add(HtmlElement.br())

        view_select = FilterSelectWdg(SObjectAddAttrCmd.CURRENT_VIEW)
        view_select.set_option('values', '|'.join(my.view_list))
        view_select.set_option('labels', '|'.join(my.view_list))
        view_select.add_empty_option()
        filtered_view = view_select.get_value()
        filter_span = SpanWdg("View: ", css='med')
        filter_span.add(view_select)
        control_div.add(filter_span)
        remove_button = IconSubmitWdg(SObjectAddAttrCmd.REMOVE_VIEW, IconWdg.RETIRE, \
            long=True)
        view_name = view_select.get_value()
        remove_button.add_event('onclick', "if (!remove_view('%s')) \
                    return false;" % view_name )
        remove_button.set_text("Remove %s" % view_name)
        remove_button.add_style('color: #c97061')
        if view_name and \
            not WebContainer.get_web().get_form_value(SObjectAddAttrCmd.REMOVE_VIEW):
            control_div.add(SpanWdg(remove_button, css='med'))

        view_input = TextWdg("view_name")
        view_submit = SubmitWdg(SObjectAddAttrCmd.CREATE_VIEW)
        div.add("Name: ")
        div.add(view_input)
        div.add(view_submit)
        div.add(HtmlElement.br(2))
        div.add( my._get_views_attr_wdg(my.configs, filtered_view) )
        my.add(div)

        # test out overrides per project (bit of a hack for a filter)
        '''
        search = Search("sthpw/widget_config")
        search.add_regex_filter("search_type", '%s_' % my.search_type, op='EQ')
        
        configs = search.get_sobjects()
        '''
        my.init_script()
        
    def init_script(my):
        # setup script has to be added before the main script div
        setup_script = HtmlElement.script('SET_DHTML(CURSOR_MOVE,TRANSPARENT, "%s")' \
            % ('","'.join(my.row_ids)))
        my.add(setup_script)
        my.add(my.script_div)
        my.script_div.add(HtmlElement.script('''
        
var dy;
var top_elem_y;
var cur_y;
var cur_x;
var view;
var Elts;

// Array intended to reflect the order of the draggable items

function my_PickFunc()
{
    // Store position of the item about to be dragged
    // so we can interchange positions of items when the drag operation ends
    cur_y = dd.obj.y;
    cur_x = dd.obj.x;
    //alert('name ' + dd.obj.name)
    obj = document.getElementById(dd.obj.name)
    view = obj.getAttribute('view')
    Elts = eval(view + "_Elts")
    top_elem_y = dd.elements[Elts[0].id].y
    dy = dd.elements[Elts[1].id].y - top_elem_y

   
}
    
function my_DragFunc()
{
}

function my_DropFunc()
{
    // Calculate the snap position which is closest to the drop coordinates
    var y = dd.obj.y+dy/2;
    
    y = Math.max(top_elem_y, Math.min(y - (y-top_elem_y)%dy, top_elem_y + (Elts.length-1)*dy));
    // Index of the new position within the spatial order of all items
    
    var i = (y-top_elem_y)/dy;
    
    var old_i
    
    for (var k = 0; k < Elts.length; k++)
    {
        if (Elts[k] == dd.obj)
            old_i = k
    }
                
    if (i >= old_i)
    {
        for (k=old_i; k <= i; k++)
        {
            Elts[k].moveTo(cur_x, Elts[k].y -dy)
            Elts[k] = Elts[k+1]
        }
    }
    else
    {
        for (k=old_i; k >= i; k--)
        {
            Elts[k].moveTo(cur_x, Elts[k].y +dy)
            Elts[k] = Elts[k-1]
        }
    }
    // Let the dropped item snap to position
    dd.obj.moveTo(cur_x, y);
    
    // Update the array according to the changed succession of items
    Elts[i] = dd.obj;
    var Elts_id = new Array()
    for (k=0; k<Elts.length; k++)
        Elts_id[k] = Elts[k].id
    document.getElementsByName(view + "_Elts")[0].value = Elts_id.join(',')
     
}

function my_select_elements(this_obj, name_id, select_id)
{
    var val = this_obj.value; 
    text = document.getElementsByName(name_id)[0]; 
    custom_span = document.getElementById('custom_element_span')
    if (val != 'Custom. . .') 
    {
        text.value = val; 
        custom_span.style.display = 'None';
    }
    else 
    { 
        text.value = ''; 
        custom_span.style.display = 'inline';
    }

    // select attr type accordingly
    var attr_type_sel = document.getElementsByName(select_id)[0]
    if (text.value == 'timestamp')
        attr_type_sel.value = 'Date'
    else if (text.value == 'discussion')
        attr_type_sel.value = 'Text'
    else if (text.value == 'images' || text.value == 'snapshot' || text.value =='update')
        attr_type_sel.value = ''
        
}    
        '''))


        return my.script_div




    def _get_views_attr_wdg(my, configs, filtered_view):

        div = DivWdg()

        table = Table()
        for config in configs:

            view = config.get_value("view")
            # skip views not currently selected
            if view != filtered_view:
                continue

            table.add_row()
            '''
            checkbox = CheckboxWdg("view_select")
            checkbox.set_option("value", view)
            table.add_cell(checkbox)

            table.add_cell(view)
            '''
            table.add_cell( my._get_list_attr_wdg(view) )
       
            update_wdg = UpdateWdg()
            update_wdg.set_name("update")
            update_wdg.set_sobject(config)
            table.add_cell(update_wdg)
            table.add_row()
            table.add_blank_cell()

        div.add(table)


        return div






    def _get_title_wdg(my):

        # create the select widget for the asset type
        
        select = FilterSelectWdg("search_type_current")
        select.add_empty_option()
        search = Search( SearchType.SEARCH_TYPE )

        # ignore standard tactic types
        search.add_regex_filter("search_type", "^(sthpw|prod|flash).*", op='NEQ')
        
        checkbox = CheckboxWdg('project_only')
        checkbox.set_submit_onchange()
        checkbox.set_persistence()
        cb_span = SpanWdg(checkbox, css='med')
        cb_span.add('project only')
        #checkbox.set_checked()
        cb_value = checkbox.get_value()
        if cb_value:
            search.add_filter("namespace", my.namespace)
        search.add_order_by('search_type')
        select.set_search_for_options(search,"search_type","search_type")
       
        title = DivWdg(css='filter_box')
        title.add_style('height','2em')
        title.add(cb_span)
        title.add_style("text-align: center")
        title.add(HtmlElement.b("Current Asset Type: "))
        title.add(select)
        # The refresh button is necessary for getting the right config for search type
        title.add(IconRefreshWdg())

        my.search_type = select.get_value()

        return title



    def _get_current_view_wdg(my):

        div = DivWdg(HtmlElement.br())

        my.view_list = [ x.get_value("view") for x in my.configs]
        try:
            my.view_list.remove('definition')
        except ValueError:
            pass
        view_current = SelectWdg(SObjectAddAttrCmd.ADD_TO_VIEW)
        view_current.set_option("values", "|".join(my.view_list))
        
        view_current.set_persistence()
        
        div.add("View: ")
        div.add(view_current)

        add_attr_button = SubmitWdg(SObjectAddAttrCmd.ADD_ELEM_TO_VIEW)
        div.add( add_attr_button )

        # set the current view
        current_view = view_current.get_value()
        if current_view == "":
            current_view = "definition"

        my.current_config = None
        for config in my.configs:
            if config.get_value("view") == current_view:
                my.current_config = config
        if my.current_config == None:
            my.current_config = my.configs[0]

        return div



    def _get_list_attr_wdg(my,view):

        # attrs are only added to the default view
        widget_config = WidgetDbConfigCache(my.search_type,view)
        
        attr_div = DivWdg(HiddenWdg("%s_Elts" % view))
        
        # display all of the templates
        title_div = DivWdg(css='cell_header')
        title_div.set_style("width: 80em")
        attr_div.add(title_div)
        title_div.add(DivWdg("Select", css='sm_cell'))
        title_div.add(DivWdg("Element", css='med_cell'))
        title_div.add(DivWdg("Display", css='med_cell'))
        title_div.add(DivWdg("Options", css='med_cell'))
        title_div.add(DivWdg("Action", css='med_cell'))
        reorder = IconSubmitWdg("Update", IconWdg.REFRESH, long=True) 
        reorder.add_event('onmousedown', \
            "var a=document.getElementsByName('%s');a[0].value='%s'"%(my.REORDER, view))
        title_div.add(DivWdg(reorder, css='sm_cell'))
        title_div.add(DivWdg("&nbsp;", css='sm_cell'))
        attr_div.add(HtmlElement.br(2))
        elem_names = widget_config.get_element_names()
        row_ids = []
        for elem_name in elem_names:

            row_div = DivWdg()
            row_div.set_style("position: absolute; padding-left: 8px")
            attr_div.add(row_div)
            attr_div.add(HtmlElement.br(2))
            row_id = '%s_%s' %(view, elem_name)
            row_ids.append(row_id)  
            row_div.set_id(row_id) 
            row_div.set_attr('view',view)
            row_div.add_style('width','80em')
 
            # add the select checkbox
            checkbox = CheckboxWdg("attr_select")
            checkbox.set_option("value", elem_name)
            sub_div = DivWdg(checkbox, css='sm_cell')
            row_div.add(sub_div)


            # add the attribute name
            row_div.add(DivWdg(elem_name, css='med_cell'))


            # add the handlers
            display = widget_config.get_display_handler(elem_name).strip()
            if not display:
                display = "&nbsp;"
            text = TextWdg('%s_%s_display' %(view, elem_name))
            text.set_value(display)
            row_div.add(DivWdg(text, css='med_cell'))
            
            display_options = widget_config.get_display_options(elem_name)
            if display_options.keys():
                options_list = ['%s %s' %(x,y) for x, y in display_options.items()]
                row_div.add(DivWdg(", ".join(options_list), css='med_cell'))
            else:
                row_div.add(DivWdg("&nbsp;", css='med_cell'))
            action = widget_config.get_action_handler(elem_name)
            if not action:
                action = "&nbsp;"
            text = TextWdg('%s_%s_action' %(view, elem_name))
            text.set_value(action)    
            row_div.add(DivWdg(text, css='med_cell'))



            # add the remove button
            remove_button = IconSubmitWdg("Remove_%s_%s" % (view, elem_name), \
                IconWdg.RETIRE, False)
            remove_button.add_event('onclick', "if (!remove_attr('%s')) return false; document.form.%s.value='%s|%s'"\
                %(view, SObjectAddAttrCmd.REMOVE_ATTR, view, elem_name))
            # can't do this now
            #remove_button.set_attr("onsubmit","javascript:return remove_attr()")
            row_div.add(DivWdg(remove_button, css='sm_cell'))

       


        if row_ids:
            my.row_ids.extend(row_ids)
        
            order_script = HtmlElement.script("var %s_Elts = [%s] "\
                % (view, ', '.join(["dd.elements['%s']"%id for id in row_ids])))
            my.script_div.add(order_script)
        return attr_div




    def _get_create_attr_wdg(my):

        types = ["Name/Code", "Number", "Date", "Text", "Upload"]

        attr_div = DivWdg()


        # custom attributes
        name_input = TextWdg("attr_name")
        type_input = SelectWdg("attr_type")
        type_input.add_empty_option()
        type_input.set_option("labels", "|".join(types) )
        type_input.set_option("values", "|".join(types) )

        submit_input = SubmitWdg(SObjectAddAttrCmd.ADD_ATTR)
        
        predefined_attrs = ["timestamp","discussion","images","snapshot",
                            "update", "Custom. . ."]
        predefined_input = SelectWdg("predefined_attr")
        predefined_input.add_empty_option()
        predefined_input.set_option("values", "|".join(predefined_attrs) )
        predefined_input.set_option("labels", "|".join(predefined_attrs) )
        predefined_input.add_event('onchange', "my_select_elements(this,'attr_name','attr_type')")  
        predefined_span = SpanWdg("Predefined Element: ", css='med')
        predefined_span.add(predefined_input)
        attr_div.add(predefined_span)
        
        custom_span = SpanWdg("Name: ", css='med')
        custom_span.add_style('display: None')
        custom_span.set_id('custom_element_span')
        custom_span.add(name_input)

        type_span = SpanWdg("Type: ", css='med')
        custom_span.add(type_span)
        type_span.add(type_input)
        attr_div.add(custom_span)
        attr_div.add(submit_input)
        attr_div.add(HiddenWdg(SObjectAddAttrCmd.REMOVE_ATTR))


        return attr_div





class SObjectAddAttrCmd(Command):
    ADD_ATTR = "Add_Element"
    REMOVE_ATTR = "Remove_Element"
    CREATE_VIEW = "Create_View"
    REMOVE_VIEW = "Remove_View"
    ADD_ELEM_TO_VIEW = "Add Element(s) To View"
    ADD_TO_VIEW ="Add_to_View"
    CURRENT_VIEW = "Current_View"
    
    def get_title(my):
        return "Alter Attribute"

    def check(my):
        return True

    def execute(my):
        web = WebContainer.get_web()

        my.search_type = web.get_form_value("search_type_current")
        if my.search_type == "":
            raise CommandExitException()

        # depending on what was submitted, perform the appropriate action
        if web.get_form_value(my.ADD_ATTR) != "":
            my.view = "definition"
            attr_name = web.get_form_value("attr_name")
            attr_type = web.get_form_value("attr_type")

            pat = re.compile(r".*(!|\+|-|\*|/|\s)+.*")
            m = pat.search(attr_name)
            
            if m:
                raise UserException("[%s] is not allowed in the name of a process." %m.group(1))
                
            my._create_db_column(attr_name, attr_type)
            my._add_node(attr_name)


        elif web.get_form_value(my.REMOVE_ATTR) != "":
            my._remove_attr()


        my.view = web.get_form_value(my.ADD_TO_VIEW)
        #if my.view == "":
        #    return


        if web.get_form_value(my.ADD_ELEM_TO_VIEW):
            attr_selects = web.get_form_values("attr_select")
            my._add_nodes(attr_selects)

        elif web.get_form_value(my.CREATE_VIEW) != "":
            view_name = web.get_form_value("view_name").strip()
            pat = re.compile(r".*(!|\+|-|\*|/|\s)+.*")
            m = pat.search(view_name)
            if m:
                raise UserException("[%s] is not allowed in the name of a view." %m.group(1))
            if view_name:
                my._add_view(view_name)
        elif web.get_form_value(my.REMOVE_VIEW) != "":
            my._remove_view()

        # reorder and update
        else:
            my._switch_elems()
            my._update_elems()




    def _add_view(my, view_name):

        xml = "<config>\n  <%s/>\n</config>" % view_name
        WidgetDbConfig.create(my.search_type, view_name, xml)
        return



    def _add_nodes(my,attr_selects):
        for attr in attr_selects:
            print "Adding node: ", attr, "to", my.view
            my._add_node(attr)




    def _add_node(my, attr_name):

        if attr_name == "":
            raise CommandExitException("attr_name is empty")

        config = WidgetDbConfig.get_by_search_type(my.search_type, my.view)
        if not config:
            config = WidgetDbConfig.create(my.search_type, my.view, None)

        xml = config.get_xml_value("config")

        # find the node that has this attr_name
        node = xml.get_node("config/%s/element[@name='%s']" % \
            (my.view, attr_name) )

        # if it doesn't exist, then add it
        if node != None:
            raise CommandExitException()

        # create a new element for the table
        table = xml.get_node("config/%s" % my.view )

        element = xml.create_element("element")
        Xml.set_attribute(element,"name", attr_name)

        #table.appendChild(element)
        xml.append_child(table, element)
            


        # commit the changes
        config.set_value("config", xml.get_xml())
        config.set_value("view", my.view)
        config.set_value('timestamp', Sql.get_timestamp_now(), quoted=False)
        config.commit()




    def _create_db_column(my, attr_name, attr_type):

        type = None
        if attr_type == "Number":
            type = "int4"
        elif attr_type == "Name/Code":
            type = "varchar(256)"
        elif attr_type == "Date":
            type = "timestamp"
        elif attr_type == "Category":
            type = "varchar(256)"
        elif attr_type == "Text":
            type = "text"
        else:
            type = ""

        # if there is no type, then no column is created for widget_config
        if type != "":
            # alter the table
            search_type_obj = SearchType.get(my.search_type)
            database = search_type_obj.get_database()
            table = search_type_obj.get_table()
            sql = DbContainer.get(database)
            columns = sql.get_columns(table)
            # if the column exists already, skips
            if attr_name in columns:
                return
            
            from pyasm.search.sql import Sql
            if Sql.get_database_type() == 'SQLServer':
                statement = 'ALTER TABLE [%s] ADD "%s" %s' % \
                    (table, attr_name, type)
            else:
                statement = "ALTER TABLE %s ADD COLUMN %s %s" % \
                    (table, attr_name, type)

            sql.do_update(statement)
            AlterTableUndo.log_add(database,table,attr_name,type)


        my.add_description("Added attribute '%s' of type '%s'" % (attr_name, attr_type) )


    def _remove_view(my):
        web = WebContainer.get_web()
        view = web.get_form_value(my.CURRENT_VIEW)
        if view:
            config = WidgetDbConfig.get_by_search_type(my.search_type, view)
            if config:
                config.delete()
                my.description = 'Deleted view [%s]' % view


    def _remove_attr(my):

        web = WebContainer.get_web()

        view_attrs = web.get_form_values(my.REMOVE_ATTR)
        if not view_attrs:
            raise CommandExitException("No attrs selected to remove")

        

        for view_attr in view_attrs:
            view, attr_name = view_attr.split('|')
            config = WidgetDbConfig.get_by_search_type(my.search_type, view)
            xml = config.get_xml_value("config")
            
            # find the node that has this attr_name
            node = xml.get_node("config/%s/element[@name='%s']" % (view, attr_name))
            if node != None:
                # remove element
                table = xml.get_node("config/%s" %view )
                table.removeChild(node)

            # find the node that has this attr_name
            '''
            node = xml.get_node("config/edit/element[@name='%s']" % attr_name)
            if node != None:
                # remove element
                table = xml.get_node("config/edit")
                table.removeChild(node)
            '''
            
            # alter the table
            search_type_obj = SearchType.get(my.search_type)
            database = search_type_obj.get_database()
            table = search_type_obj.get_table()
            sql = DbContainer.get(database)

            if view == 'definition':
                columns = sql.get_columns(table)
                # if the column exists, drop it
                if attr_name in columns:

                    from pyasm.search.sql import Sql
                    if Sql.get_database_type() == 'SQLServer':
                        statement = 'ALTER TABLE [%s] DROP "%s" %s' % \
                            (table, attr_name)
                    else:
                        statement = "ALTER TABLE %s DROP COLUMN %s" % \
                            (table, attr_name)

                    AlterTableUndo.log_drop(database, table, attr_name)
                    sql.do_update(statement)
                



        config.set_value("config", xml.get_xml() )
        config.set_value('timestamp', Sql.get_timestamp_now(), quoted=False)
        config.commit()


    def _update_elems(my):
        ''' look for params named "<view>_<elem_name>_display" '''
        web = WebContainer.get_web()
        view = web.get_form_value(SObjectEditorWdg.REORDER)

        keys = web.get_form_keys()
        display_map = {}
        action_map = {}
        disp_pat = '(%s_)(.*)(_display$)'% view
        action_pat = '(%s_)(.*)(_action$)'% view
        disp_p = re.compile(disp_pat)  
        action_p = re.compile(action_pat)
        for key in keys:
            disp_m = disp_p.match(key)
            value = web.get_form_value(key).strip()
            if disp_m:
                display_map[disp_m.group(2)] = value 
                continue
            action_m = action_p.match(key)
            value = web.get_form_value(key).strip()
            if action_m:
                action_map[action_m.group(2)] = value     
            

        config = WidgetDbConfig.get_by_search_type(my.search_type, view)
        if not config:
            return
        xml = config.get_xml_value("config")

        my.__process_nodes(xml, view, 'display', display_map)
        my.__process_nodes(xml, view, 'action', action_map)
        

        config.set_value("config", xml.get_xml() )
        config.set_value("timestamp", Sql.get_timestamp_now(), quoted=False )
        config.commit()

        my.add_description("Update elements in '%s'" % (view) )

    def __process_nodes(my, xml, view, node_type, value_map):
        '''updates the info on a group of nodes or remove it'''
        nodes = xml.get_nodes("config/%s/element" % view)
        for node in nodes:
            elem_name = Xml.get_attribute(node, "name")
            try:
                
                target_node = xml.get_node("config/%s/element[@name='%s']/%s" \
                    %(view, elem_name, node_type))
                if not target_node:
                    target_node = xml.create_element(node_type)
                    #node.appendChild(target_node)
                    xml.append_child(node, target_node)
                   
                Xml.set_attribute(target_node, "class",  value_map[elem_name]) 
                if not value_map[elem_name]:
                    node.removeChild(target_node)
                    
            except KeyError:
                continue
       

    def _switch_elems(my):
        ''' look for params named "<view>_Elts" '''
        web = WebContainer.get_web()

        keys = web.get_form_keys()
        attr_name = ""
        view = web.get_form_value(SObjectEditorWdg.REORDER)

        for key in keys:
            if key == ("%s_Elts" %view) and web.get_form_value(key).strip():
                attr_name = web.get_form_value(key)
                
        
        pat = '(%s_)(.*)'% view
        p = re.compile(pat)
                  
        elem_ids = attr_name.split(",")
        attr_names = []
        for elem_id in elem_ids:
            m = p.match(elem_id)
            if not m:
                return CommandExitException("matching failed")
            attr_names.append(elem_id.replace(m.group(1), ""))

        if not attr_names:
            return CommandExitException("No attrs selected to reorder")

        config = WidgetDbConfig.get_by_search_type(my.search_type, view)
        if not config:
            return
        xml = config.get_xml_value("config")


        # reorder the nodes
        nodes = xml.get_nodes("config/%s/element" % view)
        attr_names.reverse()
        
        for attr_name in attr_names:
            for node in nodes:
                if Xml.get_attribute(node, "name") == attr_name:
                    parent = node.parentNode
                    node.parentNode.insertBefore(node, parent.firstChild)
                    break

        config.set_value("config", xml.get_xml() )
        config.set_value("timestamp", Sql.get_timestamp_now(), quoted=False )
        config.commit()

        my.add_description("Order switch for attributes in '%s'" % (view) )
          











