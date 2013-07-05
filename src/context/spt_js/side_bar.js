// -----------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// 
// -----------------------------------------------------------------------------

spt.side_bar = {};

// Side bar panel functionality

//
//
spt.side_bar.load_section = function(evt, bvr)
{
    var dst_el = bvr.dst_el;
    var options = bvr.options;

    // get the class name from the destination element
    var top_el = dst_el.firstChild
    var class_name = top_el.getAttribute("spt_class_name")

    Effects.fade_out(dst_el, 150);

    var server = TacticServerStub.get();

    var kwargs = {'args': options};
    var widget_html = server.get_widget(class_name, kwargs);

    spt.behavior.replace_inner_html( dst_el, widget_html );

    Effects.fade_in(dst_el, 150);

}





// Displays a table to a target id
//
// behavior:
//  target_id: the target id element that the table will be put in
//  search_type: the search_type of the sobjects in the table
//  view: the view of the table
//
spt.side_bar.display_link_cbk = function(evt, bvr) {
    var target_id = bvr.target_id;
    var title = bvr.title;
    var options = bvr.options;
    var values = bvr.values;
    var is_popup = bvr.is_popup;

    spt.side_bar._display_link_action( target_id, title, options, values, is_popup );

    /*
    var cmd = new spt.side_bar.DisplayLinkCmd(target_id, title, options, values, is_popup);
    Command.execute_cmd(cmd);
    */
}


spt.side_bar._display_link_action = function(target_id, title, options, values, is_popup)
{
    var busy_title = 'Load View';
    var busy_msg = 'View is now loading in a popup window ...';

    if( ! spt.is_TRUE(is_popup) ) {
        /*
        // Replaced by App Busy indicator (keeping here for reference)
        $("breadcrumb").innerHTML = '<div><img src="/context/icons/common/indicator_snake.gif" border="0"> ' +
                                    'Loading "' + title + '" ...</div>';
        */
        busy_msg = '"' + title + '" view is now loading ...';
    }

    //show busy message
    spt.app_busy.show( busy_title, busy_msg );

    setTimeout( function() {
                        spt.side_bar._load_for_display_link_change(target_id, title, options, values, is_popup);
                        if( spt.is_TRUE(is_popup) )
                            spt.app_busy.hide();
                    }, 10 );
}


spt.side_bar._load_for_display_link_change = function(target_id, title, options, values, is_popup)
{
    // var link = spt.side_bar._link_display_info;
    var path = options['path'];

    // display a table
    var widget_class = options['class_name'];
    if (widget_class == null) {
        widget_class = "tactic.ui.panel.ViewPanelWdg";
    }
    options["title"] = title;
    if( spt.is_TRUE(is_popup) ) {
        // set a default width of 600px
        //options['width'] = '600px';
        options['target_id'] = target_id;
        spt.panel.load_popup(title, widget_class, options);
    }
    else {
        var target_element = $(target_id);
        // Make sure to send back the link title for the saved last link options
        // options["title"] = title


        var main_body = $('main_body');
        var tab_top = main_body.getElement(".spt_tab_top");
        spt.tab.top = tab_top;


        var class_name = options['class_name'];
        // Use path instead
        //var element_name = options['element_name'];
        var element_name = options['path'];
        //spt.tab.add_new(element_name, title, class_name, options, values);
        spt.tab.load_selected(element_name, title, class_name, options, values);
        //spt.tab.save_state();

        //spt.panel.load(target_element, widget_class, options, values)

        // Set the state of the page
        var key = "top_layout";
        var panel_id = "main_body";
        var server = TacticServerStub.get();
        server.set_application_state(key, panel_id, widget_class, options, values);

        // also set the breadcrumb
        //$("breadcrumb").innerHTML = path
        $("breadcrumb").innerHTML = title

        // set the url hash
        if (typeof(options.element_name) != "undefined") {
            var hash = "/link/"+options.element_name;
            if( ! spt.browser.is_Firefox() && ! spt.browser.is_Opera() ) {
                hash = encodeURI( hash );
            }
            spt.last_hash = hash;
            window.location.hash = hash;
        }
        else {
            
            var kwargs = {'predefined': true};
            spt.panel.set_hash(panel_id, widget_class, options, kwargs)
        }
    }
}



