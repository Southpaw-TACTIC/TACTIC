// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//
// -------------------------------------------------------------------------------------------------------------------


// Command is DEPRECATED: the command class is only used here
// keep around because this may be used for reference if we put
// a real command system in the interface

Command = new Class({

    initialize: function(){
        return;
    },
    execute: function() {
        spt.js_log.debug("execute");
    },

    get_description: function() { return ''; },

    undo: function() {
        spt.js_log.debug("undo");
    },

    redo: function() {
        spt.js_log.debug("redo");
    }
});


// store a list of commands that have been executed
Command.commands = [];
Command.command_index = -1;
Command.execute_cmd = function(cmd) {
    cmd.execute();

    try {
        var description = cmd.get_description();
        spt.js_log.debug( "CMD: " + description);
    } catch(e) {
        spt.js_log.debug( "No description" );
    }
    // FIXME: do not add to undo just yet
    //this.add_to_undo(cmd);
}


Command.add_to_undo = function(cmd) {

    // remove old commands
    for (var i=Command.commands.length;i>Command.command_index+1;i--) {
        Command.commands.pop();
    }

    Command.commands.push(cmd);
    Command.command_index += 1;
}


Command.undo_last = function() {
    if (Command.command_index == -1) {
        alert("Nothing to undo");
        return;
    }

    var cmd = Command.commands[Command.command_index];
    cmd.undo();
    Command.command_index -= 1;
    return cmd

}


Command.redo_last = function() {

    if (Command.command_index == Command.commands.length-1) {
        alert("Nothing to redo");
        return;
    }

    var cmd = Command.commands[Command.command_index+1];
    cmd.redo();
    Command.command_index += 1;
    return cmd

}



Command.undo_all = function() {
    for (var i = Command.commands.length-1; i >= 0; i--) {
        var cmd = Command.commands[i];
        cmd.undo();
    }
}


Command.test = function() {
    for (var i=0; i < 5; i++) {
        var cmd = new Command();
        Command.execute_cmd(cmd);
    }

    // undo all of the commands
    Command.undo_all()

}



spt.DgTable = function(table_id) {
    this.table_id = table_id;

}

spt.DgTable.instances = {};
spt.DgTable.get = function(table_id) {
    var dg_table = spt.DgTable.instances[table_id];
    if (dg_table) {
        return dg_table;
    }

    dg_table = new spt.DgTable(table_id);
    spt.DgTable.instances[table_id] = dg_table;
    return dg_table;
}



// Data-Grid Table functionality ...
spt.dg_table = {};
spt.dg_table.HEADER_ROW = 0;
spt.dg_table.INSERT_ROW = 1;
spt.dg_table.EDIT_ROW = 2;
spt.dg_table.FIRST_ROW = 3;



spt.dg_table.get_all_column_element_tds = function( table, spt_element_name )
{
    var table = document.id(table);
    var tbodies = spt.ctags.find_elements( table, "spt_table_tbody", "spt_table" );

    var col_el_td_list = [];

    if( tbodies.length ) {

        var td_list = spt.ctags.find_elements( tbodies[0], "spt_table_td", "spt_table" );
        var td_idx = -1;
        for( var c=0; c < td_list.length; c ++ ) {
            var td = document.id(td_list[c]);
            if( td.getProperty("spt_element_name") == spt_element_name ) {
                td_idx = c;
                break;
            }
        }

        if( td_idx > -1 ) {
            // need to skip insert and edit rows (idx 0 and 1)
            for( var t=2; t < tbodies.length; t++ ) {
                td_list = spt.ctags.find_elements( tbodies[t], "spt_table_td", "spt_table" );
                col_el_td_list.push( td_list[ td_idx ] );
            }
        }
    }

    return col_el_td_list;
}


//
// Key function for gathering only the row select TDs for the given table (it DOES NOT gather the row select
// TDs of any embedded/child tables)
//
spt.dg_table.gather_row_select_tds = function( el, row_select_tds, kwargs )
{

    // check for option to get all selected row-select-tds, even embedded ones ...
    if( kwargs && spt.is_TRUE( kwargs.include_embedded_tables ) ) {
        var tmp_list = document.id(el).getElements(".SPT_ROW_SELECT_TD");
        for( var c=0; c < tmp_list.length; c++ ) {
            if (tmp_list[c].hasClass("SPT_ROW_NO_SELECT"))
                continue
            row_select_tds.push( tmp_list[c] );
        }
        return;
    }

    var unique_id = ".SPT_ROW_SELECT_TD_" + el.getAttribute("unique_id");
    var tmp_list = document.id(el).getElements(unique_id);
    for( var c=0; c < tmp_list.length; c++ ) {
        if (tmp_list[c].hasClass("SPT_ROW_NO_SELECT"))
            continue

        row_select_tds.push( tmp_list[c] );
    }

    return

}


//
// Get the selected rows of this table.
//
spt.dg_table.get_selected = function( table_id, kwargs )
{
    var table = document.id(table_id);
    if (! table)
        return [];

    var td_el_list = [];
    spt.dg_table.gather_row_select_tds( table, td_el_list, kwargs );

    var selected_tr = [];

    // go through each row and determine if it selected or not
    if( td_el_list ) {
        for( var c=0; c < td_el_list.length; c++ ) {
            var td_el = td_el_list[c];
            var tr_el = td_el.getParent("tr");
            if( td_el.selected == 'yes' ) {
                selected_tr.push(tr_el);
            }
        }
    }

    return selected_tr;
}


spt.dg_table.get_selected_tbodies = function( table_id, kwargs )
{
    var table = document.id(table_id);
    if (! table)
        return [];

    var row_select_tds = [];
    spt.dg_table.gather_row_select_tds( table, row_select_tds, kwargs );

    var selected_tbodies = [];
    for( var c=0; c < row_select_tds.length; c++ ) {
        var td_el = row_select_tds[c];
        var tbody_el = td_el.getParent(".spt_table_tbody");
        if( td_el.selected == 'yes' ) {
            selected_tbodies.push(tbody_el);
        }
    }

    return selected_tbodies;
}



spt.dg_table.get_all_tbodies = function( table_id, kwargs )
{
    var table = document.id(table_id);
    if (! table)
        return [];

    var row_select_tds = [];
    spt.dg_table.gather_row_select_tds( table, row_select_tds, kwargs );

    var tbodies = [];
    for( var c=0; c < row_select_tds.length; c++ ) {
        var td_el = row_select_tds[c];
        var tbody_el = td_el.getParent(".spt_table_tbody");
        tbodies.push(tbody_el);
    }

    return tbodies;
}





//
// Gets all of the selected search keys in a table
//
// pass in kwargs of {'include_embedded_tables': true} if you want to get all
// search keys of items selected in current table and all embedded tables
//
spt.dg_table.get_selected_search_keys = function( table_id, kwargs )
{
    var selected_rows = spt.dg_table.get_selected(table_id,kwargs);
    var search_keys = [];

    for (var c=0; c < selected_rows.length; c++) {
        search_key = selected_rows[c].getAttribute("spt_search_key");
        search_keys.push(search_key);
    }
    return search_keys;
}


// Get all of the element_names as a list
spt.dg_table.get_element_names = function(table_id) {
    var table = document.id(table_id);


    // Return nothing is table.rows can't be found.  This is for tile
    // view which is not really configurable.
    if (typeof(table.rows) == 'undefined') {
        return [];
    }

    var header_row = table.rows[spt.dg_table.HEADER_ROW];
    var elements = document.id(header_row).getChildren();
    var element_names = [];

    for (var i=0; i<elements.length; i++) {
        var element = elements[i];
        var element_name = element.getAttribute("spt_element_name");
        if (element_name == null || element_name=="None") {
            continue;
        }

        // check if this is a generated element
        var generator = element.getAttribute("spt_generator_element");
        if (generator != null) {
            if (!( generator in element_names)) {
                element_names.push(generator);
            }
            continue;
        }
        element_names.push(element_name);
    }

    return element_names

}



// Get input value of a named element
spt.dg_table.get_element_value = function(src_element, element_name) {
    var table = src_element.getParent(".spt_table");
    var element_names = spt.dg_table.get_element_names(table);

    // get the index of the element_name
    var index = -1;
    for (var i=0; i<element_names.length; i++) {
        if (element_name == element_names[i]) {
            index = i;
            break;
        }
    }

    if (index == -1) {
        spt.alert("Element ["+element_name+"] not in table");
        return 'default';
    }

    // get the tds
    var tbody = src_element.getParent(".spt_table_tbody");
    var tds = tbody.getElements(".spt_table_td");
    var td = tds[index+1];

    var value = td.getAttribute("spt_input_value");
    return value;
}



// Get the cell of a named element
spt.dg_table.get_element_cell = function(src_element, element_name) {
    var tbody = src_element.getParent(".spt_table_tbody");
    var tds = tbody.getElements(".spt_table_td");
    for (var i=0; i<tds.length; i++) {
        var td_element_name = tds[i].getAttribute("spt_element_name");
        if (td_element_name == element_name) {
            return tds[i]
        }

    }

    spt.alert("Element ["+element_name+"] not in table");
    return null;
}



spt.dg_table.get_bottom_cell = function(src_element, element_name) {
    var tbody = src_element.getParent(".spt_table").getElement(".spt_table_bottom");
    var tds = tbody.getElements(".spt_table_td");
    for (var i=0; i<tds.length; i++) {
        var td_element_name = tds[i].getAttribute("spt_element_name");
        if (td_element_name == element_name) {
            return tds[i]
        }

    }
    spt.alert("Element ["+element_name+"] not in table");
    return null;
}



// get all of the column cells for a given element
//
spt.dg_table.get_element_cells = function(table_id, element_name) {

    var table = document.id(table_id);

    var found = false;
    var element_names = spt.dg_table.get_element_names(table);
    for (var i=0; i < element_names.length; i++) {
        if (element_name == element_names[i]) {
            found = true;
            break;
        }
    }
    if (!found) {
        spt.alert( "Element ["+element_name+"] not found" );
        return;
    }


    // there is one extra element_name
    var index = i + 1;

    var col_tds = [];
    var tbodies = table.getElements(".spt_table_tbody");
    for (var j=0; j<tbodies.length; j++) {
        var tds = tbodies[j].getElements(".spt_table_td");
        col_tds.push( tds[index] );
    }

    return col_tds;
}




// Add a new item to the top of the table
//
//
spt.dg_table.add_item_cbk = function(evt, bvr) {
    var element = bvr.src_el;

    var table_top = element.getParent('.spt_table_top');
    if (table_top == null) {
        table_top.getElement(".spt_panel");
    }

    var table = table_top.getElement(".spt_table_content");
    if (table == null) {
        table = table_top.getElement(".spt_table");
    }
    var table_id = table.getAttribute("id")


    // if there are empty rows, then destroy the empty rows
    var empty_row = table.getElement(".spt_empty_tbody");
    if (empty_row != null) {
        empty_row.destroy();
    }


    // clone the hidden
    var insert_tbody = table.getElement('.spt_insert_tbody' );

    var new_tbody;
    if (spt.browser.is_IE()) {
        new_tbody = spt.behavior.duplicate_element(insert_tbody);
    } else {
        new_tbody = spt.behavior.clone(insert_tbody);
    }
    var search_key = new_tbody.getAttribute('spt_search_key');
    new_tbody.setAttribute("id", table_id+"|"+search_key);

    var new_row = document.id(new_tbody).getElement('.spt_insert_row' );

    new_tbody.style.display = '';
    new_row.style.display = '';

    var group = element.getParent(".spt_table_group");
    if (group == null) {
        // by default add it after the edit_tbody
        group = table.getElement('.spt_edit_tbody' );
    }
    new_tbody.inject(group, 'after');

    var select = new_tbody.getElement(".SPT_ROW_NO_SELECT");
    select.removeClass("SPT_ROW_NO_SELECT");

}


//
// Gear Menu -> Selected -> Retire Selected Items ...
//
spt.dg_table.gear_smenu_retire_selected_cbk = function( evt, bvr )
{
    var activator = spt.smenu.get_activator(bvr);
    var layout = activator.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");
    if (version == "2") {
        spt.table.set_layout(layout);
        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table_table' );
        spt.table.retire_selected();
    }
    else {
        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table' );
        spt.dg_table.retire_selected( table );
    }
}


//
// Retires all selected rows in the table
//
// params:
//  table_id: the dom id of the table which contain the selected rows
//
spt.dg_table.retire_selected = function(table)
{
    var selected_rows = spt.dg_table.get_selected(table);

    var num = selected_rows.length;
    if (num == 0) {
        spt.alert("Nothing selected to retire");
        return;
    }

    var show_retired = spt.dg_table.get_show_retired_flag( selected_rows[0] );
    var search_key_info = spt.dg_table.parse_search_key( selected_rows[0].getAttribute("spt_search_key") );

    var title = 'RETIRE Selected Items';
    var msg = 'Retiring ' + num + '  "' + search_key_info.search_type + '" items ...';

    spt.app_busy.show( title, msg );

    var msg = "Are you sure you wish to retire [" + num + "] items?";
    if (! confirm(msg) ) {
        spt.app_busy.hide();
        return;
    }
    setTimeout( function() {
        var aborted = false;
        var server = TacticServerStub.get();
        server.start({title: "Retired ["+num+"] items"});
        try {
            for (var i=0; i < selected_rows.length; i++)
            {
                var search_key = selected_rows[i].getAttribute("spt_search_key");
                var api_key = selected_rows[i].getAttribute("SPT_RET_API_KEY");
                server.set_api_key(api_key);
                server.retire_sobject(search_key);
                server.clear_api_key();
            }
        }
        catch(e) {
            // TODO: do nicer error message for user
            spt.alert("Error: " + spt.exception.handler(e));
            server.abort();
            aborted = true;
            spt.app_busy.hide();
        }

        server.finish()

        if( ! aborted ) {
            for (var i=0; i < selected_rows.length; i++)
            {
                var tbody = selected_rows[i].getParent('.spt_table_tbody');
                var refresh = tbody.getAttribute("refresh");

                var fade = false;
                if( show_retired ) {
                    spt.panel.refresh(tbody, {}, fade);
                } else {
                    if (refresh == 'table') {
                        // do nothing
                        //spt.panel.refresh(document.id(table_id), {}, fade);
                    }
                    else {
                        on_complete = "document.id(id).setStyle('display', 'none')";
                        Effects.fade_out(tbody, 500, on_complete);
                        spt.behavior.destroy_element(tbody);
                    }
                }
            }
        }

        spt.app_busy.hide();
    }, 0 );
}


//
// Gear Menu -> Selected -> Delete Selected Items ...
//
spt.dg_table.gear_smenu_delete_selected_cbk = function( evt, bvr )
{
    var activator = spt.smenu.get_activator(bvr);
    var layout = activator.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");

    if (version == "2") {
        spt.table.set_layout(layout);
        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table_table' );
        // no support for post delete handler
        spt.table.delete_selected();
    } else {

        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table' );
        spt.dg_table.delete_selected( table, { 'table_el': table,
            'bvr': bvr, 'activator_el': activator,
            'post_delete_handler_fn': spt.dg_table._post_delete_handler } );
    }
    // Re-check to see if all changes in the table are now valid (after deleting rows) to see if the commit button needs to be shown (if currently hidden) to allow for saving the changes ...
    //
    var invalid_list = spt.ctags.find_elements( table, "spt_input_validation_failed", "spt_table" )
    if( invalid_list.length ) {
        spt.dg_table._new_toggle_commit_btn( activator, true );   // hide = true (meaning do not display commit btn)
    } else {
        spt.dg_table._new_toggle_commit_btn( activator, false );  // hide = false (meaning display commit btn)
    }

}


//
// Delete selected items from table ...
//
spt.dg_table.delete_selected = function(table, kwargs)
{
    var selected_rows = spt.dg_table.get_selected(table);
    var num = selected_rows.length;
    if (num == 0) {
        spt.alert("Nothing selected to delete");
        return;
    }

    var search_key_info = spt.dg_table.parse_search_key( selected_rows[0].getAttribute("spt_search_key") );
    var title = 'Retire Delete Items:';
    var msg = 'Deleting ' + num + ' "' + search_key_info.search_type + '" items ...';

    var stype_display = search_key_info.search_type.split('/')[1];
    var bits = stype_display.split('_');
    var stype_arr = [];
    for( var b=0; b < bits.length; b++ ) {
        stype_arr.push( bits[b].substring(0,1).toUpperCase() + bits[b].substring(1) );
    }
    stype_display = stype_arr.join(' ');

    var msg = "Are you sure you wish to delete [" + num + "] items?";
    if (! confirm(msg) ) {
        return;
    }

    // delete any rows that are inserts
    var num_inserts = 0;
    for (var i = 0; i<selected_rows.length; i++) {
        var row = selected_rows[i];
        var search_key = row.getAttribute('spt_search_key');

        if (search_key.match('id=-1$') == 'id=-1') {
            var tr = selected_rows[i];
            var tbody = tr.getParent(".spt_table_tbody");
            tbody.destroy();
            num_inserts += 1;
        }
    }
    // if inserts were removed, then we have to relook at the table for what was actually selected
    if (num_inserts > 0) {
        selected_rows = spt.dg_table.get_selected(table);
        var num = selected_rows.length;
        if (num == 0) {
            return;
        }
    }
    var plural_s = '';
    if (parseInt(num, 10) > 1) plural_s = 's';

    var title = 'DELETE Selected Items';
    var msg = 'Deleting ' + num + '  "' + stype_display + '" item' + plural_s + ' ...';
    spt.app_busy.show( title, msg );


    // Set up any defined post delete action variables from kwargs ...
    var table_el = kwargs[ 'table_el' ];
    var activator_el = kwargs[ 'activator_el' ];
    var originating_bvr = kwargs[ 'bvr' ];
    var post_delete_handler_fn = kwargs[ 'post_delete_handler_fn' ];

    // Execute delete operation ...
    setTimeout( function() {
            spt.dg_table._delete_selected( table, kwargs, num, selected_rows, search_key_info );
            if( table_el && activator_el && originating_bvr && post_delete_handler_fn ) {
                post_delete_handler_fn( table_el, originating_bvr, activator_el );
            }
            spt.app_busy.hide();
        }, 0 );
}


