// ------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// ------------------------------------------------------------------------------------------------------


spt.dg_table_action = {};


spt.dg_table_action.get_popup_wdg = function( evt, bvr )
{
    var popup = $("popup");

    var args = bvr.args;
    if (typeof(args) == "undefined") {
        args = {};
    }

    var server = TacticServerStub.get();
    values = {}
    if (bvr.values)
    {
        for (i in bvr.values)
            values[i] = eval(bvr.values[i]);
    }
    var kwargs = {'args': args, 'values': values};
    var widget_html = server.get_widget(bvr.class_name, kwargs);

    // replace the popup html
    spt.behavior.replace_inner_html( popup, widget_html );
    spt.popup.open( bvr.args.popup_id );
    return popup;
}


spt.dg_table_action.set_actionbar_aux_content = function( evt, bvr )
{
    //var aux_div = $("ActionBar_Aux");
    //var aux_content = $("ActionBar_Aux_Content");
    //var aux_title = $("ActionBar_Aux_Title");
    //
    var table_id = bvr.args['table_id'];
    var table = $(table_id);
    var table_top = table.getParent(".spt_table_top")

    var aux_div = table_top.getElement(".spt_table_aux")
    var aux_title = table_top.getElement(".spt_table_aux_title")
    var aux_content = table_top.getElement(".spt_table_aux_content")
    
    arg_dict = {};
    for ( i in bvr.args )
    {
        // insert some table related args into the dict
        if (i=='table_id')
        {
            var table_id = bvr.args['table_id'];
            var table = $(table_id);
            if (table)
            {
                var view = table.getProperty("spt_view");
                var search_type = table.getProperty("spt_search_type");
                arg_dict['search_type'] = search_type;
                arg_dict['view'] = view;
                arg_dict['selected_search_keys'] = spt.dg_table.get_selected_search_keys(table_id).join(',');
            }
        }
        arg_dict[i] = bvr.args[i];
    }
 
    spt.panel.load(aux_content, bvr.class_name, arg_dict, [], true);
    arg_dict['is_aux_title'] ='true';
    spt.panel.load(aux_title, bvr.class_name, arg_dict, [], false);
    aux_div.setStyle("display", "block");
    aux_div.setStyle("visibility", "visible");
    
    
    spt.ctx_menu.clear();
}


spt.dg_table_action.get_popup_wdg2 = function( evt, bvr )
{
    // get the common popup, clone it and fill it in
    var container = $("popup_container");
    var popup = $("popup_template");
    var clone = spt.behavior.clone(popup);

    clone.setAttribute("id", "whatever");
    container.appendChild(clone);


    // get the title
    var title = bvr.title;
    var width = bvr.width;
    var height = bvr.height;
    var class_name = bvr.class_name;

    // use a dst el to put this under
    var dst_el = bvr.dst_el;


    var server = TacticServerStub.get();
    var kwargs = {'args': bvr.args};
    var widget_html = server.get_widget(bvr.class_name, kwargs);

    // get the content container
    var content_wdg = clone.getElement(".spt_popup_content");
    var width_wdg = clone.getElement(".spt_popup_width");
    if (width != null) {
        width_wdg.setStyle("width", width);
    }
    if (height != null) {
        width_wdg.setStyle("height", height);
    }

    // replace the title
    if (title != null) {
        var title_wdg = clone.getElement(".spt_popup_title");
        spt.behavior.replace_inner_html( title_wdg, title );
    }
 
    // replace the popup html
    spt.behavior.replace_inner_html( content_wdg, widget_html );

    // display the clone
    clone.setStyle("display", '');
}



spt.dg_table_action.csv_export = function( evt, bvr )
{

    var project = spt.Environment.get().get_project();
    var site = spt.Environment.get().get_site();
    var my_search_type = bvr.search_type;
    var my_is_export_all = bvr.is_export_all;
    var filename = my_search_type.replace(/[\/\?\=]/g,"_") + "_" + bvr.view + ".csv";
    var class_name = "pyasm.widget.CsvDownloadWdg";
    var column_name_vals = spt.api.Utility.get_input_values('csv_export_table', 'input[name=' + bvr.column_names+']');
    var selected_search_keys = '';
    if (my_is_export_all != 'true')
        selected_search_keys = bvr.search_keys;
    
    var column_names = column_name_vals[bvr.column_names];
    var no_column_name = true;
    
    for (var k=0;  k<column_names.length; k++){
        if(column_names[k] != '') {
            no_column_name = false;
            break;
        }
    }
    var my_include_id = spt.api.Utility.get_input('csv_export_action', 
        'include_id').checked;
     
    if ( no_column_name && !my_include_id) {
        alert('Please select at least 1 column or just the "Include ID" checkbox')
        return;
    }
   
    
    var options = {
        search_type: my_search_type,
        view: bvr.view,
        filename: filename,
        column_names: column_names,
        search_keys: selected_search_keys,
        include_id: my_include_id 
    };
    var popup = bvr.src_el.getParent('.spt_popup');
    // this is assgined in spt.dg_table.gear_smenu_export_cbk 
    var values = popup.values_dict;
    
    var server = TacticServerStub.get();
   
   
    var kwargs = {'args': options, 'values': values};
    var rtn_file_name = '';
    try {
        rtn_file_name = server.get_widget(class_name, kwargs);
    } catch(e) {
        spt.error(spt.exception.handler(e));
        return;
    }
    if (rtn_file_name.length > 200 ) {
        spt.alert("Error exporting one of the widgets:\n" + rtn_file_name, {type: 'html'} );
        return;
    }
        
    var csv_file_name = encodeURIComponent(rtn_file_name);
    var param_dict = {};
    class_name = "pyasm.widget.CsvGenerator";
    param_dict['dynamic_file'] = "true";
    param_dict['widget'] = class_name;
    param_dict['filepath'] = csv_file_name;
    var url = spt.Environment.get_widget_server_url(project, param_dict);

    if (site != "default")
    {
        url = url.split('/')
        url.splice(4, 0, site);
        url = url.join('/');
    }
    
    document.location = url;

}






