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




    def can_select(self):
        return True

    def can_expand(self):
        return True

    def get_expand_behavior(self):
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


    def alter_search(self, search):
        # TODO: this should be applied to ViewPanelWdg level
        process = self.kwargs.get("process")
        if process and search.column_exists('process'):
            search.add_filter("process", process)

        context = self.kwargs.get("context")
        if context:
            search.add_filter("context", context)

        return super(ToolLayoutWdg, self).alter_search(search)



    def handle_group(self, inner, row, sobject):


        last_group_column = None
        
        for i, group_column in enumerate(self.group_columns):
            group_values = self.group_values[i]
            
            eval_group_column =  self._grouping_data.get(group_column)
            if eval_group_column:
                group_column = eval_group_column
            
            group_value = sobject.get_value(group_column, no_exception=True)
            if self.group_by_time.get(group_column): #self.group_interval:
                #group_value = sobject.get_value(group_column, no_exception=True)
                group_value = self._get_simplified_time(group_value)
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
                    group_label_expr = self.kwargs.get("group_label_expr")
                    if group_label_expr:
                        label = Search.eval(group_label_expr, sobject, single=True)
                    else:
                        label = Common.process_unicode_string(group_value)

                title = label
                if self.group_by_time.get(group_column):
                    if self.group_interval == BaseTableLayoutWdg.GROUP_WEEKLY:
                        title = 'Week  %s' %label
                    elif self.group_interval == BaseTableLayoutWdg.GROUP_MONTHLY:
                        # order by number, but convert to alpha title
                        labels = label.split(' ')
                        if len(labels)== 2:
                            timestamp = datetime(int(labels[0]),int(labels[1]),1)
                            title = timestamp.strftime("%Y %b")

 

                group_wdg = DivWdg()

                if i == 0:
                    group_wdg.add_style("margin: 10px 0px 5px 0px")
                else:
                    group_wdg.add_style("margin: 0px 0px 5px 0px")

                group_wdg.add_style("padding: 0px 10px 0px %spx" % ((i-1)*10))

                group_wdg.add_style("width: auto")


                group_levels = len(self.group_columns)
                if i+1 >= group_levels:
                    inner.add(group_wdg)

                    group_wdg.add_style("border-bottom: solid 1px #DDD")
                    group_wdg.add_style("margin: 0px 0px 15px 0px")



                icon = IconWdg(name=title, icon="FA_FOLDER_OPEN_O")
                group_wdg.add(icon)
                icon.add_style("display: inline-block")
                icon.add_style("margin-right: 10px")
                icon.add_style("vertical-align: top")


                title_wdg = DivWdg()
                group_wdg.add(title_wdg)
                title_wdg.add(title)
                title_wdg.add_style("font-size: 1.2em")
                title_wdg.add_style("display: inline-block")



                group_values[group_column] = group_value
            
                last_group_column = group_column
                # clear the next dict to facilate proper grouping in the next major group
                next_dict = self.group_values.get(i+1)
                if next_dict:
                    next_dict = {}
                    self.group_values[i+1] = next_dict


    def add_no_results_bvr(self, tr):
        return


    def add_no_results_style(self, td):
        div = DivWdg()
        td.add(div)
        div.add_style("height: 300px")
   

    def get_content_wdg(self):
        div = DivWdg()
        div.add_class("spt_tile_layout_top")
        if self.top_styles:
            div.add_styles(self.top_styles)
        inner = DivWdg()
        div.add(inner)


        
        menus_in = {}
        # set up the context menus
        if self.show_context_menu == True:
            menus_in['DG_HEADER_CTX'] = [ self.get_smart_header_context_menu_data() ]
            menus_in['DG_DROW_SMENU_CTX'] = [ self.get_data_row_smart_context_menu_details() ]
        elif self.show_context_menu == 'none':
            div.add_event('oncontextmenu', 'return false;')
        if menus_in:
            SmartMenu.attach_smart_context_menu( inner, menus_in, False )
        

        temp = self.kwargs.get("temp")
        has_loading = False

        
        inner.add_style("margin-left: 20px")
       

        inner.add_attr("ondragenter", "spt.thumb.background_enter(event, this) ")
        inner.add_attr("ondragleave", "spt.thumb.background_leave(event, this) ")
        inner.add_attr("ondragover", "return false")
        inner.add_attr("ondrop", "spt.thumb.background_drop(event, this)")

        inner.add("<br clear='all'/>")
        
        if self.upload_mode in ['button','both']:
            button_div = DivWdg()
            inner.add(button_div)
            button_div.add( self.get_upload_wdg() )
            button_div.add( self.get_delete_wdg() )
            button_div.add_style("height: 45px")
            
        
        if self.sobjects:
            inner.add( self.get_scale_wdg())
            if self.upload_mode in ['button','both']:
                inner.add(HtmlElement.br(3))

            self.process_groups()

            for row, sobject in enumerate(self.sobjects):

                self.handle_group(inner, row, sobject)


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


                kwargs = self.kwargs.copy()
                tile = self.get_tile_wdg(sobject)
                inner.add(tile)
                #inner.add_style("text-align: center")
                inner.add_style("text-align: left")
        else:
            table = Table()
            inner.add(table)
            self.handle_no_results(table)


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



    def init(self):
        self.scale_called = False
        self.scale = None
        top_view = self.kwargs.get("top_view")
        if top_view:
            kwargs = {
                'view': top_view,
            }
            from tactic.ui.panel import CustomLayoutWdg
            self.title_wdg = CustomLayoutWdg(**kwargs)
        else:
            self.title_wdg = None
        self.sticky_scale = self.kwargs.get('sticky_scale')
        if self.sticky_scale == 'local':
            # NOTE: each side bar link has a unique name on each level, but it's not always available
            # not in page refresh or built-in links
            # element = self.kwargs.get('element_name')
            self.scale_prefix = '%s:%s' %(self.search_type, self.view)
        else:
            self.scale_prefix = ''
        
        bottom_view = self.kwargs.get("bottom_view")
        if bottom_view:
            kwargs = {
                'view': bottom_view,
                'load': 'sequence',
            }
            from tactic.ui.panel import CustomLayoutWdg
            self.bottom = CustomLayoutWdg(**kwargs)
        else:
            self.bottom = None

        self.bottom_expr = self.kwargs.get("bottom_expr")
        self.show_drop_shadow = self.kwargs.get("show_drop_shadow") in ['true', True]

        from tactic.ui.filter import FilterData
        filter_data = FilterData.get()
        data_list = filter_data.get_values_by_prefix("tile_layout")
        if data_list:
            data = data_list[0]
        else:
            data = {}
        

        self.scale = data.get("scale")
        if self.scale == None:
            self.scale = self.kwargs.get("scale")
        if self.scale == None:
            self.scale = 100


        self.aspect_ratio = self.kwargs.get('aspect_ratio')
        if self.aspect_ratio:
            parts = re.split('[\Wx]+', self.aspect_ratio)
            self.aspect_ratio = (int(parts[0]), int(parts[1]))
        else:

            self.aspect_ratio = (240, 160)
            #self.aspect_ratio = (240, 135)
            #self.aspect_ratio = (240, 240)



        self.show_name_hover = self.kwargs.get('show_name_hover')

        self.top_styles = self.kwargs.get('styles')
        self.spacing = self.kwargs.get('spacing')
        if not self.spacing:
            self.spacing = '15'

        self.overlay_expr = self.kwargs.get('overlay_expr')
        self.overlay_color = self.kwargs.get('overlay_color')

        self.allow_drag = self.kwargs.get('allow_drag') not in ['false', False]
        self.upload_mode = self.kwargs.get('upload_mode')
        if not self.upload_mode:
            self.upload_mode = 'drop'

        self.gallery_align = self.kwargs.get('gallery_align')

        super(TileLayoutWdg, self).init()


    def add_layout_behaviors(self, layout_wdg):
        border_color = layout_wdg.get_color('border', modifier=20)
        
        if self.allow_drag:
            layout_wdg.add_behavior( {
                'type': 'smart_drag',
                'bvr_match_class': 'spt_tile_checkbox',
                'drag_el': 'drag_ghost_copy',
                'use_copy': 'true',
                'use_delta': 'true',
                'border_color': border_color,
                'dx': 10, 'dy': 10,
                'drop_code': 'DROP_ROW',
                'accepted_search_type' : self.search_type,

                
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


        detail_element_names = self.kwargs.get("detail_element_names")

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

            var element_name = search_code;
            spt.tab.add_new(element_name, name, class_name, kwargs);
            '''
        } )


        # For collections
        parts = self.search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])
        layout_wdg.add_attr("spt_collection_type", collection_type)
        layout_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'collection_type': collection_type,
            'search_type': self.search_type,
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


        process = self.kwargs.get("process")
        if not process:
            process = "publish"


        mode = self.kwargs.get("expand_mode")
        if not mode:
            mode = "gallery"

        
        gallery_width = self.kwargs.get("gallery_width")
        if not gallery_width:
            gallery_width = ''
        if mode == "plain":
            layout_wdg.add_relay_behavior( {
                'type': 'click',
                'collection_type': collection_type,
                'search_type': self.search_type,
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
            tab_element_names = self.kwargs.get("tab_element_names")
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
                'align': self.gallery_align,
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

                var thumb_top = tile_top.getElement(".spt_thumb_top");
                var main_path = thumb_top.getAttribute("spt_main_path");
                if (main_path.endsWith(".pdf")) {
                    window.open(main_path, "_blank");
                    return;
                }

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
                'align': self.gallery_align,
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
            
            script_path = self.kwargs.get("script_path")
            script = None
            if script_path:
                script_obj = CustomScript.get_by_path(script_path)
                script = script_obj.get_value("script")

            if not script:
                script = self.kwargs.get("script")

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

            var tool_el = bvr.src_el.getElement(".spt_tile_tool_top");
            if (tool_el) {
                tool_el.setStyle("display", "");
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

            var tool_el = bvr.src_el.getElement(".spt_tile_tool_top");
            if (tool_el) {
                tool_el.setStyle("display", "none");
            }

            ''' % bg1
        } )


        if self.parent_key:
            search_type = None
        else:
            search_type = self.search_type


        if self.upload_mode in ['drop','both']:
            layout_wdg.add_behavior( {
                'type': 'load',
                'search_type': search_type,
                'search_key': self.parent_key,
                'drop_shadow': self.show_drop_shadow,
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
                    var top = document.id(el);

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
                    var top = document.id(el);
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


        if self.kwargs.get("temp") != True:
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
 




    def get_tile_wdg(self, sobject):

        div = DivWdg()

        
        div.add_class("spt_tile_top")
        div.add_class("unselectable")
        div.add_style('margin-bottom', self.spacing)
        div.add_style('margin-right', self.spacing)
        div.add_style('background-color','transparent')
        div.add_style('position','relative')
        div.add_style('vertical-align','top')

        div.add_class("spt_table_row")
        div.add_class("spt_table_row_%s" % self.table_id)

        div.add(" ")

 
        if self.kwargs.get("show_title") not in ['false', False]:

            if self.title_wdg:
                self.title_wdg.set_sobject(sobject)
                div.add(self.title_wdg.get_buffer_display())
                title_wdg = self.title_wdg
            else:
                title_wdg = self.get_title(sobject)
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
        div.add_attr("spt_is_collection", sobject.get_value('_is_collection', no_exception=True))
        display_value = sobject.get_display_value(long=True)
        div.add_attr("spt_display_value", display_value)

        SmartMenu.assign_as_local_activator( div, 'DG_DROW_SMENU_CTX' )

        
        if self.show_drop_shadow:
            div.set_box_shadow()


        div.add_style("overflow: hidden")
        #div.add_style("float: left")
        div.add_style("display: inline-block")


        border_color = div.get_color('border', modifier=20)

        thumb_drag_div = DivWdg()
        div.add(thumb_drag_div)
        thumb_drag_div.add_class("spt_tile_drag")
        thumb_drag_div.add_style("width: auto")
        thumb_drag_div.add_style("height: auto")
        thumb_drag_div.add_behavior( {
            "type": "drag",
            "drag_el": '@',
            'drop_code': 'DROP_ROW',
            'border_color': border_color,
            'search_type': self.search_type,
            "cb_set_prefix": 'spt.tile_layout.image_drag'
        } )

        thumb_div = DivWdg()
        thumb_drag_div.add(thumb_div)
        thumb_div.add_class("spt_tile_content")

        thumb_div.add_style("overflow: hidden")
        thumb_div.add_style("width: %s" % self.aspect_ratio[0])

        thumb_div.add_style("height: %s" % self.aspect_ratio[1])
        #thumb_div.add_style("overflow: hidden")

        kwargs = {}
        kwargs['show_name_hover'] = self.show_name_hover
        kwargs['aspect_ratio'] = self.aspect_ratio

        thumb = ThumbWdg2(**kwargs)

        use_parent = self.kwargs.get("use_parent")
        if use_parent in [True, 'true']:
            parent = sobject.get_parent()
            thumb.set_sobject(parent)
        else:
            thumb.set_sobject(sobject)
        thumb_div.add(thumb)
        thumb_div.add_border()


        # FIXME: for some reason, the hidden overflow is not respected here
        thumb.add_style("margin-top: 30%")
        thumb.add_style("transform: translate(0%, -50%)")
        #thumb.add_style("border: solid 2px blue")
        #thumb_div.add_style("border: solid 2px red")


        # add a div on the bottom
        div.add_style("position: relative")

        tool_div = DivWdg()
        div.add(tool_div)
        tool_div.add_style("display: none")
        tool_div.add_class("spt_tile_tool_top")

        lib_path = thumb.get_lib_path()
        if lib_path:
            size = Common.get_dir_info(lib_path).get("size")
            from pyasm.common import FormatValue
            size = FormatValue().get_format_value(size, "KB")
        else:
            size = 0

        size_div = DivWdg()
        tool_div.add(size_div)
        size_div.add(size)
        size_div.add_style("float: right")
        size_div.add_style("margin-top: 3px")



        #tool_div.add_style("position: absolute")
        tool_div.add_style("position: relative")
        #tool_div.add_style("top: 30px")
        tool_div.add_style("background: #FFF")
        tool_div.add_style("color: #000")
        tool_div.add_style("height: 21px")
        tool_div.add_style("padding: 2px 5px")
        tool_div.add_style("margin-top: -26px")
        tool_div.add_border(size="0px 1px 1px 1px")

        path = thumb.get_path()

        try:
            path = thumb.snapshot.get_web_path_by_type("main")
        except:
            path = path
        if path:
            href = HtmlElement.href()
            href.add_attr("href", path)
            tool_div.add(href)


            basename = os.path.basename(path)
            href.add_attr("download", basename)


            icon = IconWdg(name="Download", icon="BS_DOWNLOAD")
            icon.add_class("hand")
            href.add(icon)
            """
            icon.add_behavior( {
                'type': 'clickX',
                'path': path,
                'cbjs_action': '''
                alert(bvr.path); 
                '''
            } )
            """




        if self.bottom:
            self.bottom.set_sobject(sobject)
            div.add(self.bottom.get_buffer_display())
        elif self.bottom_expr:
            bottom_value = Search.eval(self.bottom_expr, sobject, single=True)
            bottom_value = bottom_value.replace("\n", "<br/>")
            bottom = DivWdg()
            bottom.add(bottom_value)
            bottom.add_class("spt_tile_bottom")
            bottom.add_style("padding: 10px")
            bottom.add_style("height: 50px")
            bottom.add_style("overflow-y: auto")
            div.add(bottom)
            #bottom.add_style("width: %s" % (self.aspect_ratio[0]-20))
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
        
        if self.overlay_expr:
            from tactic.ui.widget import OverlayStatsWdg
            stat_div = OverlayStatsWdg(expr = self.overlay_expr, sobject = sobject, bg_color = self.overlay_color)
            div.add(stat_div)


        return div



    def get_view_wdg(self, sobject, view):
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



    def get_shelf_wdg(self):
        return self.get_scale_wdg()

    def get_delete_wdg(self):
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
        
    def get_upload_wdg(self):
        '''Get Upload button'''
        process = self.kwargs.get('process')
        if not process:
            process = 'publish'

        transaction_ticket = Common.generate_random_key()

        insert_search_type = ''
        if not self.parent_key:
            insert_search_type = self.search_type
        
        upload_init = '''
           var server = TacticServerStub.get();
           var ticket = server.start({title: "Tile Check-in" , description: "Tile Check-in [%s]" });
           // set the ticket to ensure a unified transaction ticket in tihs check-in
           spt.html5upload.ticket = ticket;
        '''%self.search_type

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
        ''' % (self.parent_key, insert_search_type, process)

        button = UploadButtonWdg(on_complete=on_complete, upload_init=upload_init)
        button.add_style('float: left')
        button.add_style('margin-right: 15px')

        return button

    def get_scale_wdg(self):

        if self.scale_called == True:
            return None
        self.scale_called = True

        show_scale = self.kwargs.get("show_scale")
        
        div = DivWdg()
        if show_scale in [False, 'false']:
            div.add_style("display: none")
        div.add_style("padding: 5px")
        div.add_class("spt_table_search")
        hidden = HiddenWdg("prefix", "tile_layout")
        div.add(hidden)
        div.add_behavior( {
            'type': 'load',
            'scale_prefix':  self.scale_prefix,
            'default_scale': self.scale,
            'aspect_ratio': self.aspect_ratio,
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
    bvr.mouse_start = { curr_x: mouse_411.curr_x, curr_y: mouse_411.curr_y };


}

spt.tile_layout.image_drag_motion = function(evt, bvr, mouse_411) {

    if ( Math.abs(bvr.mouse_start.curr_x-mouse_411.curr_x) < 3 && Math.abs(bvr.mouse_start.curr_y-mouse_411.curr_y) < 3) {
        return;
    }

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

    var has_drop_handler = dst_el.hasClass("spt_drop_handler");
    var drop_handler = "";
    if (!has_drop_handler) {
        var drop_handler_el = dst_el.getParent(".spt_drop_handler");
        if (drop_handler_el) {
            drop_handler = drop_handler_el.getAttribute("spt_drop_handler");
        }
    }
    else {
        drop_handler = dst_el.getAttribute("spt_drop_handler");
    }

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
        var parent_name = dst_top.getAttribute("spt_name");

        var collection_type = layout.getAttribute("spt_collection_type");
        var collection_selected = false;

        var src_codes = [];

        var get_exist = function(collection_type, parent_code, src_code) {
            var exist = server.query(collection_type, { filters:[['parent_code', parent_code], ['search_code', src_code]]});
            var exist_code_list = [];
            if (exist.length >= 1) {
                for (var k=0; k < exist.length; k++)
                    exist_code_list.push(exist[k].search_code);
                return exist_code_list;
            }    
            else
                return [];
        }
        
        var insert_collection = function(collection_type, parent_key, src_keys) {
            // check and see if collection_key is in src_keys

            if (src_keys.indexOf(parent_key) == -1){
                var kwargs = {
                    collection_keys: [parent_key],
                    search_keys: src_keys
                }

                try {
                    var rtn = server.execute_cmd("tactic.ui.panel.CollectionAddCmd" , kwargs)
                    var rtn_message = rtn.info.message;

                    if (rtn_message['circular'] == 'True') {
                        var parent_collection_names = rtn_message['parent_collection_names'].join(", ");
                        var msg = "Collection [" + parent_name + " ] is a child of the source [" + parent_collection_names + "]";
                        spt.notify.show_message(msg);

                        return;
                    }
                    else {
                        return true;
                    }
                } catch(e) {
                    log.debug("Failed to add");
                    return false;
                }
            }
            else {
                return false;
            }
        }

    

        if (parent._is_collection == true) {
            
            // Regular single drag and drop
            if (selected_tiles.indexOf(row) == -1) {
                var src_code = src_tile.getAttribute("spt_search_code");
                var src_key = src_tile.getAttribute("spt_search_key");
                src_codes.push(src_code);
                if (src_codes.length == 1 && src_codes[0] == parent_code) {
                    if (!dst_top.hasClass("spt_table_row")) {
                        spt.notify.show_message("Collection [" + parent_name + " ] cannot be added to itself.");
                    }

                    return;
                }
                var exist_cols = get_exist(collection_type, parent_code, src_code);
                if (exist_cols.length == 0) {
                    var search_keys = [src_key];

                    has_inserted = insert_collection(collection_type, parent_key, search_keys);
                    if (has_inserted == null)
                        return;
                    collection_selected = src_tile.getAttribute("spt_is_collection") == 'True';
                }

            }
            // Multiple selections drag and drop
            else {
                
                var src_is_cols = [];
                var final_is_cols = [];
                var src_keys = [];
                var final_keys = [];
                for (i=0; i < selected_tiles.length; i++) {
                    var src_code = selected_tiles[i].getAttribute("spt_search_code");
                    var src_key = selected_tiles[i].getAttribute("spt_search_key");
                    
                    src_codes.push(src_code);
                    src_keys.push(src_key);
                    var src_is_col = selected_tiles[i].getAttribute("spt_is_collection");
                    src_is_cols.push(src_is_col);
                }
                var exist_cols = get_exist(collection_type, parent_code, src_codes);

                // find the final codes that need to be added to collection
                for (var k=0; k < src_codes.length; k++) {
                    if (!exist_cols.contains(src_codes[k])) {

                        final_is_cols.push(src_is_cols[k]);

                        final_keys.push(src_keys[k]);
                    }
                }


                if (src_codes.indexOf(parent_code) != -1) {
                    if (!dst_top.hasClass("spt_table_row")) {
                        spt.notify.show_message("Collection [" + parent_name + " ] cannot be added to itself.");
                    }
                    return;
                }
                if (final_keys.length > 0) {
                    server.start({title: 'Add to collection', description: 'Add items to collection ' + parent_code } ); 
                    
                    var has_inserted = insert_collection(collection_type, parent_key, final_keys);
                    if (has_inserted == null)
                        return;
                    if (!collection_selected)
                        collection_selected = final_is_cols[k] == 'True';
                    
                }
                
            }

            if (has_inserted) {
                spt.notify.show_message("Added to Collection [ " + parent_name + " ].");
                
                // Refresh left panel if collection being dragged into other collection
                if (collection_selected) {
                    var top = bvr.src_el.getParent(".spt_collection_top");
                    var collection_left = top.getElement(".spt_collection_left_side");
                    spt.panel.refresh(collection_left);
                }
            }
            else {
                spt.notify.show_message("Item(s) are already in the Collection [ " + parent_name + " ].");
            }
            
            if (!dst_top.hasClass("spt_collection_item")) {
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
    else if (drop_handler) {
        if( bvr._drag_copy_el ) {
            spt.mouse._delete_drag_copy( bvr._drag_copy_el );
            bvr._drag_copy_el = null;
        };
        eval(drop_handler+"(evt, bvr)");

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


        scale = self.kwargs.get("scale")


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
        self.scale = data.get("scale")
        if self.scale == None:
            self.scale = self.kwargs.get("scale")
        """
        if self.scale:
            value_wdg.set_value(self.scale)
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


    def get_title(self, sobject):
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

        '''
        status = sobject.get_value("status", no_exception=True)
        if status == "Reject":
            bg_wdg.add_style("background: #e84a4d")
        elif status == "Final":
            bg_wdg.add_style("background: #a3d991")
        '''

        bg_wdg.set_box_shadow(color="#000")
        bg_wdg.add_style("opacity: 0.3")


        bg_wdg.add_style("z-index: 1")
        bg_wdg.add(" ")


        #if sobject.get_base_search_type() not in ["sthpw/snapshot"]:
        show_detail = self.kwargs.get("show_detail")
        if show_detail not in [False, 'false']:
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

                detail = IconButtonWdg(title="Detail", icon="FA_EXPAND")
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

        title_expr = self.kwargs.get("title_expr")
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

        if self.kwargs.get("hide_checkbox") in ['true', True]:
            checkbox.add_style("visibility: hidden")
            title_div.add_style("left: 10px")

        description = sobject.get_value("description", no_exception=True)
        if description:
            div.add_attr("title", sobject.get_code())



        return div


from pyasm.biz import Snapshot
from pyasm.web import HtmlElement
from pyasm.biz import FileGroup
__all__.append("ThumbWdg2")
class ThumbWdg2(BaseRefreshWdg):

    def init(self):
        self.path = None
        self.show_name_hover = self.kwargs.get("show_name_hover")
        self.main_path = ""

    def set_sobject(self, sobject):
        super(ThumbWdg2, self).set_sobject(sobject)
        self.path = self.get_path_from_sobject(sobject)

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path


    def get_lib_path(self):
        return self.lib_path

    def get_main_path(self):
        return self.main_path





    def get_display(self):

        aspect_ratio = self.kwargs.get("aspect_ratio")

        width = self.kwargs.get("width")
        if not width:
            width = "100%"
        height = self.kwargs.get("height")
        if not height:
            height = "auto"

        sobject = self.get_current_sobject()
        if not sobject:
            search_key = self.kwargs.get("search_key")
            if search_key:
                sobject = Search.get_by_search_key(search_key)
                self.set_sobject(sobject)

        div = self.top
        div.add_class("spt_thumb_top")

        path = self.path
        if self.lib_path and not FileGroup.is_sequence(self.lib_path) and not os.path.exists(self.lib_path):
            path = ""


        self.is_collection = sobject.get_value("_is_collection", no_exception=True)

        search_type = sobject.get_base_search_type()
        if path and path.endswith("indicator_snake.gif") and not FileGroup.is_sequence(self.lib_path):

            image_size = os.path.getsize(self.lib_path)
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
            if path == "__DYNAMIC__":
                base,ext = os.path.splitext(self.lib_path)
                ext = ext.upper().lstrip(".")

                #flat ui color
                colors = ['#1ABC9C', '#2ECC71', '#3498DB','#9B59B6','#34495E','#E67E22','#E74C3C','#95A5A6']
                import random
                color = colors[random.randint(0,7)]

                img = DivWdg()
                img.add_style("padding-top: 10px")
                
                inner = DivWdg()
                img.add(inner)
               
                ext_div = DivWdg()
                inner.add(ext_div)
                ext_div.add_styles("display: inline-block; vertical-align: middle; margin-top: 40%;")
                ext_div.add(ext)
                
                inner.add_style("text-align: center")
                #inner.add_style("min-width: 80px")
                #inner.add_style("min-height: 50px")
                inner.add_style("width: 53%")
                inner.add_style("height: 80%")

                inner.add_style("margin: 30px auto")
                inner.add_style("font-size: 20px")
                inner.add_style("font-weight: bold")
                inner.add_style("color: #fff")
                inner.add_style("background: %s" % color)

            else:
                if isinstance(path, unicode):
                    path = path.encode("utf-8")

                if path.endswith("indicator_snake.gif"):

                    if self.lib_path.find("#") != -1:
                        paths = self.snapshot.get_expanded_file_names()
                        # handle sequence
                        lib_dir = self.snapshot.get_lib_dir()
                        self.lib_path = "%s/%s" % (lib_dir, paths[0])

                    if not os.path.exists(self.lib_path):
                        image_size = 0
                    else:
                        image_size = os.path.getsize(self.lib_path)

                    if image_size != 0:
                        # generate icon dynamically
                        """
                        img.set_attr("spt_search_key", sobject.get_search_key())
                        img.add_class("spt_generate_icon")
                        img.set_attr("spt_image_size", image_size)
                        """

                        # generate icon inline
                        from pyasm.widget import ThumbCmd
                        search_key = self.snapshot.get_search_key()
                        thumb_cmd = ThumbCmd(search_keys=[search_key])
                        thumb_cmd.execute()
                        path = thumb_cmd.get_path()


                path = urllib.pathname2url(path)
                img = HtmlElement.img(src=path)

                div.add_attr("spt_main_path", self.get_main_path())




        else:
            search_type = sobject.get_search_type_obj()
            path = self.get_path_from_sobject(search_type)
            if path:
                if isinstance(path, unicode):
                    path = path.encode("utf-8")
                path = urllib.pathname2url(path)

                img = DivWdg()
                img.add_style("opacity: 0.3")

                img_inner = HtmlElement.img(src=path)
                img.add(img_inner)

                img_inner.add_style("width: %s" % width)

        if path and path.startswith("/context"):
            #img.add_style("padding: 15% 15%")
            img.add_style("width: auto")
            img.add_style("height: 80%")
            img.add_style("margin-top: 15%")

            img = DivWdg(img)
            img.add_style("height: auto")
            img.add_style("margin: auto")



            #div.add_style("height: 100%")
            div.add_style("text-align: center")
        elif path and path != "__DYNAMIC__":
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

        #if height or self.show_name_hover in ["True","true",True]:
        #    div.add_style("height: 100%")


        # FIXE: what is this for???
        if self.show_name_hover in ["True","true",True]:
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




    def get_path_from_sobject(self, sobject):

        if sobject.get_value("_is_collection", no_exception=True):
            from pyasm.common import Environment
            install_dir = Environment.get().get_install_dir()
            path = "/context/icons/mime-types/folder2.jpg"

            self.lib_path = "%s/src%s" % (install_dir, path)
            self.icon_path = "%s/src%s" % (install_dir, path)
            return path

        icon_path = None
        path = None
        lib_path = None
        main_path = None


        processes =  self.kwargs.get("processes") or ['icon','publish','']
        if isinstance( processes, basestring):
            processes = processes.split(",")


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
            snapshot = Snapshot.get_snapshot(search_type, search_code, process=processes)


        if not snapshot:
            snapshot = Snapshot.get_snapshot("sthpw/search_object", base_search_type, process=processes)


        if snapshot:
            file_type = "web"
            icon_path = snapshot.get_web_path_by_type(file_type)

            file_type = "main"
            main_path = snapshot.get_web_path_by_type(file_type)
            lib_path = snapshot.get_lib_path_by_type(file_type)

        if icon_path:
            path = icon_path
        elif main_path:
            path = self.find_icon_link(main_path)


        # remember the last path
        self.path = path
        self.lib_path = lib_path
        self.main_path = main_path
        self.icon_path = icon_path
        self.snapshot = snapshot
 
        return path


    def find_icon_link(self, file_path, repo_path=None):
        from pyasm.widget import ThumbWdg
        return ThumbWdg.find_icon_link(file_path, repo_path)