spt.dg_table._delete_selected = function( table, kwargs, num, selected_rows, search_key_info )
{
    var deleted_idx_map = {};
    for (var i=0; i < selected_rows.length; i++) {
        deleted_idx_map[ i ] = false;
    }
    var deletes_done = 0;

    var aborted = false;
    var server = TacticServerStub.get();
    server.start({title: "Deleted ["+num+"] items"});
    try {
        for (var i=0; i < selected_rows.length; i++) {

            var search_key = selected_rows[i].getAttribute("spt_search_key");
            var api_key = selected_rows[i].getAttribute("SPT_DEL_API_KEY");
            server.set_api_key(api_key);
            server.delete_sobject(search_key);
            server.clear_api_key();

            /*
            var tr = selected_rows[i];
            var tbody = tr.getParent(".spt_table_tbody");
            on_complete = "document.id(id).setStyle('display', 'none')";
            Effects.fade_out(tbody, 500, on_complete);
            */
        }
    }
    catch(e) {
        var error_str = spt.exception.handler(e);
        spt.alert( '"Delete Selected" aborted due to DELETE error for one of the items being deleted: "' +
                error_str + '"' );
        server.abort();
        aborted = true;
    }

    server.finish();

    if( ! aborted ) {
        for (var i=0; i < selected_rows.length; i++) {
            var tr = selected_rows[i];
            var tbody = tr.getParent(".spt_table_tbody");
            var refresh = tbody.getAttribute("refresh");

            if (refresh == 'table') {
                spt.panel.refresh(document.id(table_id), {}, fade);
            }
            else {
                on_complete = "document.id(id).setStyle('display', 'none')";
                Effects.fade_out(tbody, 300, on_complete);
                spt.behavior.destroy_element(tbody);
            }
        }
    }

    spt.app_busy.hide();
}

spt.dg_table._post_delete_handler = function( table, bvr, activator )
{
    // set up a post delete bvr if there is a delete post action script to run ... this table that deletes
    // are occurring on is going to be refreshed entirely, so the original bvr.src_el will be gone
    // (hence the need to store whatever bvr info we need just before the refresh) ...
    var post_delete_bvr = {};
    if( bvr.cbjs_dg_table_delete_post_action ) {
        post_delete_bvr.cbjs_dg_table_delete_post_action = bvr.cbjs_dg_table_delete_post_action;
        post_delete_bvr.alternate_top = table.getParent( '.spt_content' );
    }

    var table_top = activator.getParent(".spt_table_top");
    var refresh_occurred = null;
    // var refresh_occurred = spt.dg_table.refresh_table_by_refresh_button( table_top );

    if( refresh_occurred ) {
        // if we've actually refreshed the table then we use the post_delete_bvr from above ...
        // it will have needed info set since bvr.src_el is gone due to the refresh
        bvr = post_delete_bvr;
    }

    // Now run any configured "post-action on delete" javascript if its been configured ...
    if( bvr.cbjs_dg_table_delete_post_action ) {
        try {
            eval(bvr.cbjs_dg_table_delete_post_action);
        } catch(e) {
            spt.log_eval_error( e, stmt, "spt.dg_table.gear_smenu_delete_selected_cbk",
                                "error occurred in running post delete cbjs script" );
        }
    }
}


spt.dg_table.refresh_table_by_refresh_button = function( table_top )
{
    // Force refresh of the table (after deletes) by finding the refresh button and exectuing
    // the click behavior of that button ...
    var img_list = table_top.getElements(".simple_button");
    var refresh_el = null;
    for( var i=0; i < img_list.length; i++ ) {
        var img = img_list[i];
        var src = img.getAttribute('src');
        if( src.contains("refresh.png") ) {
            refresh_el = img.parentNode;
        }
    }
    if( refresh_el ) {
        var click_bvr_list = spt.behavior.get_bvrs_by_type( 'click', refresh_el );
        for( c=0; c < click_bvr_list.length; c++ ) {
            var tmp_bvr = click_bvr_list[c];
            spt.behavior.run_preaction_action_postaction( tmp_bvr, {}, {} );
        }

        return true;
    }

    return false;
}

spt.dg_table.gear_smenu_add_task_matched_cbk = function( evt, bvr )
{
    var activator = spt.smenu.get_activator(bvr);
    if (!activator) {
        activator = bvr.src_el;
    }
    var layout = activator.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");
    if (version == "2") {
        spt.table.set_layout(layout);
        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table_table' );
        var table_id = table.get('id');
    }
    else {
        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table' );
        var table_id = table.get('id');
    }

    var search_type = table.get("spt_search_type");
    var view = table.get("spt_view");
    var search_class = table.get("spt_search_class") || "";


    var search_view;
    // init the args to be passed to CsvExportWdg
    var args = {
        'table_id': table.get('id'),
        'search_type': search_type,
        'search_key_list': '',
        'view': view,
        'search_class': search_class,
        'mode': 'matched'
    };


    var popup_id = 'Add Tasks to Matched';
    var class_name = 'tactic.ui.app.AddTaskWdg';

    var top = table.getParent(".spt_view_panel");
    var search_wdg;
    if (top) {
        search_wdg = top.getElement(".spt_search");
        search_view = search_wdg.getAttribute("spt_view");
        args.search_view = search_view;
        simple_search_view = top.getAttribute("spt_simple_search_view");
        args.simple_search_view = simple_search_view;
    }
    if (!top || !search_wdg) {
        spt.alert('The search box is not found. Please use "Export Selected, Export Displayed" instead')
        return;
    }



    var search_values = spt.dg_table.get_search_values(search_wdg);
    search_values_dict = {'json' : search_values};

    spt.panel.load_popup(popup_id, class_name, args, {'values': search_values_dict} );
}

spt.dg_table.gear_smenu_add_task_selected_cbk = function( evt, bvr )
{
    var activator = spt.smenu.get_activator(bvr);
    if (!activator)
        activator = bvr.src_el;

    var layout = activator.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");

    var table_id = 0;
    if (version == "2") {
        spt.table.set_layout(layout);
        table_id = spt.table.get_table_id()
    }
    else {
        var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table' );
        table_id = table.get('id');
    }


    var sk_list = [];
    var popup_id = 'Add Tasks to Selected';
    var class_name = 'tactic.ui.app.AddTaskWdg';


    if (bvr.search_key_list) {
        sk_list = bvr.search_key_list;
    }
    else {
        var selected_rows;
        if (version == "2") {
            selected_rows = spt.table.get_selected_rows();
        }
        else {
            selected_rows = spt.dg_table.get_selected(table_id);
        }

        for (var i=0; i < selected_rows.length; i++) {
            var search_key = selected_rows[i].getAttribute("spt_search_key");
            sk_list.push(search_key);
        }
    }
    var options = {'search_key_list': sk_list, 'table_id': table_id};
    spt.panel.load_popup(popup_id, class_name, options);
}


spt.dg_table.add_task_selected = function(bvr)
{
    var search_keys = bvr.search_key_list;
    var num = search_keys.length;
    if (num == 0) {
        spt.alert("Nothing selected to create task for");
        return;
    }

    //var search_key_info = spt.dg_table.parse_search_key( selected_rows[0].getAttribute("spt_search_key") );



    var add_task_cancel = function() {
         spt.app_busy.hide();
    }

    var add_task_ok = function() {
        var aborted = false;
        var server = TacticServerStub.get();
        var title = 'Add Tasks:';
        var refresh_event = bvr.post_event;

        var msg = 'Adding tasks to  ' + num + ' items ...';

        spt.app_busy.show( title, msg );
        server.start({title: "Adding task to ["+num+"] items"});

        on_complete = function() {
            server.finish();
            if (!aborted) {
                spt.notify.show_message("Task creation completed.");
                spt.named_events.fire_event(refresh_event, {});
            }
        };

        try {
            var cmd = 'tactic.ui.app.AddTaskCbk';
            var options = {
                    'search_key_list': bvr.search_key_list};
            var values = spt.api.Utility.get_input_values(bvr.src_el.getParent('.spt_add_task_panel'))
            rtn = server.execute_cmd(cmd, options, values,{on_complete:on_complete});

            //spt.alert(rtn.description);
        }
        catch(e) {
            var error_str = spt.exception.handler(e);
            error_str = error_str.replace('\n','<br>');
            spt.app_busy.hide()
            spt.alert( '"Add Task to Selected" aborted "' +
                    error_str + '"' );
            server.abort();
            aborted = true;
        }

        spt.app_busy.hide()
        //server.finish();
        spt.popup.close(bvr.src_el.getParent('.spt_popup'));




    }
    var msg = "Are you sure you wish to add tasks to [" + num + "] items?";
    //spt.confirm(msg, add_task_ok, add_task_cancel);
    add_task_ok();

}

spt.dg_table._new_toggle_commit_btn = function(el, hide)
{
    var table_top = el.getParent(".spt_table_top");

    if( ! table_top ) {
        spt.js_log.warning('Table top not found! Cannot toggle display of commit button');
        return;
    }

    var commit_button = spt.ctags.find_single_element( table_top, "spt_table_commit_btn", "spt_table_top" );
    if (hide) {
        spt.hide( commit_button );
    } else {
        spt.show( commit_button );
    }
}

// Data-Grid Table callbcks ...

//
// Extract the size and order of the table columns
//
// Description: creates xml document of the widget config format
//
// <config>
//   <list width='800px'>
//     <element name="checkbox" width='14.5%'/>
//     <element name="coffee" width='18.4%'/>
//   </list>
// </config>
//
//
// NOTE: this method is poorly named ... it does a *LOT* more than
// just get size info.  It also builds the config xml
//
spt.dg_table.get_size_info = function(table_id, view, login, first_idx, kwargs={"extra_data": {}})
{
    var table = document.id(table_id);
    var definition_view = table.getAttribute("spt_view");
    if (view == undefined) {
        view = definition_view;
    }
    var panel = table.getParent(".spt_table_top");
    var view_attrs = panel.getAttribute("spt_view_attrs");
    if (view_attrs)
        eval('view_attrs=' + view_attrs);

    if (view_attrs == null)
        view_attrs = {};
    var search_type = table.getAttribute("spt_search_type");

    // first index is one (to avoid storing checkbox)
    if (first_idx == null)
        first_idx = 1;

    var layout = table.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");
    var row;
    if (version == "2") {
        spt.table.set_layout(layout);
        row = spt.table.get_header_row();
    }
    else {
        // find the header row with the appropriate element name
        row = null;
        for( var c=0; c < table.rows.length; c++ ) {
            var name = table.rows[c].cells[0].getAttribute("spt_element_name");
            if (name != null) {
                row = table.rows[c];
                break;
            }
        }

        if (row == null) {
            throw("Can't find header row!");
        }
    }
    //if not specified, assume TableLayoutWdg
    if (view_attrs && view_attrs.layout == null)
        view_attrs['layout'] = 'TableLayoutWdg';
    var config = '<config>\n';

    if (view.test(/@/)) {
        config += '  <view name="' + view  + '" ';

    }
    else
        config += '  <' + view ;

    for (attr in view_attrs) {
        if (attr == 'name') continue;

        if (view_attrs.hasOwnProperty(attr))
            config += ' ' + attr +'="'+view_attrs[attr] + '" ';
    }


    config += '>\n';
    // go through each header cell and get the element name
    // skip the first selection
    var table_elements = [];
    let cells = row.getElements(".spt_table_header");
    for( var c=first_idx; c < cells.length; c++ ) {
        let cell = cells[c];
        let name = cell.getAttribute("spt_element_name");
        if (name == null) {
            continue;
        }
        let width = spt.get_element_width(cell);
        config += '    <element name="'+ name +'" hidden="false" width="'+ width +'"/>\n';
        table_elements.push(name);
    }


    // if saving definitions, add elements not present in table from view, setting them as hidden
    var server = TacticServerStub.get()
    var definitions;
    var definition_elements;
    if (kwargs.save_definitions) {
        definitions = server.eval("@GET(config/widget_config['search_type', '" + search_type + "']['view', '" + definition_view + "'].config)", {single: true});
        if (definitions) {
            var definition_xml = spt.parse_xml(definitions);
            definition_elements = Array.prototype.slice.call(definition_xml.getElementsByTagName("element"), 0);
            for (var i = 0; i < definition_elements.length; i++) {
                var name = definition_elements[i].getAttribute("name");

                if (table_elements.indexOf(name) == -1) {
                    config += '    <element name="'+ name +'" hidden="true"/>\n';
                }
            }
        }
    }
    if (view.test(/@/))
        config += '  </view>\n';
    else
        config += '  </' + view + '>\n';


    config += '</config>\n';

    // copy definitions
    if (definitions) {
        // work with XML doc for convenience
        var config_xml = spt.parse_xml(config);

        // get all elements to check for definitions, and all available definitions respectively
        var config_elements = config_xml.getElementsByTagName("element");

        // for each element in the new config, copy the element definition
        for (var i = 0; i < config_elements.length; i++) {

            // check if a definition with the same name exists
            var definition_element = definition_elements.filter(function(el) {
                return config_elements[i].getAttribute("name") == el.getAttribute("name");
            });

            // copy only the first definition found
            if (definition_element.length > 0) {
                definition_element = definition_element[0];

                // copy over the definition, prioritizing newly defined attribute values (just "width"
                // and "hidden" for now) and using the unmodified ones from the definition
                var attributes = config_elements[i].getAttributeNames();

                for (var j = 0; j < attributes.length; j++) {
                    definition_element.setAttribute(attributes[j], config_elements[i].getAttribute(attributes[j]))
                }

                config_elements[i].outerHTML = definition_element.outerHTML;
            }
        }

        // re-serialize the config with the definitions
        config = new XMLSerializer().serializeToString(config_xml);
    }

    var config_search_type = 'config/widget_config';
    var code = view;
    var data = {'view': view, 'search_type': search_type };
    // only if view starts with <login>. then add the login info
    if (login && (/\./).test(view) ) {
        data['login'] = login;
    }
    config_obj = server.get_unique_sobject( config_search_type, data );
    var config_search_key = config_obj["__search_key__"];

    //redefine data
    var data = {};
    var extra_data = kwargs.extra_data;
    for (var key in extra_data) {
      data[key] = extra_data[key];
    }
    data['config'] = config;
    config_obj = server.update(config_search_key, data);

    // change view attribute of table
    table.setAttribute("spt_view", view);
    layout.setAttribute("spt_view", view);

    var layout_top = layout.getParent(".spt_layout_top");
    layout_top.setAttribute("spt_view", view);

    var panel = layout_top.getParent(".spt_view_panel_top");
    if (panel) {
        panel.setAttribute("spt_view", view);
    }

    return config;

}


spt.dg_table.get_selection_value = function(element) {
    // get the value of the element
    var value;
    if (typeof(element) == 'string')
        value = element;
    else
        value = element.value;
    return value;
}

// Callback for the table action widget. The action is delegated to the
// appropriate method depending on the value of the selection
//
// TODO: make this into a real callback
//
spt.dg_table.table_action_cbk = function(element, table_id ) {

    var table = document.getElementById(table_id);
    var view = table.getAttribute("spt_view");
    var search_type = table.getAttribute("spt_search_type");

    var server = TacticServerStub.get();

    // get the value of the element
    var value = spt.dg_table.get_selection_value(element);
    switch(value) {
    case "retire":

        // put the retire in a transaction
        server.start({"title": "Retire selected sobjects"});
        try {
            spt.dg_table.retire_selected(table_id);
        }
        catch(e) {
            server.abort();
            throw(e);
        }
        server.finish();
        break;


    case "delete":
        // put the delete in a transaction
        server.start({"title": "Delete selected sobjects"});
        try {
            if (confirm("Are you sure you wish to delete the select items?")) {
                spt.dg_table.delete_selected(table_id);
            }
        }
        catch(e) {
            server.abort();
            throw(e);
        }
        server.finish();
        break;

    default:
        spt.alert("Unimplemented option: " + value);
    }
    element.value = "";
}