// This is a convenience method which sets the row to be commitable
//
spt.dg_table_action.set_commitable = function(top_el, value_wdg) {
    // Utilize edit cell keyboard handler call-back mechanism to do all the modified field goodness
    // (e.g. turning row green) ... TODO: refactor this mechanism to pull out common functionality
    // from being so entwined with keyboard input cell edit handling ...
    spt.dg_table.edit.widget = top_el;
    spt.dg_table.inline_edit_cell_cbk( value_wdg );
}





//
// Called when edit button on editing definition of a column in a table
//
spt.dg_table_action.edit_definition_cbk = function(evt, bvr) {
    //var popup = $('EditColumnDefinitionWdg_panel');
    var panel= bvr.src_el.getParent('.spt_panel');
    var popup =  bvr.src_el.getParent('.spt_popup');
    panel.setAttribute("spt_refresh", "true");
    var values = spt.api.Utility.get_input_values(panel);
    if (!values.save_view[0] ) {
        alert('Please select if you want to save for definition or current view.')
        return;
    }

    //var server = TacticServerStub.get();
    //server.add_config_element(search_type, section_id, name, class_name, options);

    var args={};
    args['search_type']=panel.getAttribute("spt_search_type");
    args['view']=panel.getAttribute("spt_view");
    args['element_name']=panel.getAttribute("spt_element_name");
    args['refresh']=panel.getAttribute("spt_refresh");

    //Refreshing widget and display err if any
    try {
        server = TacticServerStub.get();
        server.execute_cmd('tactic.ui.panel.EditColumnDefinitionCbk', args, values)
        //spt.panel.refresh(panel, values, true);
        // it's set in the cbjs_action earlier 
        var activator = popup.activator;
        var bvr2 = {};
        bvr2.src_el = activator;
        spt.dg_table.search_cbk(evt, bvr2);

        //hide popup afterwards as the activator is gone with the table refresh
        spt.popup.close(popup);
    }
    catch (e) {
        var error_str = spt.exception.handler(e);
        alert(error_str);
    }
    
}



// Drop functionality
// NOTE: this is still used in vesion 2 (fast table)
spt.dg_table_action.sobject_drop_setup = function( evt, bvr )
{
    var ghost_el = $("drag_ghost_copy");
    ghost_el.setStyle("width","auto");
    ghost_el.setStyle("height","auto");
    ghost_el.setStyle("text-align","left");

    // Assumes that source items being dragged are from a DG table ...
    //var src_el = bvr.src_el; 
    var src_el = spt.behavior.get_bvr_src( bvr );
    if (spt.drop) {
        spt.drop.src_el = src_el;
    }

    var src_table_top = src_el.getParent(".spt_table_top");
    var src_table = src_table_top.getElement(".spt_table");
    var src_search_keys = spt.dg_table.get_selected_search_keys(src_table);


    if (src_search_keys.length == 0) {
        // if items aren't selected in the table then just get the specific row that was dragged ...
        var row = src_el.getParent(".spt_table_row");
        var src_search_key = row.getAttribute("spt_search_key");
        if (src_search_key != null) {
            src_search_keys = [src_search_key];
        }
        else {
            var tbody = src_el.getParent(".spt_table_tbody");
            src_search_keys = [ tbody.get("id").split("|")[1] ];
        }
    }

    var inner_html = [ "<i><b>--- Drop Package Contents ---</b></i><br/><pre>" ];
    for( var c=0; c < src_search_keys.length; c++ ) {
        var search_key = src_search_keys[c];
        if( search_key.indexOf("-1") != -1 ) {
            continue;
        }
        inner_html.push( "    " + search_key.strip() );
        if( c + 1 < src_search_keys.length ) {
            inner_html.push( "\n" );
        }
    }
    inner_html.push("</pre>");

    ghost_el.innerHTML = inner_html.join("");
}