// Command that occurs when a user clicks on a link
//
spt.side_bar.DisplayLinkCmd = function(target_id, title, options, values, is_popup) {
    
    this.target_id = target_id;
    this.title = title;
    this.options = options;
    this.values = values;
    this.is_popup = is_popup;

    this.prev_options = {};

    this.get_description = function () { return "DisplayLinkCmd"};
    this.execute = function() { 

        // get the target element
        var target_element = $(this.target_id);

        this.redo();
    }


    this.redo = function() {


        // display a table
        var widget_class = this.options['class_name'];
        if (widget_class == null) {
            widget_class = "tactic.ui.panel.ViewPanelWdg";
        }

        var path = this.options['path'];

        if (this.is_popup == 'true' || this.is_popup == true) {
            // set a default width of 600px
            //this.options['width'] = '600px';
            this.options['target_id'] = this.target_id;
            spt.panel.load_popup(path, widget_class, this.options);
        }
        else {
            var target_element = $(this.target_id);

            $("breadcrumb").innerHTML = '<div><img src="/context/icons/common/indicator_snake.gif" border="0"> ' +
                                        'Loading "' + this.title + '" ...</div>';

            spt.panel.load(target_element, widget_class, this.options, this.values)

            // Set the state of the page
            var key = "top_layout";
            var panel_id = "main_body";
            var server = TacticServerStub.get();

            // Make sure to send back the link title for the saved last link options
            this.options["title"] = this.title

            server.set_application_state(key, panel_id, widget_class, this.options, this.values);

            // also set the breadcrumb
            //$("breadcrumb").innerHTML = path
            $("breadcrumb").innerHTML = this.title

            // set the url hash
            if (typeof(this.options.element_name) != "undefined") {
                var hash = "link="+this.options.element_name;
                if( ! spt.browser.is_Firefox && ! spt.browser.is_Opera ) {
                    hash = encodeURI( hash );
                }
                spt.last_hash = hash;
                window.location.hash = hash;
            }

        }

    }

    this.undo = function() {

        var target_element = $(this.target_id);

        Effects.fade_out(this.prev_target_id, 150);

        var server = TacticServerStub.get();

        // display a table
        widget_class = "tactic.ui.panel.ViewPanelWdg";
        args = {
            "search_type": this.prev_search_type,
            "view": this.prev_view,
            "search_view": this.prev_search_view
        };

        var kwargs = {'args': args};
        widget_html = server.get_widget(widget_class, kwargs);

        // Set the state of the page
        key = "top_layout";
        panel_name = "main_body";
        widget_class = "tactic.ui.panel.ViewPanelWdg";
        server.set_application_state(key, panel_name, widget_class, args);

        // replace the former element with the new element
        spt.behavior.replace_inner_html( target_element, widget_html );
        Effects.fade_in(this.prev_target_id, 150);


        // set the url
        var hash = "search_type=" + this.search_type + "&view=" + this.view;
        window.location.hash = hash;

    }

}


// This occurs when you use the mouse wheel on the side bar. It causes the
// whole side bar to scroll
//
spt.side_bar.scroll = function(evt, bvr) {
    var property = "margin-top";
    var margin = $("side_bar_scroll").getStyle(property);
    margin = parseInt(margin.replace("px", ""));
    if (evt.wheel < 0) {
        margin -= 30;
    }
    else {
        margin += 30;
    }

    if (margin > 0) {
        margin = 0;
        $("side_bar_scroll_down").setStyle('display', 'none');
        var pos = $(window).getScroll();
        $(window).scrollTo(pos.x, pos.y - 30);
    }
    else {
        $("side_bar_scroll_down").setStyle('display', 'block');
    }
    $("side_bar_scroll").setStyle(property, margin);
}




// This callback is called when clicking on a section link in the side bar.
// It toggles the display of a section and then sets the state
//
// bvr.dst_el: id of the section that is displayed

spt.side_bar.toggle_section_display_cbk = function(evt, bvr)
{
    var click_el = $(bvr.src_el);
    //hide el could be the section or div inside the section
    if (spt.has_class(click_el, 'spt_side_bar_element'))
        var hide_el = click_el.getElement(".spt_side_bar_section_content");
    else
        var hide_el = spt.get_cousin(click_el, ".spt_side_bar_element", ".spt_side_bar_section_content");

    bvr.slide_direction = "vertical";
    bvr.dst_el = hide_el;

    var arrow_img_el = click_el.getElement('img');
    var arrow_img_src = arrow_img_el.get('src');

    if( arrow_img_src.match( /_right_/ ) ) {
        arrow_img_el.set('src', arrow_img_src.replace(/_right_/,"_down_"));

        hide_el.setStyle("display", "block");
        hide_el.setStyle("margin-top", "-"+hide_el.getSize().y+"px")
        new Fx.Tween(hide_el, {duration:"short"}).start('margin-top', "0px");

    }
    else {
        arrow_img_el.set('src', arrow_img_src.replace(/_down_/,"_right_"));

        hide_el.setStyle("margin-top", "0px")
        new Fx.Tween(hide_el, {duration:"short"}).start('margin-top', "-"+hide_el.getSize().y+"px");
        //hide_el.setStyle("display", "none");



    }

    spt.side_bar.store_state();
}