//
// Callback on the view action selection.  This selection allows you to
// manipulate the view.
//
spt.dg_table.view_action_cbk = function(element, table_id , bvr) {

    var table;
    if (! table_id) {
        var activator = spt.smenu.get_activator(bvr);
        table = activator.getParent(".spt_table_top").getElement(".spt_table_content");
        table_id = table.getAttribute("id");
    }
    else {
        // get information from the table
        table = document.id(table_id);
    }


    if (!table) {
        spt.alert('No table defined');
        return;
    }
    var table_search_type = table.getAttribute("spt_search_type");
    var table_view = table.getAttribute("spt_view");

    var options = {
        'search_type': table_search_type,
        'view':        table_view
    };

    var server = TacticServerStub.get();

    var value;
    if (element == "save") {
        value = "save";
    }
    else {
        value = spt.dg_table.get_selection_value(element);
    }

    bvr.src_table = table;

    if (value == "save") {
        var login = spt.Environment.get().get_user()

        var kwargs = {'login': login, 'is_admin': bvr.is_admin};
        kwargs['unique'] = false;
        kwargs['save_as_personal'] = false;

        var is_embedded = spt.dg_table.is_embedded(table);
        if (is_embedded) {
            //show busy message
            var title = 'Save Embedded View';
            var msg = 'Saving View [ ' + table_view + ' ]';
            spt.app_busy.show( title, msg );

            kwargs['new_title'] = table_view;
            kwargs['save_a_link'] = false;
            setTimeout( function() {spt.table.save_view(table_id, table_view, kwargs);
                spt.app_busy.hide();}, 0 )
            return;
        }

        var panel = table.getParent('.spt_view_panel');
        if ( panel) {
            var schema_default_view = panel.getAttribute("spt_schema_default_view")=='true';
            if (schema_default_view) {
                spt.alert("You cannot save over a schema default view. Choose Save a New View.");
                return;
            }
            var element_name = panel.getAttribute("spt_element_name");

            // FIXME: this is relying on a piece of data that is often not
            // in existence.  It relies on the fact that this table came
            // from a link, which is often *not* the case.
            if (element_name != null) {

                var parts = element_name.split('.');
                // FIXME: this is a bit weak for checking rights
                if (!bvr.is_admin && !(/\./).test(element_name)) {
                    spt.alert("You do not have the admin right to save over this view");
                    return;
                }

                // this element_name will go into the definition view of SideBarWdg
                if (parts && parts[0] == login || bvr.is_admin) {
                    kwargs['element_name'] = element_name;
                }
            }
            else {
                element_name == '';
            }
        }
        var new_view = table_view;


        var new_title = '';
        var last_element = '';
        if (panel) {
            new_title = panel.getAttribute('spt_title');
            last_element = panel.getAttribute("spt_element_name");
        }
        if (!new_title && panel) {
            var tab_top = panel.getParent('.spt_tab_content');
            if (tab_top) new_title = tab_top.getAttribute('spt_title');
        }
        if (!new_title)
            new_title = new_view;
        kwargs['new_title'] = new_title;
        kwargs['save_mode'] = 'save_view_only';
        kwargs['last_element_name'] = last_element;

        //kwargs['new_title'] = table_view;


        if ((/\./).test(element_name)) {
            kwargs['save_as_personal'] = true;
        }
        var panel_id = "main_body";

        //show busy message
        var title = 'Save Current View';
        var msg = 'Saving View [ ' + kwargs.new_title + ' ]';
        spt.app_busy.show( title, msg );
        setTimeout( function() {spt.dg_table.save_view(table_id, new_view, kwargs);spt.app_busy.hide();}, 0 );

    }
    else if (value == "save_project_view") {
        var view = "project_view";
        //var widget_class = "tactic.ui.panel.ViewPanelSaveWdg";
        var widget_class = "tactic.ui.panel.ViewPanelSaveDialogWdg";
        var args = {
            'table_id': table_id,
            'view': view
        };
        bvr.class_name = widget_class;
        bvr.args = args;
        //spt.dg_table_action.set_actionbar_aux_content( {}, bvr);
        spt.panel.load_popup("Save Project View", widget_class, args);

    }
    else if (value == "edit_current_view") {
        spt.panel.load_popup('View Manager', 'tactic.ui.manager.ViewManagerWdg', options);
    }
    else if (value == "custom_property") {

        var widget_class = "tactic.ui.app.CustomPropertyAdderWdg";
        bvr.class_name = widget_class;
        bvr.args = options;
        spt.dg_table_action.set_actionbar_aux_content( {}, bvr);

    }

    else {
        spt.alert("Unimplemented option: " + value);
    }

    element.value = "";
}



// Callback that gets executed when "Save My/Project View As" is selected
// DEPRECATED: this has been moved inline
spt.dg_table.save_view_cbk = function(table_id, login) {
    alert("spt.dg_table.save_view_cbk is deprecated")

    var table = document.id(table_id);
    var top = table.getParent(".spt_view_panel");
    // it may not always be a View Panel top
    if (!top) top = table.getParent(".spt_table_top");

    //var search_wdg = top.getElement(".spt_search");

    // TODO: Will this break on embedded tables now?????  Maybe not
    // because the first instance is probably what we want ... however,
    // a little tenous
    var view_info = top.getElement(".spt_save_top");

    var values;
    if (view_info != null) {
        values = spt.api.Utility.get_input_values(view_info , null, false);
    }
    else {
        // NOTE: this is deprecated
        var aux_content = top.getElement(".spt_table_aux_content")
        values = spt.api.Utility.get_input_values(aux_content , null, false);
    }
    // rename view
    var new_view = values["save_view_name"];
    var new_title = values["save_view_title"];
    var same_as_title = values["same_as_title"] == 'on';
    //var save_a_link = values["save_a_link"] == 'on';

    var save_mode = values['save_mode'];
    if (!save_mode) {
        var save_project_views = values['save_project_views'] == 'on';
        if (save_project_views) {
            save_mode = 'save_project_views';
        }
        var save_my_views = values['save_my_views'] == 'on';
        if (save_my_views) {
            save_mode = 'save_my_views';
        }
        var save_view_only = values['save_view_only'] == 'on';
        if (save_view_only) {
            save_mode = 'save_view_only';
        }
    }

    if (same_as_title) {
        new_view = new_title;
    }

    if (spt.input.has_special_chars(new_view)) {
        spt.alert("The name contains special characters. Do not use empty spaces.");
        return;
    }
    if (new_view == "") {
        spt.alert("Empty view name not permitted");
        return;
    }

    if ((/^(saved_search|link_search)/i).test(new_view)) {
        spt.alert('view names starting with these words [saved_search, link_search] are reserved.');
        return;
    }
    var table = document.getElementById(table_id);
    if (!table) {
        spt.alert('This command requires a Table in the main viewing area');
        return;
    }
    var table_search_type = table.getAttribute("spt_search_type");
    var table_view = table.getAttribute("spt_view");
    var last_element = top.getAttribute("spt_element_name");


    var kwargs = {'login' : login, 'new_title' : new_title,
        'element_name': new_view,
        'last_element_name': last_element,
        'save_mode': save_mode,
    }

    spt.app_busy.show( 'Saving View', new_title );
    var rtn = spt.dg_table.save_view(table_id, table_view, kwargs);
    spt.app_busy.hide();

    if (!rtn)
        return;

    return true;
}

//verify matching spt_view
spt.dg_table.is_embedded = function(table){
    var top = table.getParent(".spt_view_panel");
    // top is null if it's a pure Table Layout
    if (!top) return false;

    var panel_table_view = top.getAttribute('spt_view');
    var table_view = table.getAttribute('spt_view');
    var panel_search_type = top.getAttribute("spt_search_type");
    var table_search_type = table.getAttribute("spt_search_type");

    var is_embedded = false;
    if (panel_table_view != table_view || panel_search_type != table_search_type) {
        //spt.alert('Embedded table view saving not supported yet');
        is_embedded = true;

    }
    return is_embedded;
}

spt.dg_table.save_view = function(table_id, new_view, kwargs)
{
    try {
        var table = document.id(table_id);
        var top = table.getParent(".spt_view_panel");
        var search_wdg = top ? top.getElement(".spt_search"): null;

        var save_mode = kwargs['save_mode'];

        if (spt.dg_table.is_embedded(table)) {
            //spt.alert('Embedded table view saving not supported yet');
            var login = kwargs.login;
            this.get_size_info(table, new_view, login);
            return false;
        }

        var table_search_type = table.getAttribute("spt_search_type");


        var dis_options = {};


        var login = kwargs.login;
        var save_as_personal = (save_mode == 'save_my_views') ? true : false;


        var side_bar_view = 'project_view';
        if (save_as_personal) {
            side_bar_view = 'my_view_' + login;
        }

        // start a transaction
        var server = TacticServerStub.get();
        var title = side_bar_view + " updated from: " + new_view;
        server.start({"title": "Saving View", "description": "Saving View: " +  title});

        var element_name = new_view;
        var unique = kwargs.unique;

        // Save My View allows to save over the current view if it is already a personal view
        // or if the user is admin, he can save over anything
        if (kwargs.element_name ) {
            element_name = kwargs.element_name;
        }
        var new_title = kwargs.new_title;


        var last_element_name = kwargs.last_element_name;

        // If it is saving as a new personal view, we try to append login name
        if (save_as_personal) {
            //only do this to search_view to make it easier to retrieve a search for my_view_<user>
            if (login && !(/\./).test(element_name) ) {
                element_name = login + '.' + element_name;
            }
        }

        var custom_search_view = null;
        if (search_wdg) {
            var search_view = 'link_search:'+ element_name;
            // auto generate a new search for this view
            search_wdg.setAttribute("spt_search_view", search_view);
            spt.dg_table.save_search(search_wdg, search_view, {'unique': kwargs.unique, 'personal': save_as_personal});

            custom_search_view = search_wdg.getAttribute('spt_custom_search_view');
        }
        // add to the project views
        var search_type = "SideBarWdg";
        var class_name = "LinkWdg";

        var simple_search_view = top ? top.getAttribute('spt_simple_search_view'): null;
        var insert_view = top ? top.getAttribute('spt_insert_view'): null;
        var edit_view = top ? top.getAttribute('spt_edit_view'): null;
        var layout = top ? top.getAttribute('spt_layout'): null;


        dis_options['search_type'] = table_search_type;
        dis_options['view'] = element_name;
        dis_options['search_view'] = search_view;
        if (custom_search_view)
            dis_options['custom_search_view'] = custom_search_view;
        if (simple_search_view)
            dis_options['simple_search_view'] = simple_search_view;
        if (insert_view)
            dis_options['insert_view'] = insert_view;
        if (edit_view)
            dis_options['edit_view'] = edit_view;
        if (layout)
            dis_options['layout'] = layout;

        // redefine kwargs
        var kwargs = {};
        kwargs['login'] = null;
        if (save_as_personal)
            kwargs['login'] = login;
        kwargs['class_name'] = class_name;
        kwargs['display_options'] = dis_options;

        kwargs['unique'] = unique;


        // these are the server oprations


        // Copy the value of the "icon" attribute from the previous XML widget
        // config.
        var icon = null;
        var widget_config_before = server.get_config_definition(search_type, "definition", last_element_name);
        // Skip if there is no previous matching XML widget config.
        if (widget_config_before != "") {
            xmlDoc = spt.parse_xml(widget_config_before);
            var elem_nodes = xmlDoc.getElementsByTagName("element");

            if (elem_nodes.length > 0) {
                var attr_node = elem_nodes[0].getAttributeNode("icon")

                // Skip if there is no icon to copy over from the old link.
                if (attr_node != null) {
                    icon = attr_node.nodeValue;
                }

                // keep title
                if ( save_mode == 'save_view_only' ) {
                    var title_node = elem_nodes[0].getAttributeNode("title")
                    if (title_node)
                        new_title = title_node.nodeValue;
                }

            }
        }


        if (new_title)
            kwargs['element_attrs'] = {'title': new_title, 'icon': icon};


        // add the definiton to the list
        var info = server.add_config_element(search_type, "definition", element_name, kwargs);
        var unique_el_name = info['element_name'];

        //raw and static_table layout has no checkbox in the first row
        var first_idx = 1;
        if (['raw_table','static_table'].contains(layout))
            first_idx = 0;

        // create the view for this table
        this.get_size_info(table, unique_el_name, kwargs.login, first_idx);

        //if (side_bar_view && save_a_link) {
        if (save_mode != 'save_view_only') {
            var kwargs2 = save_as_personal ? {'login': login } : {};

            server.add_config_element(search_type, side_bar_view, unique_el_name, kwargs2);
        }
        server.finish();

        spt.panel.refresh("side_bar");
    } catch(e) {
        spt.alert(spt.exception.handler(e));
        return false;
    }
    return true;

}




//
// Dynamically loading and removing columns
//

spt.dg_table.toggle_column_cbk = function(table_id, element_name, element_index, popup_id)
{
    var table = document.id(table_id);

    var layout = table.getParent(".spt_layout");
    if (table.hasClass("spt_layout")) {
        layout = table;
    }
    if (layout.getAttribute("spt_version") == "2")
        var element_names = spt.table.get_element_names();
    else
        var element_names = spt.dg_table.get_element_names(table_id);

    var is_present = false;
    for (var i=0; i<element_names.length; i++) {
        if (element_names[i] == element_name) {
            is_present = true;
            break;
        }
    }


    if (layout.getAttribute("spt_version") == "2") {


        spt.table.set_layout(layout);
        try {
            if (is_present) {
                spt.app_busy.show( 'Column Manager', 'Removing Column');
                spt.table.remove_column(element_name);
            } else {
                spt.app_busy.show( 'Column Manager', 'Adding Column');
                setTimeout(function() {
                    spt.table.add_column(element_name);
                    //spt.dg_table.search_cbk( {}, {'src_el': layout} )
                    // need to do this twice
                    spt.table.expand_table();
                    spt.table.expand_table();
                }, 50);
            }
            spt.app_busy.hide();
        } catch(e) {
            spt.alert(spt.exception.handler(e));
        }
        return;
    }

    element_index = element_names.length + 1;


    if (is_present) {
        var bvr2 = {};
        bvr2.options = {
            table_id: table_id,
            element_name: element_name,
            element_index: element_index
        };
        spt.dg_table.remove_column_cbk({}, bvr2);
    }
    else {
        spt.dg_table.load_column_cbk(table_id, element_name, element_index)
    }

}



spt.dg_table.load_column_cbk = function(table_id, element_name, element_index)
{
    spt.app_busy.show( 'Column Manager', 'Adding Column');

    //IE and FF compatible
    setTimeout(function() { var cmd = new spt.dg_table.LoadColumnCmd(
                table_id, element_name, element_index);
                Command.execute_cmd(cmd);
                spt.app_busy.hide();
                    }, 50 );

}


// Command to load in a column
spt.dg_table.LoadColumnCmd = function(table_id, element_name, element_index)
{
    this.table_id= table_id;

    this.element_name = element_name;
    this.element_index = element_index;

    this.get_description = function() {
        return "Loaded column";
    }

    this.execute = function() {
        this.redo();
    }

    this.redo = function() {
        var table = document.id(this.table_id);
        //WHAT IS THIS?
        var column_index = element_index*2;
        var args = {};
        var server = TacticServerStub.get();

        // get the search_keys
        var search_keys = [];
        var search_type = table.getAttribute("spt_search_type");


        for (var i = spt.dg_table.INSERT_ROW; i < spt.dg_table.EDIT_ROW; i++) {
            var row = table.rows[i];
            var search_key = row.getAttribute("spt_search_key");
            if (search_key == null) {
                continue;
            }
            search_keys.push(search_key);
        }


        // get widgets
        var widgets_html = server.get_column_widgets(search_type, search_keys, this.element_name);
        // iterate through the widgets
        var widgets_html_idx = 0;



        for (var i = 0; i < 1; i++) {
            var row = table.rows[i];
            // skip empty rows
            var search_key = row.getAttribute("spt_search_key");
            if (i >= spt.dg_table.FIRST_ROW && search_key == null) {
                // this is a table grouping row (commented out as it is NOT IE compatible)
                //var grouping_td = row.getElement("td");
                var grouping_td = row.firstChild;
                // add 2 (for column and its corresponding resize column) to the colspan for each grouping row ...
                var new_num_cols = parseInt( grouping_td.getAttribute("colspan"), 10 ) + 2;
                grouping_td.setAttribute("colspan", (""+ new_num_cols) );
                continue;
            }

            if (column_index < 0) {
                right_cell = null;
            }
            else {
                right_cell = row.cells[column_index];
            }

            var widgets_html_value =  widgets_html[ widgets_html_idx ];

            // we really only need the header 'cuz the table is refreshed at the
            // end anyways
            if (widgets_html_idx > 0) {
                continue;
            }
            // create a new column and add it to the table
            if (widgets_html_value) {

                for (j = 0; j <widgets_html_value.length; j++) {
                    var widget_html = widgets_html_value[j];

                    // hack a full table in the html
                    widget_html = "<table><tbody><tr>" + widget_html + "</tr></tbody></table>"

                    // create a dummy node
                    var dummy = document.createElement("div");

                    // replace the widget
                    spt.behavior.replace_inner_html( dummy, widget_html );
                    // do some magic
                    var child = dummy.firstChild.firstChild.firstChild.firstChild;
                    if (right_cell != null) {
                        row.insertBefore(child, right_cell);
                    }
                    else {
                        row.appendChild(child);
                    }

                    //Effects.fade_in(child, 500);
                }
            }
            widgets_html_idx += 1;
        }

        //DEPRECATED (this is not deprecated! column reorder still uses the col_idx value!)
        // reset col_idx
        var first_row = table.rows[0];
        for (var i=0; i<first_row.cells.length;i++) {
            var cell = first_row.cells[i];
            cell.setAttribute("col_idx", String(i));
        }

        //not sure how it all works above, just refresh it so the green arrows align properly
        spt.dg_table.search_cbk( {}, {'src_el': table} );
    }

    this.undo = function() {

        var table = document.id(this.table_id);
        var column_index = this.element_index*2;

        for (var i = 0; i < table.rows.length; i++) {
            var row = table.rows[i];

            if (column_index < 0)
                column_index = row.cells.length - 2;


            var cell = row.cells[column_index];
            var space = row.cells[column_index+1];
            row.removeChild( cell );
            row.removeChild( space );
        }

        // reset col_idx
        var first_row = table.rows[0];
        for (var i=0; i<first_row.cells.length;i++) {
            var cell = first_row.cells[i];
            cell.setAttribute("col_idx", String(i));
        }


    }
}




