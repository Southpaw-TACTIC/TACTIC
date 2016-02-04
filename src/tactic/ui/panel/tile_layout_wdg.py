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

import re, os
import urllib

from pyasm.biz import CustomScript, Project
from pyasm.common import Common
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table, SpanWdg
from pyasm.widget import ThumbWdg, IconWdg, TextWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg, ActionButtonWdg
from tactic.ui.input import UploadButtonWdg
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


    ARGS_KEYS['bottom_expr'] = {
            'description': 'an optional expression for the bottom of the tile',
            'order' : '03',
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
    ARGS_KEYS['script_path'] = {
            'description': 'Script to execute when clicked on',
            'type': 'TextWdg',
            'order' : '09',
            'category': 'Display'

    },
    ARGS_KEYS['title_expr'] = {
            'description': 'an expression that drives the display of the title in each tile',
            'type': 'TextWdg',
            'order' : '09a',
            'category': 'Display'

    },
    ARGS_KEYS['overlay_expr'] = {
            'description': 'If a @PYTHON expression is set, expression-driven stats will display in bottom right corner',
            'type': 'TextWdg',
            'order' : '10',
            'category': 'Display'

    },
    ARGS_KEYS['overlay_color'] = {
            'description': 'If comma separated color is set, it controls the background color of overlay stats displayed in bottom right corner',
            'type': 'TextWdg',
            'order' : '11',
            'category': 'Display'

    },

    ARGS_KEYS['show_name_hover'] = {
            'description': 'If set to true, it shows the name on hover over',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order' : '12',
            'category': 'Display'

    },
    ARGS_KEYS['show_drop_shadow'] = {
            'description': 'If set to true, it shows the drop shadow',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order' : '13',
            'category': 'Display'

    },
    ARGS_KEYS['allow_drag'] = {
            'description': 'If set to true, it allows tiles to be dragged to droppable area like planner',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order' : '14',
            'category': 'Display'

    },
    ARGS_KEYS['upload_mode'] = {
            'description': 'support drop,button,both,false mode',
            'type': 'SelectWdg',
            'values': 'drop|button|both|false',
            'order' : '15',
            'category': 'Display'

    },
    ARGS_KEYS['expand_mode'] = {
            'description': 'support gallery, single_gallery, plain, detail, and custom mode',
            'type': 'SelectWdg',
            'values': 'gallery|single_gallery|plain|detail|custom',
            'order' : '16',
            'category': 'Display'

    },

    ARGS_KEYS['gallery_align'] = {
            'description': 'top or bottom gallery vertical alignment',
            'type': 'SelectWdg',
            'values': 'top|bottom',
            'order' : '17',
            'category': 'Display'

    },

    ARGS_KEYS['hide_checkbox'] = {
            'description': 'If set to true, the checkbox on the tile title will be hidden',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order' : '18',
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


    def alter_search(my, search):
        # TODO: this should be applied to ViewPanelWdg level
        process = my.kwargs.get("process")
        if process and search.column_exists('process'):
            search.add_filter("process", process)

        context = my.kwargs.get("context")
        if context:
            search.add_filter("context", context)

        return super(ToolLayoutWdg, my).alter_search(search)



    def handle_group(my, inner, row, sobject):


        last_group_column = None
        
        for i, group_column in enumerate(my.group_columns):
            group_values = my.group_values[i]
            
            eval_group_column =  my._grouping_data.get(group_column)
            if eval_group_column:
                group_column = eval_group_column
            
            group_value = sobject.get_value(group_column, no_exception=True)
            if my.group_by_time.get(group_column): #my.group_interval:
                #group_value = sobject.get_value(group_column, no_exception=True)
                group_value = my._get_simplified_time(group_value)
            if not group_value:
                group_value = "__NONE__"
            
            last_value = group_values.get(group_column)
           
            # if this is the first row or the group value has changed,
            # then create a new group
            if last_value == None or group_value != last_value:
                if row != 0:
                    inner.add("<br clear='all'/>")


                if group_value == '__NONE__':
                    label = '---'
                else:
                    group_label_expr = my.kwargs.get("group_label_expr")
                    if group_label_expr:
                        label = Search.eval(group_label_expr, sobject, single=True)
                    else:
                        label = Common.process_unicode_string(group_value)

                title = label
                if my.group_by_time.get(group_column):
                    if my.group_interval == BaseTableLayoutWdg.GROUP_WEEKLY:
                        title = 'Week  %s' %label
                    elif my.group_interval == BaseTableLayoutWdg.GROUP_MONTHLY:
                        # order by number, but convert to alpha title
                        labels = label.split(' ')
                        if len(labels)== 2:
                            timestamp = datetime(int(labels[0]),int(labels[1]),1)
                            title = timestamp.strftime("%Y %b")


                group_wdg = DivWdg()
                inner.add(group_wdg)
                group_wdg.add_style("margin: 20px 0px 5px 0px")
                group_wdg.add_style("padding: 10px 10px")
                group_wdg.add_style("width: auto")

                icon = IconWdg(name=title, icon="BS_FOLDER_OPEN")
                group_wdg.add(icon)
                icon.add_style("display: inline-block")
                icon.add_style("margin-right: 10px")
                icon.add_style("vertical-align: top")


                title_wdg = DivWdg()
                group_wdg.add(title_wdg)
                title_wdg.add(title)
                title_wdg.add_style("font-size: 1.2em")
                title_wdg.add_style("font-weight: bold")
                title_wdg.add_style("display: inline-block")

                title_wdg.add("<div style='margin-top: 5px; opacity: 0.5; font-size: 0.8em; font-weight: normal'>This is a description</div>")



                group_values[group_column] = group_value
            
                last_group_column = group_column
                # clear the next dict to facilate proper grouping in the next major group
                next_dict = my.group_values.get(i+1)
                if next_dict:
                    next_dict = {}
                    my.group_values[i+1] = next_dict


    def add_no_results_bvr(my, tr):
        return


    def add_no_results_style(my, td):
        div = DivWdg()
        td.add(div)
        div.add_style("height: 300px")
   

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
       

        inner.add_attr("ondragenter", "spt.thumb.background_enter(event, this) ")
        inner.add_attr("ondragleave", "spt.thumb.background_leave(event, this) ")
        inner.add_attr("ondragover", "return false")
        inner.add_attr("ondrop", "spt.thumb.background_drop(event, this)")

        inner.add("<br clear='all'/>")
        
        if my.upload_mode in ['button','both']:
            button_div = DivWdg()
            inner.add(button_div)
            button_div.add( my.get_upload_wdg() )
            button_div.add( my.get_delete_wdg() )
            button_div.add_style("height: 45px")
            
        
        if my.sobjects:
            inner.add( my.get_scale_wdg())
            if my.upload_mode in ['button','both']:
                inner.add(HtmlElement.br(3))

            my.process_groups()

            for row, sobject in enumerate(my.sobjects):

                my.handle_group(inner, row, sobject)


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

        my.bottom_expr = my.kwargs.get("bottom_expr")
        my.show_drop_shadow = my.kwargs.get("show_drop_shadow") in ['true', True]

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
            #my.aspect_ratio = (240, 135)
            #my.aspect_ratio = (240, 240)



        my.show_name_hover = my.kwargs.get('show_name_hover')

        my.top_styles = my.kwargs.get('styles')
        my.spacing = my.kwargs.get('spacing')
        if not my.spacing:
            my.spacing = '10'

        my.overlay_expr = my.kwargs.get('overlay_expr')
        my.overlay_color = my.kwargs.get('overlay_color')

        my.allow_drag = my.kwargs.get('allow_drag') not in ['false', False]
        my.upload_mode = my.kwargs.get('upload_mode')
        if not my.upload_mode:
            my.upload_mode = 'drop'

        my.gallery_align = my.kwargs.get('gallery_align')

        super(TileLayoutWdg, my).init()


    def add_layout_behaviors(my, layout_wdg):
        border_color = layout_wdg.get_color('border', modifier=20)
        
        if my.allow_drag:
            layout_wdg.add_behavior( {
                'type': 'smart_drag',
                'bvr_match_class': 'spt_tile_checkbox',
                'drag_el': 'drag_ghost_copy',
                'use_copy': 'true',
                'use_delta': 'true',
                'border_color': border_color,
                'dx': 10, 'dy': 10,
                'drop_code': 'DROP_ROW',
                'accepted_search_type' : my.search_type,

                
                 # don't use cbjs_pre_motion_setup as it assumes the drag el
                                    
                'copy_styles': 'z-index: 1000; opacity: 0.7; border: solid 1px %s; text-align: left; padding: 10px; width: 0px; background: %s' \
                        % (layout_wdg.get_color("border"), layout_wdg.get_color("background")),

                'cbjs_setup': '''
                if(spt.drop) {spt.drop.sobject_drop_setup( evt, bvr );}
                ''',

                "cbjs_motion": '''
                    spt.mouse._smart_default_drag_motion(evt, bvr, mouse_411);
                    var target_el = spt.get_event_target(evt);
                    target_el = spt.mouse.check_parent(target_el, bvr.drop_code);
                    if (target_el) {
                        var orig_border_color = target_el.getStyle('border-color');
                        var orig_border_style = target_el.getStyle('border-style');
                        target_el.setStyle('border','dashed 2px ' + bvr.border_color);
                        if (!target_el.getAttribute('orig_border_color')) {
                            target_el.setAttribute('orig_border_color', orig_border_color);
                            target_el.setAttribute('orig_border_style', orig_border_style);
                        }
                    }
                ''',
                "cbjs_action": '''
                if (spt.drop) {
                    spt.drop.sobject_drop_action(evt, bvr);
                }
                '''
            } )


        detail_element_names = my.kwargs.get("detail_element_names")

        layout_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_tile_detail',
            'detail_element_names': detail_element_names,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var top = bvr.src_el.getParent(".spt_tile_top");
            var search_key = top.getAttribute("spt_search_key");
            var name = top.getAttribute("spt_name");
            var search_code = top.getAttribute("spt_search_code");
            var class_name = 'tactic.ui.tools.SObjectDetailWdg';
            var kwargs = {
                search_key: search_key,
                tab_element_names: bvr.detail_element_names
            };
            spt.tab.add_new(search_code, name, class_name, kwargs);
            '''
        } )


        # For collections
        parts = my.search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])
        layout_wdg.add_attr("spt_collection_type", collection_type)
        layout_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'collection_type': collection_type,
            'search_type': my.search_type,
            'bvr_match_class': 'spt_tile_collection',
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            var top = bvr.src_el.getParent(".spt_tile_top");

            var name = top.getAttribute("spt_name");
            var parent_keys = [];

            var search_key = top.getAttribute("spt_search_key");
            var parent_code = top.getAttribute("spt_search_code");

            var expr = "@SEARCH("+bvr.collection_type+"['parent_code','"+parent_code+"']."+bvr.search_type+")";
            var class_name = "tactic.ui.panel.CollectionContentWdg";
            
            var kwargs = {
                search_type: bvr.search_type,
                collection_key: search_key,
                expression: expr,
                use_last_search: false,
                show_shelf: false,
                parent_keys: parent_keys,
                path: name,
                is_new_tab: true
            }
            spt.tab.add_new(parent_code, name, class_name, kwargs);
            '''
        } )


        process = my.kwargs.get("process")
        if not process:
            process = "publish"


        mode = my.kwargs.get("expand_mode")
        if not mode:
            mode = "gallery"

        
        gallery_width = my.kwargs.get("gallery_width")
        if not gallery_width:
            gallery_width = ''
        if mode == "plain":
            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'collection_type': collection_type,
                'search_type': my.search_type,
                'process': process,
                'bvr_match_class': 'spt_tile_content',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_tile_top");
                var search_key = top.getAttribute("spt_search_key");
                var server = TacticServerStub.get();
                var tmps = server.split_search_key(search_key);

                var encode = function(path){
                    var path_list = path.split("/");
                    var filename = path_list.pop();
                    filename = encodeURIComponent(filename);
                    path_list.push(filename);
                    snapshot_path = path_list.join("/");

                    return snapshot_path;
                }

                if (/sthpw\/snapshot/.test(search_key)) {
                    snapshots = server.query_snapshots({filters: [['id', tmps[1]]], include_web_paths_dict: true});
                    
                    var snapshot_path = encode(snapshots[0].__web_paths_dict__.main[0]);
                    window.open(snapshot_path);
                }
                else {
                    var asset_sobject = server.get_by_search_key(search_key);
                    var is_collection = asset_sobject._is_collection;

                    var snapshot = server.get_snapshot(search_key, {context: "", process: bvr.process, include_web_paths_dict:true});
                    if (snapshot.__search_key__) {
                        var snapshot_path = encode(snapshot.__web_paths_dict__.main[0]);
                        window.open(snapshot_path);
                    }
                    // The relay behavior for spt_tile_collection does not work, therefore adding the code here.
                    else if (is_collection == true) {
                        var layout = bvr.src_el.getParent(".spt_layout");
                        var top = bvr.src_el.getParent(".spt_tile_top");

                        var name = top.getAttribute("spt_name");
                        var parent_keys = [];

                        var search_key = top.getAttribute("spt_search_key");
                        var parent_code = top.getAttribute("spt_search_code");

                        var expr = "@SEARCH("+bvr.collection_type+"['parent_code','"+parent_code+"']."+bvr.search_type+")";
                        var class_name = "tactic.ui.panel.CollectionContentWdg";
                        
                        var kwargs = {
                            search_type: bvr.search_type,
                            collection_key: search_key,
                            expression: expr,
                            use_last_search: false,
                            show_shelf: false,
                            parent_keys: parent_keys,
                            path: name,
                            is_new_tab: true
                        }
                        spt.tab.add_new(parent_code, name, class_name, kwargs);
                    }
                    else {
                        var snapshot = server.get_snapshot(search_key, {context: "", include_web_paths_dict:true});
                        if (snapshot.__search_key__) {
                            var snapshot_path = encode(snapshot.__web_paths_dict__.main[0]);
                            window.open(snapshot_path);
                        }
                        else {
                            alert("WARNING: No file for this asset");
                        }
                    }
                }
                '''
            } )
        elif mode == "detail":
            tab_element_names = my.kwargs.get("tab_element_names")
            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_tile_content',
                'tab_element_names': tab_element_names,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_tile_top");
                var search_key = top.getAttribute("spt_search_key");

                spt.tab.set_main_body_tab();
                var class_name = 'tactic.ui.tools.SObjectDetailWdg';
                var kwargs = {
                    search_key: search_key,
                    tab_element_names: bvr.tab_element_names,
                };
                spt.tab.add_new(search_key, "Detail", class_name, kwargs);
                '''
            } )

        elif mode == "gallery":
            gallery_div = DivWdg()
            layout_wdg.add( gallery_div )
            gallery_div.add_class("spt_tile_gallery")
            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'width': gallery_width,
                'align': my.gallery_align,
                'bvr_match_class': 'spt_tile_content',
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                var tile_tops = layout.getElements(".spt_tile_top");

                var search_keys = [];
                for (var i = 0; i < tile_tops.length; i++) {
                    var tile_top = tile_tops[i];
                    var search_key = tile_top.getAttribute("spt_search_key_v2");
                    search_keys.push(search_key);
                }

                var tile_top = bvr.src_el.getParent(".spt_tile_top");
                var search_key = tile_top.getAttribute("spt_search_key_v2");

                var class_name = 'tactic.ui.widget.gallery_wdg.GalleryWdg';
                var kwargs = {
                    search_keys: search_keys,
                    search_key: search_key,
                    align: bvr.align
                };
                if (bvr.width) 
                    kwargs['width'] = bvr.width;
                var gallery_el = layout.getElement(".spt_tile_gallery");
                spt.panel.load(gallery_el, class_name, kwargs);

                '''
            } )
        elif mode == "single_gallery":
            gallery_div = DivWdg()
            layout_wdg.add( gallery_div )
            gallery_div.add_class("spt_tile_gallery")
            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'width': gallery_width,
                'align': my.gallery_align,
                'process': process,
                'bvr_match_class': 'spt_tile_content',
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                var tile_top = bvr.src_el.getParent(".spt_tile_top");
                
                var search_keys = [];
                var snapshot_list = []
                var server = TacticServerStub.get();
               
                var search_key = tile_top.getAttribute("spt_search_key_v2");
                search_keys.push(search_key);
                var tmps = server.split_search_key(search_key)
                var search_type = tmps[0];
                var search_code = tmps[1];

                snapshots = server.query_snapshots( {filters: [['process', bvr.process], ['search_type', search_type],
                    ['search_code', search_code]] , include_paths_dict:true});
                for (var k=0; k < snapshots.length; k++)
                    snapshot_list.push(snapshots[k].__search_key__);
                

                var tile_top = bvr.src_el.getParent(".spt_tile_top");
                var search_key = tile_top.getAttribute("spt_search_key_v2");

                var class_name = 'tactic.ui.widget.gallery_wdg.GalleryWdg';
                var kwargs = {
                    search_keys: snapshot_list,
                    search_key: snapshot_list[0],
                    align: bvr.align
                };

                if (bvr.width) 
                    kwargs['width'] = bvr.width;
                var gallery_el = layout.getElement(".spt_tile_gallery");
                spt.panel.load(gallery_el, class_name, kwargs);

                '''
            } )
 
        elif mode == "custom":
            
            script_path = my.kwargs.get("script_path")
            script = None
            if script_path:
                script_obj = CustomScript.get_by_path(script_path)
                script = script_obj.get_value("script")

            if not script:
                script = my.kwargs.get("script")

            if not script:
                script = '''
                alert("Script path [%s] not implemented");
                ''' % script_path

            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_tile_content',
                'cbjs_action': script
            } )
 

        bg1 = layout_wdg.get_color("background3")
        bg2 = layout_wdg.get_color("background3", 5)
        layout_wdg.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "0.8");
            var el = bvr.src_el.getElement(".spt_tile_title");
            if (el) {
                //el.setStyle("background", "%s");
            }
            ''' % bg2
        } )

        layout_wdg.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            var el = bvr.src_el.getElement(".spt_tile_title");
            if (el) {
                //el.setStyle("background", "%s");
            }
            ''' % bg1
        } )


        if my.parent_key:
            search_type = None
        else:
            search_type = my.search_type


        if my.upload_mode in ['drop','both']:
            layout_wdg.add_behavior( {
                'type': 'load',
                'search_type': search_type,
                'search_key': my.parent_key,
                'drop_shadow': my.show_drop_shadow,
                'process': process,
                'border_color': border_color,
                'cbjs_action': '''
                
                spt.thumb = {};

                spt.thumb.background_enter = function(evt, el) {
                    evt.preventDefault();
                    el.setStyle('border','2px dashed ' + bvr.border_color);
                }
                spt.thumb.background_leave = function(evt, el) {
                    evt.preventDefault();
                    el.setStyle('border','none');
                }

                // background_drop creates an entirely new item based on the file name that is being inserted
                spt.thumb.background_drop = function(evt, el) {
                    //evt.stopPropagation();
                    //evt.preventDefault();

                    el.setStyle('border','none');
                    var top = $(el);

                    spt.html5upload.clear();
                    var server = TacticServerStub.get();
                    
                    evt.dataTransfer.dropEffect = 'copy';
                    var files = evt.dataTransfer.files;
                    evt.stopPropagation();
                    evt.preventDefault();

                    var filenames = [];
                    for (var i = 0; i < files.length; i++) {
                        var file = files[i];

                        filenames.push(file.name);
                    }   
                    
                    var yes = function() {
                        spt.app_busy.show("Attaching file");

                            var ticket = server.start({title: "Tile Check-in" , description: "Tile Check-in [" + filenames[0] + "]" });
                            var upload_file_kwargs =  {
                                files: files,
                                ticket: ticket,
                               
                                upload_complete: function() {

                                    try {
                                        var server = TacticServerStub.get();
                                        server.set_transaction_ticket(ticket);
                                        
                                        for (var i = 0; i < files.length; i++) {
                                            var size = files[i].size;
                                            var file = files[i];

                                            var filename = file.name;

                                            var search_key;
                                            var data = {
                                                name: filename
                                            }
                                            if (bvr.search_key) {
                                                search_key = bvr.search_key;
                                            }
                                            else {
                                                var search_type = bvr.search_type;
                                                var item = server.insert(search_type, data);
                                                search_key = item.__search_key__;
                                            }

                                            var context = bvr.process + "/" + filename;
                                        
                                        
                                        var kwargs = {mode: 'uploaded'};
                                        server.simple_checkin( search_key, context, filename, kwargs);

                                        }
                                        server.finish();
                                        var layout = el.getParent(".spt_layout");
                                        spt.table.set_layout(layout);
                                        spt.table.run_search();
                                    } catch(e) {
                                        spt.alert(spt.exception.handler(e));
                                        server.abort();
                                    }
                                }
                            };
                            spt.html5upload.upload_file(upload_file_kwargs);

                            // just support one file at the moment
                            //break;
                     
                        spt.app_busy.hide();
                    }
                    spt.confirm('Check in [' + filenames[0] + '] for a new item?', yes);
                }
     
                // noop means inserting a file into an already existing tile
                spt.thumb.noop_enter = function(evt, el) {
                    evt.preventDefault();
                    el.setStyle("box-shadow", "0px 0px 15px #970");
                }
                spt.thumb.noop_leave = function(evt, el) {
                    evt.preventDefault();
                    if (bvr.drop_shadow)
                        el.setStyle("box-shadow", "0px 0px 15px rgba(0,0,0,0.5)");
                    else
                        el.setStyle("box-shadow", "none");


                }

                spt.thumb.noop = function(evt, el) {
                    evt.dataTransfer.dropEffect = 'copy';
                    var files = evt.dataTransfer.files;
                    evt.stopPropagation();
                    evt.preventDefault();

                    if (bvr.drop_shadow)
                        el.setStyle("box-shadow", "0px 0px 15px rgba(0,0,0,0.5)");
                    else
                        el.setStyle("box-shadow", "none");
                    var top = $(el);
                    var thumb_el = top.getElement(".spt_thumb_top");


                    var filenames = [];
                    for (var i = 0; i < files.length; i++) {
                        var file = files[i];
                        filenames.push(file.name);
                    }   

                    // use the parent key if available
                    var search_key = bvr.search_key ? bvr.search_key : top.getAttribute("spt_search_key");
                    var yes = function() {
                        for (var i = 0; i < files.length; i++) {
                            var size = files[i].size;
                            var file = files[i];

                            setTimeout( function() {
                                var loadingImage = loadImage(
                                    file,
                                    function (img) {
                                        img.setStyle("width", "100%");
                                        img.setStyle("height", "");
                                        thumb_el.innerHTML = "";
                                        thumb_el.appendChild(img);
                                    },
                                    {maxWidth: 240, canvas: true, contain: true}
                                );
                            }, 0 );


                            var filename = file.name;
                            var context = bvr.process + "/" + filename;

                            var upload_file_kwargs =  {
                                files: files,
                                upload_complete: function() {
                                    try {
                                        var server = TacticServerStub.get();
                                        var kwargs = {mode: 'uploaded'};
                                        server.simple_checkin( search_key, context, filename, kwargs);
                                        spt.notify.show_message("Check-in completed for " + search_key);
                                    } catch(e) {
                                        spt.alert(spt.exception.handler(e));
                                        server.abort();
                                        
                                    }
                                }
                            };
                            spt.html5upload.upload_file(upload_file_kwargs);
             
                        }
                    }
                    
                    spt.confirm('Check in [' + filenames + '] for '+ search_key + '?', yes);
                    

                }
                '''
            } )

        
        border = layout_wdg.get_color("border")
        layout_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'border': border,
            'bvr_match_class': 'spt_tile_select',
            'cbjs_action': '''

            var checkbox = bvr.src_el.getElement('.spt_tile_checkbox');

            spt.table.set_table(bvr.src_el);
            if (evt.shift == true) {
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

                
                var select = last_selected ? last_selected.hasClass("spt_table_selected") : false;
                for (var i = start_index; i < end_index + 1; i++) {

                    var row = rows[i];
                    if (row) {

                        var checkbox = row.getElement(".spt_tile_checkbox");
                        var bg = row.getElement(".spt_tile_bg");

                        if (select) {
                            checkbox.checked = true;
                            row.removeClass("spt_table_selected");
                            spt.table.select_row(row);
                            bg.setStyle("opacity", "0.7");


                        }
                        else {
                            checkbox.checked = false;
                            row.addClass("spt_table_selected");
                            spt.table.unselect_row(row);

                            bg.setStyle("opacity", "0.3");

                        }
                    }
                }

            }
            else {

                var row = bvr.src_el.getParent(".spt_table_row");
                var checkbox = bvr.src_el.getElement(".spt_tile_checkbox");
                var bg = row.getElement(".spt_tile_bg");

                if (checkbox.checked == true) {
                    checkbox.checked = false;
                   
                    spt.table.unselect_row(row);
                    bg.setStyle("opacity", "0.3");

                }
                else {
                    checkbox.checked = true;
                    
                    spt.table.select_row(row);
                    bg.setStyle("opacity", "0.7");

                }

            }

            '''
        } )

        # this is working in conjunction with the above mouseup event for the tile header
        # TODO: make the shift select work when the shift clicked index is < the first click
        layout_wdg.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_tile_checkbox',
            'cbjs_action': '''

            var row = bvr.src_el.getParent(".spt_table_row");

            spt.table.set_table(row);
            if (evt.shift == true) {

              

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

                
                var select = last_selected ? last_selected.hasClass("spt_table_selected") : false;


                var row = rows[end_index];
                if (row) {

                    var checkbox = bvr.src_el;
                    var bg = row.getElement(".spt_tile_bg");

                    if (select) {
                        checkbox.checked = true;
                        row.removeClass("spt_table_selected");
                        spt.table.select_row(row);

                        bg.setStyle("opacity", "0.7");


                    }
                    else {
                        checkbox.checked = false;
                        row.addClass("spt_table_selected");
                        spt.table.unselect_row(row);

                        bg.setStyle("opacity", "0.3");

                    }
                }
            }
            else {
                var bg = row.getElement(".spt_tile_bg");
                if (bvr.src_el.checked) {
                    spt.table.select_row(row);
                    bg.setStyle("opacity", "0.7");
                }
                else {
                    spt.table.unselect_row(row);
                    bg.setStyle("opacity", "0.3");
                }
            }
            evt.stopPropagation();

            '''
        } )


        if my.kwargs.get("temp") != True:
            #unique_id = layout_wdg.get_table_id()
            layout_wdg.add_behavior( {
                #'type': 'listen',
                #'event_name': "loading|%s" % unique_id,
                'type': 'load',
                'cbjs_action': '''

                var elements = bvr.src_el.getElements(".spt_generate_icon");

                var rows = [];
                for (var i = 0; i < elements.length; i++) {
                    elements[i].removeClass("spt_generate_icon");
                    var row = elements[i].getParent(".spt_table_row");
                    rows.push(row);
                }

                if (rows.length == 0) {
                    return;
                }

                var jobs = [];
                var count = 0;
                var chunk = 5;
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

                    var on_complete = function(ret_val) {
                        spt.table.refresh_rows(rows, null, null, {
                            on_complete: func,
                            icon_generate_refresh:false
                        });
                    }
                    var cmd = 'pyasm.widget.ThumbCmd';

                    var search_keys = [];
                    for (var i = 0; i < rows.length; i++) {
                        var search_key = rows[i].getAttribute("spt_search_key");
                        search_keys.push(search_key);
                    }

                    var server = TacticServerStub.get();
                    var kwargs = {
                        search_keys: search_keys
                    };
                    server.execute_cmd(cmd, kwargs, {}, {
                                on_complete:on_complete, use_transaction:false
                    });
                }
                func();

                '''
            } )
 




    def get_tile_wdg(my, sobject):

        div = DivWdg()

        
        div.add_class("spt_tile_top")
        div.add_class("unselectable")
        div.add_style('margin', my.spacing)
        div.add_style('background-color','transparent')
        div.add_style('position','relative')

        div.add_class("spt_table_row")
        div.add_class("spt_table_row_%s" % my.table_id)

 
        if my.kwargs.get("show_title") not in ['false', False]:

            if my.title_wdg:
                my.title_wdg.set_sobject(sobject)
                div.add(my.title_wdg.get_buffer_display())
            else:
                title_wdg = my.get_title(sobject)
                div.add( title_wdg )


            title_wdg.add_style("position: absolute")
            title_wdg.add_style("top: 0")
            title_wdg.add_style("left: 0")
            title_wdg.add_style("width: 100%")
            #title_wdg.add_style("opacity: 0.5")


        div.add_attr("spt_search_key", sobject.get_search_key(use_id=True))
        div.add_attr("spt_search_key_v2", sobject.get_search_key())
        div.add_attr("spt_name", sobject.get_name())
        div.add_attr("spt_search_code", sobject.get_code())

        display_value = sobject.get_display_value(long=True)
        div.add_attr("spt_display_value", display_value)

        SmartMenu.assign_as_local_activator( div, 'DG_DROW_SMENU_CTX' )

        
        if my.show_drop_shadow:
            div.set_box_shadow()

        #div.add_color("background", "background", -3)
        
        div.add_style("overflow: hidden")

        div.add_style("float: left")

        border_color = div.get_color('border', modifier=20)

        thumb_drag_div = DivWdg()
        div.add(thumb_drag_div)
        thumb_drag_div.add_class("spt_tile_drag")
        thumb_drag_div.add_style("width: auto")
        thumb_drag_div.add_style("height: auto")
        thumb_drag_div.add_behavior( {
            "type": "drag",
            #'drag_el': 'drag_ghost_copy',
            #//'use_copy': 'true',
            "drag_el": '@',
            'drop_code': 'DROP_ROW',
            'border_color': border_color,
            'search_type': my.search_type,
            "cb_set_prefix": 'spt.tile_layout.image_drag'
        } )

        thumb_div = DivWdg()
        thumb_drag_div.add(thumb_div)
        thumb_div.add_class("spt_tile_content")

        thumb_div.add_style("overflow: hidden")
        thumb_div.add_style("width: %s" % my.aspect_ratio[0])

        thumb_div.add_style("height: %s" % my.aspect_ratio[1])
        #thumb_div.add_style("overflow: hidden")

        kwargs = {}
        kwargs['show_name_hover'] = my.show_name_hover
        kwargs['aspect_ratio'] = my.aspect_ratio

        thumb = ThumbWdg2(**kwargs)
        thumb.set_sobject(sobject)
        thumb_div.add(thumb)
        thumb_div.add_border()

        #bottom_view = my.kwargs.get("bottom_view")
        #if bottom_view:
        #    div.add( my.get_view_wdg(sobject, bottom_view) )
        if my.bottom:
            my.bottom.set_sobject(sobject)
            div.add(my.bottom.get_buffer_display())
        elif my.bottom_expr:
            bottom_value = Search.eval(my.bottom_expr, sobject, single=True)
            bottom_value = bottom_value.replace("\n", "<br/>")
            bottom = DivWdg()
            bottom.add(bottom_value)
            bottom.add_class("spt_tile_bottom")
            bottom.add_style("padding: 10px")
            bottom.add_style("height: 50px")
            bottom.add_style("overflow-y: auto")
            div.add(bottom)
            #bottom.add_style("width: %s" % (my.aspect_ratio[0]-20))
        else:
            table = Table()
            #div.add(table)

            table.add_style("width: 100%")
            table.add_style("margin: 5px 10px")
            table.add_row()
            table.add_cell("Name:")
            table.add_cell("Whatever")
            table.add_row()
            table.add_cell("File Type:")
            table.add_cell("Image.jpg")
 
        

        div.add_attr("ondragenter", "spt.thumb.noop_enter(event, this)")
        div.add_attr("ondragleave", "spt.thumb.noop_leave(event, this)")
        div.add_attr("ondragover", "return false")
        div.add_attr("ondrop", "spt.thumb.noop(event, this)")
        
        if my.overlay_expr:
            from tactic.ui.widget import OverlayStatsWdg
            stat_div = OverlayStatsWdg(expr = my.overlay_expr, sobject = sobject, bg_color = my.overlay_color)
            div.add(stat_div)


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

    def get_delete_wdg(my):
        '''Get Delete button'''
        button = ActionButtonWdg(title='Delete')
        button.add_style('float','left')
        button.add_style('margin-right: 25px')
        button.add_behavior({'type':'click_up',
        'cbjs_action':  '''
            spt.tile_layout.set_layout(bvr.src_el); 
            spt.table.delete_selected();
                '''
        })
        return button
        
    def get_upload_wdg(my):
        '''Get Upload button'''
        process = my.kwargs.get('process')
        if not process:
            process = 'publish'

        transaction_ticket = Common.generate_random_key()

        insert_search_type = ''
        if not my.parent_key:
            insert_search_type = my.search_type
        
        upload_init = '''
           var server = TacticServerStub.get();
           var ticket = server.start({title: "Tile Check-in" , description: "Tile Check-in [%s]" });
           // set the ticket to ensure a unified transaction ticket in tihs check-in
           spt.html5upload.ticket = ticket;
        '''%my.search_type

        on_complete = '''
           var server = TacticServerStub.get();
           server.set_transaction_ticket(spt.html5upload.ticket);

            var file = spt.html5upload.get_file();
            if (file) {
               try {
                   var file_name = file.name;

                   var sk = "%s";
                   if (!sk) {
                        var data = { name: file_name };
                        var item = server.insert("%s", data);
                        sk = item.__search_key__;
                   }
                   var context = "%s" + "/" + file_name;
                    
                   server.simple_checkin(sk, context, file_name, {mode:'uploaded', checkin_type:''});
                   server.finish();
                   spt.notify.show_message("Check-in of ["+file_name+"] successful");
                   var layout = bvr.src_el.getParent(".spt_layout");
                   spt.table.set_layout(layout);
                   spt.table.run_search();
               } catch(e) {
                   spt.alert(spt.exception.handler(e));
                   server.abort();
               }

            }
            else  {
               spt.alert('Error: file object cannot be found.')
            }
            spt.app_busy.hide();
        ''' % (my.parent_key, insert_search_type, process)

        button = UploadButtonWdg(on_complete=on_complete, upload_init=upload_init)
        button.add_style('float: left')
        button.add_style('margin-right: 15px')

        return button

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

    var els = top.getElements(".spt_tile_bottom");
    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        el.setStyle( "width",  size_x-20);
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



