// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// Only to be called on "body" tag "onload" event ...
//
spt.onload_startup = function()
{
    // Set-up keyboard handler to allow for trapping keyboard events on a per element basis ...
    //
    spt.kbd.setup_handler();

    spt.behavior.construct_behaviors_on_startup();

    var body_el = document.getElement("body");

    // setup body event for context menu and smart menu click-off checking ...
    //
    // Click off registery is inline (not in this file) and defined in
    // TopWdg ... but the ctx_menu and smenu call-backs should be left
    // as is below, as they are a more general system that does stuff
    // under the hood.
    //
    body_el.addEvent( "mousedown", function(evt) {
        spt.ctx_menu.click_off_check_cbk(evt);
    });
    body_el.addEvent( "mousedown", function(evt) {
        spt.smenu.click_off_check_cbk(evt);
    });

    body_el.addEvent( "mousedown", spt.popup._check_focus_cbk );


    // handle hash changes
    spt.hash.handle_hash();

    spt.hash.set_interval();

}


spt.hash = {};

spt.hash.hash;

spt.hash.interval_id = null;

spt.hash.clear_interval = function() {
    if (spt.hash.interval_id) {
        clearInterval(spt.hash.interval_id);
        spt.hash.interval_id = null;
    }
}

spt.hash.set_interval = function() {
    spt.hash.interval_id = setInterval(spt.hash.test_handle_hash, 250);
}



spt.hash.test_handle_hash = function() {
    var hash = window.location.hash;
    hash = hash.replace("#", "");
    if (hash == spt.hash.last_hash) {
        return;
    }
    // remember this as the last one
    spt.hash.last_hash = hash;
    var action = spt.hash.links[hash];
    if (action) {
        action();
    }
    else {
        // just ignore the request
        console.log("No action found for ["+hash+"]");
    }
}


spt.hash.links = {};
spt.hash.add = function(hash, action) {
    //spt.hash.links.push([hash, action]);
    spt.hash.links[hash] = action;
    spt.hash.last_hash = hash;
}



spt.hash.onload_first = function() {
    var hash = window.location.hash;
    if (!hash) {
        hash = spt.hash.hash;
        if (!hash) {
            hash = "#";
        }
    }
    //var hash = spt.get_raw_hash();
    hash = hash.replace(/#/, '');
    var options = {
        'hash': decodeURI(hash)
    }


    var server = TacticServerStub.get();
    var class_name = "tactic.ui.app.TopContainerWdg";
    var kwargs = {'args': options, 'values': {}};
    var widget_html = server.get_widget(class_name, kwargs);
    spt.behavior.replace_inner_html($("top_of_application"), widget_html);

    if (spt.side_bar) {
        spt.side_bar.restore_state();
    }
}


spt.hash.last_hash = "";
spt.hash.first_load = true;
spt.hash.handle_hash = function() {

    //var hash = spt.get_raw_hash();
    var hash = window.location.hash;
    // handle the first entry
    if (spt.hash.first_load == true) {
        spt.hash.onload_first();
        spt.hash.first_load = false;
        spt.hash.last_hash = hash;
        return;
    }

    // check if the hash has changed
    if ( hash == "" || hash == spt.hash.last_hash || hash == "#"+spt.hash.last_hash) {
        return;
    }

    spt.hash.last_hash = hash;

    hash = hash.replace(/#/, '');


    /*
    var action = spt.hash.links[hash];
    if (action) {
        action();
        return;
    }
    */



    if (hash.substring(0,1) == "/") {

        spt.app_busy.show("Loading ... ", "Retriving url \""+hash+"\"");
        class_name = 'tactic.ui.panel.HashPanelWdg';
        options = {
            hash: hash
        };

        // add to the selected tab ...
        var top = $("main_body").getElement(".spt_tab_top");
        spt.tab.top = top;
        spt.tab.load_selected(hash, hash, class_name, options);

        spt.app_busy.hide();

    }

    /*

    else {
        
        var parts = hash.split(/&/);
        var options = {};
        for (var i=0; i<parts.length; i++) {
            var part = parts[i];
            var nvpair = part.split("=");
            var name = nvpair[0];
            var value = nvpair[1];
            value = decodeURIComponent(value);
            options[name] = value;
        }


        var class_name = options['class_name'];
        if (class_name == null) {
            class_name = "tactic.ui.panel.ViewPanelWdg";
        }
        // load the new panel
        var panel_id = 'main_body';
        spt.panel.load(panel_id, class_name, options);

    }

    var title = hash;
    if (options.title){
        title = options.title;
    }
    $("breadcrumb").innerHTML = title;
    */

}