// Called when selected search_types are dropped onto a drop zone
//
spt.dg_table_action.sobject_drop_action = function( evt, bvr )
{
    var src_el = bvr._drop_source_bvr.src_el; 
    var drop_el = bvr.src_el;

    // get the current value
    var tds = [];
    // FIXME: this assumes a table (not a good assumption)
    var td = drop_el.getParent(".spt_table_td");
    var col_idx = td.getAttribute('col_idx');
    var dst_table = drop_el.getParent(".spt_table");
    var dst_rows = spt.dg_table.get_selected(dst_table);
    
    if (dst_rows.length == 0) {
        tds.push(td);
    }
    for (var i=0; i< dst_rows.length; i++){
        var row = dst_rows[i];
        tds.push(row.getElement('td[col_idx=' + col_idx + ']'));
    }

    //var value = td.getAttribute("spt_input_value");

    var src_table = src_el.getParent(".spt_table");
    var src_tbodies = spt.dg_table.get_selected_tbodies(src_table);


    var src_search_keys = [];
    var src_display_values = [];
    var tbody = null;
    if (src_tbodies.length == 0) {
        tbody = src_el.getParent(".spt_table_tbody");
        src_search_keys.push( tbody.getAttribute("spt_search_key") );
        src_display_values.push( tbody.getAttribute("spt_display_value") );
    }
    else {
        for (var i=0; i<src_tbodies.length; i++) {
            tbody = src_tbodies[i];
            src_search_keys.push(tbody.getAttribute("spt_search_key"));
            src_display_values.push(tbody.getAttribute("spt_display_value"));
        }
    }



    var accepted_search_type = bvr.accepted_search_type;
    var search_type = tbody.getAttribute("spt_search_type");
    if (typeof(accepted_search_type) != 'undefined' && accepted_search_type != '' && accepted_search_type != search_type) {
        spt.alert('Only search types ['+accepted_search_type+'] are accepted');
        return;
    }


    for (var i=0; i< tds.length; i++){
        spt.dg_table_action.clone_src_to_droppable(tds[i], src_search_keys, src_display_values);
    }

}


// function to clone src contents to a droppable td
//td - droppable cell
spt.dg_table_action.clone_src_to_droppable = function(td, src_search_keys, src_display_values)
{
    var top_el = td.getElement(".spt_drop_element_top");
    var template = td.getElement(".spt_drop_template");
    var content = td.getElement(".spt_drop_content");


    // get the value
    var value_wdg = top_el.getElement(".spt_drop_element_value");
    
    // get the values
    var items = content.getElements(".spt_drop_item");
    var value = [];
    for (var i=0; i<items.length; i++) {
        var search_key = items[i].getAttribute("spt_search_key");
        value.push(search_key);
    }

    for (var i=0; i<src_search_keys.length; i++) {
        var src_search_key = src_search_keys[i];
        var src_display_value = src_display_values[i];

        var clone = spt.behavior.clone(template);
        var item = clone.getElement(".spt_drop_display_value");
        item.innerHTML = src_display_value;
        clone.setAttribute("spt_search_key", src_search_key);

        content.appendChild(clone);

        value.push(src_search_key);
    }

    value = JSON.stringify(value);
    value_wdg.value = value;
    // Utilize edit cell keyboard handler call-back mechanism to do all the modified field goodness
    // (e.g. turning row green) ... TODO: refactor this mechanism to pull out common functionality
    // from being so entwined with keyboard input cell edit handling ...
    spt.dg_table.edit.widget = top_el;
    var key_code = spt.kbd.special_keys_map.ENTER;
    spt.dg_table.edit_cell_cbk( value_wdg, key_code );
}


spt.dg_table_action.sobject_drop_remove = function( evt, bvr ) {
    var src_el = bvr.src_el;

    src_el.setStyle("border", "solid 1px red");
    Effects.fade_out(src_el, 500);

    var top_el = src_el.getParent(".spt_drop_element_top");
    var value_wdg = top_el.getElement(".spt_drop_element_value");
    var content = top_el.getElement(".spt_drop_content");

    src_el.destroy();

    // get the values
    var items = content.getElements(".spt_drop_item");
    var value = [];
    for (var i=0; i<items.length; i++) {
        var search_key = items[i].getAttribute("spt_search_key");
        value.push(search_key);
    }
    value = JSON.stringify(value);
    value_wdg.value = value;


    // set the row as being edited
    spt.dg_table.edit.widget = top_el;
    var key_code = spt.kbd.special_keys_map.ENTER;
    spt.dg_table.edit_cell_cbk( value_wdg, key_code );

 
}







