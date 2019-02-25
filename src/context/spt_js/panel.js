// ------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to
//   Southpaw Technology Inc., and is not to be reproduced, transmitted,
//   or disclosed in any way without written permission.
// 
// ------------------------------------------------------------------------------



spt.panel = {}

//
// Method to refresh an element.  It will look for the closest parent panel
// and refresh
//
spt.panel.refresh_element = function(element, data, kwargs) {

    var panel = spt.has_class(element, "spt_panel") ? element : document.id(element).getParent(".spt_panel");
    var fade = kwargs ? kwargs.fade : false;

    if (data) {
        if (!kwargs) {
            kwargs = {};
        }
        kwargs['data'] = data;
    }

    spt.panel._refresh_widget(panel, null, kwargs);
}


//
// Callback to refresh a panel widget
//
spt.panel.refresh = function(panel_id, values, kwargs) {
    var panel = document.id(panel_id);
    if (panel == null) {
        spt.js_log.warning("panel[" + panel_id + "] cannot be found ");
        return;
    }
    // either the panel or the first child will have all the necessary
    // information
    if (! panel.getAttribute("spt_class_name") ) {
        // go up the hierarchy to find the next panel
        panel = panel.getParent(".spt_panel");
    }

    if (values == null || values == undefined || values == {}) {
        values = spt.api.Utility.get_input_values(panel);
    }

    spt.panel._refresh_widget(panel, values, kwargs);

}



//
// load a panel with a specified widget
spt.panel.load_cbk = function(aux, bvr) {
    class_name = bvr.options["class_name"];
    args = bvr.args;
    spt.panel.load(aux, class_name, args, null, {fade: true});
}




spt.panel.async_load = function(panel_id, class_name, options, values) {
    return spt.panel.load(panel_id, class_name, options, values);
}


spt.panel.load = function(panel_id, class_name, options, values, kwargs) {
    var fade = kwargs ? kwargs.fade : true;
    var async = kwargs ? kwargs.async : true;
    var show_loading = kwargs ? kwargs.show_loading : true;
    if (async == null) { async = true; }
    if (show_loading == null) { show_loading = true; }

    var callback = kwargs ? kwargs.callback : null;
    if (callback) {
        async = true;
    }
    var panel = document.id(panel_id);
    if (!panel)
    {
        spt.js_log.critical('WARNING: Panel with id [' + panel_id + '] does not exist yet');
        return;
    }
    
    var tween = null;
    if (!spt.browser.is_IE() && fade == true) {
        // define the tween instance 
        tween = new Fx.Tween(panel,  {property: 'opacity', duration: 300 });
    }
    
    var draw_content = function() {
        var server = TacticServerStub.get();
        var wdg_kwargs = {'args': options, 'values': values};

        if (async) {

            var size = document.id(panel).getSize();
            console.log(size);

            var env = spt.Environment.get();
            var colors = env.get_colors();
            var fade_color = "#FFF";
            var border = "#999";
            var bgcolor = "#333";
            var shadow = "#333";
            if (colors) {
                var theme = colors.theme;
                if (theme == "dark") {
                    fade_color = "#000"
                }
                bgcolor = colors.background3;
                shadow = colors.shadow;
            }


            // the panel must have a position
            had_position = true;
            if (!panel.getStyle("position")) {
                panel.setStyle("position", "relative");
                had_position = false;
            }


            var element = document.id(document.createElement("div"));
            element.innerHTML = '<div class="spt_spin" style="border: solid 1px '+border+';background: '+bgcolor+'; background: #EEE; margin: 20px auto; width: 150px; text-align: center; padding: 5px 10px;"><img src="/context/icons/common/indicator_snake.gif" border="0"/> <b>Loading ...</b></div>';
            element.setStyle("z-index", "100");
            //element.setStyle("margin-top", -size.y);
            element.setStyle("position", "absolute");
            element.setStyle("top", "10px");
            element.setStyle("left", size.x/2-75);


            var xelement = document.id(document.createElement("div"));
            xelement.setStyle("opacity", "0.4");
            xelement.innerHTML = '<div style="background: '+fade_color+'; width: '+size.x+'; height: '+size.y+'"></div>';
            xelement.setStyle("margin-top", -size.y);
            xelement.setStyle("position", "relative");

            if (show_loading) {
                panel.appendChild(xelement);
                panel.appendChild(element);
            }


            wdg_kwargs.cbjs_action = function(widget_html) {
                xelement.setStyle("opacity", "0.4");

                if (had_position == false) {
                    panel.setStyle("position", "");
                }


                xelement.destroy();
                element.destroy();

                spt.behavior.replace_inner_html(panel, widget_html);
                new Fx.Tween(xelement, {duration: "short"}).start('opacity', '0');
                if (callback) callback(panel);
            }
            wdg_kwargs.on_error = function(error) {
                xelement.destroy();
                element.destroy();
                spt.alert(error);
            }


            var widget_html = server.async_get_widget(class_name, wdg_kwargs);



        }
        else {
            var widget_html = server.get_widget(class_name, wdg_kwargs);
            spt.behavior.replace_inner_html( panel, widget_html );
        }
    }

    if (!async && !spt.browser.is_IE() && fade == true) {
        panel.setStyle("opacity", "0.5");
        tween.chain(draw_content()).start(0.5, 1);

    }
    else {
        draw_content();
    }

    // remove the old information of what is in the panel
    var attrs = panel.attributes;
    for (var i = 0; i < attrs.length; i++) {
        var attr = attrs[i];
        var node_name = attr.nodeName
        if (node_name.substring(0, 4) == 'spt_' ) {
            panel.removeAttribute(node_name);
        }
    }

    // fill in the loaded information in the panel
    panel.setAttribute("spt_class_name", class_name);


    new_options = {}
    for (name in options) {
        new_options[name] = options[name];
    }
    delete new_options['path'];
 
    // store more complex object as JSON string
    for (var name in options) {
        var value = new_options[name];
        if (value && typeof(value) == 'object')
            new_options[name] = JSON.stringify(value);
        panel.setAttribute("spt_"+name, new_options[name]);
    }


    //panel.setStyle("opacity", "0");
    //new Fx.Tween(panel, {duration: "short"}).start('opacity', '1');

}



