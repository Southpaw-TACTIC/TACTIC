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

from pyasm.common import Common
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table
from pyasm.widget import ThumbWdg, IconWdg, TextWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg, ActionButtonWdg



from tool_layout_wdg import ToolLayoutWdg
class TileLayoutWdg(ToolLayoutWdg):

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
        inner = DivWdg()
        div.add(inner)

        # set up the context menus
        menus_in = {
            'DG_HEADER_CTX': [ my.get_smart_header_context_menu_data() ],
            'DG_DROW_SMENU_CTX': [ my.get_data_row_smart_context_menu_details() ]
        }
        SmartMenu.attach_smart_context_menu( inner, menus_in, False )


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

        
        inner.add_style("margin-left: 20px")

        if my.sobjects:
            inner.add( my.get_scale_wdg() )

            for sobject in my.sobjects:
                kwargs = my.kwargs.copy()
                tile = my.get_tile_wdg(sobject)
                inner.add(tile)
        else:
            table = Table()
            inner.add(table)
            my.handle_no_results(table)


        inner.add("<br clear='all'/>")
        return div


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
            var class_name = 'tactic.ui.tools.SObjectDetailWdg'
            var kwargs = {
                search_key: search_key
            }
            spt.tab.add_new(search_code, name, class_name, kwargs);
            '''
        } )

        layout_wdg.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_tile_content',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_tile_top");
            var search_key = top.getAttribute("spt_search_key");
            var server = TacticServerStub.get();
            var snapshot = server.get_snapshot(search_key, {context: "", process:"publish",include_web_paths_dict:true});
            if (snapshot) {
                window.open(snapshot.__web_paths_dict__.main);
            }
            else {
                alert("Can't find file");
            }
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
            el.setStyle("background", "%s");
            ''' % bg2
        } )

        layout_wdg.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            var el = bvr.src_el.getElement(".spt_tile_title");
            el.setStyle("background", "%s");
            ''' % bg1
        } )



        layout_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            spt.thumb = {};

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

                    }
                    else {
                        checkbox.checked = true;
                        //row.addClass("spt_table_selected");
                        row.setStyle("border", "solid 1px yellow");
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

                }
                else {
                    checkbox.checked = true;
                    //row.addClass("spt_table_selected");
                    row.setStyle("border", "solid 1px yellow");
                    spt.table.select_row(row);

                }

            }

            '''
        } )





    def get_tile_wdg(my, sobject):

        div = DivWdg()
        div.add_class("spt_tile_top")

        div.add_class("spt_table_row")


        top_view = my.kwargs.get("top_view")
        if top_view:
            title_wdg = my.get_view_wdg(sobject, top_view)
        else:
            title_wdg = my.get_title(sobject)
        div.add( title_wdg )


        div.add_attr("spt_search_key", sobject.get_search_key())
        div.add_attr("spt_name", sobject.get_name())
        div.add_attr("spt_search_code", sobject.get_code())

        SmartMenu.assign_as_local_activator( div, 'DG_DROW_SMENU_CTX' )

        div.add_border()
        div.set_box_shadow()
        div.add_color("background", "background", -3)
        div.add_style("margin: 10px")
        div.add_style("overflow: hidden")

        div.add_style("float: left")

        thumb_div = DivWdg()
        thumb_div.add_class("spt_tile_content")
        #thumb_div.add_class("spt_tile_detail")
        div.add(thumb_div)

        width =  240
        height = 160

        thumb_div.add_style("width: %s" % width)
        thumb_div.add_style("height: %s" % height)
        thumb_div.add_style("overflow: hidden")

        thumb = ThumbWdg2()
        thumb.set_sobject(sobject)
        thumb_div.add(thumb)


        bottom_view = my.kwargs.get("bottom_view")
        if bottom_view:
            div.add( my.get_view_wdg(sobject, bottom_view) )



        div.add_attr("ondragenter", "return false")
        div.add_attr("ondragover", "return false")
        div.add_attr("ondrop", "spt.thumb.noop(event, this)")


        return div



    def get_view_wdg(my, sobject, view):
        div = DivWdg()
        div.add_style("overflow: hidden")

        kwargs = {
            'search_key': sobject.get_search_key(),
            'sobject': sobject,
            'view': view,
        }
        from tactic.ui.panel import CustomLayoutWdg
        layout = CustomLayoutWdg(**kwargs)
        div.add(layout.get_buffer_display())
        return div




    def get_scale_wdg(my):


        div = DivWdg()
        div.add_style("padding: 5px")
        div.add_class("spt_table_search")
        hidden = HiddenWdg("prefix", "tile_layout")
        div.add(hidden)

        div.add_behavior( {
            'type': 'load',
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

    var size_x = 240*scale/100;
    var size_y = 160*scale/100;

    //var top = bvr.src_el.getParent(".spt_tile_layout_top");
    var top = spt.tile_layout.layout;
    var els = top.getElements(".spt_tile_content");
    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        el.setStyle( "width",  size_x);
        el.setStyle( "height", size_y);
    }

    spt.container.set_value("tile_layout::scale", scale);

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
    scale = parseInt(scale);
    spt.tile_layout.set_scale(scale);

}


        ''' } )



        div.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.tile_layout.set_layout(bvr.src_el);
        var scale = spt.container.get_value("tile_layout::scale");
        if (scale) {
            spt.tile_layout.set_scale(scale);
        }
        '''
        } )


        table = Table()
        div.add(table)
        table.add_row()

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


 
        value_wdg = TextWdg("scale")
        value_wdg.add_class("spt_scale_value")
        td = table.add_cell(value_wdg)
        td.add("&nbsp;%")
        td.add_style("padding: 3px 8px")
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



        return div


    def get_title(my, sobject):
        div = DivWdg()

        div.add_class("spt_tile_title")

        div.add_color("background", "background3")
        div.add_style("padding: 5px")
        div.add_style("height: 15px")


        detail_div = DivWdg()
        div.add(detail_div)
        detail_div.add_class("spt_tile_detail")
        detail_div.add_style("float: right")
        detail_div.add_style("margin-top: -2px")

        detail = IconButtonWdg(title="Detail", icon=IconWdg.ZOOM)
        detail_div.add(detail)


        title_div = DivWdg()
        title_div.add_class("spt_tile_select")
        title_div.add_class("hand")
        div.add(title_div)
        title_div.add_class("SPT_DTS")

        from pyasm.widget import CheckboxWdg
        checkbox = CheckboxWdg("select")
        checkbox.add_class("spt_tile_checkbox")
        title_div.add(checkbox)
        title_div.add(" ")

        title = sobject.get_name()
        if not title:
            title = sobject.get_code()

        description = sobject.get_value("description", no_exception=True)
        if description:
            div.add_attr("title", sobject.get_code())

        title_div.add(title)


        return div