//
// Side bar state methods
//
// Stores the state of the sidebar in a cookie.
spt.side_bar.cookie = null;
spt.side_bar.get_state = function()
{
    if (spt.side_bar_cookie == null) {
        spt.side_bar.cookie = new Cookie('sidebar_status');
    }
    return spt.side_bar.cookie;
}


spt.side_bar.store_state = function()
{
    var elements = $("side_bar").getElements(".spt_side_bar_section_content");

    var open_folders = {};

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        if ( element.getStyle("display") == "block" ) {
            var path = element.getAttribute("spt_path");
            open_folders[path] = true;
        }
    }

    var state = spt.side_bar.get_state();
    state.write(JSON.stringify(open_folders))
}



spt.side_bar.restore_state = function()
{
    var side_bar_el = $("side_bar");
    if( ! side_bar_el ) {
        spt.js_log.warning( "WARNING: in spt.side_bar.restore_state(), element with ID 'side_bar' not found." );
        return;
    }

    var elements = side_bar_el.getElements(".spt_side_bar_section_content");

    var state = spt.side_bar.get_state();
    var open_folders = {};
    if( state.read() ) {
        open_folders = JSON.parse( state.read() );
    }
    else {
        return;
    }

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        var path = element.getAttribute("spt_path");
       
        // Find the element with the arrow indicator for open or closed state of section ...
        var prev = $(element).getPrevious();
        if (!prev) continue;
        var arrow_img_el = prev.getElement("img");
        var img_src = arrow_img_el.get('src');

        if (open_folders[path] == true) {
            element.setStyle("display", "block");
            arrow_img_el.set('src', img_src.replace(/_right_/,"_down_"));
        }
        else {
            element.setStyle("display", "none");
            arrow_img_el.set('src', img_src.replace(/_down_/,"_right_"));
        }
    }
}



