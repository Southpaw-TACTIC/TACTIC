// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2009, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.named_events = {};

// _event_map is of format: { 'event_name' : { <el_id': {'element': <el>, 'bvr': {...}} } }
spt.named_events._event_map = {};
spt.named_events._element_events_map = {};  // { <element_id> : [ { 'event_name': <name>, 'arr_index': <idx> } ] }


spt.named_events._register_listener = function( event_name, listen_bvr )
{
    var listen_el = listen_bvr.src_el;
    if( ! listen_el.get('id') ) {
        listen_el.set('id', spt.unique_id.get_next());
    }
    var listen_id = listen_el.get('id');

    if( ! spt.named_events._event_map.hasOwnProperty( event_name ) ) {
        spt.named_events._event_map[ event_name ] = {};
    }

    if( !(listen_id in spt.named_events._event_map[ event_name ]) ) {
        spt.named_events._event_map[ event_name ][ listen_id ] = [];
    }
    spt.named_events._event_map[ event_name ][ listen_id ].push( { 'element': listen_el, 'bvr': listen_bvr } );

    // Also add event name to element's event list, mapped by element ID ...
    if( ! spt.named_events._element_events_map.hasOwnProperty( listen_id ) ) {
        spt.named_events._element_events_map[ listen_id ] = [];
    }
    spt.named_events._element_events_map[ listen_id ].push( event_name );
}


spt.named_events.has_listeners = function( event_name )
{
    if( spt.named_events._event_map.hasOwnProperty( event_name ) ) {
        if( spt.named_events._event_map[event_name] ) {
            for( var name in spt.named_events._event_map[event_name] ) {
                if( spt.named_events._event_map[event_name].hasOwnProperty( name ) ) {
                    return true;
                }
            }
        }
    }

    return false;
}


spt.named_events._clear_event_for_element = function( event_name, el_id )
{
    var arr = spt.named_events._element_events_map[ el_id ];
    var idx = -1;

    for( var i=0; i < arr.length; i++ ) {
        if( arr[i] == event_name ) {
            idx = i;
            break;
        }
    }

    if( idx > -1 ) {
        // remove the array element at idx ...
        spt.named_events._element_events_map[ el_id ] = arr.slice(0,idx).concat( arr.slice(idx+1) );
    }
}


spt.named_events.purge_listener_element = function( element )
{
    var el_id = element.get('id');
    if( ! spt.named_events._element_events_map.hasOwnProperty( el_id ) ) {
        return;
    }

    var events_list = spt.named_events._element_events_map[ el_id ];
    for( var c=0; c < events_list.length; c++ ) {
        var event_name = events_list[c];
        spt.named_events._clear_event_for_element( event_name, el_id );
        delete spt.named_events._event_map[ event_name ][ el_id ];
    }

    if( spt.obj_is_empty( spt.named_events._element_events_map[ el_id ] ) ) {
        delete spt.named_events._element_events_map[ el_id ];
    }

    if( spt.obj_is_empty( spt.named_events._event_map[ event_name ] ) ) {
        delete spt.named_events._event_map[ event_name ];
    }
}


spt.named_events.element_is_registered = function( element )
{
    var el_id = element.get('id');
    if( spt.named_events._element_events_map.hasOwnProperty( el_id ) ) {
        return true;
    }
    return false;
}


spt.named_events._execute_listeners = function( event_name, firing_element, firing_data )
{
    if (!spt.named_events._event_map[ event_name ])
    {
        // -- commenting out this warning, as there will be many times we'll fire an event without having
        // -- listeners necessarily registered for it ... just return and don't do any processing
        //
        // spt.js_log.warning("WARNING: attempting to fire a named event ["+ event_name 
        //     + "], but event name has not been registered.");
        return
    }

    for( var listener_id in spt.named_events._event_map[ event_name ] ) {
        if( ! spt.named_events._event_map[ event_name ].hasOwnProperty( listener_id ) ) { continue; }

        var listener_list = spt.named_events._event_map[ event_name ][ listener_id ];

        for( var c=0; c < listener_list.length; c++ )
        {
            var listener = listener_list[c];
            if (listener.bvr.disabled) {
                continue;
            }
            // run preaction call-back, if specified ...
            if( listener.bvr.cbjs_preaction ) {
                spt.behavior.run_cbjs( listener.bvr.cbjs_preaction, listener.bvr, null, null );
            }
            else if( listener.bvr.hasOwnProperty('cbfn_preaction') ) {
                var target_options = {};
                if( listener.bvr.hasOwnProperty('options') ) {
                    target_options = listener.bvr.options;
                }
                listener.bvr.cbfn_preaction( event_name, firing_element, firing_data,
                                             listener.element, target_options );
            }

            // run action call-back ...
            if( listener.bvr.cbjs_action ) {
                listener.bvr.firing_element = firing_element;
                //listener.bvr.src_el = firing_element;
                listener.bvr.firing_data = firing_data;
                spt.behavior.run_cbjs( listener.bvr.cbjs_action, listener.bvr, null, null );
            }
            else if( listener.bvr.hasOwnProperty('cbfn_action') ) {
                var target_options = {};
                if( listener.bvr.hasOwnProperty('options') ) {
                    target_options = listener.bvr.options;
                }
                listener.bvr.cbfn_action( event_name, firing_element, firing_data, listener.element, target_options );
            } else {
                spt.js_log.warning("No callback found for element with ID '" + listener.element.get('id') +
                                   "' for fired event named '" + event_name + "'");
            }

            // run postaction call-back, if specified ...
            if( listener.bvr.cbjs_postaction ) {
                spt.behavior.run_cbjs( listener.bvr.cbjs_postaction, listener.bvr, null, null );
            }
            else if( listener.bvr.hasOwnProperty('cbfn_postaction') ) {
                var target_options = {};
                if( listener.bvr.hasOwnProperty('options') ) {
                    target_options = listener.bvr.options;
                }
                listener.bvr.cbfn_postaction( event_name, firing_element, firing_data,
                                              listener.element, target_options );
            }
        }
    }
}


