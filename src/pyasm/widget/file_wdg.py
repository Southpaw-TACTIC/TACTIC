###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ["ThumbWdg", "ThumbCmd", "FileInfoWdg"]

import re, time, types, string, os, sys
import urllib

from pyasm.common import Xml, Container, Environment, Config, Common
from pyasm.search import Search, SearchException, SearchKey, SqlException, DbContainer
from pyasm.biz import *
from pyasm.command import Command
from pyasm.web import DivWdg, HtmlElement, Table, Html, SpanWdg, AjaxWdg, WebContainer, AjaxLoader, FloatDivWdg, Widget

from .table_element_wdg import BaseTableElementWdg
from .icon_wdg import *
from .clipboard_wdg import ClipboardAddWdg

import six
basestring = six.string_types

IS_Pv3 = sys.version_info[0] > 2


class ThumbWdg(BaseTableElementWdg):
    '''standard widget that looks at a threesome of files, a main, icon
    and a web file in the snapshot'''
    SQL_ERROR = None
    DEFAULT_CONTEXT = 'publish'
    DEFAULT_PROCESS = 'publish'
    ICON_SIZE = 120
    ARGS_KEYS ={
        "script_path": {
            "description": "Javascript path override for action when preview is clicked",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Action'
            },
        "detail_class_name": {
            "description": "Python widget to display in a new tab when preview is clicked",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Action'
            },


        "icon_context": {
            "description": "context on which the search is applied",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Display'
            },


         "icon_size": {
            "description": "control the icon size by percentage. e.g. 80%",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Display',
            },
         "min_icon_size": {
            "description": "The smallest size the icon will become on resize",
            'type': 'TextWdg',
            'order': 3,
            'category': 'Display',
            },
 
        "cascade_search": {
            "description": "determines whether to keep looking for any image to use as an icon",
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Display'
            },


        "filename": {
            "description": "whether to display the main file name for download",
            'type': 'SelectWdg',
            'order': 5,
            'category': 'Display',
            'values': 'true|false'
            },
        "latest_icon": {
            "description": "whether to display the latest version under any context",
            'type': 'SelectWdg',
            'order': 4,
            'category': 'Display',
            'values': 'true|false'
            },
         "original": {
            "description": "whether to display the original file when clicked on",
            'type': 'SelectWdg',
            'order': 6,
            'category': 'Display',
            'values': 'true|false'
            },
         "file_type": {
            "description": "whether to display the file type for download",
            'type': 'SelectWdg',
            'order': 7,
            'category': 'Display',
            'values': 'true|false'
            },


        "detail": {
            "description": "whether to display the single asset view when clicked on",
            'type': 'SelectWdg',
            'order': 8,
            'category': 'Display',
            'values': 'true|false'
            },
        "protocol": {
            "description": "whether to open the link over http or file system",
            'type': 'SelectWdg',
            'order': 9,
            'category': 'Display',
            'values': 'http|file'
            },
        "search_key": {
            "description": "search_key of sobject to use for displaying icon",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Search',
            },
        "redirect_expr": {
            "description": "expression to control another image related to this sobject. This is slower in performance. e.g. @SOBJECT(prod/sequence)",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Search',
            },
        }



    def get_args_keys(cls):
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)



    def init(self):
        self.top = DivWdg()


        self.icon_size = None
        self.show_filename_flag = False
        self.show_clipboard_flag = True
        self.show_orig_icon = False
        self.show_file_type = False
        self.show_versionless = False
        self.show_latest_icon = False
        self.has_img_link = True
        self.context = None
        # it's getting is_latest by default
        self.version = None
        #self.icon_context = None
        self.name = "snapshot"

        self.data = {}
        self.file_objects = {}
        self.info = {}
        self.image_link_order = []
        self.is_preprocess_run = False

        # DetailWdg for instance can change this to display the web type as icon
        self.icon_type = 'default'
        self.aspect = "width"


    def handle_layout_behaviors(self, layout):
        # Drag will allow the dragging of items from a table onto
        # anywhere else!
        layout.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_image',
            'drag_el': 'drag_ghost_copy',
            'use_copy': 'true',
            'use_delta': 'true',
            'dx': 10, 'dy': 10,
            'drop_code': 'DROP_ROW',
            'copy_styles': 'z-index: 1000; opacity: 0.7; border: solid 1px %s; text-align: left; padding: 10px; max-width: 250px; background: %s' % (layout.get_color("border"), layout.get_color("background")),

            'cbjs_setup': '''
                if(spt.drop) {
                    spt.drop.sobject_drop_setup( evt, bvr );
                }
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


        script_path = self.options.get("script_path")
        class_name = self.options.get("detail_class_name")
        if script_path:
            layout.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_thumb_script_path',
            'script_path': script_path,
            'cbjs_action': '''
                var search_key = bvr.src_el.getAttribute("spt_search_key");
                spt.CustomProject.run_script_by_path(bvr.script_path, {search_key: search_key});
            '''
            } )

        else:
            layout.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_thumb_detail_class_name',
            'class_name': class_name,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = bvr.class_name;
            if ( ! class_name ) {
                class_name = 'tactic.ui.tools.SObjectDetailWdg';
            }


            var search_key = bvr.src_el.getAttribute("spt_search_key");
            var code = bvr.src_el.getAttribute("spt_code");

            var kwargs = {
                search_key: search_key
            };
            var element_name = "detail_"+code;
            var title = "Detail ["+code+"]";
            spt.tab.add_new(element_name, title, class_name, kwargs);
            '''
            } )



            layout.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_thumb_href',
            'class_name': class_name,
            'cbjs_action': '''
            var link = bvr.src_el.getAttribute("spt_href");
            window.open(link);
            '''
            } )
        
 
        #if False:
        #if self.layout_wdg.kwargs.get("icon_generate_refresh") != False \
        if self.layout_wdg and self.layout_wdg.kwargs.get('temp') != True:
            #unique_id = self.layout_wdg.get_unique_id()
            unique_id = self.layout_wdg.get_table_id()
            layout.add_behavior( {
                'type': 'listen',
                'event_name': "loading|%s" % unique_id,
                #'type': 'load',
                'cbjs_action': '''
                var elements = bvr.src_el.getElements(".spt_generate_icon");
                var search_keys = [];
                var rows = [];
                for (var i = 0; i < elements.length; i++) {
                    var search_key = elements[i].getAttribute("spt_search_key");
                    elements[i].removeClass("spt_generate_icon");
                    search_keys.push(search_key);
                    var row = elements[i].getParent(".spt_table_row")
                    rows.push(row);
                }

                if (search_keys.length == 0) {
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
 


    def preprocess(self):
        self.is_preprocess_run = True

        if self.get_option('filename') == 'true':
            self.show_filename_flag = True
        if self.get_option('file_type') == 'true':
            self.show_file_type = True
        if self.get_option('original') == 'true':
            self.show_orig_icon = True
        if self.get_option('versionless') == 'true':
            self.show_versionless = True

        if self.get_option('latest_icon') == 'true':
            self.show_latest_icon = True
        context = self.get_option('icon_context')

        if not context and self.sobjects:
            sobject = self.sobjects[0]
            assert(sobject)
            if sobject:     # protect agains it being None
                context = sobject.get_icon_context(self.context)


        if context:
            self.context = context
        
        if not self.image_link_order:
            order = self.get_option('image_link_order')
            if order:
                order = order.split('|')
            self.set_image_link_order(order)
        
        # preselect all of the snapshots (don't do this for redirect right now)
        redirect = self.get_option("redirect")
        redirect_expr = self.get_option("redirect_expr")

        if not redirect and not redirect_expr and self.sobjects:
            if not self.sobjects[0]:
                # retired
                return

            snapshots = []
            # if it is snapshot, there is no need to search for it again
            # and we dont' try to to look for publish context icons for it to save time
            if isinstance(self.sobjects[0], Snapshot):
                
                snapshots = self.sobjects
            else:
                if self.show_latest_icon:
                    icon_context = None
                else:
                    icon_context = self.sobjects[0].get_icon_context(self.context)


                cascade_search = self.get_option('cascade_search') or 'true'

                try:
                    if self.version == None:
                        self.data = Snapshot.get_by_sobjects(self.sobjects, icon_context, is_latest=True, return_dict=True)


                        if cascade_search != "false":

                            # verify if we get icon for all
                            if len(self.data) < len(self.sobjects):
                                publish_data =  Snapshot.get_by_sobjects(self.sobjects, self.DEFAULT_CONTEXT, is_latest=True, return_dict=True)
                                self._update_data(publish_data)

                            # verify if we get icon for all
                            if len(self.data) < len(self.sobjects):
                                publish_data =  Snapshot.get_by_sobjects(self.sobjects, process=self.DEFAULT_PROCESS, is_latest=True, return_dict=True)
                                self._update_data(publish_data)


                            # verify if we get icon for all
                            if len(self.data) < len(self.sobjects):
                                publish_data =  Snapshot.get_by_sobjects(self.sobjects, is_latest=True, return_dict=True)
                                self._update_data(publish_data)





                    else:
                        self.data = Snapshot.get_by_sobjects(self.sobjects, icon_context, version=self.version, return_dict=True)

                        if cascade_search != "false":

                            # verify if we get icon for all
                            if len(self.data) < len(self.sobjects):
                                publish_data =  Snapshot.get_by_sobjects(self.sobjects, self.DEFAULT_CONTEXT, version=self.version, return_dict=True)
                                self._update_data(publish_data)

                            # verify if we get icon for all
                            if len(self.data) < len(self.sobjects):
                                publish_data =  Snapshot.get_by_sobjects(self.sobjects, process=self.DEFAULT_PROCESS, version=self.version, return_dict=True)
                                self._update_data(publish_data)

                            # verify if we get icon for all
                            if len(self.data) < len(self.sobjects):
                                publish_data =  Snapshot.get_by_sobjects(self.sobjects, version=self.version, return_dict=True)
                                self._update_data(publish_data)




 

                except SqlException as e:
                    self.SQL_ERROR = True 
                    DbContainer.abort_thread_sql()
                    return


                snapshots = self.data.values()

                


            # get all of the file objects
            file_objects = File.get_by_snapshots(snapshots)
            for file_object in file_objects:
                file_code = file_object.get_code()
                self.file_objects[file_code] = file_object



    def _update_data(self, publish_data):
        '''update self.data with 2nd choice publish context data to display an icon'''
        publish_data.update(self.data)
        self.data = publish_data


    def get_title(self):
        return super(ThumbWdg,self).get_title();

    #def is_editable(self):
    #    sobject = self.get_current_sobject()
    #    if sobject and sobject.get_id() == -1:
    #        return False
    #    else:
    #        return True
    def is_editable(self):
        return False



    def get_info(self):
        # FIXME: temporary fix to make flash_swf_view_wdg.py work
        return self.info


    def handle_th(self, th, cell_idx):
        th.add_style("min-width", "55px")
        return

        if not self.width:
            th.add_style("width", "55px")
        else:
            th.add_style("width: %s" % self.width)


    def handle_td(self, td):
        td.set_attr('spt_input_type', 'upload')
        td.add_style("min-width", "55px")
        td.add_class("spt_cell_never_edit")


    def set_icon_size(self, size):
        self.icon_size = str(size)
    

    def get_icon_size(self):
        ICON_SIZE = 120
        if not self.icon_size:
            self.icon_size = 120

        unit = None
        icon_size = self.icon_size
        if isinstance(self.icon_size, basestring):
            icon_size, unit = self.split_icon_size(self.icon_size)

        icon_mult = PrefSetting.get_value_by_key("thumb_multiplier")
        if not icon_mult:
            icon_mult = 1
        else:
            icon_mult = float(icon_mult)

        if not icon_size:
            size = float(ICON_SIZE * icon_mult)
        else:
            size = float(icon_size * icon_mult)

        # cap the size to 15
        if size < 15:
            size = 15
            
        if unit:
            size = '%s%s' %(icon_size, unit)
        return size


    def set_aspect(self, aspect):
        self.aspect = aspect

    def set_show_filename(self, flag):
        self.show_filename_flag = flag

    def set_show_clipboard(self, flag):
        self.show_clipboard_flag = flag

    def set_show_orig_icon(self, flag):
        self.show_orig_icon = flag

    def set_show_latest_icon(self, flag):
        self.show_latest_icon = flag

    def set_show_file_type(self, flag):
        self.show_file_type = flag

    def set_has_img_link(self, show):
        self.has_img_link = show

    def set_icon_type(self, icon_type):
        self.icon_type = icon_type


    def set_image_link_order(self, order):
        if order:
            self.image_link_order = order

    def set_context(self, context):
        ''' if set externally, the sobject's icon_context will be ignored '''
        self.context = context

    def set_version(self, version):
        self.version = version


    def get_no_icon_wdg(self, missing=False):
        sobject = self.get_current_sobject()
        if not sobject:
            return ''

        div = DivWdg()

        div.add_style("position: relative")
        div.add_style("margin: 2px")
        div.add_class("spt_thumb_top")
        div.add_style("box-sizing: border-box")

        div.add_style("box-shadow: 0px 0px 10px rgba(0,0,0,0.1)")
        div.add_style("border-radius: 5px")
        div.add_style("overflow: hidden")
        div.add_style("opacity: 0.4")

        div.set_id( "thumb_%s" %  sobject.get_search_key() )
        icon_size = self.get_icon_size()

        if icon_size:
            div.add_style("%s: %s" % (self.aspect, icon_size) )

        if missing:
            img = HtmlElement.img(ThumbWdg.get_missing_image())
        elif sobject.get_value("_is_collection", no_exception=True):
            img = HtmlElement.img("/context/icons/mime-types/folder2.jpg")
        else:
            img = HtmlElement.img(ThumbWdg.get_no_image())

        img.add_class("spt_image")


        #from tactic.ui.table import SObjectDetailElementWdg
        #detail = SObjectDetailElementWdg()
        #detail.set_widget(img)
        #detail.set_sobject(sobject)
        #div.add(detail)

        div.add(img)
        div.add_class("hand")
        if self.SQL_ERROR:
            warning_div = DivWdg('<i>-- preprocess error --</i>')
            warning_div.add_styles('position: absolute; z-index: 100; float: left; top: 0; left: 0; font-size: smaller;')
            div.add_style('position: relative')
            div.add(warning_div)

        search_key = SearchKey.get_by_sobject(sobject)
        code = sobject.get_code()
       
        
        detail = self.get_option("detail")
        if detail != 'false':
            self.add_icon_behavior(div, sobject)

        unit = None
        if isinstance(icon_size, basestring):
            icon_size, unit = self.split_icon_size(icon_size)

            img.add_style("%s: 100%%" % self.aspect )
        else:
            img.add_style("%s: %s" % (self.aspect, self.get_icon_size()) )
            img.add_style("min-%s: 15px" % self.aspect)

        return div


    def is_simple_viewable(self):
        return False

    def add_style(self, name, value=None):
        self.top.add_style(name, value)



    def get_data(self, sobject):

        # if there is a redirect to the sobject (a relation), use that
        redirect = self.get_option("redirect")
        redirect_expr = self.get_option("redirect_expr")
        parser = ExpressionParser()
        
        if redirect and sobject:
            if redirect == "true":
                # use search_type and search_id pair
                # FIXME: go up a maximum of 2 .. this is not so stable as
                # the parent may have a similar relationship
                for i in range(0,2):
                    if not sobject:
                        #return self.get_no_icon_wdg()
                        return ""

                    if sobject.has_value("search_type"):
                        search_type = sobject.get_value("search_type")
                        # if search_type does not exist, just break out
                        if not search_type:
                            break

                        search_code = sobject.get_value("search_code", no_exception=True)
                        if search_code:
                            sobject = Search.get_by_code(search_type, search_code)
                        else:
                            search_id = sobject.get_value("search_id", no_exception=True)
                            sobject = Search.get_by_id(search_type, search_id)
                        if sobject:
                            break

            elif redirect.count("|") == 2:
                search_type, col1, col2 = redirect.split("|")
                search = Search(search_type)
                search.add_filter(col1, sobject.get_value(col2) )
                sobject = search.get_sobject()
                if not sobject:
                    #return self.get_no_icon_wdg()
                    return ""

        elif redirect_expr and sobject:
            redirect_sobject = parser.eval(redirect_expr, sobjects=[sobject], single=True)
            if redirect_sobject:
                sobject = redirect_sobject
            else:
                #return self.get_no_icon_wdg()
                return ""

        # get the icon context from the sobject
        icon_context = self.get_option("icon_context")
        if not icon_context:
            icon_context = sobject.get_icon_context(self.context)

        # try to get an icon first
        if isinstance(sobject, Snapshot):
            snapshot = sobject
            # check if the sobject actually exists
            try:
                snapshot.get_sobject()
            except SObjectNotFoundException as e:
                #return IconWdg('sobject n/a for snapshot code[%s]' %snapshot.get_code(), icon=IconWdg.ERROR)
                return ""
            except SearchException as e:
                #return IconWdg('parent for snapshot [%s] not found' %snapshot.get_code(), icon=IconWdg.ERROR)
                return ""
       
        else:
            # this is to limit unnecessary queries
            snapshot = None
            if self.data:
                search_key = SearchKey.get_by_sobject(sobject, use_id=False)
                snapshot = self.data.get(search_key)
            elif self.is_ajax(check_name=False) or redirect or redirect_expr:
                if self.show_latest_icon:
                    icon_context = None
                    
                snapshot = Snapshot.get_latest_by_sobject(sobject, icon_context, show_retired=False)

                # get the latest icon period
                if not snapshot and icon_context == 'icon':
                    snapshot = Snapshot.get_latest_by_sobject(sobject, show_retired=False)


        if not snapshot:
            #return self.get_no_icon_wdg()
            return ""


        xml = snapshot.get_xml_value("snapshot")
        
        # data structure to store self.info
        self.info = {}
        # get the file objects if they have not already been cached
        if not self.file_objects:
            file_objects = {}
            snapshot_file_objects = File.get_by_snapshot(snapshot)
            
            for file_object in snapshot_file_objects:
                file_objects[file_object.get_code()] = file_object
        else:
            file_objects = self.file_objects

        protocol = self.get_option("protocol")
        if not protocol:
            from pyasm.prod.biz import ProdSetting
            protocol = ProdSetting.get_value_by_key('thumbnail_protocol')

        # go through the nodes and try to find appropriate paths
        self.info = ThumbWdg.get_file_info(xml, file_objects, sobject, snapshot, self.show_versionless, protocol=protocol) 
        # find the link that will be used when clicking on the icon
        link_path = ThumbWdg.get_link_path(self.info, image_link_order=self.image_link_order)

        if link_path == None:
            
            # check for ref snapshot
            snapshots = snapshot.get_all_ref_snapshots()
            snapshot_file_objects = []
            if snapshots:
                snapshot = snapshots[0]
                # change the sobject value here also, affects the Thumb id below
                sobject = snapshot.get_sobject()
                xml = snapshot.get_xml_value("snapshot")
                snapshot_file_objects = File.get_by_snapshot(snapshot)
                
            for file_object in snapshot_file_objects:
                file_objects[file_object.get_code()] = file_object
            self.info = ThumbWdg.get_file_info(xml, file_objects, sobject, snapshot, self.show_versionless, protocol=protocol) 
            link_path = ThumbWdg.get_link_path(self.info, image_link_order=self.image_link_order)

        return link_path
 



    def get_display(self):
        self.aspect = self.get_option('aspect')
        if not self.aspect:
            self.aspect = "width"

        search_key = self.get_option('search_key')
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            self.set_sobject(sobject)

        if not self.is_preprocess_run:
            self.preprocess()

 
  
        # get the set size
        icon_size = self.get_option("icon_size")
        if icon_size:
            self.set_icon_size(icon_size)
        # get the real size
        icon_size = self.get_icon_size()


        min_size = self.get_option("min_icon_size")
        if not min_size:
            min_size = 45 




        sobject = self.get_current_sobject()
        # get it from the web container
        if not sobject:
            web = WebContainer.get_web()
            search_type = web.get_form_value("search_type")
            search_code = web.get_form_value("search_code")
            search_id = web.get_form_value("search_id")
            icon_size = web.get_form_value("icon_size")
            if icon_size:
                self.icon_size = icon_size
            if search_type and search_code:
                sobject = Search.get_by_code(search_type, search_code)
                self.set_sobject(sobject)
            elif search_type and search_id:
                sobject = Search.get_by_id(search_type, search_id)
                self.set_sobject(sobject)
            else:
                return self.get_no_icon_wdg()

        elif sobject.get_id() == -1:
            """
            div = DivWdg()
            div.add("&nbsp;")
            div.add_style("text-align: center")
            return div
            """
            pass




        # if there is a redirect to the sobject (a relation), use that
        redirect = self.get_option("redirect")
        redirect_expr = self.get_option("redirect_expr")
        parser = ExpressionParser()
        
        if redirect and sobject:
            if redirect == "true":
                # use search_type and search_id pair
                # FIXME: go up a maximum of 2 .. this is not so stable as
                # the parent may have a similar relationship
                for i in range(0,2):
                    if not sobject:
                        return self.get_no_icon_wdg()

                    if sobject.has_value("search_type"):
                        search_type = sobject.get_value("search_type")
                        # if search_type does not exist, just break out
                        if not search_type:
                            break

                        search_code = sobject.get_value("search_code", no_exception=True)
                        if search_code:
                            sobject = Search.get_by_code(search_type, search_code)
                        else:
                            search_id = sobject.get_value("search_id", no_exception=True)
                            sobject = Search.get_by_id(search_type, search_id)
                        if sobject:
                            break

            elif redirect.count("|") == 2:
                search_type, col1, col2 = redirect.split("|")
                search = Search(search_type)
                search.add_filter(col1, sobject.get_value(col2) )
                sobject = search.get_sobject()
                if not sobject:
                    return self.get_no_icon_wdg()

        elif redirect_expr and sobject:
            redirect_sobject = parser.eval(redirect_expr, sobjects=[sobject], single=True)
            if redirect_sobject:
                sobject = redirect_sobject
            else:
                return self.get_no_icon_wdg()

        # get the icon context from the sobject
        icon_context = self.get_option("icon_context")
        if not icon_context:
            icon_context = sobject.get_icon_context(self.context)

        # try to get an icon first
        if isinstance(sobject, Snapshot):
            snapshot = sobject
            # check if the sobject actually exists
            try:
                snapshot.get_sobject()
            except SObjectNotFoundException as e:
                return IconWdg('sobject n/a for snapshot code[%s]' %snapshot.get_code(), icon=IconWdg.ERROR)
            except SearchException as e:
                return IconWdg('parent for snapshot [%s] not found' %snapshot.get_code(), icon=IconWdg.ERROR)
       
        else:
            # this is to limit unnecessary queries
            snapshot = None
            if self.data:
                search_key = SearchKey.get_by_sobject(sobject, use_id=False)
                snapshot = self.data.get(search_key)
            elif self.is_ajax(check_name=False) or redirect or redirect_expr:
                if self.show_latest_icon:
                    icon_context = None
                    
                snapshot = Snapshot.get_latest_by_sobject(sobject, icon_context, show_retired=False)

                # get the latest icon period
                if not snapshot and icon_context == 'icon':
                    snapshot = Snapshot.get_latest_by_sobject(sobject, show_retired=False)


        if not snapshot:
            icon = self.get_no_icon_wdg()
            return icon


        xml = snapshot.get_xml_value("snapshot")
        
        # data structure to store self.info
        self.info = {}
        # get the file objects if they have not already been cached
        if not self.file_objects:
            file_objects = {}
            snapshot_file_objects = File.get_by_snapshot(snapshot)
            
            for file_object in snapshot_file_objects:
                file_objects[file_object.get_code()] = file_object
        else:
            file_objects = self.file_objects

        protocol = self.get_option("protocol")
        if not protocol:
            from pyasm.prod.biz import ProdSetting
            protocol = ProdSetting.get_value_by_key('thumbnail_protocol')

        # go through the nodes and try to find appropriate paths
        self.info = ThumbWdg.get_file_info(xml, file_objects, sobject, snapshot, self.show_versionless, protocol=protocol) 
        # find the link that will be used when clicking on the icon
        link_path = ThumbWdg.get_link_path(self.info, image_link_order=self.image_link_order)

        if link_path == None:
            
            # check for ref snapshot
            snapshots = snapshot.get_all_ref_snapshots()
            snapshot_file_objects = []
            if snapshots:
                snapshot = snapshots[0]
                # change the sobject value here also, affects the Thumb id below
                sobject = snapshot.get_sobject()
                xml = snapshot.get_xml_value("snapshot")
                snapshot_file_objects = File.get_by_snapshot(snapshot)
                
            for file_object in snapshot_file_objects:
                file_objects[file_object.get_code()] = file_object
            self.info = ThumbWdg.get_file_info(xml, file_objects, sobject, snapshot, self.show_versionless, protocol=protocol) 
            link_path = ThumbWdg.get_link_path(self.info, image_link_order=self.image_link_order)
            
        # define a div
        div = DivWdg()
        div.add_class("spt_thumb_top")
        div.set_attr('SPT_ACCEPT_DROP', 'DROP_ROW')


        div.add_style("box-shadow: 0px 0px 10px rgba(0,0,0,0.1)")
        div.add_style("border-radius: 5px")
        div.add_style("overflow: hidden")

      
        # if no link path is found, display the no icon image
        if link_path == None:
            return self.get_no_icon_wdg()


        repo_path = ThumbWdg.get_link_path(self.info['_repo'], image_link_order=self.image_link_order)
        #if repo_path and repo_path.startswith("//"):
        if False:
            # PERFORCE
            # FIXME: need a better check the this.  This is test code
            # for viewing perforce images when running perforce web server
            version = snapshot.get_value("version")
            link_path = "http://localhost:8080%s&rev=%s" % (link_path, version)

        elif not repo_path or not os.path.exists(repo_path):
            return self.get_no_icon_wdg(missing=True)

        elif repo_path.endswith(".svg"):
            f = open(repo_path, 'r')
            html = f.read()
            f.close()
            div.add(html)
            return div

        if self.icon_type == 'default':
            # Fix Template icon_size=100% icon_type always load web versions
            
            if isinstance(icon_size, basestring):
                icon_size, unit = self.split_icon_size(icon_size)

            icon_size_check = float(icon_size)
 
    
            if icon_size_check > 120:
                icon_type = 'web'
            else:
                icon_type = 'icon'
        else:
            icon_type = self.icon_type

        icon_info = self.get_icon_info(link_path, repo_path=repo_path, icon_type=icon_type)
        icon_link = icon_info.get('icon_link')
        icon_size = icon_info.get('icon_size')
        icon_missing = icon_info.get('icon_missing')

        search_type = sobject.get_base_search_type()
        if icon_link.endswith("indicator_snake.gif"):
            if search_type != 'sthpw/snapshotXYZ':
                image_size = os.path.getsize(repo_path)
                if image_size != 0:
                    # generate icon inline
                    """
                    search_key = sobject.get_search_key()
                    thumb_cmd = ThumbCmd(search_keys=[search_key])
                    thumb_cmd.execute()
                    icon_link = thumb_cmd.get_path()
                    """

                    # generate icon dynamically
                    div.set_attr("spt_search_key", sobject.get_search_key())
                    div.add_class("spt_generate_icon")
                    div.set_attr("spt_image_size", image_size)
                else:
                    icon_missing = True
            else:
                icon_link = icon_link.replace("indicator_snake.gif", "generic_image.png")


        div.set_id( "thumb_%s" %  sobject.get_search_key() )
        div.add_style( "display: block" )
        div.add_style("%s: %s" % (self.aspect, icon_size) )
        div.add_style("min-%s: %s" % (self.aspect, min_size) )
        #div.set_box_shadow("0px 0px 5px")
        div.add_style("overflow: hidden")
        div.add_style("text-overflow: ellipsis")
        div.add_style("white-space: nowrap")
        div.add_border()

        div.add_style("text-align: left" )


        if self.kwargs.get("shape") in ['circle']:
            div.add_style("border-radius: %s" % icon_size)
            div.add_style("overflow: hidden")




        if icon_missing:
            missing_div = DivWdg()
            div.add(missing_div)
            missing_icon = IconWdg("Missing files", IconWdg.ERROR, width='12px')
            missing_div.add(missing_icon)

            missing_div.add_style("margin-top: 0px")
            missing_div.add_style("position: absolute")


        elif icon_link == "__DYNAMIC__":

            base, ext = os.path.splitext(repo_path)
            ext = ext.upper().lstrip(".")

            #flat ui color
            colors = ['#1ABC9C', '#2ECC71', '#3498DB','#9B59B6','#34495E','#E67E22','#E74C3C','#95A5A6']
            color = colors[Common.randint(0,7)]




            img = DivWdg()
            img.add_class("spt_image")
            div.add(img)
            img.add("<div style='padding-top: 30%%'>%s</div>" % ext)
            img.add_style("text-align: center")
            img.add_style("color: #fff")
            img.add_style("background: %s" % color)

            img.add_style("min-width: 50px")
            img.add_style("min-height: 30px")
            #img.add_style("width: 95%")
            img.add_style("padding-bottom: 40%")

            img.add_style("padding: 0px")
            img.add_style("font-size: 20px")
            img.add_style("font-weight: bold")




        else:

            img = HtmlElement.img(icon_link)
            img.add_class("spt_image")

            # TODO: make this a preference
            img.add_style("background: #ccc")

            if isinstance(icon_size, basestring):
                icon_size, unit = self.split_icon_size(icon_size)
                img.add_style("%s: 100%%" % self.aspect)
            else:
                img.add_style("%s: %s" % (self.aspect, icon_size) )


        detail = self.get_option("detail")

        #deals with the icon attributes
        if detail == "false":
            if self.has_img_link:
                if protocol =='file':
                    dir_naming = DirNaming()
                    client_base_dir = dir_naming.get_base_dir('client_repo')
                    web_base_dir = Config.get_value("checkin", "web_base_dir")

                    link_path = re.sub('^%s'%web_base_dir,'', link_path)
                    link_path = '%s%s' %(client_base_dir[0], link_path)
                    href = DivWdg(img)
                    href.add_attr('title', 'Click to open via file system')
                    href.add_behavior({'type':'click' ,
                        'cbjs_action': "spt.Applet.get().open_explorer('%s')" %link_path})
                
                else: # protocol not set or equals 'http'
                    is_dir = True
                    # add a file browser for directories
                    if repo_path and os.path.isdir(repo_path):
                        img.add_behavior( {
                        'type': 'click_up',
                        'repo_path': repo_path,
                        'cbjs_action': '''
                        var base_dir = bvr.repo_path;
                        var class_name = 'tactic.ui.tools.SnapshotDirListWdg';
                        var kwargs = {
                            'base_dir': base_dir,
                            'location': 'server'
                        }
                        spt.panel.load_popup("Folder", class_name, kwargs);
                        '''
                        } )
                        href = img

                    else:
                        href = HtmlElement.href(img, link_path)
                        href.add_class("spt_thumb_href")
                        href.add_attr("spt_href", link_path)
                        href.add_attr("target", "_blank")



                    
                div.add(href)

            else:
                div.add(img)
        elif detail == "none":
            div.add(img)
        else:
            div.add(img)
            div.add_class("hand")

            self.add_icon_behavior(div, sobject)


        
        # add an optional source/original file icon
        if self.show_orig_icon:
            # make sure main is first
            link_order = ['main', 'web'] 
            link_path = ThumbWdg.get_link_path(self.info, link_order)
            img = IconWdg("source file", icon= IconWdg.IMAGE)
            
            href = HtmlElement.href(img, link_path)
            href.add_style('float: left')
            href.set_attr("spt_href", link_path)
            href.add_class("spt_thumb_href")
            
            div.add(HtmlElement.br(clear="all"))
            div.add(href)

        # add an optional text link
        if self.show_filename_flag:
            text_link = ThumbWdg.get_link_path(self.info, self.image_link_order)
            self.set_text_link(div, div, text_link)

        if self.show_file_type:
            links_list = ThumbWdg.get_file_info_list(xml, file_objects, sobject, snapshot, self.show_versionless)
            self.set_type_link(div, links_list) 



        return div



    def add_icon_behavior(self, widget, sobject):
        search_key = SearchKey.get_by_sobject(sobject)
        code = sobject.get_code()

        widget.add_attr("spt_search_key", search_key)
        widget.add_attr("spt_code", code)

        script_path = self.options.get("script_path")
        class_name = self.options.get("detail_class_name")

        if script_path:
            widget.add_class("spt_thumb_script_path")
        else:
            widget.add_class("spt_thumb_detail_class_name")


        return


    
    def set_type_link(self, widget, link_path_list):
        ''' set the format of the file type links '''
        type_div = DivWdg()
        for type, link_path in link_path_list:
            href = HtmlElement.href(type, link_path)
            href.add_color('color','color')
            href.set_attr("target", "_blank")
            href.add_tip('Right-click and choose [Save Link As..] to save to disk') 
            type_div.add(SpanWdg(href, 'small'))

        widget.add(type_div)
    
    def set_text_link(self, widget, div, link_path):
        ''' set the format of the text link. Overridable for different formats '''
        filename = os.path.basename(link_path)
        if len(filename) > 30:
            filename = "%s..." % (filename[0:30])

        href = HtmlElement.href(filename, link_path)
        href.add_style('font-size: 0.8em')
        href.add_color('color','color')
        href.set_attr("target", "_blank")
        href.add_tip('%s::<i>Right-click and choose [Save Link As..]'\
            'to save to disk</i>' % filename) 
 
        # avoid double link break
        if not self.show_orig_icon:
            div.add(HtmlElement.br(2))
        widget.add(href)




    def get_link_path( info, image_link_order=None):
        ''' get the link for the thumbnail '''
        image_link = None

        default_image_link_order = ['web', 'main', '.swf']
        
        if image_link_order:
            default_image_link_order = image_link_order


        for item in default_image_link_order:
            if item in info:
                image_link = info[item]
                break
        else:
            # grab the first one that is not an icon
            for key, value in info.items():
                # _repo and icon are special, skip it
                if key in ["icon", "_repo"]:
                    continue
                image_link = info[key]
                break

        # as a last resort, get the icon path
        if not image_link:
            image_link = info.get('icon')

        return image_link
    get_link_path = staticmethod(get_link_path)


    def get_icon_info(self, image_link, repo_path=None, icon_type='icon'):
        ''' if no icon is specified then get the icon based on the main file,
        otherwise use the specified icon '''

        icon_info = {}

        icon_size = self.get_icon_size()
        icon_link = None
        if icon_type in self.info:
            icon_link = self.info[icon_type]
            if not os.path.exists(repo_path):
                icon_link = ThumbWdg.get_no_image()
                icon_info['icon_missing'] = True

            # HACK for pdf icons
            if image_link.endswith(".pdf"):
                #check if icon_size is a string: integer num endswith unit

                if isinstance(icon_size, basestring):
                    icon_size, unit = self.split_icon_size(icon_size)
                    icon_size = int( 80.0 / 120.0 * float(icon_size) )
                    icon_size = '%s%s' %(icon_size, unit)
                        
                else:
                    icon_size = int( 80.0 / 120.0 * float(icon_size) )
            
        else:
            icon_link = ThumbWdg.find_icon_link(image_link, repo_path)
            #icon_size = int( 60.0 / 120.0 * float(icon_size) )
        icon_info['icon_size'] = icon_size
        icon_info['icon_link'] = icon_link

        return icon_info


    def find_icon_link(file_path, repo_path=None):
        base = "/context/icons/mime-types"
        icon = None
        if not file_path:
            return ThumbWdg.get_no_image()
        ext = File.get_extension(file_path)
        ext = ext.lower()

        if ext in ["xls", "xlsx"]:
            #icon = "gnome-application-vnd.ms-excel.png"
            icon = "microsoft/Excel-2013.png"
        elif ext in ["ppt", "pptx"]:
            #icon = "gnome-application-vnd.ms-excel.png"
            icon = "microsoft/Powerpoint-2013.png"
        elif ext in ["doc", "docx", "rtf"]:
            icon = "microsoft/Word-2013.png"
        elif ext == "mp3" or ext == "wav":
            icon = "mp3_and_wav.jpg"
        elif ext == "aif" or ext == 'aiff':
            #icon = "gnome-audio-x-aiff.png"
            icon = "mp3_and_wav.jpg"
        elif ext == "mpg":
            icon = "gnome-video-mpeg.png"
        elif ext in ["mov"]:
            icon = "icon_qt_big.jpg"
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
            icon = "adobe-PDF-icon.jpg"
        elif ext == "shk":
            icon = "icon_shake_white.gif"
        elif ext == "comp":
            icon = "fusion.png"
        elif ext == "txt":
            icon = "txt-notes.png"
        elif ext in ["obj", "mtl"]:
            icon = "3d_obj.png"
        elif ext == "rdc":
            icon = "red_camera.png"
        
        #for adobe products
        elif ext == 'ps':
            icon = "adobe/Photoshop.png"
        elif ext == 'psd':
            icon = "adobe/Photoshop.png"
        elif ext == 'ai':
            icon = "adobe/Illustrator.png"
        elif ext == 'br':
            icon = "adobe/Bridge.png"
        elif ext == 'au':
            icon = "adobe/Audition.png"
        elif ext == 'ae':
            icon = "adobe/After_Effects.png"
        elif ext == 'dw':
            icon = "adobe/Dreamweaver.png"
        elif ext == 'en':
            icon = "adobe/Encode.png"
        elif ext == 'fw':
            icon = "adobe/Fireworks.png"
        elif ext == 'fi':
            icon = "adobe/Fireworks.png"
        elif ext == 'fb':
            icon = "adobe/Flash_Builder.png"
        elif ext == 'id':
            icon = "adobe/InDesign.png"
        elif ext == 'lr':
            icon = "adobe/LightRoom.png"
        elif ext == 'pl':
            icon = "adobe/Prelude.png"
        elif ext == 'pr':
            icon = "adobe/Premiere_Pro.png"
        elif ext == 'swf':
            icon = "adobe/SWF.png"

        #for web files
        #elif ext == "html":
        #    icon = "html.png"
        elif ext == "css":
            icon = "css.png"
        elif ext == "js":
            icon = "javascript.png"

        elif ext == 'fdx':
            icon = "finaldraft.png"
        elif ext == 'unity3d':
            icon = "unity_icon.jpg"
        elif repo_path and os.path.isdir(repo_path):
            icon = "folder2.jpg"
        elif ext in File.VIDEO_EXT:
            #icon = "general_video.png"
            icon = "indicator_snake.gif"
        elif ext in File.IMAGE_EXT:
            icon = "indicator_snake.gif"
        else:
            icon = "__DYNAMIC__"

        if base and icon != "__DYNAMIC__":
            path = "%s/%s" % ( base,icon)
        else:
            path = icon
        return path

    find_icon_link = staticmethod(find_icon_link)
    
    def get_no_image():
        return "/context/icons/common/no_image.png"
    get_no_image = staticmethod(get_no_image)

    def get_missing_image():
        return "/context/icons/common/missing_files.png"
    get_missing_image = staticmethod(get_missing_image)


   

    def get_file_info(xml, file_objects, sobject, snapshot, show_versionless=False, is_list=False, protocol='http'):
        
        info = {}
        #TODO: {'file_type': [file_type]: [path], 'base_type': [base_type]: [file|directory|sequence]}

        if is_list:
            info = []
        else:
            repo_info = {}
            info['_repo'] = repo_info

        nodes = xml.get_nodes("snapshot/file")
        for node in nodes:
            type = Xml.get_attribute(node, "type")

            file_code = Xml.get_attribute(node, "file_code")

            file_object = file_objects.get(file_code)
            if not file_object:
                if isinstance(info, dict):
                    info[type] = ThumbWdg.get_no_image()
                else:
                    info.append((type, ThumbWdg.get_no_image()))
                Environment.add_warning("No file object", "No file object found for file code '%s'" % file_code)
                continue

            file_name = file_object.get_full_file_name()
            web_dir = sobject.get_web_dir(snapshot, file_object=file_object)

            # handle a range if it exists
            file_range = file_object.get_value("file_range")
            if file_range:
                from pyasm.biz import FileGroup, FileRange
                file_range = FileRange.get(file_range)
                file_names = FileGroup.expand_paths(file_name, file_range)
                # just check the first frame
                if file_names:
                    file_name = file_names[0]
            path = "%s/%s" % (web_dir, file_name)

            if protocol != "file":
                if not IS_Pv3:
                    if isinstance(path, unicode):
                        path = path.encode("utf-8")
                        path = urllib.pathname2url(path)
                else:
                    path = urllib.request.pathname2url(path)

            if isinstance(info, dict):
                info[type] = path

                lib_dir = sobject.get_lib_dir(snapshot, file_object=file_object)
                repo_info[type] = "%s/%s" % (lib_dir, file_name)
            else:
                info.append((type, path))

        return info
    get_file_info = staticmethod(get_file_info)

    def get_refresh_script(sobject, icon_size=None, show_progress=True):
        print("DEPRECATED: Snapshot.get_refresh_script!")

        # get the ajax loader for the thumbnail
        ajax = AjaxLoader("thumb_%s" % sobject.get_search_key() )
        ajax.set_load_class("pyasm.widget.ThumbWdg")
        ajax.set_option("search_type", sobject.get_search_type() )
        ajax.set_option("search_id", sobject.get_id() )
        if icon_size:
            ajax.set_option("icon_size", icon_size )
        return ajax.get_on_script(show_progress=show_progress)

    get_refresh_script = staticmethod(get_refresh_script)



    def get_file_info_list(xml, file_objects, sobject, snapshot, show_versionless=False):
        info = ThumbWdg.get_file_info( xml, file_objects, sobject, snapshot, show_versionless=False, is_list=True)

        return info

    get_file_info_list = staticmethod(get_file_info_list)



    def split_icon_size(self, icon_size):
        m = re.match('(\d+\.?\d*)(pt|em|%|px)*', icon_size)
        num = 0
        unit = ''
        if m:
            num, unit = m.groups()
            icon_size = float(num)
        return icon_size, unit



class ThumbCmd(Command):

    def get_path(self):
        return self.path

    def execute(self):

        search_keys  = self.kwargs.get("search_keys")
        self.path = None

        for search_key in search_keys:
            self.generate_icon(search_key)


        self.info = {
            'search_keys': search_keys
        }
        self.add_description('Generate Thumbnail with ThumbCmd')

    def generate_icon(self, search_key):

        sobject = Search.get_by_search_key(search_key)
        search_code = sobject.get_code()
        search_type = sobject.get_search_type()
        base_search_type = sobject.get_base_search_type()


        if base_search_type == 'sthpw/snapshot':
            snapshot_code = sobject.get_code()

            file_type = "main"
            path = sobject.get_lib_path_by_type(file_type)

            if path.find("#") != -1:
                lib_dir = sobject.get_lib_dir()
                file_name = sobject.get_expanded_file_names()[0]
                path = "%s/%s" % (lib_dir, file_name)


            """
            # To check if it is a sequence checkin
            all_snapshots=sobject.get_all_file_objects()
            for single_snapshot in all_snapshots:
                if single_snapshot.get('base_type') == 'sequence':
                    return
            """

            icon_creator = IconCreator(path)
            icon_creator.execute()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()
            if web_path:
                sub_file_paths = [web_path, icon_path]
                sub_file_types = ['web', 'icon']

                from pyasm.checkin import FileAppendCheckin
                checkin = FileAppendCheckin(snapshot_code, sub_file_paths, sub_file_types, mode="inplace")
                checkin.execute()
                snapshot = checkin.get_snapshot()
            else:
                snapshot = sobject


        else:

            snapshot = Snapshot.get_snapshot(search_type, search_code, process=['publish',''])

            if not snapshot:
                return


            #To check if it is a sequence checkin
            all_snapshots=snapshot.get_all_file_objects()
            for single_snapshot in all_snapshots:
                if single_snapshot.get('base_type') == 'sequence':
                    return

            file_type = "main"
            path = snapshot.get_lib_path_by_type(file_type)
            ext = File.get_extension(path)
            ext = ext.lower()
            if ext in File.NORMAL_EXT:

                return

            # use api
            """
            from tactic_client_lib import TacticServerStub
            server = TacticServerStub.get()
            snapshot = server.simple_checkin(search_key, "icon", path, mode="copy")
            """

            print("path: ", path)
            if not os.path.exists(path):
                print("WARNING: path [%s] does not exist" % path)
                return

            icon_creator = IconCreator(path)
            icon_creator.execute()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()
            if web_path and icon_path:
                sub_file_paths = [path, web_path, icon_path]
                sub_file_types = ['main', 'web', 'icon']

                from pyasm.checkin import FileCheckin
                checkin = FileCheckin(sobject, sub_file_paths, sub_file_types, context='icon', mode="copy")
                checkin.execute()
                snapshot = checkin.get_snapshot()

            # need the actual sobject to get the path to replace the icon
            # in the ui
            #snapshot = Search.get_by_search_key(snapshot.get("__search_key__"))


        self.path = snapshot.get_web_path_by_type("icon")







class FileInfoWdg(BaseTableElementWdg):

    def get_title(self):
        return "File Info"


    def get_display(self):
        sobject = self.get_current_sobject()

        if self.name == None:
            self.name = "snapshot"

        xml = sobject.get_xml_value(self.name)

        images = xml.get_values("snapshot/file/@name")
        if len(images) != 3:
            return "No images"
        file_codes = xml.get_values("snapshot/file/@file_code")

        html = Html()
        for i in range(0, len(images)):
            html.writeln("%0.10d : %s<br/>" % (int(file_codes[i]), images[i]) )

        return html.getvalue()