spt.tile_layout.image_drag_setup = function(evt, bvr, mouse_411) {
    bvr.use_copy = true;
    bvr.use_delta = true;
    //bvr.border_color = border_color;
    bvr.dx = 10;
    bvr.dy = 10;
    bvr.drop_code = 'DROP_ROW';
    bvr.accepted_search_type = bvr.search_type;


}

spt.tile_layout.image_drag_motion = function(evt, bvr, mouse_411) {

    spt.mouse._smart_default_drag_motion(evt, bvr, mouse_411);
    var target_el = spt.get_event_target(evt);
    target_el = spt.mouse.check_parent(target_el, bvr.drop_code);
    if (target_el) {
        var orig_border_color = target_el.getStyle('border-color');
        var orig_border_style = target_el.getStyle('border-style');
        target_el.setStyle('border','dashed 2px ' + bvr.border_color);
        if (!target_el.getAttribute('orig_border_color')) {
            target_el.setAttribute('orig_border_color', orig_border_color);
            target_el.setAttribute('orig_border_style', orig_border_style);
        }
    }

}

spt.tile_layout.image_drag_action = function(evt, bvr, mouse_411) {
    
    var row = bvr.src_el.getParent(".spt_table_row");

    var dst_el = spt.get_event_target(evt);
    var dst_top = dst_el.hasClass("spt_tile_top") ? dst_el : dst_el.getParent(".spt_tile_top");
    
    var layout = bvr.src_el.getParent(".spt_layout");
    var src_tile = bvr.src_el.getParent(".spt_tile_top");
    var has_inserted = false;

    if (dst_top) {
        if( bvr._drag_copy_el ) {
            spt.mouse._delete_drag_copy( bvr._drag_copy_el );
            bvr._drag_copy_el = null;
        }
        var selected_tiles = spt.table.get_selected_rows();
        
        var parent_key = dst_top.getAttribute("spt_search_key");
        var server = TacticServerStub.get();
        var parent = server.get_by_search_key(parent_key);
        var parent_code = dst_top.getAttribute("spt_search_code");

        var collection_type = layout.getAttribute("spt_collection_type");

        var insert_collection = function(src_code) {
            if (parent_code != src_code){
                var data = {
                    parent_code: parent_code,
                    search_code: src_code
                };
                try { 
                server.insert(collection_type, data);
                has_inserted = true;
                } catch(e) {
                log.debug("Failed to add");
                }
            }
            else {
                return;
            }
        }

        if (parent._is_collection == true) {
            
            // Regular single drag and drop
            if (selected_tiles.indexOf(row) == -1) {
                var src_code = src_tile.getAttribute("spt_search_code");
                insert_collection(src_code);
            }
            // Multiple selections drag and drop
            else {
                for (i=0; i < selected_tiles.length; i++) {
                    var src_code = selected_tiles[i].getAttribute("spt_search_code");
                    insert_collection(src_code);
                }  
            }
            if (parent_code != src_code){
                if (has_inserted) {
                    spt.notify.show_message("Added to Collection");
                }
                else {
                    spt.notify.show_message("The Asset is already in the Collection");
                }
            }
            if (!dst_top.hasClass("spt_collection_item")){
                spt.table.refresh_rows([dst_top], null, null);
            } 
        }

        else {
            var src_code = src_tile.getAttribute("spt_search_code");
            if (parent_code != src_code){
                spt.notify.show_message("The destination is not a Collection");
                return;
            }
        }

    }
    else {
        if (spt.drop) {
            spt.drop.sobject_drop_action(evt, bvr);
        }
        else {
            if( bvr._drag_copy_el ) {
                spt.mouse._delete_drag_copy( bvr._drag_copy_el );
                bvr._drag_copy_el = null;
            }
        }
    }
}

        ''' } )


        scale = my.kwargs.get("scale")


        div.add_behavior( {
        'type': 'load',
        'scale': scale,
        'cbjs_action': '''
        spt.tile_layout.set_layout(bvr.src_el);

        spt.tile_layout.setup_control();

        if (bvr.scale) {
            spt.tile_layout.set_scale(bvr.scale);
        }
      
        '''
        } )

        table = Table()
        div.add(table)
        table.add_row()


        title = DivWdg()
        title.add("Scale: ")
        table.add_cell(title)
        title.add_style("padding: 0px 10px 0px 0px")

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
        slider_div.add_styles('valign: bottom; background: %s; height: 6px; width: 100px;'% light_color)
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
        value_wdg.add_style("width: 28px")
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

        #div.add_color("background", "background3")
        div.add_style("padding: 3px")
        div.add_style("height: 20px")
        div.add_style("position: relative")


        bg_wdg = DivWdg()
        div.add(bg_wdg)
        bg_wdg.add_class("spt_tile_bg")
        bg_wdg.add_style("position: absolute")
        bg_wdg.add_style("top: 0")
        bg_wdg.add_style("left: 0")
        bg_wdg.add_style("height: 100%")
        bg_wdg.add_style("width: 100%")
        #bg_wdg.add_style("background: rgba(0,0,0,0.3)")
        bg_wdg.add_style("background: #000")
        bg_wdg.add_style("opacity: 0.3")
        bg_wdg.add_style("z-index: 1")
        bg_wdg.add(" ")


        if sobject.get_base_search_type() not in ["sthpw/snapshot"]:
            detail_div = DivWdg()
            div.add(detail_div)
            detail_div.add_style("float: right")
            detail_div.add_style("margin-top: -2px")
            detail_div.add_style("position: relative")
            detail_div.add_style("z-index: 2")

            if sobject.get_value("_is_collection", no_exception=True) == True:
                detail_div.add_class("spt_tile_collection");

                search_type = sobject.get_base_search_type()
                parts = search_type.split("/")
                collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

                num_items = Search.eval("@COUNT(%s['parent_code','%s'])" % (collection_type, sobject.get("code")) )
                detail_div.add("<div style='margin-top: 2px; float: right' class='hand badge'>%s</div>" % num_items)
                detail_div.add_style("margin-right: 5px")
            else:
                detail_div.add_class("spt_tile_detail")
                detail_div.add_style("color: #FFF")

                detail = IconButtonWdg(title="Detail", icon="BS_SEARCH")
                detail_div.add(detail)
                detail_div.add_style("margin-right: 3px")


        header_div = DivWdg()
        header_div.add_class("spt_tile_select")
        div.add(header_div)
        header_div.add_class("SPT_DTS")
        header_div.add_style("overflow-x: hidden")
        header_div.add_style("overflow-y: hidden")
        header_div.add_style("position: relative")
        header_div.add_style("z-index: 3");

        from pyasm.widget import CheckboxWdg
        checkbox = CheckboxWdg("select")
        checkbox.add_class("spt_tile_checkbox")
        checkbox.add_style("margin-top: 2px")
        # to prevent clicking on the checkbox directly and not turning on the yellow border
        #checkbox.add_attr("disabled","disabled")

        title_expr = my.kwargs.get("title_expr")
        if title_expr:
            title = Search.eval(title_expr, sobject, single=True)
        elif sobject.get_base_search_type() == "sthpw/snapshot":
            title = sobject.get_value("context")
        else:
            title = sobject.get_value("name", no_exception=True)
        if not title:
            title = sobject.get_value("code", no_exception=True)
      
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
        title_div.add_style("text-overflow: ellipsis")
        title_div.add_style("white-space: nowrap")
        title_div.add_style("color: #FFF")
        title_div.add("<br clear='all'/>")
        title_div.add_class("hand")

        if my.kwargs.get("hide_checkbox") in ['true', True]:
            checkbox.add_style("visibility: hidden")
            title_div.add_style("left: 10px")

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
        my.show_name_hover = my.kwargs.get("show_name_hover")

    def set_sobject(my, sobject):
        super(ThumbWdg2, my).set_sobject(sobject)
        my.path = my.get_path_from_sobject(sobject)

    def set_path(my, path):
        my.path = path

    def get_path(my):
        return my.path


    def get_lib_path(my):
        return my.lib_path




    def get_display(my):

        aspect_ratio = my.kwargs.get("aspect_ratio")

        width = my.kwargs.get("width")
        if not width:
            width = "100%"
        height = my.kwargs.get("height")
        if not height:
            height = "auto"

        sobject = my.get_current_sobject()

        div = my.top
        div.add_class("spt_thumb_top")

        path = my.path

        my.is_collection = sobject.get_value("_is_collection", no_exception=True)

        search_type = sobject.get_base_search_type()
        from pyasm.biz import FileGroup
        if path and path.endswith("indicator_snake.gif") and not FileGroup.is_sequence(my.lib_path):   

            image_size = os.path.getsize(my.lib_path)
            if image_size != 0:
                # generate icon dynamically

                if search_type == 'sthpw/snapshot':
                    #parent = sobject.get_parent()
                    #if parent:
                    #    div.set_attr("spt_search_key", parent.get_search_key())
                    div.set_attr("spt_search_key", sobject.get_search_key())
                else:
                    div.set_attr("spt_search_key", sobject.get_search_key())
                div.add_class("spt_generate_icon")
                div.set_attr("spt_image_size", image_size)


        if path:
            path = urllib.pathname2url(path)
            img = HtmlElement.img(src=path)
        else:
            search_type = sobject.get_search_type_obj()
            path = my.get_path_from_sobject(search_type)
            if path:
                path = urllib.pathname2url(path)

                img = DivWdg()
                img.add_style("opacity: 0.3")

                img_inner = HtmlElement.img(src=path)
                img.add(img_inner)

                img_inner.add_style("width: %s" % width)

        if path and path.startswith("/context"):
            #img.add_style("padding: 15% 15%")
            img.add_style("width: auto")
            img.add_style("height: 70%")
            img.add_style("margin: 10%")

            img = DivWdg(img)
            img.add_style("height: auto")
            #img.add_style("border: solid 1px blue")
            img.add_style("margin: auto")



            #div.add_style("height: 100%")
            div.add_style("text-align: center")
        elif path:
            img.add_style("width: %s" % width)
            if height:
                img.add_style("height: %s" % height)
            else:
                img.add_style("height: auto")

            img.add_style('margin-left','auto')
            img.add_style('margin-right','auto')

        if not path:
            img = DivWdg()
        img.add_class("spt_image")
        div.add(img)

        if height or my.show_name_hover in ["True","true",True]:
            div.add_style("height: 100%")

        if my.show_name_hover in ["True","true",True]:
            name_hover = DivWdg()
            name_hover.add_class("spt_name_hover")
            name_hover.add(sobject.get('name'))
            name_hover.add_attr('onmouseenter',"this.setStyle('opacity',1)")
            name_hover.add_attr('onmouseleave',"this.setStyle('opacity',0)")
            name_hover.add_styles('opacity: 0; font-size: 16px; color: rgb(217, 217, 217); top: 0px; \
                                transition: opacity 0s ease-out; -webkit-transition: opacity 0s ease-out; \
                                height: 100%; width: 100%; position: absolute; padding-top: 20px; \
                                text-align: center; background-color: rgba(0, 0, 0, 0.6);')
            div.add(name_hover)

        return div




    def get_path_from_sobject(my, sobject):

        if sobject.get_value("_is_collection", no_exception=True):
            from pyasm.common import Environment
            install_dir = Environment.get().get_install_dir()
            path = "/context/icons/mime-types/folder2.jpg"

            my.lib_path = "%s/src%s" % (install_dir, path)
            my.icon_path = "%s/src%s" % (install_dir, path)
            return path

        icon_path = None
        path = None
        lib_path = None

        base_search_type = sobject.get_base_search_type()
        if base_search_type == "sthpw/snapshot":
            #sobject = sobject.get_parent()
            snapshot = sobject

        else:
            search_type = sobject.get_search_type()
            search_code = sobject.get_value("code", no_exception=True)
            if not search_code:
                search_code = sobject.get_id()


            # FIXME: make this faster
            snapshot = Snapshot.get_snapshot(search_type, search_code, process=['icon','publish',''])


        if not snapshot:
            snapshot = Snapshot.get_snapshot("sthpw/search_object", base_search_type, process=['icon','publish',''])


        if snapshot:
            file_type = "web"
            icon_path = snapshot.get_web_path_by_type(file_type)

            file_type = "main"
            path = snapshot.get_web_path_by_type(file_type)
            lib_path = snapshot.get_lib_path_by_type(file_type)

        if icon_path:
            path = icon_path
        elif path:
            path = my.find_icon_link(path)


        # remember the last path
        my.path = path
        my.lib_path = lib_path
        my.icon_path = icon_path
 
        return path


    def find_icon_link(my, file_path, repo_path=None):
        from pyasm.widget import ThumbWdg
        return ThumbWdg.find_icon_link(file_path, repo_path)





