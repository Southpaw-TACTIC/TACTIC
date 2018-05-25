// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// -------------------------------------------------------------------------------------------------------------------
//
//  MooTools based fx animation wrappers (contained in the spt.fx_anim object)
//
// -------------------------------------------------------------------------------------------------------------------

spt.fx_anim = {};

spt.fx_anim.toggle_slide_el = function( evt, bvr )
{
    //var slide_el_id = bvr.dst_el.get('id');
    var slide_el_id = bvr.dst_el

    if ( ! slide_el_id ) {
        return;
    }

    // NOTE: that if the Fx.Slide hasn't been created for the slide element then it is created,
    //       only on demand, as needed
    //
    if( ! bvr.hasOwnProperty( 'slide_el' ) ) {
        bvr.slide_el = new Fx.Slide( slide_el_id );
        if( bvr.dst_el.getStyle("display") == "none" ) {
            bvr.dst_el.setStyle("display", "");
            bvr.slide_el.hide();
        }
    }

    var direction = 'horizontal';
    if( bvr.slide_direction ) {
        direction = bvr.slide_direction;
    }

    bvr.slide_el.toggle(direction);
}



// -------------------------------------------------------------------------------------------------------------------
//
//  SPT fx functions (contained in the spt.fx object)
//
//  NOTE: these fx animation functions were written to compensate for limitations in MooTools fx animation
//        features (which tend to be based on static size elements).
//
// -------------------------------------------------------------------------------------------------------------------

spt.fx = {};

spt.fx.side_map = { 'horiz': 'width', 'vert': 'height', 'horizontal': 'width', 'vertical': 'height' };
spt.fx.c_side_map = { 'horiz': 'clientWidth', 'vert': 'clientHeight',
                      'horizontal': 'clientWidth', 'vertical': 'clientHeight'};

spt.fx.margin_map = { 'horiz': 'margin-left', 'vert': 'margin-top',
                      'horizontal': 'margin-left', 'vertical': 'margin-top' };


spt.fx.slide_anim_cbk = function( evt, bvr )
{
    if( ! bvr.hasOwnProperty('dst_el') ) {
        spt.js_log.warning("WARNING: no 'dst_el' value found for behavior on spt.fx_slide_cbk().");
        return false;
    }

    if( ! bvr.hasOwnProperty('options') ) {
        bvr.options = {};
    }

    var frame_rate = 24;
    var duration = 500;  // default to a half a second duration
    var direction = 'horiz';  // or 'vert'

    var options = bvr.options;
    if( options.hasOwnProperty('frame_rate') ) { frame_rate = parseInt( options.frame_rate ); }
    if( options.hasOwnProperty('duration') ) { duration = parseInt( options.duration ); }
    if( options.hasOwnProperty('direction') ) { direction = options.direction; }

    var interval = duration / frame_rate;    // e.g. 1000 ms / 24 frames per second = 41.667

    var slide_el = bvr.dst_el;
    var activator_el = bvr.src_el;
    if( ! activator_el.get('id') ) {
        activator_el.set('id', spt.unique_id.get_next());
    }

    var wrap_div = null;
    var slide_id = null;

    if( ! ('spt_fx' in slide_el) ) {
        // construct spt_fx slide info ...
        slide_el.spt_fx = {};
        slide_id = slide_el.get('id');
        if( ! slide_id ) {
            slide_id = spt.unique_id.get_next();
            slide_el.set('id', slide_id);
        }
        slide_el.addClass("SPT_FX");

        var display = slide_el.getStyle("display");
        if( display == "none" ) {
            slide_el.spt_fx.state = "closed";
            slide_el.setStyle( "display", "block" );
        } else {
            slide_el.spt_fx.state = "open";
        }

        // need to create wrapper div ...
        wrap_div  = new Element('div', {id: (slide_id + "_slide_wrapper")});
        wrap_div.setStyles( { margin: "0px", overflow: "hidden", position: "static" } );
        wrap_div.inject( slide_el, "before" );


        if( slide_el.spt_fx.state == 'closed' ) {
            wrap_div.setStyle( spt.fx.side_map[direction], 0 );
        } else {
            // assume 'open' otherwise ...
            wrap_div.setStyle( spt.fx.side_map[direction], '' );
        }

        slide_el.inject( wrap_div );
        slide_el.setStyle( "margin", 0 );
    }
    else {
        wrap_div = slide_el.parentNode;
        slide_id = slide_el.get('id');
    }

    slide_el.spt_fx.interval = interval;
    slide_el.spt_fx.duration = duration;
    slide_el.spt_fx.direction = direction;

    // Do setup for animation ...

    var abs_distance = 0;
    var stmt = 'abs_distance = parseInt( slide_el.' + spt.fx.c_side_map[direction] + ' );';
    eval(stmt);

    var frame_portion = duration / interval;
    var pixel_delta = 0;

    pixel_delta = Math.floor( (abs_distance / frame_portion) + 0.5 );

    if( slide_el.spt_fx.state == 'open' ) {
        wrap_div.setStyle( spt.fx.side_map[direction], abs_distance );
        slide_el.setStyle( "margin", 0 );
    }
    else {
        // otherwise closed ...
        wrap_div.setStyle( spt.fx.side_map[direction], 0 );
        slide_el.setStyle( spt.fx.margin_map[direction], (0 - abs_distance) );
    }
    slide_el.setStyle( "min-" + spt.fx.side_map[direction], abs_distance );

    slide_el.spt_fx.pixel_delta = pixel_delta;
    slide_el.spt_fx.abs_distance = abs_distance;
    slide_el.spt_fx.running_dist = 0;

    // launch the interval and launch the timeout ...
    //
    slide_el.spt_fx.interval_id = setInterval( "spt.fx._slide_anim_interval_fn('" + slide_id + "')", interval );
    setTimeout( "spt.fx._slide_anim_finish_fn('" + slide_id + "')", duration );
}