spt.panel.load_popup = function(popup_id, class_name, args, kwargs) {

    // load into a popup
    if (!kwargs)
        kwargs = {};
    var bvr2 = {
        options:  {
            title: popup_id,
            class_name: class_name,
            popup_id: popup_id
        },
        args: args,
        kwargs: kwargs
    }
    
    if (kwargs.values) {
        bvr2.values = kwargs.values;
    }
    if (kwargs.width) 
        bvr2.options.width = kwargs.width;
    if (kwargs.height) 
        bvr2.options.height = kwargs.height;
    if (kwargs.resize)
        bvr2.options.resize = kwargs.resize;
    if (kwargs.on_close)
        bvr2.options.on_close = kwargs.on_close;
    if (kwargs.allow_close != null) 
        bvr2.options.allow_close = kwargs.allow_close;
    if (kwargs.top_class) 
        bvr2.options.top_class = kwargs.top_class;

    return spt.popup.get_widget({}, bvr2);

}


spt.panel.load_popup_with_html = function(popup_id, html) {

    // load into a popup
    var bvr2 = {
        options:  {
            title: popup_id,
            class_name: '',
            html: html
        },
        args: [],
        kwargs: {}
    }
    spt.popup.get_widget({}, bvr2);

}



spt.panel.load_link = function( element, link ) {

    var class_name = 'tactic.ui.panel.HashPanelWdg';
    var cls_kwargs = {
        hash: link
    }
    spt.panel.load(element, class_name, cls_kwargs);

}



spt.panel.load_custom_layout = function( element, view ) {

    var class_name = 'tactic.ui.panel.CustomLayoutWdg';
    var cls_kwargs = {
        'view': view
    }
    spt.panel.load(element, class_name, cls_kwargs);

}