spt.dg_table.remove_column_cbk = function(evt, bvr)
{
    var src_el = bvr.src_el;

    var element_name = bvr.options['element_name'];
    var element_idx = bvr.options['element_idx'];

    var table = null;
    if (bvr.options && bvr.options.table_id) {
        table = document.id(bvr.options.table_id);
    }
    else {
        var activator = spt.smenu.get_activator(bvr);
        if (activator != null) {
            table = activator.getParent(".spt_table");
        }
    }
    if (table == null) {
        table = src_el.getParent(".spt_table");
    }
    if (table == null) {
        var panel = src_el.getParent(".spt_panel");
        table = src_el.getElement(".spt_table_content");
    }

    // FIXME: this is storing a table in a command ... serious memory leak
    // can occur here!!
    var cmd = new spt.dg_table.RemoveColumnCmd(table, element_name, element_idx);
    Command.execute_cmd(cmd);
}



// Command to remove a column
spt.dg_table.RemoveColumnCmd = new Class({

    Extends: Command,
    initialize: function(table_id, element_name, element_index)
    {
        this.table_id = table_id;
        this.element_name = element_name;
        this.element_index = element_index;
    },

    get_description: function() {
        return "Removed column";
    },

    execute: function() {
        this.redo();
    },

    redo: function() {
        var column_index = this.element_index*2;
        var table = document.id(this.table_id);

        // find the index
        var header_row = table.rows[0];
        for (var i = 0; i < header_row.cells.length; i++) {
            var cell = header_row.cells[i];
            if (cell.getAttribute("spt_element_name") == this.element_name) {
                column_index = i;
                break;
            }
        }
        // remove all of the cells
        for (var i = 0; i < table.rows.length; i++) {
            var row = table.rows[i];
            var cell = row.cells[column_index];
            var space = row.cells[column_index+1];

            try {
                row.removeChild( cell );
                row.removeChild( space );
            } catch(e) {
                //throw(e);
                continue;
            }
        }

        //DEPRECATED
        // reset col_idx
        var first_row = table.rows[0];
        for (var i=0; i<first_row.cells.length;i++) {
            var cell = first_row.cells[i];
            cell.setAttribute("col_idx", String(i));
        }

    },

    undo: function() {
        spt.js_log.debug("Unimplemented");
    }
});







//
// Search functions
//

// Callback when search is pressed
// @param:
// bvr.search_el - child element of the search_top. If unspecified, it equals bvr.src_el
// bvr.src_el - child element of the table_top
spt.dg_table.search_cbk = function(evt, bvr){
    var panel = null;
    if (bvr.panel != null) {
        panel = bvr.panel;
    }
    else if (bvr.src_el.hasClass('spt_view_panel')) {
        panel = bvr.src_el;
    }
    else {
        panel = spt.get_parent(bvr.src_el, ".spt_view_panel");
    }

    bvr.panel = panel;
    el_name = '';
    if (panel)
        el_name = panel.getAttribute('spt_title');
    if (el_name == null)
        el_name = '';

    if (bvr.return_html) {
        var ret_val = spt.dg_table._search_cbk(evt, bvr);
        return ret_val;
    }
    setTimeout( function() {
        spt.dg_table._search_cbk(evt, bvr);
    }, 10 );
}


spt.dg_table._search_cbk = function(evt, bvr)
{
    var element = bvr.src_el;
    var new_search = bvr.new_search == true;

    var panel = bvr.panel;
    var title = "";
    if (panel) {
        title = panel.getAttribute("spt_title") || "";
    }
    // If there is an "spt_view_panel", VERIFY if it is for the given table or if we are in an
    // embedded table
    if( panel ) {
        var pnode = document.id(element.parentNode);
        var table_top_count = 0;
        while( pnode && pnode.hasClass && !pnode.hasClass("spt_view_panel") ) {
            if( pnode.hasClass("spt_table_top") ) {
                table_top_count ++;
            }
            pnode = document.id(pnode.parentNode);
        }
        if( table_top_count > 1 ) {
            panel = null;
        }
    }



    var layout;
    // adopt it if element is already the layout
    if (element.hasClass("spt_layout"))
        layout = element;
    else {
        layout = element.getParent(".spt_layout");
        if (!layout) {

            if (panel)
                layout = panel.getElement(".spt_layout");
        }
    }
    // default to version 2 table
    var version = "2";
    if (layout) {
        version = layout.getAttribute("spt_version");
        if (version == "2") {
            spt.table.set_layout(layout);
        }
    }


    if (spt.table.has_changes()) {
        /*
        if (!confirm("Changes made. Continue without saving?")) {
            return;
        }
        */
    }
    // if panel doesn't exist, then likely this is a table on its own
    if (panel == null) {
        var table_top;
        if (element.hasClass('spt_panel')) {
            table_top = element;
        }
        else {
            table_top = element.getParent(".spt_panel");
        }
        if (table_top){
            var table = table_top.getElement('.spt_table_content');
            if (table){

                   var element_names = version == "2" ? spt.table.get_element_names() :  spt.dg_table.get_element_names(table);


                   if (element_names)
                        table_top.setAttribute('spt_element_names', element_names);
            }
            var new_values = [];
            var table_searches = table_top.getElements(".spt_table_search");
            for (var i = 0; i < table_searches.length; i++) {
                var table_search = table_searches[i];
                var values = spt.api.Utility.get_input_values(table_search,null,false);
                new_values.push(values);
            }
            var search_dict = {'json' : JSON.stringify(new_values)};
        }
        var on_complete = function(){
            //
        }
        spt.panel.refresh(table_top, search_dict, {call_back: on_complete});
        return;
    }

    var search_el = bvr.src_el;
    if (bvr.search_el)
        search_el = bvr.search_el;


    var search_top = search_el.getParent(".spt_search");

    // this is usually null
    if (search_top == null) {
        if (spt.has_class( search_el, "spt_view_panel")){
            search_top = search_el.getElement('.spt_search');
        } else {
            search_top = spt.get_cousin(search_el, ".spt_view_panel", ".spt_search");
        }
    }
    if (search_top == null) {
        spt.panel.refresh(panel);
        return;
    }

    // search_top is only meaningful for this if it is the Search Criteria box
    // If show_search is false, the simple search top will be found if available
    // which is essential for retrieving the search_parameters later.

    var custom_search_view = search_top.getAttribute('spt_custom_search_view');
    if (!custom_search_view) custom_search_view = '';

    //var modified = search_top.getAttribute('spt_search_modified');
    // panel could be the same as target
    var target;
    if (spt.has_class( panel, "spt_table_top")){
        target = panel;
    }
    else {
        target = panel.getElement(".spt_table_top");
    }
    var table = panel.getElement(".spt_table_content");


    // if table is not found, maybe due to error, just refresh the whole panel
    if (!table) {
        spt.panel.refresh(panel);
        return;
    }
    var table_id = table.getAttribute("id");
    var search_type = table.getAttribute("spt_search_type");


    // the view filter overrides
    var view = null;
    if (view == '' || view == null) {
        view = table.getAttribute("spt_view");
        var class_name = target.getAttribute("spt_class_name");
        if (class_name == 'tactic.ui.panel.CustomLayoutWdg') {
            if (!view.includes(".")) {
                view = target.getAttribute("spt_view");
            }
        }
    }

    // get all of the search input values
    var new_values = [];
    if (search_top) {
        var search_containers = search_top.getElements('.spt_search_filter');
        for (var i = 0; i < search_containers.length; i++) {
            var values = spt.api.Utility.get_input_values(search_containers[i],null, false);
            new_values.push(values);
        }
        var ops = search_top.getElements(".spt_op");

        // special code for ops
        var results = [];
        var levels = [];
        var modes = [];
        var op_values = [];
        for (var i = 0; i < ops.length; i++) {
            var op = ops[i];
            var level = op.getAttribute("spt_level");
            level = parseInt(level);
            var op_value = op.getAttribute("spt_op");
            results.push( [level, op_value] );
            var op_mode = op.getAttribute("spt_mode");
            levels.push(level);
            op_values.push(op_value);
            modes.push(op_mode);

        }
        var values = {
            prefix: 'search_ops',
            levels: levels,
            ops: op_values,
            modes: modes
        };
        new_values.push(values);

    }
    // find the table search as well.  These can be extra search items outside
    // of the reqular SearchWdg. e.g. Simple search filters, grouping, limit
    var table_searches = panel.getElements(".spt_table_search");
    for (var i = 0; i < table_searches.length; i++) {
        var table_search = table_searches[i];
        var values = spt.api.Utility.get_input_values(table_search,null,false);
        if (new_search) {
            if (values['prefix'] == 'search_limit')
                values.Showing = '';
            else if (values['prefix'] == 'search_limit_simple')
                values.page = '';
        }
        new_values.push(values);
    }



    // append search data from local search
    if (bvr.search_values) {
        for (var i=0; i < bvr.search_values.length; i++)
            new_values.push(bvr.search_values[i]);
    }
    // convert to json
    var search_values_dict = {'json' : JSON.stringify(new_values)};

    // get the actual filter
    var filter_json= '';
    if (search_top){
        filter_json = search_top.getAttribute("spt_filter");
    }
    // handle state
    var state = target.getAttribute("spt_state");
    if (!state) {
        state = {};
    }
    var view_attrs = target.getAttribute("spt_view_attrs");
    var expr = target.getAttribute("spt_expression");
    var search_limit = target.getAttribute("spt_search_limit");
    var parent_key = target.getAttribute("spt_parent_key");
    var search_key = target.getAttribute("spt_search_key");
    var search_class = target.getAttribute("spt_search_class") || "";
    var search_view = target.getAttribute('spt_search_view');
    var show_search = target.getAttribute("spt_show_search");
    var show_keyword_search = target.getAttribute("spt_show_keyword_search");
    var show_insert = target.getAttribute("spt_show_insert");
    var show_select = target.getAttribute("spt_show_select");
    var show_shelf = target.getAttribute("spt_show_shelf");
    var show_gear = target.getAttribute("spt_show_gear");
    var show_expand = target.getAttribute("spt_show_expand");
    var show_column_manager = target.getAttribute("spt_show_column_manager");
    var show_layout_switcher = target.getAttribute("spt_show_layout_switcher");
    var show_context_menu = target.getAttribute("spt_show_context_menu");
    var show_help = target.getAttribute("spt_show_help");
    var insert_view = target.getAttribute("spt_insert_view");
    var edit_view = target.getAttribute("spt_edit_view");
    var edit_class = target.getAttribute("spt_edit_class");
    var ingest_data_view = target.getAttribute("spt_ingest_data_view");
    var ingest_custom_view = target.getAttribute("spt_ingest_custom_view");
    var checkin_context = target.getAttribute("spt_checkin_context");
    var checkin_type = target.getAttribute("spt_checkin_type");
    var group_elements = target.getAttribute("spt_group_elements");
    var group_label_expr = target.getAttribute("spt_group_label_expr");
    var class_name = target.getAttribute("spt_class_name");
    if (class_name == null) {
        class_name = "tactic.ui.panel.TableLayoutWdg";
    }
    var simple_search_view = target.getAttribute("spt_simple_search_view");
    var simple_search_config = target.getAttribute("spt_simple_search_config");
    var simple_search_mode = target.getAttribute("spt_simple_search_mode");
    var search_limit_mode = target.getAttribute("spt_search_limit_mode");
    var search_dialog_id = target.getAttribute("spt_search_dialog_id");
    var do_initial_search = target.getAttribute("spt_do_initial_search");
    var init_load_num = target.getAttribute("spt_init_load_num");
    var mode = target.getAttribute("spt_mode");
    var no_results_msg = target.getAttribute("spt_no_results_msg");
    var show_border = target.getAttribute("spt_show_border");
    var show_collection_tool = target.getAttribute("spt_show_collection_tool");
    var order_by = target.getAttribute("spt_order_by");

    var file_system_edit = target.getAttribute("spt_file_system_edit") || "";
    var base_dir = target.getAttribute("spt_base_dir") || "";
    var parent_mode = target.getAttribute("spt_parent_mode") || "";

    var settings = target.getAttribute("spt_settings") || "";
    var gear_settings = target.getAttribute("spt_gear_settings") || "";

    var shelf_view = target.getAttribute("spt_shelf_view") || "";
    var badge_view = target.getAttribute("spt_badge_view") || "";
    var extra_data = target.getAttribute("spt_extra_data") || "";
    var default_data = target.getAttribute("spt_default_data") || "";

    var resize_cbjs = target.getAttribute("spt_resize_cbjs") || "";
    var reorder_cbjs = target.getAttribute("spt_reorder_cbjs") || "";

    var filter_view = target.getAttribute("spt_filter_view") || "";

    var config_xml = target.getAttribute("spt_config_xml") || "";
    var edit_config_xml = target.getAttribute("spt_edit_config_xml") || "";

    var keyword_column = target.getAttribute("spt_keyword_column") || "";

    var height = target.getAttribute("spt_height") || "";
    var window_resize_offset = target.getAttribute("spt_window_resize_offset")
    var element_names;
    var column_widths = [];
    var search_keys = [];
    var custom_views = target.getAttribute("spt_custom_views") || "{}";

    if (version == "2") {
        if (bvr.element_names) {
            element_names = bvr.element_names;
        }
        else {
            element_names = spt.table.get_element_names();
        }
        var headers = spt.table.get_headers();
        for (var i = 0; i < headers.length; i++) {
            var size = headers[i].getSize();
            column_widths.push(size.x);
        }
        // specify selected search keys (disabling for now)
        //search_keys = spt.table.get_selected_search_keys();
        search_keys = []
    }
    else {
        if (bvr.element_names) {
            element_names = bvr.element_names;
        }
        else {
            element_names = spt.dg_table.get_element_names(table);
        }
        search_keys = []
    }


    var args = {
        'table_id': table_id,
        'search_type': search_type,
        'element_names': element_names,
        'group_elements': group_elements,
        'column_widths': column_widths,
        'view': view,
        'search_view': search_view,
        'custom_search_view': custom_search_view,
        'do_search': 'true',
        'state': state,
        'view_attrs': view_attrs,
        //'filter': filter_json,
        'expression': expr,
        'search_limit': search_limit,
        'parent_key': parent_key,
        'search_key': search_key,
        'search_class': search_class,
        'show_search': show_search,
        'show_keyword_search': show_keyword_search,
        'show_insert': show_insert,
        'show_select': show_select,
        'show_shelf': show_shelf,
        'show_gear': show_gear,
        'show_expand': show_expand,
        'show_column_manager': show_column_manager,
        'show_context_menu': show_context_menu,
        'show_layout_switcher': show_layout_switcher,
        'show_help': show_help,
        'insert_view': insert_view,
        'edit_view': edit_view,
        'edit_class': edit_class,
        'simple_search_view': simple_search_view,
        'simple_search_config': simple_search_config,
        'simple_search_mode': simple_search_mode,
        'search_limit_mode': search_limit_mode,
        'search_dialog_id': search_dialog_id,
        'do_initial_search': do_initial_search,
        'checkin_type': checkin_type,
        'checkin_context': checkin_context,
        'ingest_data_view': ingest_data_view,
        'ingest_custom_view': ingest_custom_view,
        'init_load_num': init_load_num,
        'mode': mode,
        'no_results_msg': no_results_msg,
        'show_border': show_border,
        'height': height,
        'is_refresh': 'true',
        'search_keys': search_keys,
        'show_collection_tool': show_collection_tool,
        'order_by': order_by,
        'file_system_edit': file_system_edit,
        'base_dir': base_dir,
        'parent_mode': parent_mode,
        'settings': settings,
        'gear_settings': gear_settings,
        'shelf_view': shelf_view,
        'badge_view': badge_view,
        'filter_view': filter_view,
        'extra_data': extra_data,
        'default_data': default_data,
        'window_resize_offset': window_resize_offset,
        'custom_views': custom_views,
        'resize_cbjs': resize_cbjs,
        'reorder_cbjs': reorder_cbjs,
        'title': title,
        'config_xml': config_xml,
        'edit_config_xml': edit_config_xml,
        'keyword_column': keyword_column,
    }

    var pat = /TileLayoutWdg|CollectionLayoutWdg/;
    var attr_list = ['expand_mode','show_name_hover','scale','sticky_scale','top_view', 'bottom_view','aspect_ratio','show_drop_shadow', 'title_expr', 'overlay_expr', 'overlay_color', 'allow_drag', 'upload_mode','process','gallery_align','detail_element_names','hide_checkbox'];
    for (var k=0; k < attr_list.length; k++) {
        var attr_val = target.getAttribute('spt_'+ attr_list[k]);
        if (attr_val)
            args[attr_list[k]] = attr_val;
    }

    if (bvr.extra_args) {
        for (k in bvr.extra_args)
            args[k] = bvr.extra_args[k];
    }


    // This is now the method for adding extra args
    var extra_keys = target.getAttribute("spt_extra_keys") || "";
    if (extra_keys) {
        args['extra_keys'] = extra_keys;
        extra_keys = extra_keys.split(",");
        for (var k = 0; k < extra_keys.length; k++) {
            var key = extra_keys[k];
            args[key] = target.getAttribute("spt_"+key) || "";
        }
    }


    var fade = true;


    // if bvr has an override_target then that becomes the target to replace
    // the contents of ...
    if( bvr.override_target ) {
        target = eval(bvr.override_target);

        fade = false;
    }

    // this is used to override the usual TableLayoutWdg class name ... for now it's
    // needed for the TablePrintLayoutWdg used for general print functionality ...
    // possible use for other TableLayoutWdg derived things
    if( bvr.override_class_name ) {
        class_name = bvr.override_class_name;
    }

    // have a chance to specify whether or not to show the search_limit_wdg ... needed
    // if you want all the results that match your search and not just the current
    // page ...
    args['show_search_limit'] = target.getAttribute('spt_show_search_limit');
    if( 'show_search_limit' in bvr ) {
        if( spt.is_FALSE( bvr.show_search_limit ) ) {
            args['show_search_limit'] = 'false';
        }
    }


    // Here is where you can target the list of items shown with a specific, arbitrary list of
    // search keys ... this will override the .handle_search() call
    if( 'selected_search_keys' in bvr ) {
        args['selected_search_keys'] = bvr.selected_search_keys;
    }

    if( ('use_short_search_type_label' in bvr) &&  spt.is_TRUE( bvr.use_short_search_type_label ) )  {
        args['use_short_search_type_label'] = 'true';
    }

    if( bvr.direct_replace_flag || bvr.return_html ) {
        var server = TacticServerStub.get();
        var kwargs = { 'args': args, 'values': search_values_dict };
        var widget_html = server.get_widget( class_name, kwargs );

        if( bvr.return_html ) {
            return widget_html;
        }
        // just directly replace innerHTML and return ... do not call spt.panel.load() when
        // the direct_replace_flag is true ...
        target.innerHTML = widget_html;
        return;
    }
    spt.kbd.clear_handler_stack();
    var on_complete = function(){
        //
    }

    spt.panel.load(target, class_name, args, search_values_dict, {fade: fade, callback: on_complete});

     // for reference on how to use ctags

     //var table_top = spt.ctags.find_parent( activator_el, "spt_table_top", "spt_table_top spt_view_panel spt_search" );
    //var search_top = spt.ctags.find_parent( activator_el, "spt_search", "spt_table_top spt_view_panel spt_search" );

}