// this fire_cbk call-back will be attached to an on-click event ...
//
spt.named_events.fire_cbk = function( evt, bvr, mouse_411 )
{
    if( ! bvr.hasOwnProperty("cb_fire_named_event") ) {
        spt.js_log.debug("WARNING: attempting to fire a named event, but no event name specified " +
                         "[in spt.named_events.fire_cbk()]")
        return false;  // do nothing ... no event name found to fire with!
    }

    spt.named_events.fire_event( bvr.cb_fire_named_event, bvr );
}


// NEW usage for specifying named event fire call-back ... use 'cbjs_' + [ 'action' | 'preaction' | 'postaction' ]
// parameter with this following call-back method (only need to provide event name) ...
//
//    e.g.  bvr = { 'type': 'click_up', 'cbjs_action': 'spt.named_events.fire_event("blah",bvr);' }
//
spt.named_events.fire_event = function( event_name, bvr )
{

    if (!bvr) {
        bvr = {};
    }

    var execute_listeners_flag = true;
    if( bvr.cbjs_preprocess ) {
        spt.behavior.run_cbjs( bvr.cbjs_preprocess, bvr, null, null );
    }
    else if( bvr.cbfn_preprocess ) {
        execute_listeners_flag = bvr.cbfn_preprocess( event_name, bvr );
    }

    if( execute_listeners_flag ) {
        var firing_element = bvr.src_el;
        var firing_data = {};
        if( bvr.hasOwnProperty("options") ) {
            firing_data = bvr.options;
        }

        spt.named_events._execute_listeners( event_name, firing_element, firing_data );
    }

    if( bvr.cbjs_postprocess ) {
        spt.behavior.run_cbjs( bvr.cbjs_postprocess, bvr, null, null );
    }
    else if( bvr.cbfn_postprocess ) {
        bvr.cbfn_postprocess( event_name, bvr, execute_listeners_flag );
    }
}


spt.named_events._process_listener_bvr = function( bvr, unique )
{
    var event_name_list = [];
    // Can have multiple "named event" listen behaviors ...
    if( spt.get_typeof( bvr.event_name ) == 'array' ) {
        for( var c=0; c < bvr.event_name.length; c++ ) {
            event_name_list.push( bvr.event_name[c] );
        }
    }
    else {
        event_name_list.push( bvr.event_name );
    }


    if (bvr.bvr_match_class) {
        var src_el = bvr.src_el;
        var listen_els = src_el.getElements("."+bvr.bvr_match_class);

        for (var i = 0; i < listen_els.length; i++) {

            for( var c = 0; c < event_name_list.length; c++ ) {
                var event_name =  event_name_list[c];
                if (unique && spt.named_events.has_listeners(event_name)) {
                    continue;
                }

                var new_bvr = {};
                for (var name in bvr) {
                    new_bvr[name] = bvr[name];
                }
                new_bvr.src_el = listen_els[i];

                spt.named_events._register_listener(event_name, new_bvr);
            }
        }

        // if there is no match class, then be backwards compatible
        if (listen_els.length == 0) {
            for( var c=0; c < event_name_list.length; c++ ) {
                var event_name =  event_name_list[c];
                if (unique && spt.named_events.has_listeners(event_name)) {
                    continue;
                }

                spt.named_events._register_listener(event_name, bvr);
            }
        }

    }
    else {

        for( var c=0; c < event_name_list.length; c++ ) {
            var event_name =  event_name_list[c];
            if (unique && spt.named_events.has_listeners(event_name)) {
                continue;
            }

            spt.named_events._register_listener(event_name, bvr);
        }
    }
}


// Access to adding named event listeners dynamically on the client-side

spt.named_events.add_listener = function( listener_el, event_name, bvr )
{
    bvr.src_el = listener_el;
    bvr.type = "listen";
    bvr.event_name = event_name;

    spt.named_events._process_listener_bvr( bvr );
}


