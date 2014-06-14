###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["TileLayoutWdg"]

import re
from pyasm.common import Common
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table, SpanWdg
from pyasm.widget import ThumbWdg, IconWdg, TextWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg, ActionButtonWdg

from tool_layout_wdg import ToolLayoutWdg

class TileLayoutWdg(ToolLayoutWdg):

    ARGS_KEYS = ToolLayoutWdg.ARGS_KEYS.copy()
    ARGS_KEYS['top_view'] = {
            'description': 'an optional custom layout for the title area of the tile',
            'order' : '01',
            'category': 'Display'
        }


    ARGS_KEYS['bottom_view'] = {
            'description': 'an optional custom layout for the bottom area of the tile',
            'order' : '02',
            'category': 'Display'
        }

    ARGS_KEYS['show_scale'] = {
            'description': 'If set to true, the scale slider bar is displayed',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order' : '03',
            'category': 'Display'
    }
    ARGS_KEYS['scale'] = {
            'description': 'Initial Scale. If not set, it defaults to 100',
            'type': 'TextWdg',
            'order' : '04',
            'category': 'Display'

    }
    ARGS_KEYS['sticky_scale'] = {
            'description': 'If set to local, the scale is sticky in the current view until page refresh',
            'type': 'SelectWdg',
            'values': 'local|global',
            'order' : '05',
            'category': 'Display'

    }
    ARGS_KEYS['styles'] = {
            'description': 'styles in a string that can be applied to the top container of this Tile Layout',
            'type': 'TextWdg',
            'order' : '06',
            'category': 'Display'

    }
    ARGS_KEYS['aspect_ratio'] = {
            'description': 'Custom aspect ratio like 240,110 for the tiles',
            'type': 'TextWdg',
            'order' : '07',
            'category': 'Display'

    }
    ARGS_KEYS['spacing'] = {
            'description': 'Custom tile spacing between tiles',
            'type': 'TextWdg',
            'order' : '08',
            'category': 'Display'

    }

    


    def can_select(my):
        return True

    def can_expand(my):
        return True

    def get_expand_behavior(my):
        return {
            'type': 'click_up',
            'cbjs_action': '''
            var layout = spt.tile_layout.set_layout(bvr.src_el);

            // get the current scale
            var scale = spt.tile_layout.get_scale();
            if (scale) scale = parseInt(scale);

            if (scale == 100) {
                scale = layout.getAttribute("last_scale");
                if (scale) scale = parseInt(scale)
                else scale = 100
            }
            else {
                layout.setAttribute("last_scale", scale);
                scale = 100;
            }


            spt.tile_layout.set_scale(scale);
            '''

        }


    def get_content_wdg(my):
        div = DivWdg()
        div.add_class("spt_tile_layout_top")
        if my.top_styles:
            div.add_styles(my.top_styles)
        inner = DivWdg()
        div.add(inner)


        
        menus_in = {}
        # set up the context menus
        if my.show_context_menu == True:
            menus_in['DG_HEADER_CTX'] = [ my.get_smart_header_context_menu_data() ]
            menus_in['DG_DROW_SMENU_CTX'] = [ my.get_data_row_smart_context_menu_details() ]
        elif my.show_context_menu == 'none':
            div.add_event('oncontextmenu', 'return false;')
        if menus_in:
            SmartMenu.attach_smart_context_menu( inner, menus_in, False )
 




        

        temp = my.kwargs.get("temp")
        has_loading = False

        
        inner.add_style("margin-left: 20px")
       

        inner.add_attr("ondragenter", "return false")
        inner.add_attr("ondragover", "return false")
        inner.add_attr("ondrop", "spt.thumb.background_drop(event, this)")

        inner.add("<br clear='all'/>")

        if my.sobjects:
            inner.add( my.get_scale_wdg() )

            for row, sobject in enumerate(my.sobjects):

                if False and not temp and row > 4: 
                    tile_wdg = DivWdg()
                    inner.add(tile_wdg)
                    tile_wdg.add_style("width: 120px")
                    tile_wdg.add_style("height: 120px")
                    tile_wdg.add_style("float: left")
                    tile_wdg.add_style("padding: 20px")
                    tile_wdg.add_style("text-align: center")
                    tile_wdg.add('<img src="/context/icons/common/indicator_snake.gif" border="0"/>')
                    tile_wdg.add(" Loading ...")
                    tile_wdg.add_attr("spt_search_key", sobject.get_search_key())
                    tile_wdg.add_class("spt_loading")
                    has_loading = True
                    continue


                kwargs = my.kwargs.copy()
                tile = my.get_tile_wdg(sobject)
                inner.add(tile)
        else:
            table = Table()
            inner.add(table)
            my.handle_no_results(table)


        chunk_size = 5
        if has_loading:
            inner.add_behavior( {
            'type': 'load',
            'chunk': chunk_size,
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);
            var rows = layout.getElements(".spt_loading");

            var jobs = [];
            var count = 0;
            var chunk = bvr.chunk;
            while (true) {
                var job_item = rows.slice(count, count+chunk);
                if (job_item.length == 0) {
                    break;
                }
                jobs.push(job_item);
                count += chunk;
            }

            var count = -1;
            var func = function() {
                count += 1;
                var rows = jobs[count];
                if (! rows || rows.length == 0) {
                    return;
                }
                for (var i = 0; i < rows.length; i++) {
                    rows[i].removeClass("spt_loading");
                }
                spt.table.refresh_rows(rows, null, null, {on_complete: func});
            }
            func();

            '''
            } )





        inner.add("<br clear='all'/>")
        return div



    def init(my):
        my.scale_called = False
        my.scale = None
        top_view = my.kwargs.get("top_view")
        if top_view:
            kwargs = {
                'view': top_view,
            }
            from tactic.ui.panel import CustomLayoutWdg
            my.title_wdg = CustomLayoutWdg(**kwargs)
        else:
            my.title_wdg = None
        my.sticky_scale = my.kwargs.get('sticky_scale')
        if my.sticky_scale == 'local':
            # NOTE: each side bar link has a unique name on each level, but it's not always available
            # not in page refresh or built-in links
            # element = my.kwargs.get('element_name')
            my.scale_prefix = '%s:%s' %(my.search_type, my.view)
        else:
            my.scale_prefix = ''
        
        bottom_view = my.kwargs.get("bottom_view")
        if bottom_view:
            kwargs = {
                'view': bottom_view,
                'load': 'sequence',
            }
            from tactic.ui.panel import CustomLayoutWdg
            my.bottom = CustomLayoutWdg(**kwargs)
        else:
            my.bottom = None

        from tactic.ui.filter import FilterData
        filter_data = FilterData.get()
        data_list = filter_data.get_values_by_prefix("tile_layout")
        if data_list:
            data = data_list[0]
        else:
            data = {}
        

        my.scale = data.get("scale")
        if my.scale == None:
            my.scale = my.kwargs.get("scale")
        if my.scale == None:
            my.scale = 100


        my.aspect_ratio = my.kwargs.get('aspect_ratio')
        if my.aspect_ratio:
            parts = re.split('[\Wx]+', my.aspect_ratio)
            my.aspect_ratio = (int(parts[0]), int(parts[1]))
        else:
            my.aspect_ratio = (240, 160)


        my.top_styles = my.kwargs.get('styles')
        my.spacing = my.kwargs.get('spacing')
        if not my.spacing:
            my.spacing = '10'

        super(TileLayoutWdg, my).init()


    def add_layout_behaviors(my, layout_wdg):

        layout_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_tile_detail',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var top = bvr.src_el.getParent(".spt_tile_top");
            var search_key = top.getAttribute("spt_search_key");
            var name = top.getAttribute("spt_name");
            var search_code = top.getAttribute("spt_search_code");
            var class_name = 'tactic.ui.tools.SObjectDetailWdg';
            //var class_name = 'tactic.ui.tools.RepoBrowserContentWdg';
            var kwargs = {
                search_key: search_key
            };
            spt.tab.add_new(search_code, name, class_name, kwargs);
            '''
        } )

        mode = my.kwargs.get("expand_mode")
        if not mode:
            mode = "gallery"

        gallery_width = my.kwargs.get("gallery_width")
        if not gallery_width:
            gallery_width = ''
        if mode == "view":
            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_tile_content',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_tile_top");
                var search_key = top.getAttribute("spt_search_key");
                var server = TacticServerStub.get();
                var snapshot = server.get_snapshot(search_key, {context: "", process:"publish",include_web_paths_dict:true});
                if (snapshot.__search_key__) {
                    window.open(snapshot.__web_paths_dict__.main);
                }
                else {
                    var snapshot = server.get_snapshot(search_key, {context: "",include_web_paths_dict:true});
                    if (snapshot.__search_key__) {
                        window.open(snapshot.__web_paths_dict__.main);
                    }
                    else {
                        alert("WARNING: No file for this asset");
                    }
                }
                '''
            } )
        elif mode == "gallery":
            gallery_div = DivWdg()
            layout_wdg.add( gallery_div )
            gallery_div.add_class("spt_tile_gallery")

            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'width': gallery_width,
                'bvr_match_class': 'spt_tile_content',
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                var tile_tops = layout.getElements(".spt_tile_top");

                var search_keys = [];
                for (var i = 0; i < tile_tops.length; i++) {
                    var tile_top = tile_tops[i];
                    var search_key = tile_top.getAttribute("spt_search_key");
                    search_keys.push(search_key);
                }

                var tile_top = bvr.src_el.getParent(".spt_tile_top");
                var search_key = tile_top.getAttribute("spt_search_key");

                var class_name = 'tactic.ui.widget.gallery_wdg.GalleryWdg';
                var kwargs = {
                    search_keys: search_keys,
                    search_key: search_key,
                };
                if (bvr.width) 
                    kwargs['width'] = bvr.width;
                var gallery_el = layout.getElement(".spt_tile_gallery");
                spt.panel.load(gallery_el, class_name, kwargs);



                '''
            } )
 



        bg1 = layout_wdg.get_color("background3")
        bg2 = layout_wdg.get_color("background3", 5)
        layout_wdg.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "0.8");
            var el = bvr.src_el.getElement(".spt_tile_title");
            if (el)
                el.setStyle("background", "%s");
            ''' % bg2
        } )

        layout_wdg.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            var el = bvr.src_el.getElement(".spt_tile_title");
            if (el)
                el.setStyle("background", "%s");
            ''' % bg1
        } )



        layout_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            spt.thumb = {};

            spt.thumb.background_drop = function(evt, el) {
                evt.stopPropagation();
                evt.preventDefault();

                var top = $(el);
                top.setStyle("background", "#0F0");
            }
 

            spt.thumb.noop = function(evt, el) {
                evt.stopPropagation();
                evt.preventDefault();
                evt.dataTransfer.dropEffect = 'copy';
                var files = evt.dataTransfer.files;

                var top = $(el);
                var thumb_el = top.getElement(".spt_thumb_top");

                for (var i = 0; i < files.length; i++) {
                    var size = files[i].size;
                    var file = files[i];

                    setTimeout( function() {
                        var loadingImage = loadImage(
                            file,
                            function (img) {
                                thumb_el.innerHTML = "";
                                thumb_el.appendChild(img);
                            },
                            {maxWidth: 240, canvas: true, contain: true}
                        );
                    }, 0 );


                    var search_key = top.getAttribute("spt_search_key");
                    var filename = file.name;
                    var context = "publish" + "/" + filename;



                    var upload_file_kwargs =  {
                        files: files,
                        upload_complete: function() {
                            var server = TacticServerStub.get();
                            var kwargs = {mode: 'uploaded'};
                            server.simple_checkin( search_key, context, filename, kwargs);
                        }
                    };
                    spt.html5upload.upload_file(upload_file_kwargs);
         


     
                }
            }
            '''
        } )

        
        border = layout_wdg.get_color("border")

        layout_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'border': border,
            'bvr_match_class': 'spt_tile_select',
            'cbjs_action': '''
            if (evt.shift == true) {

                spt.table.set_table(bvr.src_el);
                var row = bvr.src_el.getParent(".spt_table_row");


                var rows = spt.table.get_all_rows(true);
                var last_selected = spt.table.last_selected_row;
                var last_index = -1;
                var cur_index = -1;
                for (var i = 0; i < rows.length; i++) {
                    if (rows[i] == last_selected) {
                        last_index = i;
                    }
                    if (rows[i] == row) {
                        cur_index = i;
                    }

                    if (cur_index != -1 && last_index != -1) {
                        break;
                    }

                }
                var start_index;
                var end_index;
                if (last_index < cur_index) {
                    start_index = last_index;
                    end_index = cur_index;
                }
                else {
                    start_index = cur_index;
                    end_index = last_index;
                }


                var select = last_selected.hasClass("spt_table_selected");
                for (var i = start_index; i < end_index+1; i++) {

                    var row = rows[i];
                    var checkbox = row.getElement(".spt_tile_checkbox");

                    if (!select) {
                        checkbox.checked = false;
                        row.removeClass("spt_table_selected");

                        row.setStyle("border", "solid 1px " + bvr.border);
                        var size = row.getSize();
                        row.setStyle("width", size.x+6);
                        row.setStyle("height", size.y+6);


                    }
                    else {
                        checkbox.checked = true;
                        //row.addClass("spt_table_selected");
                        var size = row.getSize();
                        row.setStyle("width", size.x-10);
                        row.setStyle("height", size.y-10);
                        row.setStyle("border", "solid 5px yellow");
                        spt.table.select_row(row);

                    }
                }

            }
            else {

                var row = bvr.src_el.getParent(".spt_table_row");
                var checkbox = bvr.src_el.getElement(".spt_tile_checkbox");

                if (checkbox.checked == true) {
                    checkbox.checked = false;
                    row.removeClass("spt_table_selected");

                    row.setStyle("border", "solid 1px " + bvr.border);

                    var size = row.getSize();
                    row.setStyle("width", size.x+6);
                    row.setStyle("height", size.y+6);

                }
                else {
                    checkbox.checked = true;
                    //row.addClass("spt_table_selected");

                    var size = row.getSize();
                    row.setStyle("width", size.x-10);
                    row.setStyle("height", size.y-10);
                    row.setStyle("border", "solid 5px yellow");
                    spt.table.select_row(row);



                }

            }

            '''
        } )





    def get_tile_wdg(my, sobject):

        div = DivWdg()
        div.add_class("spt_tile_top")
        div.add_style('margin', my.spacing)
        div.add_style('background-color','transparent')

        div.add_class("spt_table_row")
        div.add_class("spt_table_row_%s" % my.table_id)

        if my.kwargs.get("show_title") not in ['false', False]:
            if my.title_wdg:
                my.title_wdg.set_sobject(sobject)
                div.add(my.title_wdg.get_buffer_display())
            else:
                title_wdg = my.get_title(sobject)
                div.add( title_wdg )

        div.add_attr("spt_search_key", sobject.get_search_key())
        div.add_attr("spt_name", sobject.get_name())
        div.add_attr("spt_search_code", sobject.get_code())

        SmartMenu.assign_as_local_activator( div, 'DG_DROW_SMENU_CTX' )

        
        if my.kwargs.get("show_drop_shadow") not in ['false', False]:
            div.set_box_shadow()
        div.add_color("background", "background", -3)
        
        div.add_style("overflow: hidden")

        div.add_style("float: left")

        thumb_div = DivWdg()
        #thumb_div.add_styles('margin-left: auto; margin-right: auto')
        thumb_div.add_class("spt_tile_content")
        #thumb_div.add_class("spt_tile_detail")
        div.add(thumb_div)


        
        thumb_div.add_style("width: %s" % my.aspect_ratio[0])

        thumb_div.add_style("height: %s" % my.aspect_ratio[1])
        #thumb_div.add_style("overflow: hidden")

        thumb = ThumbWdg2()
        thumb.set_sobject(sobject)
        thumb_div.add(thumb)
        thumb_div.add_border()

        #bottom_view = my.kwargs.get("bottom_view")
        #if bottom_view:
        #    div.add( my.get_view_wdg(sobject, bottom_view) )
        if my.bottom:
            my.bottom.set_sobject(sobject)
            div.add(my.bottom.get_buffer_display())


        div.add_attr("ondragenter", "return false")
        div.add_attr("ondragover", "return false")
        div.add_attr("ondrop", "spt.thumb.noop(event, this)")


        return div



    def get_view_wdg(my, sobject, view):
        div = DivWdg()
        #div.add_style("overflow: hidden")

        kwargs = {
            'view': view,
        }
        from tactic.ui.panel import CustomLayoutWdg
        layout = CustomLayoutWdg(**kwargs)
        layout.set_sobject(sobject)
        div.add(layout.get_buffer_display())
        return div



    def get_shelf_wdg(my):
        return my.get_scale_wdg()


    def get_scale_wdg(my):

        if my.scale_called == True:
            return None
        my.scale_called = True

        show_scale = my.kwargs.get("show_scale")

        div = DivWdg()
        if show_scale in [False, 'false']:
            div.add_style("display: none")
        div.add_style("padding: 5px")
        div.add_class("spt_table_search")
        hidden = HiddenWdg("prefix", "tile_layout")
        div.add(hidden)
        div.add_behavior( {
            'type': 'load',
            'scale_prefix':  my.scale_prefix,
            'default_scale': my.scale,
            'aspect_ratio': my.aspect_ratio,
            'cbjs_action': '''