// action widget callback
//
spt.side_bar.manage_section_action_cbk = function(element, view, is_personal) {

    // get the value of the element
    var value = element.value;
    if (value == "save") {
        // it could be saving other sub-views involved as well like reordering 
        // within the predefined views
        if (confirm("Save ordering of this view [" + view + "] ?") ) {
            var server = TacticServerStub.get();
            server.start({"title": "Updating views"});

            for (changed_view in spt.side_bar.changed_views) {
                var search_type = "SideBarWdg";
                spt.side_bar.save_view(search_type, changed_view, is_personal);
            }
            spt.side_bar.changed_views = {};
            server.finish();
            spt.panel.refresh("side_bar");
            spt.panel.refresh("ManageSideBarBookmark_" + view);
        }
    }
    else if (value == "predefined") {
        spt.popup.open('predefined_side_bar');
    }

    else if ( ["new_link",'new_folder','new_separator'].contains(value) ) {
        spt.side_bar.context_menu_cbk(value, view, is_personal);
    }

    else if (value == "save_folder") {
        var popup_id = "New Item Panel";
        var values = spt.api.Utility.get_input_values(popup_id , null, false);
        // Convert the user input new folder name all in lower case and replace all spaces with underscores.
        //var new_title = values['new_name'].toLowerCase().replace(/ /g,"_");;
        var new_title = values['new_title'];
        var new_name = values['new_name']
     
        if (spt.input.has_special_chars(new_name)) {
            alert("The view name cannot contain special characters.  Please try again.");  
            return;
        }
        if (spt.input.start_with_num(new_name)) {
            alert("A view starting with a number is not allowed.");
            return;
        }

        // folder view cannot be one of the predefined views
        var predefined_views = ['_my_tactic', '_preproduction','_asset_pipeline', '_shot_pipeline', '_site_admin', '_project_admin', '_overview', '_application', '_editorial', '_template', 'definition', 'search', 'publish'];
        if (predefined_views.contains(new_title)) {
            alert('This view name [' + new_name + '] is reserved');
            return;
        }
        
        
        // don't assign login for "project_view", but personal and project view 
        // share the same definition
        var kwargs = {};
        var kwargs2 = {};
        if (is_personal) {
            var user = spt.Environment.get().get_user();
            kwargs['login'] = user;
            kwargs2['login'] = user;
            new_name = user + '.' +  new_name;
        } 
      
        // save this user-defined view
        var server = TacticServerStub.get();
        server.start({"title": "Adding folder", 
            "description": "Adding folder [" + new_title + "]"});
        kwargs['class_name'] ='SideBarSectionLinkWdg';
        kwargs['element_attrs'] = {'title': new_title};
        kwargs['display_options'] = {'view': new_name};
        kwargs['auto_unique_name'] = false;
        kwargs['auto_unique_view'] = false;
        kwargs['unique'] = true;
        
        try{       
            // add it to the project_view
            search_type = 'SideBarWdg';

            // Order matters here
            // set an option to auto adjust the element_name to be unique
            var info = server.add_config_element(search_type, 'definition', new_name, kwargs);
            var unique_el_name = info['element_name'];
            // now add to project_view or my_view_...
            server.add_config_element(search_type, view, unique_el_name, kwargs2);
            
            // only extract elements inside the folder view "new_folder"
            var folder_elements = spt.side_bar.get_elements('new_folder', popup_id);
            var folder_element_names = [];
            folder_elements.each( function(x) 
                    {folder_element_names.push(x.getAttribute("spt_element_name"))});
            if (folder_element_names.length > 0)
                server.update_config(search_type, unique_el_name, folder_element_names, kwargs2);

            server.finish();
        }
        catch(err) {
            var error_str = spt.exception.handler(err);
            alert(error_str);
            server.abort();
            return;
        }
        //refresh 
        spt.popup.destroy(popup_id);
        spt.panel.refresh("ManageSideBarBookmark_" + view);
        spt.panel.refresh("side_bar");
    }
    else if (value == "save_link") {
        var popup_id = "New Item Panel";
        var values = spt.api.Utility.get_input_values(popup_id , null, false);
        // Convert the user input link title all in lower case and replace all spaces with underscores.
        var link_name = values['new_link_title'].toLowerCase().replace(/ /g,"_");
        var include_search_view = values["include_search_view"] == 'on'; 

        if (spt.input.has_special_chars(link_name)) {
            alert("The view name cannot contain special characters.  Please try again.");  
            return;
        }
      
        // link name cannot be one of the predefined views
        var predefined_views = ['_my_tactic', '_preproduction','_asset_pipeline', '_shot_pipeline', '_site_admin', '_project_admin', '_overview', '_application', '_editorial', '_template', 'definition', 'search', 'publish','edit','insert','edit_definition'];
        if (predefined_views.contains(link_name)) {
            alert('This view name [' + link_name + '] is reserved');
            return;
        }
            
        var new_title = link_name;
        var search_type = values['new_search_type'];
        if (!link_name || !search_type) {
            alert('A title and a search type are required.');
            return;
        }
     
        
        var kwargs = {};
        var kwargs2 = {};
        var new_view = values['new_link_view'];
        if (is_personal) {
            var user = spt.Environment.get().get_user();
            kwargs['login'] = user;
            kwargs2['login'] = user;
            link_name = user + '.' +  link_name;
            //new_view = user + '.' + new_view;
        }

        if (confirm("Save this link [" + new_title + "] ?") ) {
            try {
                var server = TacticServerStub.get();
                server.start({"title": "Adding link",
                    "description": "Adding link [" + new_title + "]"});
                //hard-code table view for now
                
                kwargs['class_name'] = 'LinkWdg';
                kwargs['element_attrs'] = {'title': new_title};
                
                var display_options =  {'search_type': search_type, 'view': new_view};
                if (include_search_view) {
                    display_options['search_view'] = 'link_search:' + new_view;
                }
                // special case for CustomLayoutWdg
                if (search_type == 'CustomLayoutWdg') {
                    delete display_options['search_view'];
                    delete display_options['search_type'];
                    display_options['class_name'] = 'tactic.ui.panel.CustomLayoutWdg';
                }
                kwargs['display_options'] = display_options;
                
                //kwargs['auto_unique_name'] = true;
                kwargs['unique'] = true;
                
                // add it to the view, if view is my personal view, add login
                search_type = 'SideBarWdg';
                var info = server.add_config_element(search_type, 'definition', link_name, kwargs);
                var unique_el_name = info['element_name'];
                
                // now add to project_view
                server.add_config_element(search_type, view, unique_el_name, kwargs2);
                server.finish();
                //refresh 
                spt.popup.destroy(popup_id);
                spt.panel.refresh("ManageSideBarBookmark_" + view);
                spt.panel.refresh("side_bar");
            }
            catch(e) {
                alert(spt.exception.handler(e));
            }
            
        }
    }
    else if (value == "save_separator") {
        var popup_id = "New Item Panel";
        var name = 'separator';
        
        var server = TacticServerStub.get();
        server.start({"title": "Adding separator"});
        var kwargs = {'class_name' : 'SeparatorWdg',
                      'element_attrs' : {'title': 'Separator'},
                      'unique': false,
                      'auto_unique_name': true,
                       'auto_unique_view': true}; 
        // add it to the project_view
        search_type = 'SideBarWdg';
        var kwargs2 = {};

        //have login for the view, and definition
        if (is_personal){
            var user = spt.Environment.get().get_user();
            kwargs['login'] = user;
            kwargs2['login'] = user;
            name = user + '.' +  name;
        }

        var info = server.add_config_element(search_type, 'definition', name, kwargs);
        var unique_el_name = info['element_name'];
        
        // now add to project_view
        server.add_config_element(search_type, view, unique_el_name, kwargs2);
        server.finish();
        //refresh 
        spt.popup.destroy(popup_id);
        spt.panel.refresh("ManageSideBarBookmark_" + view);
        spt.panel.refresh("side_bar");
        
    }
    else {
        alert("Unimplemented option: " + value);
    }

    element.value = "";
}


