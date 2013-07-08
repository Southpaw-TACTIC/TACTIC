
spt.mockup = {};


spt.mockup.set_classes_in_left_nav = function( page_name )
{
    var option_list = document.getElementsByClassName('rc_content_option');
    if( option_list.length < 1 ) {
        option_list = this.parent.document.getElementsByClassName('rc_content_option');
    }

    for( var i=0; i < option_list.length; i++ )
    {
        if( option_list[i] )  // make sure not NULL ... Safari can return NULL objects in these lists
        {
            if( option_list[i].id == page_name ) {
                spt.add_class( option_list[i], "rc_content_selected" );
            }
            else {
                spt.remove_class( option_list[i], "rc_content_selected" );
            }
        }
    }
}


spt.mockup.toggle_resize_debug = function( evt )   // GOOD!
{
    if( ! evt ) { evt = window.event; }

    var el_list = document.getElementsByClassName("header_cell_resize");
    for( var i=0; i < el_list.length; i++ ) {
        var el = el_list[i];
        if( el.hasClass ) {
            if( el.hasClass("debug_cell_resize") ) {
                el.removeClass("debug_cell_resize");
            } else {
                el.addClass("debug_cell_resize");
            }
        }
    }
}


// ------------- pop-up menu functions ---------------------------


spt.mockup.menu_action = function( action_function, action_menu_id )
{
    var el_list2 = document.getElementsByClassName( "maq_action_menu_popup" );
    var el2 = undefined;

    for( var i=0; i < el_list2.length; i++ )
    {
        var el = el_list2[i];
        if( el.id == action_menu_id ) {
            el2 = el;
        }
    }

    if( el2 ) {
        el2.style.visibility = "hidden";
    }

    if( action_function )
    {
        action_function();
    }
}


spt.mockup.get_action = function( action_type_id, action_menu_id )
{
    var el_list = document.getElementsByClassName( 'maq_action_menu_button' );
    var offset_info = undefined;

    for( var i=0; i < el_list.length; i++ )
    {
        var el = el_list[i];
        if( el.id == action_type_id ) {
            offset_info = get_total_offset_info( el );
        }
    }

    if( offset_info )
    {
        var el_list2 = document.getElementsByClassName( "maq_action_menu_popup" );
        var el2 = undefined;

        for( var i=0; i < el_list2.length; i++ )
        {
            var el = el_list2[i];
            if( el.id == action_menu_id ) {
                el2 = el;
            }
        }

        if( el2 ) {
            if( el2.style.visibility != "visible" )
            {
                var top_pos = offset_info.top + offset_info.height;
                var right_pos = offset_info.left + offset_info.width;

                el2.style.top = top_pos;
                el2.style.left = right_pos - el2.clientWidth - 1;
                /*
                el2.style.top = 0;
                el2.style.right = 0;
                */
                el2.style.visibility = "visible";
            }
            else {
                el2.style.visibility = "hidden";
            }
        }
    }
}

/*
   clientWidth 55
   clientHeight 12
   offsetLeft 1143
   offsetTop 80
   offsetWidth 57
   offsetHeight 14
   scrollLeft 0
   scrollTop 0
   scrollWidth 57
   scrollHeight 14
*/

spt.mockup.get_total_offset_info = function( el )
{
    var left_offset = 0;
    var top_offset = 0;

    var offset_width = el.offsetWidth;
    var offset_height = el.offsetHeight;

    while( el )
    {
        left_offset = left_offset + el.offsetLeft;
        top_offset = top_offset + el.offsetTop;
        el = el.offsetParent;
    }

    return { 'left' : left_offset, 'top' : top_offset, 'width' : offset_width, 'height' : offset_height };
}

spt.mockup.sort_table = function( headers, rows )
{
    var el_list = document.getElementsByClassName( "sort_column" );
    var el = el_list[0];

    var reg = /des/;
    var replace_str = 'asc';

    if( el.innerHTML.match( /asc/ ) ) {
        reg = /asc/;
        replace_str = 'des';
    }

    rows.reverse();
    generate_table( "maq_view_table_div", headers, rows );

    el_list = document.getElementsByClassName( "sort_column" );
    el = el_list[0];
    el.innerHTML = el.innerHTML.replace( reg, replace_str );
}