// Collect local search data for a column and run the main search with it
spt.dg_table.local_search_cbk = function(evt, bvr)
{
    var search_el = bvr.src_el;
    if (bvr.search_el)
        search_el = bvr.search_el;
    var search_top = search_el.getParent(".spt_search");
     // get all of the search input values
    var new_values = [];
    if (search_top) {
        var search_containers = search_top.getElements('.spt_search_filter')
        for (var i = 0; i < search_containers.length; i++) {
            var values = spt.api.Utility.get_input_values(search_containers[i], null, false);
            new_values.push(values);
        }
    }

    // have to hard-code main_body_search for now
    var src_el = document.id('main_body_search');
    var bvr2 = {}
    bvr2.src_el = src_el;
    bvr2.search_values = new_values;
    spt.dg_table.search_cbk(evt, bvr2);
}

// Callback called when the search widget is inline
spt.dg_table.toggle_search_cbk = function(evt, bvr) {
    var src_el = bvr.src_el;
    var dst_el = spt.get_cousin(src_el, ".spt_search", ".spt_search_filters");

    bvr.dst_el = dst_el;
    spt.fx_anim.toggle_slide_el(evt, bvr);
}



spt.dg_table.search_action_cbk = function(element ) {

    var value = element.value;
    if (value == "retrieve") {
        spt.popup.open('retrieve_search_wdg', false);
    }
    else if (value == "save") {
        spt.popup.open('save_search_wdg', false);
    }
    element.value = "";
}


// callback to save the parameters of the search
spt.dg_table.save_search_cbk = function(evt, bvr) {

    //alert("spt.dg_table.save_search_cbk is deprecated");

    var src_el = bvr.src_el;
    var panel = src_el.getParent(".spt_view_panel");
    var search_wdg = panel.getElement(".spt_search");
    spt.dg_table.save_search(search_wdg);
}




spt.dg_table.get_search_values = function(search_top) {

    //alert("spt.dg_table.get_search_values is deprecated");
    // NOTE: used in export_matched for csv export

    // get all of the search input values
    var new_values = [];
    if (search_top) {
        var search_containers = search_top.getElements('.spt_search_filter')
        for (var i = 0; i < search_containers.length; i++) {
            var values = spt.api.Utility.get_input_values(search_containers[i],null, false);
            new_values.push(values);
        }

        var ops = search_top.getElements(".spt_op");

        // special code for ops
        var results = [];
        var levels = [];
        var modes = [];
        var op_values = [];
        for (var i = 0; i < ops.length; i++) {
            var op = ops[i];
            var level = op.getAttribute("spt_level");
            level = parseInt(level);
            var op_value = op.getAttribute("spt_op");
            results.push( [level, op_value] );
            var op_mode = op.getAttribute("spt_mode");
            levels.push(level);
            op_values.push(op_value);
            modes.push(op_mode);

        }
        var values = {
            prefix: 'search_ops',
            levels: levels,
            ops: op_values,
            modes: modes
        };
        new_values.push(values);

        // find the table/simple search as well
        var panel = search_top.getParent(".spt_view_panel");
        var table_searches = panel.getElements(".spt_table_search");
        for (var i = 0; i < table_searches.length; i++) {
            var table_search = table_searches[i];
            var values = spt.api.Utility.get_input_values(table_search,null,false);
            new_values.push(values);
        }
    }

    // convert to json
    var json_values = JSON.stringify(new_values);
    return json_values;

}



spt.dg_table.save_search = function(search_wdg, search_view, kwargs) {

    alert("spt.dg_table.save_search is deprecated");

    var json_values = spt.dg_table.get_search_values(search_wdg);

    // build the search view
    var search_type = search_wdg.getAttribute("spt_search_type");

    /*
    var view_text = document.id('save_search_text');
    if (search_view == undefined) {
        search_view = view_text.value;
    }
    */
    if (search_view == "") {
        search_view = search_wdg.getAttribute("spt_search_view");
    }

    if (search_view == "") {
        spt.alert("No name specified for saved search");
        return;
    }


    var options = {
        'search_type': search_type,
        'display': 'block',
        'view': search_view,
        'unique': kwargs.unique,
        'personal': kwargs.personal
    };

    // replace the search widget
    var server = TacticServerStub.get();

    var class_name = "tactic.ui.app.SaveSearchCbk";
    server.execute_cmd(class_name, options, json_values);

    /*
    if (document.id('save_search_wdg'))
        document.id('save_search_wdg').style.display = 'none';
    */


}


// DEPRECATED: moved to spt.table
spt.dg_table.add_filter = function(element) {

    var element = document.id(element);
    var container = element.getParent(".spt_filter_container");
    var filter = element.getParent(".spt_filter_container_with_op");
    var op = filter.getElement(".spt_op");

    var op_value;
    if (op == null) {
        op_value = 'and';
    } else {
        op_value = op.getAttribute("spt_op");
    }

    // get template
    var filter_top = element.getParent(".spt_filter_top");
    var filter_template = filter_top.getElement(".spt_filter_template_with_op");

    var filter_options = filter_top.getElement(".spt_filter_options");
    var filters = filter_options.getElements(".spt_filter_type_wdg");
    // clear the value in the textbox if any
    for (var k=0; k< filters.length; k++){
        input = filters[k].getElement("input");
        // hidden used for expression
        if (input && input.getAttribute('type') !='hidden' ) input.value ='';
    }



    // clone the filter
    var new_filter = spt.behavior.clone(filter_template);
    new_filter.addClass("spt_filter_container_with_op");
    new_filter.inject(filter, "after");
    var display = new_filter.getElement(".spt_op_display");

    var top = element.getParent(".spt_search");
    var filter_mode = top.getElement(".spt_search_filter_mode").value;
    if (filter_mode == 'custom') {
        display.innerHTML = op_value;
    }

    // make this into a new search filter
    var children = new_filter.getElements(".spt_filter_template");
    for (var i=0; i<children.length; i++) {
        var child = children[i];
        child.addClass("spt_search_filter");
    }
    var children = new_filter.getElements(".spt_op_template");
    for (var i=0; i<children.length; i++) {
        var child = children[i];
        child.addClass("spt_op");

        child.setAttribute("spt_op", op_value);
    }



}


// DEPRECATED: moved to spt.table
spt.dg_table.remove_filter = function(element) {

    var element = document.id(element);
    var container = element.getParent(".spt_filter_container");
    //var search_filter = element.getParent(".spt_search_filter")
    var search_filter = element.getParent(".spt_filter_container_with_op")

    var all_filters = container.getElements(".spt_filter_container_with_op");
    if (all_filters.length == 1) {
        return;
    }

    if (all_filters[0] == search_filter) {
        // have to destoy the spacing and op for the first filter
        var second_filter = all_filters[1];
        var op = second_filter.getElement(".spt_op");
        op.destroy();
        var spacing = second_filter.getElement(".spt_spacing");
        spacing.destroy();
    }

    container.removeChild( search_filter );

}





// filter_top: represents the top element which contains everything
// filter_container: container for all the filters
// filter_#: top of each of the filters
// filter_template: the element to clone when creating a new filter
// filter_columns: alternatives for all of the columns depending on search type
// filter_types: alternatives for all of the filters depending on type