spt.panel.is_refreshing = false;
spt.panel.show_progress = function(element_id) {
    if (spt.panel.is_refreshing == false) {
        return;
    }

    var element = document.id(element_id);
   
    element.innerHTML = '<div style="height: 100%; font-size: 1.5em" class="spt_spin"><img src="/context/icons/common/indicator_snake.gif" border="0"> Loading ...</div>';
    //element.fade('in');
}



spt.panel.get_element_options = function(element) {
    // get all the spt attributes
    var attrs = element.attributes;
    var options = {};

    for (var j =0; j < attrs.length; j++) {
        var attr = attrs[j];
        if (attr.nodeName.substring(0, 4) == 'spt_' ) {
            var name = attr.nodeName.substring(4, attr.nodeName.length);
            if (name == 'node' || name == 'class_name') {
                continue;
            }

            // skip any bvrs
            if (attr.nodeName == 'spt_bvrs') {
                continue;
            }

            //var value = attr.nodeValue;
            var value = attr.value;
            if (typeOf(value) == 'object') {
                spt.alert( "Attribute ["+ attr.nodeName +"] is an object" );
            }
            //options[name] = attr.nodeValue;
            options[name] = attr.value;
        }
    }
    return options;
}





spt.panel._refresh_widget = function(element_id, values, kwargs) {

    var fade = kwargs ? kwargs.fade : false;
    var async = kwargs ? kwargs.async : true;

    var callback = kwargs ? kwargs.callback : null;
    if (callback) {
        async = true;
    }

    var element = document.id(element_id);
    if (! element) {
        spt.js_log.warning("_refresh_widget " + element_id +  " not found ");
        return;
    }
    element_id = element.getAttribute('id');

    var target_id = element.getAttribute("spt_target_id");
    var title = element.getAttribute("spt_title");
    var view = element.getAttribute("spt_view");

    var widget_class = element.getAttribute("spt_class_name");
    if( ! widget_class || widget_class == 'undefined' ) {
        spt.alert("Cannot refresh ["+element_id+"].  No spt_class_name attribute found");
        return;
    }
    spt.panel.is_refreshing = true;
    
    if (fade) {
        element.fade('out');
    }
    
    var options = spt.panel.get_element_options(element);
    // add an is_refresh option
    options['is_refresh'] = "true";


    var data = kwargs ? kwargs.data : false;
    if (data) {
        for (var key in data) {
            options[key] = data[key];
        }
    }

    var server = TacticServerStub.get();
    var wdg_kwargs = {'args': options, 'values': values};

    if (async) {

        wdg_kwargs.cbjs_action = function(widget_html) {
            spt.behavior.replace_inner_html(element, widget_html);
            if (callback) {
                callback();
            }
            if (fade) {
                element.fade('in');
            }
            spt.panel.is_refreshing = false;
        }
        server.async_get_widget(widget_class, wdg_kwargs);
    }
    else {
        var widget_html = server.get_widget(widget_class, wdg_kwargs);
        // replace the former element with the new element
        spt.behavior.replace_inner_html( element, widget_html );
   
        //note: this fade out/in effect doesn't work well if placed back 
        //to back in a function
        if (fade) {
            element.fade('in');
        }
        spt.panel.is_refreshing = false;
    }
}




spt.panel.set_hash = function(panel_id, class_name, options, kwargs) {

    alert("spt.panel.set_hash is DEPRECATED");

    // for now, ignore all panels that are not the main_body
    if ( document.id(panel_id).getAttribute('id') != 'main_body' ) {
        return;
    }

    // set the url for the /#/sobject/...
    var hash = [];

    var search_key = options['search_key'];
    if (class_name == 'tactic.ui.panel.SObjectPanelWdg' && kwargs.predefined){
        hash.push('sobject');

        if ( search_key != null ) {
            // because search keys are too close to url, we break it up
            // to pass through url encoding
            var parts = search_key.split(/[\?\&\=]/);
            var search_type = parts[0];
            var project_code = parts[2];
            var code = parts[4];
        }
        hash.push(search_type);
        hash.push(code);
        hash = hash.join('/');
    }

    // skip if empty
    if (hash == "") {
        return;
    }

    hash = '#/' + hash;
    // set the url hash
    spt.last_hash = hash;
    window.location.hash = hash;

}

