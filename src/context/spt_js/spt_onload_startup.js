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
    spt.hash.onload_first();

    //spt.hash.set_interval();

}


spt.hash = {};

spt.hash.hash;

/*
spt.hash.interval_id = null;

spt.hash.clear_interval = function() {
    if (spt.hash.interval_id) {
        clearInterval(spt.hash.interval_id);
        spt.hash.interval_id = null;
    }
}


spt.hash.set_interval = function() {
    interval = 200;
    spt.hash.interval_id = setInterval(spt.hash.handle_hash, interval);
}



spt.hash.handle_hash = function() {
    var hash = window.location.hash;
    hash = hash.replace("#", "");
    if (hash == spt.hash.last_hash) {
        return;
    }


    //console.log("     hash: " + hash);
    //console.log("last_hash: " + spt.hash.last_hash);
    //console.log("---");


    // remember this as the last one
    spt.hash.set_last_hash(hash);


    var class_name = "tactic.ui.panel.HashPanelWdg";
    var kwargs = {
        hash: hash
    }


    //spt.tab.set_main_body_tab();
    //spt.tab.add_new(name, name, class_name, kwargs);

    document.location.reload()

    return;




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

*/



spt.hash.last_hash = "";
spt.hash.first_load = true;


spt.hash.set_hash = function(state, title, url) {

    var env = spt.Environment.get();
    var project = env.get_project();

    var pathname = document.location.pathname;
    var parts = pathname.split("/");

    var base_url = [];
    for (var i = 0; i < parts.length; i++) {
        var part = parts[i];
        base_url.push(part);
        if (part == project) {
            if (parts.length > i && parts[i+1] == "admin") {
                base_url.push("admin")
            }
            break;
        }
    }
    base_url = base_url.join("/");

    if (url.substr(0,1) == "/") {
        url = base_url + url;
    }
    else {
        url = base_url + "/" + url;
    }

    window.history.pushState(state, title, url);
}


spt.hash.set_last_hash = function(hash) {
    hash = hash.replace("#", "");
    spt.hash.last_hash = hash;
}



spt.hash.onpopstate = function(evt) {
    var state = evt.state;
    if (!state) {
        document.location.reload();
        return;
    }


    var class_name = state.class_name;
    var kwargs = state.kwargs;
    var hash = state.hash;
    var title = state.title;
    var name = state.element_name;

    var class_name = "tactic.ui.panel.HashPanelWdg";
    var kwargs = {
        hash: "/" + hash,
        use_index: false
    }
    var tab = spt.tab.set_main_body_tab();
    if (tab) {
        var set_hash = false;
        spt.tab.add_new(name, title, class_name, kwargs, {}, set_hash);
    }
    else {
        alert("Cannot load ["+title+"] ... no tabs available");
    }

}



spt.hash.onload_first = function() {

    window.onpopstate = spt.hash.onpopstate;

    var hash = window.location.hash;
    spt.hash.first_load = false;
    spt.hash.set_last_hash(hash);

    if (!hash) {
        hash = spt.hash.hash;
        if (!hash) {
            hash = "#";
        }
    }
    hash = hash.replace(/#/, '');



    var options = {
        'hash': decodeURI(hash),
        'first_load': true
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