// save the changed views
spt.side_bar.save_view = function(search_type, view, is_personal, list_top) {

    // backwards compatibility (this is an id)
    if (typeof(list_top) == 'undefined') {

        var elements;
        if (view == "definition") {
            elements = spt.side_bar.get_elements(view, "menu_item_definition_list");
        }
        else {
            elements = spt.side_bar.get_elements(view);
        }
    }
    else {
        elements = spt.side_bar.get_elements(view, list_top);
    }


    if (spt.side_bar.found_view == false) {
        return;
    }

    var element_names = [];
    for (var i = 0; i < elements.length; i++) {
        var element_name = elements[i].getAttribute("spt_element_name");
        element_names.push(element_name);
    }
    var server = TacticServerStub.get();
    // will get unexpected results if multiple folders share the same view
    //
    var kwargs = {};
    if (is_personal){
        kwargs['login'] = spt.Environment.get().get_user();
    }
    //add the trashed items
    kwargs['deleted_element_names'] = spt.side_bar.trashed_items;
    
    server.update_config(search_type, view, element_names, kwargs);
    spt.side_bar.trashed_items = [];
}



// get all the elements of a specific view
spt.side_bar.found_view = false;
spt.side_bar.get_elements = function(view, list_id) {
    if (typeof(list_id) == 'undefined' || list_id == null) {
        list_id = "menu_item_list";
    }

    var elements = $(list_id).getElements(".spt_side_bar_element");
    if (typeof(view) == 'undefined') {
        return elements;
    }

    spt.side_bar.found_view = false;

    var data = {};
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];

        var element_view = element.getAttribute("spt_view");
        if (element_view == view) {
            spt.side_bar.found_view = true;
        }
        // ignore the dummy created when there are no elements
        if (element.hasClass("spt_side_bar_dummy")) {
            continue;
        }

        // dynamically create the list
        var element_list = data[element_view];
        if (element_list == null) {
            element_list = [];
            data[element_view] = element_list;
        }

        //var element_name = elements[i].getAttribute("spt_element_name");
        element_list.push(element);
    }
    if (spt.side_bar.found_view) {
        var element_list = data[view];
        if (element_list)
            return element_list;
        else
            return [];
    }
    else {
        // to prevent undefined from being returned
        return [];
    }
}





//
// Drag and drop actions for the elements
//