spt.fx._slide_anim_interval_fn = function( slide_el_id )
{
    var slide_el = document.id(slide_el_id);
    var slide_wrap = slide_el.parentNode;

    var fx = slide_el.spt_fx;

    fx.running_dist += fx.pixel_delta;

    var wrap_dist = 0;
    var margin_dist = 0;

    if( fx.state == "open" ) {
        wrap_dist = fx.abs_distance - fx.running_dist;
        if( wrap_dist < 0 ) { wrap_dist = 0; }
        margin_dist = 0 - fx.running_dist;
        if( margin_dist < (0 - fx.abs_distance) ) { margin_dist = 0 - fx.abs_distance; }
    } else {
        wrap_dist = fx.running_dist;
        if( wrap_dist > fx.abs_distance ) { wrap_dist = fx.abs_distance; }
        margin_dist = fx.running_dist - fx.abs_distance;
        if( margin_dist > 0 ) { margin_dist = 0; }
    }

    wrap_dist = Math.floor(wrap_dist + 0.5);
    margin_dist = Math.floor(margin_dist + 0.5);

    slide_el.setStyle( spt.fx.margin_map[fx.direction], margin_dist );
    slide_wrap.setStyle( spt.fx.side_map[fx.direction], wrap_dist );
}


spt.fx._slide_anim_finish_fn = function( slide_el_id )
{
    // make sure we are at the final state, and clear the interval ...
    var slide_el = document.id(slide_el_id);
    var slide_wrap = slide_el.parentNode;

    var fx = slide_el.spt_fx;

    // clear the interval ...
    if( fx.interval_id ) {
        clearInterval( fx.interval_id );
        fx.interval_id = null;
    }

    if( slide_el.spt_fx.state == 'open' ) {
        // make closed now ...
        slide_el.spt_fx.state = 'closed';

        slide_wrap.setStyle( spt.fx.side_map[fx.direction], 0 );
        slide_el.setStyle( spt.fx.margin_map[fx.direction], (0 - fx.abs_distance) );
    }
    else {
        // otherwise it was closed, and now it's open ...
        slide_el.spt_fx.state = 'open';

        slide_wrap.setStyle( spt.fx.side_map[fx.direction], '' );
        slide_el.setStyle( spt.fx.margin_map[fx.direction], 0 );
        slide_el.setStyle( "min-" + spt.fx.side_map[fx.direction], '' );
    }
}


