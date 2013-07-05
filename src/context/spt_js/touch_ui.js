// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2010, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// -------------------------------------------------------------------------------------------------------------------
//  Functionality to support touch devices (like Apple iPad)
// -------------------------------------------------------------------------------------------------------------------

spt.touch_ui = {};


// tap multi command ...


//    bvr = { 'type': 'click_up',
//            'cbjs_action': 'spt.touch_ui.tap_multi_command( evt, bvr );',
//            'cbjs_multi_pre_select': 'log.error("WTF!");',
//            'multi_options': [
//                { 'title': 'Block Select', 'callback_key': 'cbjs_block_select' }
//            ]
//    }


spt.touch_ui.tap_multi = {};
spt.touch_ui.tap_multi.timeout_count = 0;


spt.touch_ui.tap_multi.show_options = function( evt, bvr )
{
    if( ! ('_options_el' in spt.touch_ui.tap_multi) ) {

        var div = document.createElement("div");

        div.setStyles({
            "background-color": "white",
            "-webkit-border-radius": "10px",
            "-webkit-border-top-left-radius": "0px",
            "padding": "10px",
            "display": "none",
            "position": "absolute",
            "z-index": "400",
            "width": "200px"
        });

        div.addClass("spt_tap_multi_options_div");

        spt.touch_ui.tap_multi._options_el = div;

        var global_container = document.getElement("#global_container");
        global_container.appendChild( div );
    }

    // first clear any previous stuff ...
    var options_el = spt.touch_ui.tap_multi._options_el;
    spt.behavior.replace_inner_html( options_el, "<div style='display: none'>&nbsp;</div>" );

    // now build the new options ...
    var multi_opts = bvr.multi_options;
    for( var c=0; c < multi_opts.length; c++ ) {
        var opt_div = document.createElement("div");
        options_el.appendChild( opt_div );

        opt_div.setStyles({
            "background-color": "grey",
            "border-color": "black",
            "-webkit-border-radius": "5px",
            "text-align": "center",
            "font-size": "12px",
            "font-weight": "bold",
            "color": "white",
            "height": "40px",
            "z-index": "401"
        });

        opt_div.innerHTML =  "<span style='font-size: 9px'><br/></span>" +
                             "<span style='font-size: 14px; font-weight: bold;'>" +
                             multi_opts[c].title + "</span>";

        // NOTE: tried using 'spt.behavior.add()' here and it only worked for the first option and only on the
        //       first time that the option is clicked ... very strange! But using the onclick directly works
        //       like a charm. Because this is done using an in-line function the callback does get evt and
        //       bvr appropriately, just like in the core behavior mechanism!
        //
        var stmt = "opt_div.onclick = function() { " + bvr[ multi_opts[c].callback_key ] +
                    "; document.getElement('.spt_tap_multi_options_div').setStyle('display','none'); }; ";
        eval(stmt);

        if( c+1 < multi_opts.length ) {
            var spacer_div = document.createElement("div");
            options_el.appendChild( spacer_div );
            spacer_div.setStyles( {
                    "background-color": "white",
                    "height": "5px"
            } );
        }
    }

    var e = evt;
    if( 'event' in e ) {
        e = evt.event;
    }
    var pos_left = e.clientX + 8 ;
    var pos_top = e.clientY;

    options_el.setStyle("display","");
    if( 'menu_width' in bvr ) {
        options_el.setStyle("width",bvr.menu_width);
    }
    options_el.setStyle("left", pos_left+"px");
    options_el.setStyle("top", pos_top+"px");

    spt.touch_ui.tap_multi.timeout_count ++ ;
    setTimeout(
        function() {
            if( spt.touch_ui.tap_multi.timeout_count < 2 ) {
                spt.touch_ui.tap_multi._options_el.setStyle("display","none");
            }
            spt.touch_ui.tap_multi.timeout_count -- ;
        },
        5000
    );
}


spt.touch_ui.tap_multi.cbk = function( evt, bvr )
{
    // ?
    if( 'cbjs_multi_pre_select' in bvr ) {
        spt.behavior.run_cbjs( bvr.cbjs_multi_pre_select, bvr, evt, null );
    }

    spt.touch_ui.tap_multi.show_options( evt, bvr );
}


// ---- drag and drop support -----

spt.touch_ui.drag = {};

spt.touch_ui.drag.current_drag_bvr = null;
spt.touch_ui.drag.info = { 'mouse_411': {} };


spt.touch_ui.drag.drop_cb_fn = function( evt )
{
    var cursor_pos = spt.mouse.get_abs_cusor_position(evt);

    var mouse_411 = spt.touch_ui.drag.info.mouse_411;

    mouse_411.curr_x = cursor_pos.x;
    mouse_411.curr_y = cursor_pos.y;

    spt.mouse.default_drag_motion( evt, spt.touch_ui.drag.current_drag_bvr, mouse_411 );

    spt.touch_ui.current_drag_bvr = null;
    spt.app_busy.hide();
}


spt.touch_ui.drag.do_nothing = function( evt )
{
    return true;
}