spt.side_bar.changed_views = {};
spt.side_bar.trashed_items = [];
spt.side_bar.active_elems = {};
spt.side_bar.pp_setup = function(evt, bvr, mouse_411)
{   
    var clonable = bvr.src_el;
    if (! clonable.hasClass("spt_side_bar_element")) {
        clonable = bvr.src_el.getParent('.spt_side_bar_element');
    }
    // make sure that the src element is actually a side bar element.
    //if (! bvr.src_el.hasClass("spt_side_bar_element")) {
    //    bvr.src_el = bvr.src_el.parentNode;
    //}

    var ghost_el = $(bvr.drag_el);
    if( ghost_el )
    {
        // Make a clone of the source div that we clicked on to drag ...
        var src_copy = spt.behavior.clone(clonable);
        var w = clonable.clientWidth;
        var h = clonable.clientHeight;

        /*
        // Use this if you want the initial ghost div position right over top of the source element ...
        var pos = spt.get_absolute_offset( bvr.src_el );
        ghost_el.setStyle( "left", pos.x );
        ghost_el.setStyle( "top", pos.y );
        */

        // Use this if you want the initial ghost div position to be offset from mouse same as on mouse momve ...
        ghost_el.setStyle( "left", (mouse_411.curr_x + 10) );
        ghost_el.setStyle( "top", (mouse_411.curr_y + 10) );

        ghost_el.setStyle( "width", w );
        ghost_el.setStyle( "height", h );

        // Then plug the clone div into the Utility ghost_el div to be the contents of the drop ...
        ghost_el.innerHTML = "";
        ghost_el.appendChild( $(src_copy) );

        ghost_el.setStyle( "display", "block" );
        ghost_el.setStyle( "text-align", "left" );
        ghost_el.setStyle( "background", "#4F4FC4");
    }
    else {
        spt.js_log.debug("WARNING: NO ghost el found in spt.side_bar.pp_setup() callback!");
    }
}


spt.side_bar.pp_motion = function(evt, bvr, mouse_411)
{
    var ghost_el = $(bvr.drag_el);
    if( ghost_el )
    {
        ghost_el.setStyle( "left", (mouse_411.curr_x + 10) );
        ghost_el.setStyle( "top", (mouse_411.curr_y + 10) );
        var elem = spt.side_bar.pp_find_drop_elem(evt, bvr, mouse_411);
        //make the Trash can having a hard border
        if (spt.side_bar.pp_is_trash(elem))
            spt.add_class(elem, 'look_menu_hover');
        else
        {
            elem = spt.side_bar.active_elems['trash'];
            if (elem)
                spt.remove_class(elem, 'look_menu_hover');
        }
    }
}
// Find valid droppable element
spt.side_bar.pp_find_drop_elem = function(evt, bvr)
{
    // find drop element inside out
    var found = false;
    var drop_on_el = spt.get_event_target(evt);
    while( drop_on_el ) {
        if( ('getAttribute' in drop_on_el) && drop_on_el.getAttribute("SPT_ACCEPT_DROP") == "manageSideBar" ) {
            found = true;
            break;
        }
        drop_on_el = drop_on_el.parentNode;
    }
    if ( found )
        return drop_on_el;
    else
        return null;
    
}