from pyasm.biz import Snapshot
from pyasm.web import HtmlElement
__all__.append("ThumbWdg2")
class ThumbWdg2(BaseRefreshWdg):
    def get_display(my):

        width = "100%"

        div = DivWdg()
        div.add_class("spt_thumb_top")

        sobject = my.get_current_sobject()
        path = my.get_path_from_sobject(sobject)
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
            img.add_style("padding: 20px 0px")
            img.add_border()
            img.add_style("width: 100%")

        if not path:
            img = DivWdg()
        img.add_class("spt_image")
        div.add(img)
        img.add_style("width: %s" % width)

        div.add_style("height: 100%")


        return div


    def get_path_from_sobject(my, sobject):

        icon_path = None
        path = None

        search_type = sobject.get_search_type()
        search_code = sobject.get_value("code", no_exception=True)
        if not search_code:
            search_code = sobject.get_id()
        snapshot = Snapshot.get_snapshot(search_type, search_code, context='icon')
        if not snapshot:
            snapshot = Snapshot.get_snapshot(search_type, search_code, context='publish')
        if not snapshot:
            snapshot = Snapshot.get_snapshot(search_type, search_code, process='publish')
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
        base = "/context/icons/mime-types"
        icon = None
        if not file_path:
            return ""
            #return ThumbWdg.get_no_image()
        #ext = File.get_extension(file_path)
        import os
        root, ext = os.path.splitext(file_path)
        ext = ext[1:]

        if ext == "xls":
            icon = "gnome-application-vnd.ms-excel.png"
        elif ext == "mp3" or ext == "wav":
            icon = "mp3_and_wav.jpg"
        elif ext == "aif" or ext == 'aiff':
            icon = "gnome-audio-x-aiff.png"
        elif ext == "mpg":
            icon = "gnome-video-mpeg.png"
        elif ext in ["mov", "MOV"] or ext == "mp4":
            icon = "quicktime-logo.png"    
        elif ext == "ma" or ext == "mb" or ext == "anim":
            icon = "maya.png"
        elif ext == "lwo":
            icon = "lwo.jpg"
        elif ext == "max":
            icon = "max.jpg"
        elif ext == "fbx":
            icon = "fbx.jpg"
        elif ext == "hip" or ext == "otl":
            icon = "houdini.png"
        elif ext in ["scn", "scntoc", "xsi"]:
            icon = "xsi_scn.jpg"
        elif ext == "emdl":
            icon = "xsi_emdl.png"
        elif ext == "fla":
            icon = "flash.png"
        elif ext == "dae":
            icon = "collada.png"
        elif ext == "pdf":
            icon = "pdficon_large.gif"
        elif ext == "shk":
            icon = "icon_shake_white.gif"
        elif ext == "comp":
            icon = "fusion.png"
        elif ext == "txt":
            icon = "gnome-textfile.png"
        elif ext == "obj":
            icon = "3d_obj.png"
        elif ext in ["rdc", "RDC"]:
            icon = "red_camera.png"
        elif ext == 'ps':
            icon = "ps_icon.jpg"
        elif ext == 'psd':
            icon = "ps_icon.jpg"
        elif ext == 'ai':
            icon = "icon_illustrator_lg.png"
        elif ext == 'unity3d':
            icon = "unity_icon.jpg"
        elif repo_path and os.path.isdir(repo_path):
            icon = "folder.png"
        else:
            icon = "default_doc.png"
        return "%s/%s" % ( base,icon)