spt.dg_table.set_filter = function(selector, prefix) {
    // get the column type mapping
    var filter_top = selector.getParent(".spt_filter_top");
    var hidden = filter_top.getElement(".spt_filter_indexes");
    var value = hidden.value;

    value = value.replace(/'/g, '"')
    var column_indexes = JSON.parse(value);

    // get a handle on all of the alternative filters
    var filter_options = filter_top.getElement(".spt_filter_options");
    var filters = filter_options.getElements(".spt_filter_type_wdg");

    // get the value of the column selector
    var value = selector.value;

    // get the target and the column index
    //var filter = document.id(selector.parentNode.parentNode);
    var filter = document.id(selector).getParent(".spt_filter_wdg")
    var column_index = column_indexes[value];
    if (typeof(column_index) == "undefined") {
        column_index = 0;
    }

    // clone and replace
    var clone = spt.behavior.clone( filters[column_index] )
    //var children = filter.getChildren();
    //filter.replaceChild( clone, children[4] );
    var filter_type_wdg = filter.getElement(".spt_filter_type_wdg");
    filter.replaceChild( clone, filter.getElement(".spt_filter_type_wdg") );

    clone.style.display = "inline";

}


spt.dg_table.set_filter2 = function(evt, bvr) {
    var prefix = bvr.prefix;
    var selector = bvr.src_el;

    // get the column type mapping
    //var value = document.id(prefix+"_search_type_indexes").value;
    //value = value.replace(/'/g, '"')
    //var column_indexes = JSON.parse(value);
    var column_indexes = bvr.search_type_indexes;

    //var filter_types = document.id(prefix + '_filter_columns');
    var filter_types = spt.get_cousin(selector, '.spt_filter_top', '.' + prefix + '_filter_columns');

    // get a handle on all of the alternative filters
    var filters = filter_types.getChildren();

    // get the value of the column selector
    var value = selector.value;

    // WARNING: MAGIC!!

    // get the target and the column index
    var filter = selector.getParent('.spt_filter_wdg');
    var column_index = column_indexes[value];
    if (column_index == undefined) {
        column_index = 0;
    }
    // clone and replace
    var clone = filters[column_index].clone();
    var replacee = filter.getElement('.spt_filter_columns');
    filter.replaceChild( clone, replacee );
    spt.show(clone);
    //clone.style.display = "inline";

}



spt.dg_table.disable_filter_cbk = function(element, filter_id) {

    // FIXME: disabled
    return

    var panel_id = 'main_body';
    var is_checked = element.checked;

    document.id(filter_id).style.color = '#333';
    document.id(filter_id).setAttribute('disabled', true)
    var input_list = document.id(panel_id+'_filter_container').getElements('.spt_input' );

    for (var i=1; i<input_list.length; i++) {
        var input = input_list[i];

        if (is_checked == false) {
            input.disabled = true;
            input.style.color = '#333';
        }
        else {
            input.disabled = false;
            input.style.color = '#fff';
        }
    }
}


// data dealing with editing of cells in the a table
//
spt.dg_table.edit = {};

spt.dg_table.edit.col = -1;
spt.dg_table.edit.row = -1;
spt.dg_table.edit.wdg_home_cell = null;
spt.dg_table.edit.wdg_home_index = 0;
spt.dg_table.edit.widget = null;
spt.dg_table.edit.orig_cell_value = null;
spt.dg_table.edit.widget_select_clicks = 0;


spt.dg_table.select_cell_for_edit_cbk = function( evt, bvr )
{
    var element = bvr.src_el;
    //var col = bvr.col;
    //var row = bvr.row;
    var col = element.getAttribute("spt_col");
    var row = element.getAttribute("spt_row");

    var table = element.getParent(".spt_table");

    spt.dg_table.edit.widget_select_clicks ++;

    if (spt.dg_table.edit.widget && col == spt.dg_table.edit.col && row == spt.dg_table.edit.row) {
        return null;
    }

    // First check to see if there is already an edit widget open and if so then return it to its
    // home cell ...
    //
    if( spt.dg_table.edit.widget != null ) {
        spt.dg_table.return_last_edit_wdg();
    }

    var type = element.getAttribute("spt_input_type");
    var element_name = element.getAttribute( 'spt_element_name' );

    if (type == 'upload')
    {
        var edit_wdg = spt.dg_table.adopt_preview_edit_wdg( table, element );
        //edit_wdg.setStyle( "min-height", '100px');
        //edit_wdg.setStyle( "min-width", '200px');
        return edit_wdg;
    }

    // Store the row and column numbers for this cell that is being edited ...
    spt.dg_table.edit.col = col;
    spt.dg_table.edit.row = row;

    // Now grab the edit widget from the home cell of the given column for the cell that is now
    // going to be edited ...
    //
    var edit_wdg = spt.dg_table.adopt_edit_wdg( table, element );
    /* if not edit_wdg exit */
    if (!edit_wdg)
        return;


    var value = element.getAttribute('spt_input_value');
    var input = spt.api.Utility.set_input_values(edit_wdg, value);
    if (input && input.type !='checkbox') {
        input.setStyle("width", "100%");
        input.setStyle("height", "100%");
    }
    if (['datetime','date'].contains(type)){
        if (value && value.test( /^\d\d\d\d-\d\d-\d\d .*/ ) ) {
            var parts = value.split(" ");
            var date_values = parts[0].split('-');
            var time_values = parts[1].split(':');
            var hour = spt.api.Utility.set_input_values(edit_wdg, time_values[0], '.spt_time_hour');
            spt.api.Utility.set_input_values(edit_wdg, time_values[1], '.spt_time_minute');

            var cal = edit_wdg.getElement('.spt_calendar_top');
            if (cal)
                spt.panel.refresh(cal, {year: date_values[0], month: date_values[1]});
        }

    }

    // check if the last value was not valid ...
    var input_el = edit_wdg.getElement("input");
    if( ! input_el ) {
        input_el = edit_wdg.getElement("textarea");
    }
    if( input_el ) {
        var td = input_el.getParent('td');
        if( td.hasClass("spt_input_validation_failed") ) {
            spt.css.add_looks("input_validation_failed", input_el);
        } else {
            spt.css.remove_looks("input_validation_failed", input_el);
        }
    }
    edit_wdg.cell_to_edit = element;
    return edit_wdg;
}


spt.dg_table.safari_skip_on_blur_as_enter = false;

// return the last edit widget back to it's home
spt.dg_table.return_last_edit_wdg = function()
{

    // wdg_home_cell can be null for elements that do not have have a separate
    // widget for editing
    if (spt.dg_table.edit.wdg_home_cell == null) {
        return
    }


    // special case for upload widget
    if (spt.dg_table.preview_last_clone != null ) {
        spt.dg_table.preview_last_clone.setStyle("margin-left", "-5000px");
        spt.dg_table.preview_last_clone = null;
        return;
    }



    var td = spt.dg_table.edit.widget.getParent(".spt_table_td");
    if (!td || td.hasClass('spt_input_inline')) {
        return;
    }



    spt.dg_table.edit.widget.parentNode.removeChild( spt.dg_table.edit.widget );

    var children = document.id(spt.dg_table.edit.wdg_home_cell).getChildren();
    var child = children[spt.dg_table.edit.wdg_home_index];
    if (child != null) {
        spt.dg_table.edit.wdg_home_cell.insertBefore( spt.dg_table.edit.widget, child );
    }
    else {
        spt.dg_table.edit.wdg_home_cell.appendChild( spt.dg_table.edit.widget );
    }


    spt.dg_table.edit.widget = null;
    spt.dg_table.edit.wdg_home_cell = null;
    spt.dg_table.edit.col = -1;
    spt.dg_table.edit.row = -1;
    spt.dg_table.edit.widget_select_clicks = 0;


    // Make sure keyboard handler stack is cleared also, otherwise odd behavior
    // will occur in some circumstances
    spt.kbd.clear_handler_stack();
}



// FIXME: this is pretty specific to preview widget.  This is a first stab
// at trying to do an element specific edit widget
spt.dg_table.preview_last_clone = null;

spt.dg_table.adopt_preview_edit_wdg = function( table_id, cell_to_edit )
{
    var element_name = cell_to_edit.getAttribute( 'spt_element_name' );
    var table = document.id(table_id);
    var tbody = cell_to_edit.getParent( '.spt_table_tbody' );
    var search_key = tbody.getAttribute("spt_search_key");


    // find all of the uploads
    var exists = false;

    // find out if this element exists yet
    var uploads = table.getElements(".spt_upload_top");
    var clone = null;
    for (var i = 0; i < uploads.length; i++) {
        var test_search_key = uploads[i].getAttribute("spt_search_key");
        if (test_search_key == search_key) {
            exists = true;
            clone = uploads[i];
            break;
        }
    }
    // FIXME: this should be done in the the general selection of edit cells
    // set the last one offscreen
    if (spt.dg_table.preview_last_clone != null ) {
        spt.dg_table.preview_last_clone.setStyle("margin-left", "-5000px");
    }

    if ( exists) {
        clone.parentNode.setStyle("margin-left", "0px");

    }
    else {
        // get the second row
        var EDIT_ROW = 2;       // NOTE, the index is 2 because of the header
        var edit_row = table.getChildren()[EDIT_ROW];
        var edit_cells = edit_row.firstChild.getChildren();
        var edit_cell = null;
        var edit_wdg = null;
        var wdg_index = 0;

        for (var x =0; x<edit_cells.length;x++) {
            edit_cell = edit_cells[x];
            if (edit_cell.getAttribute("spt_element_name") == element_name) {
                edit_wdg = edit_cell.getChildren()[wdg_index];
                break;
            }
        }

        // hook the new one up ...
        clone = spt.behavior.clone(edit_wdg);

        cell_to_edit.insertBefore( clone, cell_to_edit.firstChild );

        clone_upload = cell_to_edit.getElement(".spt_upload_top");
        if (clone_upload)
            clone_upload.setAttribute("spt_search_key", search_key);
        /*
        // FIXME: hard coded
        // set the id so the that the swf can replace the current one
        var key = "preview|" + search_key;

        clone.setAttribute("id", key);
        var button = clone.getElement(".spt_upload_button");
        button.setAttribute("id", key+"Button");


        var context = clone_upload.getAttribute("spt_context")

        // create a new swf
        var settings = {
            'upload_complete_handler':  'spt.Upload.icon_complete',
            'file_queued_handler':  'spt.Upload.icon_file_queued'
        }
        //destroy it first to avoid Browse buttom disappearing in cases where it is shown and hidden due
        // to navigating to another link
        spt.Upload.set(key, null);
        upload = spt.Upload.get(key, {
            create: true,
            settings: settings,
            context: context
        } );
        */

    }

    var size = document.id(cell_to_edit).getSize();
    clone.setStyle( "height", size.y+'px');
    clone.setStyle( "width", size.x+'px');

    spt.dg_table.edit.widget = clone;
    spt.dg_table.preview_last_clone = clone;
    return clone
}

//set the process when the context is chosen for task page
spt.dg_table.set_process = function(bvr) {
    var value = bvr.src_el.value;
    //edit_wdg has a cell_to_edit attr
    var ele = bvr.src_el.getParent('.spt_input_option').cell_to_edit;
    if (!ele) return;

    var table = bvr.src_el.getParent('.spt_table');
    if (value) {
        var tmps = value.split('||');
        var process = tmps[0];

        var element_names = spt.dg_table.get_element_names(table);
        var process_index = -1;
        for (var i=0; i<element_names.length; i++) {
            if (element_names[i] == "process") {
                process_index = i;
                break;
            }
        }
        if (process_index != -1) {

            var tbody = ele.getParent(".spt_table_tbody");
            var tds = tbody.getElements(".spt_table_td");
            // FIXME: td index is not the same as process index!!!!
            var td = tds[process_index+1];
            td.setAttribute('spt_input_value', process);
        }
    }
}


// DEPRECATED
spt.dg_table.get_status_key = function(cell_to_edit, edit_cell) {

    alert("spt_dg_table.set_status_key() is deprecated");

    var task_pipeline = null;

    // first check to see if the process column is there
    var table = cell_to_edit.getParent(".spt_table");
    var element_names = spt.dg_table.get_element_names(table);
    var process_index = -1;
    for (var i=0; i<element_names.length; i++) {
        if (element_names[i] == "process") {
            process_index = i;
            break;
        }
    }

    if (process_index != -1) {
        var layout = cell_to_edit.getParent(".spt_layout");

        var process;
        if (layout.getAttribute("spt_version") == "2") {
            spt.table.set_layout(layout);
            var row = cell_to_edit.getParent(".spt_table_row");
            var cells = row.getElements(".spt_cell_edit");
            /*
            for (var i = 0; i < cells.length; i++) {
                console.log(cells[i].getAttribute("spt_input_value"));
            }*/
            process = "model"

        }
        else {
            var tbody = cell_to_edit.getParent(".spt_table_tbody");
            var tds = tbody.getElements(".spt_table_td");

            // FIXME: td index is not the same as process index!!!!
            var td = tds[process_index+1];
            process = td.getAttribute('spt_input_value');
        }

        var parent_pipe_code = cell_to_edit.getAttribute('spt_parent_pipeline_code');

        var input_top = edit_cell.getElement('.spt_input_top');
        var mapping_str = input_top.getAttribute('spt_task_pipeline_mapping');
        var task_pipeline_mapping = spt.json_parse(mapping_str)
        var key = parent_pipe_code + '|' + process
        task_pipeline = task_pipeline_mapping[key];
    }

    // if the process has not changed, look at the set pipeline code
    if (task_pipeline == null) {
        task_pipeline = cell_to_edit.getAttribute("spt_pipeline_code");
    }

    // if everything is still null, use task
    if (task_pipeline == null) {
        task_pipeline = 'task';
    }
    return task_pipeline;
}


// DEPRPECATED
spt.dg_table.adopt_edit_wdg = function( table_id, cell_to_edit )
{

    alert("spt.dg_table.adopt_edit_wdg is DEPRECATED")

    var element_name = cell_to_edit.getAttribute( 'spt_element_name' );
    // get the second row
    var table = document.id(table_id);
    var EDIT_ROW = 2;       // NOTE, the index is 2 because of the header
    var edit_row = table.getChildren()[EDIT_ROW];
    var edit_cells = edit_row.firstChild.getChildren();
    var edit_cell = null;
    var edit_wdg = null;
    var wdg_index = 0;


    var home_edit_cell = null;
    for (var x =0; x<edit_cells.length;x++) {
        edit_cell = edit_cells[x];
        if (edit_cell.getAttribute("spt_element_name") != element_name) {
            continue;
        }


        var edit_wdg_options = edit_cell.getElements('.spt_input_option');


        // Figure out what element to use for editing
        //
        var element_script = edit_cell.getAttribute("spt_edit_script");

        // create one from scratch
        if (element_script != null) {
            //cell_to_edit.setStyle("background-color", "yellow");

            var get_edit_wdg_code = element_script;
            var get_edit_wdg_script = spt.CustomProject.get_script(get_edit_wdg_code);
            // FIXME: this is not the way to do this.  In this case, a specific
            // function as to be created.  This function should be build
            // around the custom code.
            eval(get_edit_wdg_script);
            edit_wdg = get_edit_wdg(cell_to_edit, element_name);
            home_edit_cell = edit_cell;
        }





        //edit_wdg = edit_cell.getChildren()[wdg_index];
        else if (edit_wdg_options.length == 0) {
            var type = cell_to_edit.getAttribute("spt_input_type");
            if (type == 'inline')
                return null;
            home_edit_cell = edit_cell;
            edit_wdg = edit_cell.getChildren()[wdg_index];
        }
        else {
            home_edit_cell = edit_wdg_options[0].parentNode;

            var key = null;

            //some edit definition has specific depend attr,
            var top_wdg = edit_cell.getElement(".spt_input_top");
            var cbjs_get_key = null;
            if (top_wdg) {
                cbjs_get_key = top_wdg.getAttribute("spt_cbjs_get_input_key");
            }
            if (cbjs_get_key != null) {
                eval("key_callback = function() { " + cbjs_get_key + " }");
                key = key_callback();
            }
            if (! key)
                key = cell_to_edit.getAttribute("spt_input_value");



            // find the key
            var found = false;
            for (var y =0; y<edit_wdg_options.length;y++) {
                edit_wdg = edit_wdg_options[y];
                var input_key = edit_wdg.getAttribute("spt_input_key");
                if (input_key == key) {
                    found = true;
                    wdg_index = y;
                    break;
                }
            }
            if (!found) {
                wdg_index = 0;
                edit_wdg = edit_wdg_options[0];
            }
        }
        break;
    }


    if (home_edit_cell == null) {
        home_edit_cell = edit_cell;
    }
    if (edit_wdg == null || home_edit_cell == null) {
        spt.js_log.debug( "**************************************************" );
        if( edit_wdg == null ) { spt.js_log.debug( "WARNING: edit_wdg is NULL!" ); }
        if( home_edit_cell == null ) { spt.js_log.debug( "WARNING: home_edit_cell is NULL!" ); }
        spt.js_log.debug( "**************************************************" );
        return null;
    }
    edit_wdg.setStyle( 'padding', '0px' );
    edit_wdg.setStyle( 'margin', '0px' );
    edit_wdg.setStyle( 'z-index', '100' );

    // get the size of the cell elemnt and make the edit_wdg the same size
    var size = document.id(cell_to_edit).getSize();

    var set_focus = false;
    //var type = cell_to_edit.getAttribute("spt_input_type");
    var type = edit_cell.getAttribute("spt_input_type");
    var input = edit_wdg.getElement(".spt_input");

    /*
    if (type == 'upload') {
        set_focus = true;
        edit_wdg.setStyle( "min-height", '300px');
        edit_wdg.setStyle( "min-width", '300px');
        edit_wdg.setStyle( "border", 'solid 1px blue');
    }
    */
    if (input != null && input.hasClass("SPT_NO_RESIZE") ) {
        // do nothing
    }
    else if (input != null && input.nodeName == "SELECT") {

        // Set the size of the SELECT element to be the length of all the options available ...
        var select_size_to_set = input.options.length;
        var select_opt_value = cell_to_edit.getAttribute("spt_input_value");

        // Go through and be sure to set the default option to the one with the value matching the
        // spt_input_value of the cell you are editing ...
        if( select_opt_value == "[]" ) {
            select_opt_value = "";
        }
        var option_list = document.id(input).getElements("option");
        for( var opt_c=0; opt_c < option_list.length; opt_c++ ) {
            var opt_el = option_list[opt_c];
            var opt_value = opt_el.getProperty("value");
            var opt_selected = opt_el.getProperty("selected");
            if( opt_selected && (select_opt_value != opt_value) ) {
                opt_el.removeProperty("selected");
            }
            else if( !opt_selected && (select_opt_value == opt_value) ) {
                opt_el.setProperty("selected", "selected");
            }
        }

        // However, if the configuration specified a certain size for the SELECT in configuration
        // then use the size specified ...
        var spt_size = document.id(input).getProperty("spt_select_size");
        if( spt_size ) {
            select_size_to_set = parseInt( spt_size );
        }

        set_focus = true;
        edit_wdg.setStyle("position", "absolute");

        if( input.options.length > select_size_to_set ) {
            // only set to the configured select element size if actual number of options is larger
            input.size = select_size_to_set;
        } else {
            input.size = input.options.length;
        }

        mult = 15;
        if( spt.browser.is_IE() ) {
            if (size.y < (input.size * mult)) {
                edit_wdg.setStyle( "height", (input.size * mult) + 'px');
            }
            else {
                edit_wdg.setStyle( "height", size.y+'px');
            }
        }
    }
    // for now put a special case here so that it's even possible to edit
    // xml
    else if (input != null && input.nodeName == "TEXTAREA") {
        set_focus = true;

        if (type == 'xml') {
            edit_wdg.setStyle( "min-height", '300px');
            edit_wdg.setStyle( "min-width", '300px');
        }
        if (size.y > 100)
            edit_wdg.setStyle( "height", size.y+'px');
        else
            edit_wdg.setStyle( "height", '100px');

        if (size.x > 250)
            edit_wdg.setStyle( "width", size.x+'px');
        else
            edit_wdg.setStyle( "width", '250px');
        input.setStyle('font-family', 'Courier New');

        // TODO: make TEXTAREA edit cell RESIZABLE ...
        //edit_wdg.makeResizable({handle:edit_wdg});
        // // handle should be icon outside of widget
    }
    else if (input != null && input.type == "checkbox") {
        var cell_value = cell_to_edit.getAttribute('spt_input_value');
        if (cell_value in  {'True':1, 'true':1})
            input.checked = true;
        else
            input.checked = false;
        edit_wdg.setStyle( "width", size.x+'px');
        edit_wdg.setStyle( "height", size.y+'px');
        edit_wdg.setStyle( "text-align", 'center');
    }
    else if (input != null && input.nodeName == "INPUT") {
        set_focus = true;
        edit_wdg.setStyle( "width", size.x+'px');
        edit_wdg.setStyle( "height", size.y+'px');
    }
    else {
        edit_wdg.setStyle( "width", size.x+'px');
        edit_wdg.setStyle( "height", size.y+'px');

    }


    // hook the new one up ...
    spt.dg_table.edit.wdg_home_cell = home_edit_cell;
    spt.dg_table.edit.wdg_home_index = wdg_index;
    spt.dg_table.edit.widget = edit_wdg;
    //home_edit_cell.removeChild( edit_wdg );
    cell_to_edit.insertBefore( edit_wdg, cell_to_edit.firstChild );

    //cell_to_edit.replaceChild( edit_wdg, cell_to_edit.firstChild );

    // Need to ensure that the INPUT element gets focus (for keyboard handler)
    if (set_focus) {
        input.focus();
    }

    // remember the original value
    spt.dg_table.edit.orig_cell_value = cell_to_edit.getAttribute('spt_input_value');
    return edit_wdg;
}



// DO not use 'onchange' event for SELECT input as it has no idea of whether a change occurred from keyboard
// input or by mouse click. Instead use "click" behavior on SELECT element to process mouse clicks (keyboard
// handler will deal with key input) ...
// TODO: pass in bvr so the caller can specify what value to reject
spt.dg_table.select_wdg_clicked = function( evt, select_el )
{
    var select_value = select_el.value;
    var target = spt.get_event_target( evt );
    var new_value = target.value;
    // if offsetWidth > clientWidth, it's just clicking on the scrollbar
    // FIXME: only works in FF, but IE does not need it

    if (spt.browser.is_Firefox() &&
        target.offsetWidth > spt.get_render_display_width(target)) {
        return;
    }
    if ( new_value == '[label]') {
        spt.alert('A label was selected. Please choose a valid value.');
        spt.dg_table.edit_cell_cbk( select_el, spt.kbd.special_keys_map.ESC );
    }
    if( new_value == select_value ) {
        spt.dg_table.edit_cell_cbk( select_el, spt.kbd.special_keys_map.ESC );
    } else {
        // need to set SELECT element value here, because this call occurs before the 'onchange' event
        select_el.value = new_value;
        spt.dg_table.edit_cell_cbk( select_el, spt.kbd.special_keys_map.ENTER );
    }
}


// New edit cell callback ...
//
spt.dg_table.edit_cell_cbk = function( element, key_code )
{
    element = document.id(element);
    // ESC key
    if (key_code == spt.kbd.special_keys_map.ESC) {
        if( spt.browser.is_Safari() || spt.browser.is_Chrome() ) { spt.dg_table.safari_skip_on_blur_as_enter = true; }
        if (spt.dg_table.edit.widget != null) {
            spt.dg_table.return_last_edit_wdg();
        }
    }
    else if (key_code == spt.kbd.special_keys_map.ENTER)
    {
        if( spt.browser.is_Safari() || spt.browser.is_Chrome() ) {
            if( spt.dg_table.safari_skip_on_blur_as_enter ) {
                spt.dg_table.safari_skip_on_blur_as_enter = false;
                return;
            } else {
                spt.dg_table.safari_skip_on_blur_as_enter = true;
            }
        }

        // this means that we have received this callback from something other than ESC ...
        // meaning that it is either "ENTER" or some "click-off" activity. For "click-off" the behavior is to accept
        // the edit, to provide a fast workflow for a user needing to do multiple edits quickly across various cells
        // of the dg_table. Of course for "ENTER" we also accept the edit.

        var table = element.getParent(".spt_table");
        var search_keys = spt.dg_table.get_selected_search_keys(table);

        if (spt.dg_table.edit.widget == null) {
            return;
        }
        else
        {
            var Utility = spt.api.Utility;
            var values = Utility.get_input_values(spt.dg_table.edit.widget, null, false);
            var labels = Utility.get_input_values(spt.dg_table.edit.widget, null, false, true);


            // now get it's parent td ...
            var td = element.getParent('.spt_table_td');
            if( td )
            {
                var spt_input_column = td.get("spt_input_column");
                var td_is_selected = false;

                selected_row_list = spt.dg_table.get_selected( table );
                selected_list = [];
                if( selected_row_list && selected_row_list.length ) {
                    for( var c=0; c < selected_row_list.length; c++ ) {
                        var sel_row = selected_row_list[c];
                        var row_td_list = sel_row.getElements("td");
                        var sel_td = null;
                        for( var t=0; t < row_td_list.length; t++ ) {
                            var row_td = row_td_list[t];
                            if( row_td.get("spt_input_column") == spt_input_column ) {
                                sel_td = row_td;
                                if( sel_td == td ) {
                                    td_is_selected = true;
                                }
                                break;
                            }
                        }
                        //collect the selected td, row
                        selected_list.push( { 'td': sel_td, 'row': sel_row } );
                    }
                }

                if( td_is_selected ) {
                    // if the edit occurs in a row that is selected then do multiple edit cells
                    for( var c=0; c < selected_list.length; c++ ) {
                        var sel_td = selected_list[c]['td'];
                        var sel_row = selected_list[c]['row'];
                        var is_orig_edit_td = false;
                        if( sel_td == td ) {
                            is_orig_edit_td = true;
                        }
                        spt.dg_table.accept_single_edit_cell_td( element, sel_td, sel_row, values, labels,
                                                                 is_orig_edit_td );
                    }
                }
                else {
                    // otherwise just do single edit ...
                    var row = td.getParent("tr");
                    spt.dg_table.accept_single_edit_cell_td( element, td, row, values, labels, true );
                }
            }
            else {
                spt.dg_table.return_last_edit_wdg();
            }
        }

    }
}




// This function is a wrapper for simplifying the process of setting
// an input value in the dg_table has having changed.  It assumes
// that there is a real input element with a class of "spt_input_data"
// which stores all of the data packaged up from the rest of the
// custom element.  Generally the UI would store a json string in this
// element, which would then be sent back to the server
spt.dg_table.simple_edit_cell_cbk = function( top_el ) {
    var value_wdg = top_el.getElement(".spt_input_data");
    //var values = spt.api.Utility.get_input_values(top_el);
    //values = JSON.stringify(values);
    //value_wdg.value = values;

    spt.dg_table.edit.widget = top_el;
    spt.dg_table.inline_edit_cell_cbk( value_wdg );
}


// This is specific to cells that have inline editing.  It doesn't have the
// need to return the edit cell back to the original location, so it is
// much simpler
//
spt.dg_table.inline_edit_cell_cbk = function( element, cached_data ) {
    if (typeof(cached_data) == 'undefined') {
        cached_data = {};
    }


    var table = element.getParent(".spt_table");

    if (spt.dg_table.edit.widget == null) {
        return;
    }

    // now get the parent cell
    var td = element.getParent('.spt_table_td');
    if ( td == null) {
        return;
    }



    // get the values for this widget
    var Utility = spt.api.Utility;
    var values = Utility.get_input_values(spt.dg_table.edit.widget, null, false);
    var labels = Utility.get_input_values(spt.dg_table.edit.widget, null, null, true);

    if (cached_data['multi'] == false) {
        // otherwise just do single edit if it is handled elsewhere
        var row = td.getParent("tr");
        spt.dg_table.accept_single_edit_cell_td( element, td, row, values, labels, true );
        return;
    }


    var spt_input_column = td.get("spt_input_column");

    var td_is_selected = false;

    var selected_row_list = cached_data['selected_rows'];
    if (typeof(selected_row_list) == 'undefined') {
        selected_row_list = spt.dg_table.get_selected( table );
    }


    selected_list = [];
    if( selected_row_list && selected_row_list.length ) {
        for( var c=0; c < selected_row_list.length; c++ ) {
            var sel_row = selected_row_list[c];
            var row_td_list = sel_row.getElements("td");
            var sel_td = null;
            for( var t=0; t < row_td_list.length; t++ ) {
                var row_td = row_td_list[t];
                if( row_td.get("spt_input_column") == spt_input_column ) {
                    sel_td = row_td;
                    if( sel_td == td ) {
                        td_is_selected = true;
                    }
                    break;
                }
            }
            selected_list.push( { 'td': sel_td, 'row': sel_row } );
        }
    }


    if( td_is_selected ) {
        // if the edit occurs in a row that is selected then do multiple edit cells
        for( var c=0; c < selected_list.length; c++ ) {
            var sel_td = selected_list[c]['td'];
            var sel_row = selected_list[c]['row'];
            var is_orig_edit_td = false;
            if( sel_td == td ) {
                is_orig_edit_td = true;
            }
            spt.dg_table.accept_single_edit_cell_td( element, sel_td, sel_row, values, labels,
                                                     is_orig_edit_td );
        }
    }
    else {
        // otherwise just do single edit ...
        var row = td.getParent("tr");
        spt.dg_table.accept_single_edit_cell_td( element, td, row, values, labels, true );
    }

}


spt.dg_table.accept_single_edit_cell_td = function( element, td, row, values, labels, is_orig_edit_td )
{
    // var row = td.getParent("tr");
    var search_key = row.getAttribute("spt_search_key");

    // get the value
    var element_name = td.getAttribute("spt_element_name");
    values['element_name'] = element_name;


    // Get rid of last clone at this point ...
    if( is_orig_edit_td && !td.hasClass('spt_input_inline') ) {
        spt.dg_table.return_last_edit_wdg();
    }

    // COMPARE edit accepted value with original cell's pre-edit value
    // ... if the value is the same, then do not set anything
    if( values[element_name] == spt.dg_table.edit.orig_cell_value ) {
        return;
    }

    var tbody = td.getParent(".spt_table_tbody");

    // set the value of the cell and mark that this value
    // has changed
    td.setAttribute("spt_input_value", values[element_name]);


    // Check for any validations that need to be run on this value change ...
    //
    var new_value = values[element_name];
    var table_wrapper_div = td.getParent(".spt_table_wrapper_div");
    var table_validations_div = table_wrapper_div.getElement(".spt_table_validations");

    var cls_tag = "spt_validation_" + element_name

    var validation_div = table_validations_div.getElement( "." + cls_tag );
    if( validation_div ) {
        var v_bvr_list = spt.behavior.get_bvrs_by_type( "validation", validation_div );
        spt.validation.check( new_value, v_bvr_list, td );

        // in case we need to have the validation revise the value at all (e.g. to make upper case, etc.)
        // we check for the flag to let us push the change, and if so we push the revised value back into
        // the values and labels dicts ...
        if( '_spt_push_new_value_to_label' in td ) {
            values[element_name] = td.getAttribute("spt_input_value");
            labels[element_name] = td.getAttribute("spt_input_value");
        }
    }


    // TEST: store a cookie of the value
    /*
    var key = search_key + "|" + element_name;
    var cookie = new Cookie('session_value');
    var cookie_value = cookie.read();
    if (cookie_value == null) {
        cookie_data = {};
    }
    else {
        cookie_data = JSON.parse(cookie_value);
    }
    cookie_data[key] = values[element_name];
    cookie_value = JSON.stringify(cookie_data);
    cookie.write(cookie_value);
    spt.alert(cookie_value.length)
    var test = cookie.read();
    spt.alert(test.length)
    */


    tbody.addClass("spt_value_changed");
    td.addClass("spt_value_changed");


    // put the value back in
    //
    var type = td.getAttribute("spt_input_type");
    if (type == 'timestamp' || type == 'date') {
        var value = "" + values[element_name];
        if( value && value.match( /^\d\d\d\d-\d\d-\d\d$/ ) ) {
            var parts = value.split("-");
            var date_obj = new Date();
            date_obj.setFullYear(parts[0], (parts[1]-1), parts[2]);

            var year = date_obj.getFullYear();
            var month = spt.gantt.months[date_obj.getMonth()].substr(0,3);
            var day = date_obj.getDate();
            var label = month + " " + day + ", " + date_obj.getFullYear();
            td.innerHTML = "<div style='padding: 3px'>"+label+"</div>";
        }
    }
    if (['gantt', 'inline','work_hour'].contains(type)) {
        // do nothing.  These inputs are inline and do not need anything
        // replaced.
    }
    else {
        var value = "" + values[element_name];
        var label = "" + labels[element_name];
        var is_xml = label.substr(0,6) == '<?xml ';

        label = label.replace(/</g, "&lt;");
        label = label.replace(/>/g, "&gt;");

        if (is_xml == true) {
            td.innerHTML = "<pre>" + label + "</pre>";
        }
        else if (value == '') {
            td.innerHTML = "<div style='padding: 3px'>&nbsp;</div>";
        }
        else {
            label = label.replace(/\n/g, "<br/>");
            td.innerHTML = "<div style='padding: 3px'>"+label+"</div>";
        }
    }


    // change the colors to indicate changes have been made
    // @@@
    /*
    td.setStyle("background-color", "#131");
    row.setStyle("background-color", "#020");
    */
    var td_look = "dg_field_value_changed";

    // DO VALIDATION HERE!
    var remove_td_look = "input_validation_failed";
    if( td.hasClass("spt_input_validation_failed") )
    {
        td_look = "input_validation_failed";
        remove_td_look = "dg_field_value_changed";
        td.addClass("tactic_tip");
        td.setProperty("title", td.getProperty("spt_validation_failed_msg"));
    } else {
        td.removeClass("tactic_tip");
        td.removeProperty("title");
    }


    var resize_td = spt.find_closest_sibling_by_tag(td, 'next', 'td', null)


    spt.css.add_looks( td_look, td );
    spt.css.remove_looks( remove_td_look, td );
    if( resize_td ) {
        spt.css.add_looks( td_look, resize_td );
        spt.css.remove_looks( remove_td_look, resize_td );
    }
    spt.css.add_looks( "dg_row_value_changed", row );
    //td.setStyle("background", "green")
    //row.setStyle("background", "green")


    // make the commit button appear, but if validation failed then hide commit button ...
    var table = tbody.getParent(".spt_table");
    var failed_list = table.getElements(".spt_input_validation_failed");
    if( failed_list.length ) {
        spt.dg_table._toggle_commit_btn( td, true );   // hide = true (meaning do not display commit btn)
    } else {
        spt.dg_table._toggle_commit_btn( td, false );  // hide = false (meaning display commit btn)
    }


    // send out a named event
    if( is_orig_edit_td )
    {
        // Only send out the named event from the original td edit cell
        var search_key = tbody.getAttribute("spt_search_key")
        var event_name = 'change|' + search_key + '|' + element_name;
        spt.js_log.debug("Calling event: " + event_name);
        var bvr = {
            'src_el': element,
            'options': {
                search_key: search_key,
                element_name: element_name,
                value: values[element_name]
            }
        };
        spt.named_events.fire_event(event_name, bvr);
    }
}



spt.dg_table.get_new_kbd_edit_cell_on_tab = function( cur_cell_td, shift_key_mod )
{
    var get_sibling_fn = null;
    var tbody_start_pos = '';

    if( shift_key_mod ) {
        get_sibling_fn = spt.get_prev_same_sibling;
        tbody_start_pos = 'end';
    } else {
        get_sibling_fn = spt.get_next_same_sibling;
        tbody_start_pos = 'start';
    }

    var done = false;
    var new_edit_cel = null;

    while( ! done ) {
        var cur_row_tbody = spt.get_parent( cur_cell_td, ".spt_table_tbody" );
        var cur_edit_tr = spt.get_cousin( cur_cell_td, ".spt_table", ".spt_edit_row" );
        var cur_edit_td_list = cur_edit_tr.getElements( ".spt_table_td" );

        new_edit_cell = get_sibling_fn( cur_cell_td, "spt_table_td" );

        if( new_edit_cell ) {
            // validate ...
            var prev_siblings = spt.get_prev_same_siblings( new_edit_cell, "spt_table_td" );
            var idx = prev_siblings.length;

            var cur_edit_td = cur_edit_td_list[idx];
            var div_wrapper = cur_edit_td.getElement("div");
            if( ! div_wrapper ) {
                cur_cell_td   = new_edit_cell;
                new_edit_cell = null;
                continue;
            }
            var edit_el = div_wrapper.firstChild;
            if( ! edit_el ) {
                cur_cell_td   = new_edit_cell;
                new_edit_cell = null;
                continue;
            }

            var el_tag = edit_el.tagName.toLowerCase();
            if( "input textarea select".contains_word(el_tag) ) {
                if( el_tag == "input" ) {
                    if( edit_el.getProperty("type") != "text" ) {
                        cur_cell_td   = new_edit_cell;
                        new_edit_cell = null;
                        continue;
                    }
                }
            }
            else {
                cur_cell_td   = new_edit_cell;
                new_edit_cell = null;
                continue;
            }
        }
        else {
            // if not new_edit_cell then go to next tbody ...
            new_row_tbody = get_sibling_fn( cur_row_tbody, "spt_table_tbody" );
            if( new_row_tbody ) {
                if( new_row_tbody.hasClass( "spt_edit_tbody" ) || new_row_tbody.hasClass( "spt_insert_tbody" ) ) {
                    // otherwise, no more stuff to look through ...
                    return null;
                }
                var cur_td_list = new_row_tbody.getElements( ".spt_table_td" );
                if( tbody_start_pos == 'start' ) {
                    cur_cell_td = cur_td_list[0];
                } else {
                    cur_cell_td = cur_td_list[ cur_td_list.length - 1 ];
                }
            } else {
                // otherwise, no more stuff to look through ...
                return null;
            }
        }

        if( new_edit_cell ) {
            done = true;
        }
    }

    return new_edit_cell;
}



// DG Table utility functions ...

spt.dg_table.parse_search_key = function( search_key_str )
{
    var bits = search_key_str.split( "?" );
    var search_key_info = {};
    search_key_info['search_type'] = bits[0];

    bits = bits[1].split( "&" );
    for( var b=0; b < bits.length; b++ ) {
        if( bits[b].contains('=') ) {
            var mo_bits = bits[b].split('=');
            search_key_info[ mo_bits[0] ] = mo_bits[1];
        }
    }

    return search_key_info;
}


spt.dg_table.get_show_retired_flag = function( table_child_el )
{
    var el = spt.get_cousin( table_child_el, ".spt_view_panel", ".spt_search_show_retired" );
    if (!el)
        el = spt.get_cousin( table_child_el, ".spt_layout", ".spt_search_show_retired" );
    if (!el) return false;

    return spt.is_TRUE(el.value);
}


spt.dg_table.enable_show_retired = function( table_child_el )
{
    var el = spt.get_cousin( table_child_el, ".spt_view_panel", ".spt_search_show_retired" );
    el.value = "true";
    spt.dg_table.search_cbk( {}, {'src_el': el} );
}


spt.dg_table.disable_show_retired = function( table_child_el )
{
    var el = spt.get_cousin( table_child_el, ".spt_view_panel", ".spt_search_show_retired" );
    el.value = "";
    spt.dg_table.search_cbk( {}, {'src_el': el} );
}


// --------------------------------------------------------------------------------------------------------------
// SMART MENU function call-backs for DG Table "Gear Menu" drop down ...
// --------------------------------------------------------------------------------------------------------------

//
// Call-back to handle:
//
//     Gear Menu -> File -> Import CSV ...
//
spt.dg_table.gear_smenu_import_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table' )
    var search_type = table.get("spt_search_type");

    var tmp_bvr = {};
    tmp_bvr.args = {
        'search_type': search_type
    };

    var title = 'Import CSV';
    tmp_bvr.options = {
        'title': title,
        'class_name': 'tactic.ui.widget.CsvImportWdg',
        'popup_id': title
    };

    spt.popup.get_widget( evt, tmp_bvr );
}