spt.side_bar.pp_is_trash = function(drop_on_el)
{
    if (drop_on_el && drop_on_el.hasClass("spt_side_bar_trash") == true)
    {
        spt.side_bar.active_elems['trash'] = drop_on_el;
        return true;
    }
    return false;
}
spt.side_bar.pp_action = function(evt, bvr)
{
    var ghost_el = bvr.drag_el;
    if( ! ghost_el ) {
        return;
    }


    // Grab the cloned div that we had plugged in as the contents (firstChild) of the ghost_el Utility div ...
    var ghost_content = ghost_el.removeChild( ghost_el.firstChild );
    ghost_el.innerHTML = "";
    ghost_el.style.display = "none";

    // find valid drop element
    var drop_on_el = spt.side_bar.pp_find_drop_elem(evt, bvr);
    if (!drop_on_el)
        return;

    var mode = bvr.mode;
    if (!mode) {
        // look for parent
        var start_content = bvr.src_el.getParent(".spt_side_bar_content");
        var end_content = drop_on_el.getParent(".spt_side_bar_content");
        if (end_content == null) {
            mode = "move";
        }
        else {

            var start_view = start_content.getAttribute("spt_view");
            var end_view = end_content.getAttribute("spt_view");

            if (start_view != end_view) {
                mode = "copy";
            }
            else {
                mode = "move";
            }
        }
    }

    var contents;

    if (mode == "copy") {
        contents = ghost_content;
    }
    else {
        // make sure that the contents is actually a side bar element.
        var contents = bvr.src_el;
        if (! contents.hasClass("spt_side_bar_element")) {
            contents = contents.getParent('.spt_side_bar_element');
        }

    }


    var view;
  
    // Record that the old view has changed if not in copy mode
    var old_view = contents.getAttribute("spt_view")
    if (mode != 'copy') {
        spt.side_bar.changed_views[old_view] = true;
    }

    // up one level if dropped on a section link
    if  (drop_on_el.hasClass("spt_side_bar_section_link"))
        drop_on_el = drop_on_el.getParent(".spt_side_bar_section");
    // if dropped on trash
    if (spt.side_bar.pp_is_trash(drop_on_el) ) {
        var name = contents.getAttribute('spt_element_name');
        spt.side_bar.trashed_items.push(name);
        contents.destroy();
        elem = spt.side_bar.active_elems['trash'];
        if (elem)
            spt.remove_class(elem, 'look_menu_hover');
        return;
    }
    // if dropped on a section or a section link
    
    else if( drop_on_el.hasClass("spt_side_bar_section") ) {
        var children = drop_on_el.getElements(".spt_side_bar_element");
        if (children[0] != null && !children[0].hasClass("spt_side_bar_dummy")) {
            contents.inject(children[0], 'before');
            view = children[0].getAttribute("spt_view");
        }
        else {
            var container = drop_on_el.getElement(".spt_side_bar_section_content");
            container.appendChild(contents);
            // get the view
            // FIXME: assume view == element_name
            //view = drop_on_el.getAttribute("spt_view");
            view = drop_on_el.getAttribute("spt_element_name");
        }

    }
    // if dropped on a link
    else if ( drop_on_el.hasClass("spt_side_bar_link") == true ) {
        contents.inject(drop_on_el, 'before');
        view = drop_on_el.getAttribute("spt_view");
    }
    else if( drop_on_el.hasClass("spt_section_top") ) {
        var children = drop_on_el.getElements(".spt_side_bar_element");
        var last = children[children.length-1];
        contents.inject(last, 'after');
        view = last.getAttribute("spt_view");
    }
    // if dropped on any other element
    else {
        var parent = drop_on_el.getParent(".spt_side_bar_element");
        contents.inject(parent, 'before');
        view = parent.getAttribute("spt_view");
    }

    // switch view
    if (view == null) {
        alert("view is NULL!!!!");
    }


    //
    if (mode == 'copy') {

        var element_name = contents.getAttribute("spt_element_name");
        var element_title = contents.getAttribute("spt_title");

        //var content_view = base + "_" + element_name;
        var content_view = element_name;
        if (content_view.substr(0,1) == "_") {
            content_view = content_view.substr(1, content_view.length);
        }



        // check to see what that there are no duplicate view titles
        var menu_item_list = contents.getParent(".spt_menu_item_list");
        elements = spt.side_bar.get_elements(view, menu_item_list);

        element_list = new Array();
        for (var i = 0; i < elements.length; i++) {
            var cur_element_name = elements[i].getAttribute("spt_element_name");
            pat = new RegExp( '^' + element_name+ '\d*');
            if (cur_element_name.match(pat)) {
                element_list.push(cur_element_name);
            }
        }
        if (element_list.length > 0) {
            content_view = content_view + element_list.length;
            element_title = element_title + element_list.length;
        }
        contents.setAttribute("spt_element_name", content_view);
        contents.setAttribute("spt_title", element_title);
        // set the new view of the element
        contents.setAttribute("spt_view", view);
        // go through the elements names and change them to the new view
        var elements = contents.getElements(".spt_side_bar_element");
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            element.setAttribute("spt_view", content_view);
        }


        // change the title
        var title = contents.getElement(".spt_side_bar_title");
        if (title){
            var title_icon = title.getFirst();
            if (!title_icon) {
                title.innerHTML = element_title;
            } else {
                title.innerHTML = '';
                title.appendChild(title_icon);
                title.appendText(element_title);
            }
        }

        spt.side_bar.changed_views[view] = true;
    }
    else {
        // set the new view of the element
        contents.setAttribute("spt_view", view);
        spt.side_bar.changed_views[view] = true;
    }

    if( bvr.class_name ) {
        spt.side_bar.display_element_info_cbk(evt,bvr);
    }
}



