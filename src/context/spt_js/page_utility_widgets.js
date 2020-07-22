// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.puw = {};


spt.puw.get_loaded_map = function()
{
    var loaded_map = {};
    var puw_loaded_list = document.getElements(".SPT_PUW_LOADED");
    for( var c=0; c < puw_loaded_list.length; c++ ) {
        var el = puw_loaded_list[c];
        loaded_map[ el.get("id") ] = el;
    }
    return loaded_map;
}


spt.puw.process_new = function( start )
{
    var puw_list = document.id(start).getElements(".SPT_PUW");
    var puw_loaded_map = spt.puw.get_loaded_map();

    var global_container = document.id("global_container");

    for( var c=0; c < puw_list.length; c++ ) {
        var el = puw_list[c];
        var id = el.get("id");
        if( id == "popup_template" ) {
            // do not process popup_template!  it is meant to stay pristine (as it was originally generated)
            // so that it can be cleanly copied from ...
            continue;
        }
        if( ! id ) {
            // ensure that the puw element has an ID! So, just generate a unique one if there is not one already
            id = spt.unique_id.get_next("puw");
            el.set( "id", id );
        }

        // remove from its parent and replace it with a puw_stub ...
        var stub = document.id(document.createElement("div"));
        stub.inject( el, "before" );

        stub.addClass("SPT_PUW_STUB");
        stub.setStyle("display","none");
        stub.spt_puw_el = el;  // link-to puw (store on the element object itself for immediate, efficient access)
        stub.setProperty("spt_puw_id", id);  // store PUW id for visual cue when looking at HTML

        el.spt_puw_stub_el = stub;  // link-back to stub

        var p = el.getParent();
        el = p.removeChild( el );
        if( puw_loaded_map.hasOwnProperty(id) ) {
            // already loaded so need to replace existing one with new one ...
            var el_to_replace = puw_loaded_map[ id ];
            var stub_to_replace = el_to_replace.spt_puw_stub_el;

            el.inject( el_to_replace, "before" );

            el_to_replace.getParent().removeChild( el_to_replace );
            spt.behavior.destroy_element( el_to_replace );

            //document.id(stub_to_replace).getParent().removeChild( stub_to_replace );
            // IE: for some reason, the parent can be null.  This was found
            // when opening and closing the subtask list repeatedly
            var parent_el = stub_to_replace.getParent();
            if (parent_el) {
                parent_el.removeChild( stub_to_replace );
                spt.behavior.destroy_element( stub_to_replace );
            }
        }
        else {
            // add this to the page ...
            var z = el.getProperty("spt_z_start");
            if( z ) { el.setStyle("z-index", z); }

            // add new PUW to bottom of contents in global_container ...
            el.inject( global_container, "bottom" );
        }

        puw_loaded_map[ id ] = el;

        el.removeClass("SPT_PUW");
        el.addClass("SPT_PUW_LOADED");
    }
}



spt.puw.get_all_puws = function(start_el) {
    var stub_list = document.id(start_el).getElements(".SPT_PUW_STUB");
    var puws = [];
    stubs.forEach( function(stub) {
        var puw =  stub.spt_puw_el;
        puws.push(puw);
    } )
    return puws
}
             


spt.puw.stubs_get_element = function( start_el, mt_search_str )
{
    var found_el = null;
    var stub_list = document.id(start_el).getElements(".SPT_PUW_STUB");

    for( var c=0; c < stub_list.length; c++ ) {
        var stub = stub_list[c];
        found_el = stub.spt_puw_el.getElement( mt_search_str );
        if( found_el ) {
            return found_el;
        }
    }

    return null;
}


spt.puw.stubs_get_elements = function( start_el, mt_search_str )
{
    var found_el_list = [];
    var stub_list = document.id(start_el).getElements(".SPT_PUW_STUB");

    for( var c=0; c < stub_list.length; c++ ) {
        var stub = stub_list[c];
        var el_list = stub.spt_puw_el.getElements( mt_search_str );
        found_el_list.concat( el_list );
    }

    return found_el_list;
}


spt.puw.get_elements_thru_stubs = function( start_el, mt_search_str, puw_ids )
{
    start_el = document.id(start_el);

    var puw_id_match = {};
    var match_to_puw_ids = false;
    if( puw_ids && puw_ids.length > 0 ) {
        for( var c=0; c < puw_ids.length; c++ ) {
            puw_id_match[ puw_ids[c] ] = puw_ids[c];
        }
        match_to_puw_ids = true;
    }

    var stubs = start_el.getElements(".SPT_PUW_STUB");
    var elements = [];
    for( var c=0; c < stubs.length; c++ ) {
        var puw_el = stubs[c].spt_puw_el;

        if( match_to_puw_ids && ! (puw_el.get("id") in puw_id_match) ) {
            continue;
        }

        // Be sure to check this current puw_el element also to see if it matches the search criteria
        // and if so, add it to the found elements list ...
        if( mt_search_str.match( /^\./ ) ) {
            if( puw_el.hasClass( mt_search_str.replace( /^\./, '' ) ) ) {
                elements.push( puw_el );
            }
        } else if( mt_search_str.match( /^\#/ ) ) {
            if( puw_el.get("id") == mt_search_str.replace( /^\#/, '' ) ) {
                elements.push( puw_el );
            }
        } else if( puw_el.tagName.toLowerCase() == mt_search_str ) {
            elements.push( puw_el );
        }

        // Now search the puw_el elements descendants for any matches ...
        
        els = puw_el.getElements( mt_search_str )
        if (els.length > 0 )
            els.forEach( function(el) {
                elements.push(el);
            })
            //elements = elements.concat( els ); // This doesn't work because els is not an array
    }

    return elements;
}


spt.puw.get_parent_thru_stub = function( el, mt_search_str )
{
    if (typeof(mt_search_str) == "undefined") {
        return null;
    }

    el = document.id(el);
    var puw_el = null;
    if( el.hasClass("SPT_PUW_LOADED") ) {
        puw_el = el;
    } else {
        puw_el = el.getParent(".SPT_PUW_LOADED");
    }

    if( ! puw_el ) {
        return null;
    }

    var stub_el = puw_el.spt_puw_stub_el;
    if (typeof(stub_el) == 'undefined') {
        return null;
    }


    var found_parent = stub_el.getParent( mt_search_str );

    return found_parent;
}