//
// Call-back handling both:
//
//     Gear Menu -> File -> Export All ...
//     Gear Menu -> File -> Export Selected ...
//
spt.dg_table.gear_smenu_export_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var table = spt.get_cousin( activator, '.spt_table_top', '.spt_table' );

    var layout = activator.getParent(".spt_layout");


    var version = layout.getAttribute("spt_version");
    version = parseInt(version);

    var search_type = table.get("spt_search_type");
    var view = table.get("spt_view");
    var search_values_dict;
    if (version == 2) {
        spt.table.set_layout(layout);
        var header = spt.table.get_header_row();
        // include header input for widget specific settings
        var header_inputs = spt.api.Utility.get_input_values(header, null, false);
        search_values_dict = header_inputs;
    }
    else {
        spt.alert('You are viewing an old table layout. If you want to benefit from better features of the Fast Table Layout, please switch it in Manage Side Bar.');
    }
    var element_names = version == 2 ? spt.table.get_element_names() : [];
    var search_class = table.get("spt_search_class") || "";

    var tmp_bvr = {};




    var search_view;
    // init the args to be passed to CsvExportWdg
    tmp_bvr.args = {
        'table_id': table.get('id'),
        'search_type': search_type,
        'selected_search_keys': '',
        'view': view,
        'element_names': element_names,
        'search_class': search_class,
        'mode': bvr.mode,
        'search_view': search_view
    };

    var title = '';
    var sel_search_keys = [];
    if( bvr.mode=='export_all' ) {
        tmp_bvr.args.is_export_all = true;
        title = 'Export All items from "' + search_type + '" list ';
    }
    else if (bvr.mode=='export_matched') {
        title = 'Export Matched items from "' + search_type + '" list ';
        var top = table.getParent(".spt_view_panel");

        var search_wdg;
        if (top) {
            search_wdg = top.getElement(".spt_search");
            var matched_search_type = search_type == top.getAttribute('spt_search_type');
            var simple_search_view  = top.getAttribute('spt_simple_search_view');
            search_view = search_wdg.getAttribute("spt_view");
            tmp_bvr.args.search_view = search_view;
            tmp_bvr.args.simple_search_view = simple_search_view;
        }
        if (!top || !search_wdg || !matched_search_type) {
            spt.alert('The search box is not found. Please use "Export Selected, Export Displayed" instead')
            return;
        }
        var search_values = spt.dg_table.get_search_values(search_wdg);
        search_values_dict['json'] = search_values;

        }
    else if (bvr.mode=='export_displayed') {
        title = 'Export displayed items from "' + search_type + '" list ';
        css = (version == 2) ?  '.spt_table_row':  '.spt_table_tbody';
        var tbodies = table.getElements(css);
        for (var k=0; k < tbodies.length; k++) {
            if (tbodies[k].getStyle('display') == 'none'){
                continue;
            }
            var sk = tbodies[k].getAttribute('spt_search_key');


            sel_search_keys.push(sk);
        }
        if( sel_search_keys.length == 0 ) {
            spt.alert('No rows displayed for exporting to CSV ... skipping "Export Displayed" action.');
            return;
        }
    }

    else {
        title = 'Export Selected items from "' + search_type + '" list ';
        if (version == 2)
            var selected_rows = spt.table.get_selected_rows();
        else
            var selected_rows = spt.dg_table.get_selected(table,  {'include_embedded_tables': true} );
        var sel_search_keys = [];

        related_views = []
        for (var c=0; c < selected_rows.length; c++) {
            search_key = selected_rows[c].getAttribute("spt_search_key");
            sel_search_keys.push(search_key);

            var parent_table = selected_rows[c].getParent('.spt_table');
            var parent_view = parent_table.getAttribute('spt_view');
            if (! related_views.contains(parent_view))
                related_views.push(parent_view);
        }

        //var sel_tr_list = spt.dg_table.get_selected( table.get('id') );
        if( sel_search_keys.length == 0 ) {
            spt.alert('No rows selected for exporting to CSV ... skipping "Export Selected" action.');
            return;
        }
        if (related_views.length > 1) {
            spt.alert('More than 1 type of item is selected ... skipping "Export Selected" action.');
            return;
        }
        tmp_bvr.args.related_view = related_views[0];
    }


    var view_name = '';
    var main_panel = activator.getParent('.spt_main_panel');
    /*
    if( main_panel ) {
        var bcrumb = main_panel.getParent('div').getElement('#breadcrumb');
        if (bcrumb.firstChild) {
            view_name = bcrumb.firstChild.nodeValue;
            title += 'in [' + view_name + '] view';
        }
        else {
             title += 'in [' + view + '] view';
        }
    }
    else {
        title += 'in [' + view + '] view';
    }
    */

    title += 'in [' + view + '] view';

    tmp_bvr.options = {
        'title': title + " to CSV",
        'class_name': 'tactic.ui.widget.CsvExportWdg',
        'popup_id' : 'Export CSV'
    };
    tmp_bvr.args.selected_search_keys = sel_search_keys;
    tmp_bvr.values = search_values_dict;


    var popup = spt.popup.get_widget( evt, tmp_bvr );
    // add the search_values_dict to the popup
    popup.values_dict = search_values_dict;

}


