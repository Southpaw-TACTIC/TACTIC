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
spt.onload_startup = function(admin=false, handle_hash_changes=true)
{
    // Set-up keyboard handler to allow for trapping keyboard events on a per element basis ...
    //
    if (admin) spt.kbd.setup_handler();


    // IMPORTANT: initializes all behaviors
    spt.behavior.construct_behaviors_on_startup();

    var body_el = document.id(document.body);

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
    spt.hash.onload_first(handle_hash_changes);


}


spt.hash = {};

spt.hash.hash;
spt.hash.index_hash = null;

spt.hash.set_hash = function(state, title, url) {

    var env = spt.Environment.get();
    var project = env.get_project();
    var site = env.get_site();

    var pathname = document.location.pathname;

    if (pathname == "/") {
        if (site) {
            pathname = site + "/" + project;
        }
        else {
            pathname = project;
        }
            
    }
    else {

        // if this is the root / or /tactic the set the whole path
        // if it's /tactic/, make the path the project_code
        var keywords = ['tactic','projects'];
        for (var k=0; k < keywords.length; k++) {
            if (pathname == '/' || pathname == '/'+keywords[k]) {
                pathname = keywords[k] + "/" + project;
                break;
            }
            else if (pathname=='/' +keywords[k]+ '/')  {
                pathname = project;
                break;
            }
        } 

    }


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

    //if (site) {
    //    base_url.push(site);
    //}

    base_url = base_url.join("/");



    if (url.substr(0,1) == "/") {
        url = base_url + url;
    }
    else {
        url = base_url + "/" + url;
    }

    try {
        
        window.history.pushState(state, title, url);
    }
    catch(e) {
        console.log("Error with pushing state");
        console.log(title);
        console.log(url);
        console.log(state);
        console.log(e);
    }
}

spt.hash.set_index_hash = function(url) {

    spt.hash.index_hash = url;
}


// for some reason, onpopstate gets called on initial load on Chrome
spt.hash.ignore = false;


spt.hash.onpopstate = function(evt) {
    var state = evt.state;

    if (spt.hash.ignore) {
        spt.hash.ignore = false;
        //return;
    }


    if (!state) {
        var hash = "";
        var title = "";
        var name = "";
        var kwargs = "";
        var mode = "";
    }

    else {

        //var class_name = state.class_name;
        //var kwargs = state.kwargs;
        var hash = state.hash;
        var title = state.title;
        var name = state.element_name;
        var kwargs = state.kwargs;
        var mode = state.mode;
    }


    if (hash) {
        if (hash == "/" || hash == "") {
            if (spt.hash.index_hash) {
                hash = spt.hash.index_hash;
            }
            else {
                return;
            }
        }
        if (hash.substr(0,1) != "/") {
            hash = "/" + hash;
        }

        var class_name = "tactic.ui.panel.HashPanelWdg";
        var kwargs = {
            hash: hash,
            use_index: false
        }

    }
    else {
        var class_name = "tactic.ui.panel.CustomLayoutWdg";
    }

    if (mode == "tab") {
        var tab = spt.tab.set_main_body_tab();
        if (tab) {
            var set_hash = false;
            spt.tab.add_new(name, title, class_name, kwargs, {}, set_hash);
        }
    }
    else if (mode == "panel") {
        var panel = state.panel;
        if (!panel) {
            document.location.reload();
            return;
        }
        var panel = document.id(panel);
        spt.panel.load(panel, class_name, kwargs);
    }
    else {
        if (!spt.browser.is_Safari() ) {
            document.location.reload();
        }
    }

}


spt.hash.first_load = true;

spt.hash.onload_first = function(handle_hash_changes=true) {

    if (spt.browser.is_Chrome()) {
        spt.hash.ignore = true;
    }

    
    var hash = window.location.hash;
    if (!hash) {
        hash = spt.hash.hash;
        if (!hash) {
            hash = "#";
        }
    }
    hash = hash.replace(/#/, '');

    // On Qt browsers, this causes the page to refresh continuously
    if (!spt.browser.is_Qt() && handle_hash_changes) {
        //window.onpopstate = spt.hash.onpopstate;
    }

    spt.hash.first_load = false;




    var options = {
        hash: decodeURI(hash),
        first_load: true,
        pathname: window.location.pathname
    }

    // pass all the ? name/values in
    var search = location.search.substring(1);
    var values = search.split("&").reduce(function(prev, curr, i, arr) {
        var p = curr.split("=");
            prev[decodeURIComponent(p[0])] = decodeURIComponent(p[1]);
                    return prev;
    }, {});
        

    var server = TacticServerStub.get();
    var class_name = "tactic.ui.app.TopContainerWdg";
    var kwargs = {'args': options, 'values': values};
    var widget_html = server.get_widget(class_name, kwargs);

    setTimeout( function() {
        spt.behavior.replace_inner_html(document.id("top_of_application"), widget_html);

        if (spt.side_bar) {
            spt.side_bar.restore_state();
        }
    }, 500 );

}