spt.tile_layout = {}
spt.tile_layout.layout = null;

spt.tile_layout.set_layout = function(layout) {
    if (!layout.hasClass("spt_layout")) {
        layout = layout.getParent(".spt_layout");
    }
    spt.tile_layout.layout = layout;
    return layout;
}

spt.tile_layout.get_scale = function() {
    var scale_value = spt.tile_layout.layout.getElement(".spt_scale_value");
    var value = scale_value.value;
    value = parseInt(value);
    return value;
}


spt.tile_layout.set_scale = function(scale) {

    var scale_value = spt.tile_layout.layout.getElement(".spt_scale_value");
    scale_value.value = scale;

    var size_x = bvr.aspect_ratio[0]*scale/100;
    var size_y = bvr.aspect_ratio[1]*scale/100;

    //var top = bvr.src_el.getParent(".spt_tile_layout_top");
    var top = spt.tile_layout.layout;
    var els = top.getElements(".spt_tile_content");
    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        el.setStyle( "width",  size_x);
        el.setStyle( "height", size_y);
    }

    var container_id = "tile_layout::scale"+bvr.scale_prefix;
    spt.container.set_value( container_id, scale);
}


spt.tile_layout.drag_start_x = null;
spt.tile_layout.drag_start_value = null;

spt.tile_layout.drag_setup = function(evt, bvr, mouse_411) {
    spt.tile_layout.set_layout(bvr.src_el);
    spt.tile_layout.drag_start_x = mouse_411.curr_x;
    var src_el = spt.behavior.get_bvr_src( bvr );
    if (!src_el.value) {
        src_el.value = 0;
    }
    spt.tile_layout.drag_start_value = src_el.value;
    src_el.focus();
    src_el.select();
}
spt.tile_layout.drag_motion = function(evt, bvr, mouse_411) {
    var start_value = spt.tile_layout.drag_start_value; 
    if (isNaN(parseInt(start_value))) {
        return;
    }
    var dx = mouse_411.curr_x - spt.tile_layout.drag_start_x;
    var increment = parseInt(dx / 5);
    var multiplier;
    if (increment < 0)
        multiplier = 0.975;
    else
        multiplier = 1 / 0.975;
    increment = Math.abs(increment);
    var scale = spt.tile_layout.drag_start_value;
    for (var i = 0; i < increment; i++) {
        scale = scale * multiplier;
    }
    if (scale > 400)
        scale = 400;
    scale = parseInt(scale);
    spt.tile_layout.set_scale(scale);

}
spt.tile_layout.setup_control = function() {
   var slider = spt.tile_layout.layout.getElement('.spt_slider');
   var container_id = "tile_layout::scale"+bvr.scale_prefix;
   var initial_value = spt.container.get_value(container_id) ?  spt.container.get_value(container_id) : bvr.default_scale;

   spt.tile_layout.set_scale(initial_value);
   new Slider(slider, slider.getElement('.knob'), {
    range: [30, 400],
    steps: 74,
    initialStep: initial_value,
    onChange: function(value){
      if (value) spt.tile_layout.set_scale(value);
    }
  });
}


        ''' } )


        div.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.tile_layout.set_layout(bvr.src_el);

        spt.tile_layout.setup_control();
      
        '''
        } )


        table = Table()
        div.add(table)
        table.add_row()

        """
        # TO BE DELETED
        less_div = DivWdg()
        less_div.add("<input type='button' value='&lt;&lt;'/>")
        table.add_cell(less_div)

        less_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tile_layout.set_layout(bvr.src_el);
            var scale = spt.tile_layout.get_scale();
            scale = scale * 0.95;
            scale = parseInt(scale);
            spt.tile_layout.set_scale(scale);
            '''
        } )
        """

        dark_color = div.get_color("background", -5)
        light_color = div.get_color('color')
        med_color = div.get_color('color2')
        
        slider_div = DivWdg(css='spt_slider')
        slider_div.add_styles('valign: bottom; background: %s; height: 6px; width: 200px;'% light_color)
        knob_div = DivWdg(css='knob')
        knob_div.add_behavior({'type':'click',
                'cbjs_action': 'spt.tile_layout.set_layout(bvr.src_el)'
                })
        knob_div.add_styles('background: %s; bottom: 4px;\
                height: 16px; width: 12px; border-radius: 6px 6px 0 0;\
                border: 1px %s solid'\
                %(dark_color, med_color ))
        slider_div.add(knob_div)
        td = table.add_cell(slider_div)
        value_wdg = TextWdg("scale")
        value_wdg.add_class("spt_scale_value")
        td = table.add_cell(value_wdg)
        td.add("&nbsp;%")

        td.add_style("padding: 3px 8px")

        """
        # TO BE DELETED
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get()
        data_list = filter_data.get_values_by_prefix("tile_layout")
        if data_list:
            data = data_list[0]
        else:
            data = {}
        my.scale = data.get("scale")
        if my.scale == None:
            my.scale = my.kwargs.get("scale")
        """
        if my.scale:
            value_wdg.set_value(my.scale)
        value_wdg.add_style("width: 24px")
        value_wdg.add_style("text-align: center")
        value_wdg.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var value = bvr.src_el.value;
        var scale = parseInt(value);
        spt.tile_layout.set_layout(bvr.src_el);
        spt.tile_layout.set_scale(scale);
        '''
        } )
        value_wdg.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        var value = bvr.src_el.value;
        if (!value) {
            value = 100;
        }
        var scale = parseInt(value);
        spt.tile_layout.set_layout(bvr.src_el);
        spt.tile_layout.set_scale(scale);
        '''
        } )



 
        value_wdg.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_scale_value',
            'ignore_default_motion' : True,
            "cbjs_setup": 'spt.tile_layout.drag_setup( evt, bvr, mouse_411 );',
            "cbjs_motion": 'spt.tile_layout.drag_motion( evt, bvr, mouse_411 );'
        } )

        
        """
        # TO BE DELETED
        more_div = DivWdg()
        more_div.add("<input type='button' value='&gt;&gt;'/>")
        table.add_cell(more_div)

        more_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tile_layout.set_layout(bvr.src_el);
            var scale = spt.tile_layout.get_scale();
            scale = scale / 0.95;
            scale = parseInt(scale);
            spt.tile_layout.set_scale(scale);
            '''
        } )

        """


       

        return div


    def get_title(my, sobject):
        div = DivWdg()

        div.add_class("spt_tile_title")

        div.add_color("background", "background3")
        div.add_style("padding: 5px")
        div.add_style("height: 16px")


        detail_div = DivWdg()
        div.add(detail_div)
        detail_div.add_class("spt_tile_detail")
        detail_div.add_style("float: right")
        detail_div.add_style("margin-top: -2px")

        detail = IconButtonWdg(title="Detail", icon=IconWdg.ZOOM)
        detail_div.add(detail)


        header_div = DivWdg()
        header_div.add_class("spt_tile_select")
        header_div.add_class("hand")
        div.add(header_div)
        header_div.add_class("SPT_DTS")
        header_div.add_style("overflow-x: hidden")

        from pyasm.widget import CheckboxWdg
        checkbox = CheckboxWdg("select")
        checkbox.add_class("spt_tile_checkbox")

        title = sobject.get_name()
        if not title:
            title = sobject.get_code()
      
        table = Table()
        header_div.add(table)
        header_div.add_style("position: relative")

        table.add_cell(checkbox)

        title_div = DivWdg()
        td = table.add_cell(title_div)
        title_div.add(title)
        title_div.add_style("height: 15px")
        title_div.add_style("left: 25px")
        title_div.add_style("top: 3px")
        title_div.add_style("position: absolute")
        title_div.add_attr("title", title)
        #title_div.add_style("white-space", "nowrap")
        #td.add_style("overflow: hidden")
        title_div.add("<br clear='all'/>")


        description = sobject.get_value("description", no_exception=True)
        if description:
            div.add_attr("title", sobject.get_code())



        return div