// --------------------------------------------------------------------------------------------------------------
// SMART MENU function call-backs for data row context menus ...
// --------------------------------------------------------------------------------------------------------------

//
// Smart menu setup for data row right click context menu ...
//
spt.dg_table.drow_smenu_setup_cbk = function( menu_el, activator_el )
{
    var commit_enabled = false;
    var commit_btn = spt.get_cousin( activator_el, '.spt_table_top', '.spt_table_commit_btn' );
    if (commit_btn)
        commit_enabled = spt.is_shown( commit_btn );

    // FIXME: below is a hack!  Need better place to see if row is retired (not look classes!) ...
    var row_is_retired = activator_el.hasClass('look_dg_row_retired');

    var tbody = activator_el.getParent('tbody');
    var display_label;
    if (tbody) {
        display_label = tbody.get("spt_display_value");
        if( ! display_label ) {
            spt.js_log.warning( "WARNING: [spt.dg_table.drow_smenu_setup_cbk] could not find 'spt_display_value' for item to " +
                            "delete ... using 'search_key' as display_label." );
            display_label = tbody.get("spt_search_key");
        }
    }
    else {
        display_label = "wow what a ride";
    }


    var setup_info = {
        'commit_enabled' : commit_enabled,
        'is_retired': row_is_retired,
        'is_not_retired': (! row_is_retired),
        'display_label': display_label
    }

    return setup_info;
}


//
// Data-row Context Menu: Retire row sobject
//
spt.dg_table.drow_smenu_retire_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var layout = activator.getParent(".spt_layout");
    if (layout.getAttribute("spt_version") == "2") {
        var row = activator;
        var search_key = row.get("spt_search_key");
        var api_key = row.getAttribute("SPT_RET_API_KEY");


        var server = TacticServerStub.get();
        server.set_api_key(api_key);
        var show_retired = spt.dg_table.get_show_retired_flag( row );
        var is_project = search_key.test('sthpw/project?') ? true : false;
        try {
            if( show_retired ) {
                server.retire_sobject(search_key);

                var func = function() { spt.table.expand_table(); };

                var kw =  {on_complete: func, refresh_bottom: false};
                spt.table.refresh_rows([row], null, null, kw);

                //spt.panel.refresh(row, {}, fade);
            } else {
                server.retire_sobject(search_key);
                on_complete = function() {spt.behavior.destroy_element(row);}
                spt.table.remove_hidden_row(row);
                Effects.fade_out(row, 500, on_complete);

            }
            server.clear_api_key();
            if (is_project)
                setTimeout("spt.panel.refresh('ProjectSelectWdg');", 2000);
        } catch(e) {
            spt.alert(spt.exception.handler(e));
        }


    }
    else {
        var tbody = activator.getParent('.spt_table_tbody');
        var search_key = tbody.get("spt_search_key");
        var api_key = tbody.getAttribute("SPT_RET_API_KEY");

        var server = TacticServerStub.get();
        server.set_api_key(api_key);
        var show_retired = spt.dg_table.get_show_retired_flag( tbody );
        try {
            if( show_retired ) {
                server.retire_sobject(search_key);
                var fade = false;
                spt.panel.refresh(tbody, {}, fade);
            } else {
                on_complete = "document.id(id).setStyle('display', 'none')";
                Effects.fade_out(tbody, 500, on_complete);
                server.retire_sobject(search_key);
            }
        } catch(e) {
            spt.alert(spt.exception.handler(e));
        }
        server.clear_api_key();
    }
}


//
// Data-row Context Menu: Reactivate row sobject
//
spt.dg_table.drow_smenu_reactivate_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var layout = activator.getParent(".spt_layout");
    if (layout.getAttribute("spt_version") == "2") {
        var row = activator;
        var search_key = row.get("spt_search_key");
        var api_key = row.getAttribute("SPT_REAC_API_KEY");

        var server = TacticServerStub.get();
        server.set_api_key(api_key);
        server.reactivate_sobject(search_key);
        server.clear_api_key();
        var is_project = search_key.test('sthpw/project?') ? true : false;


        var kw = {on_complete: function() {spt.table.expand_table()}};
        on_complete = function() {
                        spt.table.refresh_rows([row], null, null, kw);
                        };
        if (is_project)
            on_complete = function() {
                spt.table.refresh_rows([row], null, null, kw);
                spt.panel.refresh('ProjectSelectWdg');}
        Effects.fade_out(row, 500, on_complete);
    }
    else {
        var tbody = activator.getParent('.spt_table_tbody');
        var search_key = tbody.get("spt_search_key");
        var api_key = tbody.getAttribute("SPT_REAC_API_KEY");

        var table = tbody.getParent(".spt_table");
        var element_names = spt.dg_table.get_element_names(table);
        var element_names_str = element_names.join(",");
        tbody.setAttribute("spt_element_names", element_names_str);

        var server = TacticServerStub.get();
        server.set_api_key(api_key);
        server.reactivate_sobject(search_key);
        server.clear_api_key();
        on_complete = "spt.panel.refresh(id)";
        Effects.fade_out(tbody, 500, on_complete);
    }
}



//
// Data-row Context Menu: DELETE row sobject
//
spt.dg_table.drow_smenu_delete_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var layout = activator.getParent(".spt_layout");
    var tbody;
    if (layout.getAttribute("spt_version") == "2") {
        tbody = activator;
    }
    else {
        tbody = activator.getParent('.spt_table_tbody');
    }

    var search_key = tbody.get("spt_search_key");
    var search_key_info = spt.dg_table.parse_search_key( search_key );
    var search_type = search_key_info.search_type;


    // open delete popup
    var class_name;
    if (search_type == "sthpw/search_type") {
        class_name = 'tactic.ui.tools.DeleteSearchTypeToolWdg';
    }
    else if (search_type == "sthpw/project") {
        class_name = 'tactic.ui.tools.DeleteProjectToolWdg';
    }
    else {
        class_name = 'tactic.ui.tools.DeleteToolWdg';
    }
    var kwargs = {
      search_key: search_key,
    }
    var popup = spt.panel.load_popup("Delete Item", class_name, kwargs);

    var on_post_delete = function() {
        var on_complete = "document.id(id).setStyle('display', 'none')";
        if (layout.getAttribute("spt_version") == "2") {
            spt.table.remove_hidden_row(activator);
        }
        Effects.fade_out(tbody, 500, on_complete);
        spt.named_events.fire_event("delete|" + search_type, {})
    }

    popup.spt_on_post_delete = on_post_delete;

    return;

}


//
// Data-row Context Menu: Item Audit Log for row sobject
//
spt.dg_table.drow_smenu_item_audit_log_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);

    var row = spt.has_class(activator, 'spt_table_row') ? activator : activator.getParent('.spt_table_row')

    var search_key = row.get("spt_search_key");
    var search_key_info = spt.dg_table.parse_search_key( search_key );

    var display_label = row.get("spt_display_value");
    if( ! display_label ) {
        spt.js_log.warning( "WARNING: [spt.dg_table.drow_smenu_item_audit_log_cbk] could not find 'spt_display_value' for " +
                        "item to delete ... using 'search_key' as display_label." );
        display_label = search_key;
    }

    var tmp_bvr = {};
    tmp_bvr.args = {
        'search_type': 'sthpw/sobject_log',
        'parent_key': search_key,
        'view': 'item'
    };

    tmp_bvr.options = {
        'title': ('Item Audit Log for "' + search_key_info.search_type + '" labeled "' + display_label + '"'),
        'class_name': 'tactic.ui.panel.ViewPanelWdg'
    };

    spt.popup.get_widget( evt, tmp_bvr );
}


//
// Data-row Context Menu: EDIT row sobject
//
spt.dg_table.drow_smenu_edit_row_context_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var tbody = activator.getParent('.spt_table_tbody');
    var search_key_info = spt.dg_table.parse_search_key( tbody.get("spt_search_key") );
    var edit_view = bvr.edit_view ? bvr.edit_view : 'edit';

    var tmp_bvr = {};
    tmp_bvr.args = {
        'search_type': search_key_info.search_type,
        'search_id': search_key_info.id,
        'input_prefix': 'edit',
        'view': edit_view
    };

    tmp_bvr.options = {
        'title': 'Edit: ' + search_key_info.search_type,
        'class_name': 'tactic.ui.panel.EditWdg',
        'popup_id': 'edit_popup'
    };

    spt.popup.get_widget( evt, tmp_bvr );
}



//
// Data-row Context Menu: COMMIT all table changes
//
// Method to dyanmically update a row by gathering all of the stored values
// and doing an update
//
spt.dg_table.drow_smenu_update_row_context_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var new_bvr = {};

    // add temporary variable ...
    new_bvr.src_el = spt.get_event_target(evt);
    new_bvr.src_activator_el = activator;
    spt.dg_table.update_row(evt, new_bvr);
}


// --- END OF Data Row (Smart) Context Menus ---------------------------------



// TODO: this is more of a way to notify the context menu that something
// has been changed in the table. The visiblity of the commit buttons can be replaced
// with another mechanism
spt.dg_table._toggle_commit_btn = function(el, hide)
{
    panel_classes = ['.spt_table_top','.spt_view_panel','.spt_panel'];
    var panel = null;
    for (var i=0; i <panel_classes.length; i++) {
        panel = el.getParent(panel_classes[i]);
        if (panel) break;
    }
    if (!panel) {
        spt.js_log.warning('panel not found! Cannot display commit button');
        return;
    }
    var table = panel.getElement('.spt_table_content');
    var commit_buttons = panel.getElements(".spt_table_commit_btn[id*='" + table.id+"']");
    // in case there are mutiple buttons like commit all
    if (hide) {
        commit_buttons.each( function(button) {
            spt.hide( button );
        } );
    } else {
        commit_buttons.each( function(button) {
            spt.show( button );
        } );
    }

}



spt.dg_table.update_uber_notes = function(table, search_type, element_names, values, info) {

    spt.table.alert("DEPRECATED: spt.dg_table.update_uber_notes");
/*
    var server = TacticServerStub.get();

    // get the search type from tbody above the tbody.
    // NOTE: this assumes that the uber notes are with a hidden table row
    //var tbody = table.getParent(".spt_table_tbody");
    //var parent_key = tbody.getAttribute("spt_search_key");
    var notes_top = table.getParent(".spt_uber_notes_top");
    if (notes_top)
        var parent_key = notes_top.getAttribute("spt_search_key");
    else
        return;

    // find out if there is a grouping
    var kwargs = {
        'use_id' : true,
        'parent_key': parent_key
    };

    var result;
    for (var i=0; i< element_names.length; i++) {
        var context = element_names[i];
        var value = values[context];

        if (value != '') {
            var note_type = "sthpw/note";
            var options = values[context + '_option'];
            var access = '';
            if (options.is_private == 'on')
                access = 'private';

            var data = {
                login: spt.Environment.get().get_user(),
                project_code: spt.Environment.get().get_project(),
                context: context,
                note: value,
                access: access
            };
            result = server.insert( note_type, data, kwargs );
            info['update_count'] += 1;
        }
        else {
            result = {};
        }
    }
    return result;
*/

}