spt.side_bar.context_menu_cbk = function(action, view, is_personal) {

    var element_name = null;
    /*
    config = document.createElement('config')
    element = document.createElement('element')
    display =  document.createElement('display')
    config.appendChild(element);
    element.appendChild(display);
    */
    if (action == "new_link") {
        element_name = "new_link";
    }
    else if (action == "new_folder") {
        element_name = "new_folder";
    }
    else if (action == "new_separator") {
       element_name = "new_separator";
    }
    
    if (element_name) {
        var clone = spt.side_bar.add_new_item(view, element_name);
        //clone.setStyle('background', '#6CB87B');
        if (element_name =='new_separator') {
            
            spt.side_bar.manage_section_action_cbk({'value':'save_separator'},view, is_personal);
        }
       
    }
}



spt.side_bar.add_new_item = function(view, element_name, template_top) {

    var list_id = "menu_item_list";
    var options = {'type': element_name, 'view': view};
    var popup_id = "New Item Panel";

    new_item_class = 'tactic.ui.panel.ManageViewNewItemWdg';
    spt.panel.load_popup(popup_id, 'tactic.ui.panel.ManageViewNewItemWdg', options, {});
    // get the template menu items
    // index is prone to error, use element_name instead

    if ( typeof(template_top) == 'undefined' ) {
        template_top = $("menu_item_template");
    }
    var menu_item = template_top.getElement("div[spt_element_name=" + element_name +"]");
  
    if (!menu_item)
        return;

    var clone = spt.behavior.clone(menu_item);

    // get the element and inject after
    var div = $(popup_id).getElement('.spt_new_item');
    div.appendChild(clone);

    // now add some properties to the new element
    if (element_name ='new_folder')
        clone.addClass("spt_side_bar_section");
    else
        clone.addClass("spt_side_bar_element");

    clone.setAttribute("spt_view", view);
    // get the current name of the cloned element
    var clone_name = clone.getAttribute("spt_element_name");
    
    bvr = {};
    bvr.src_el = clone;
  
    
    return clone;

}





//
// Element info setting and saving
//
spt.side_bar.display_element_info_cbk = function(evt, bvr)
{
    var top = bvr.src_el.getParent(".spt_view_manager_top");
    if (!top)
        return;

    var detail_panel = top.getElement(".spt_view_manager_detail");

    var src_el = bvr.src_el;

    var element_name = src_el.getAttribute("spt_element_name");
    if (element_name == null) {
        src_el = src_el.getParent(".spt_side_bar_element");
        element_name = src_el.getAttribute("spt_element_name");
    }

    var search_type = detail_panel.getAttribute("spt_search_type");
    var personal = detail_panel.getAttribute("spt_personal");
    var view = src_el.getAttribute("spt_view");
    var path = src_el.getAttribute("spt_path");
    var login = detail_panel.getAttribute("spt_login");
    var is_default = src_el.getAttribute("spt_default");
    var config_xml = bvr["config_xml"];
    // rename
    if (config_xml) {
        //it could be double or single quotes
        var pat = new RegExp('(.*element .*name=(?:\"|\'))([^\\s\\t]*)((?:\"|\').*)')
        var m = config_xml.match(pat);
        if (m) {
            config_xml = config_xml.replace(pat, '$1' + element_name +'$3');
        }
    }
    else {
        config_xml = '';
    }
    var server = TacticServerStub.get();
    var class_name = bvr.class_name;
    var options = {
        'search_type': search_type,
        'view': view,
        'element_name': element_name,
        'config_xml': config_xml,
        'config_mode': bvr.config_mode,
        'path': path,
        'login': login,
        'default': is_default,
        'personal': personal
    };
    var fade = false;
    var values = {};
    spt.panel.load(detail_panel, class_name, options, values, fade);

 
}





spt.side_bar.save_definition_cbk = function( bvr )
{
    var view_manager_top = null;
    if( bvr ) {
        view_manager_top = bvr.src_el.getParent(".SPT_VIEW_MANAGER_TOP");
    }

    var panel = view_manager_top.getElement(".spt_view_manager_detail");
    
    var values = spt.api.Utility.get_input_values( panel );

    if (values.config_element_name == "") {
        alert("Please provide a name for this element");
        return;
    }

    values['update'] = "true";

    // execute the command with the widget
    var fade = false;
    spt.panel.refresh(panel, values, fade);

    spt.panel.refresh("side_bar");

    var elements = view_manager_top.getElements(".spt_view_manager_section");
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        if (element != null) {
            spt.panel.refresh(element);
        }
    }
}