from pyasm.biz import Snapshot
from pyasm.web import HtmlElement
__all__.append("ThumbWdg2")
class ThumbWdg2(BaseRefreshWdg):

    def init(my):
        my.path = None

    def set_sobject(my, sobject):
        super(ThumbWdg2, my).set_sobject(sobject)
        my.path = my.get_path_from_sobject(sobject)

    def set_path(my, path):
        my.path = path

    def get_path(my):
        return my.path



    def get_display(my):

        width = "100%"
        height = "100%"

        sobject = my.get_current_sobject()

        div = DivWdg()
        div.add_class("spt_thumb_top")

        path = my.path
        if path:
            img = HtmlElement.img(src=path)
        else:
            search_type = sobject.get_search_type_obj()
            path = my.get_path_from_sobject(search_type)
            if path:
                img = DivWdg()
                img.add_style("opacity: 0.2")

                img_inner = HtmlElement.img(src=path)
                img.add(img_inner)

                img_inner.add_style("width: %s" % width)

        if path and path.startswith("/context"):
            img.add_style("padding: 10px 15%")
            img.add_style("width: 70%")
        elif path:
            img.add_style("width: %s" % width)
            img.add_style("height: %s" % height)
            img.add_style('margin-left','auto')
            img.add_style('margin-right','auto')

        if not path:
            img = DivWdg()
        img.add_class("spt_image")
        div.add(img)

        div.add_style("height: 100%")


        return div


    def get_path_from_sobject(my, sobject):

        icon_path = None
        path = None

        search_type = sobject.get_search_type()
        search_code = sobject.get_value("code", no_exception=True)
        if not search_code:
            search_code = sobject.get_id()


        # FIXME: make this faster

        snapshot = Snapshot.get_snapshot(search_type, search_code, process=['icon','publish',''])

        if snapshot:
            file_type = "web"
            icon_path = snapshot.get_web_path_by_type(file_type)

            file_type = "main"
            path = snapshot.get_web_path_by_type(file_type)

        if icon_path:
            path = icon_path
        elif path:
            path = my.find_icon_link(path)

 
        return path


    def find_icon_link(my, file_path, repo_path=None):
        from pyasm.widget import ThumbWdg
        return ThumbWdg.find_icon_link(file_path, repo_path)





