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

import re, time, types, string, os

from pyasm.common import Xml, Container, Environment, Config
from pyasm.search import Search, SearchException, SearchKey, SqlException, DbContainer
from pyasm.biz import *
from pyasm.command import Command
from pyasm.web import DivWdg, HtmlElement, Table, Html, SpanWdg, AjaxWdg, WebContainer, AjaxLoader, FloatDivWdg, Widget

from table_element_wdg import BaseTableElementWdg
from icon_wdg import *
from clipboard_wdg import ClipboardAddWdg

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

    def init(my):
        my.top = DivWdg()


        my.icon_size = None
        my.show_filename_flag = False
        my.show_clipboard_flag = True
        my.show_orig_icon = False
        my.show_file_type = False
        my.show_versionless = False
        my.show_latest_icon = False
        my.has_img_link = True
        my.context = None
        # it's getting is_latest by default
        my.version = None
        #my.icon_context = None
        my.name = "snapshot"

        my.data = {}
        my.file_objects = {}
        my.info = {}
        my.image_link_order = []
        my.is_preprocess_run = False

        # DetailWdg for instance can change this to display the web type as icon
        my.icon_type = 'default'
        my.aspect = "width"


    def handle_layout_behaviors(my, layout):
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
            'cbjs_pre_motion_setup': 'if(spt.drop) {spt.drop.sobject_drop_setup( evt, bvr );}',
            'copy_styles': 'z-index: 1000; opacity: 0.7; border: solid 1px %s; text-align: left; padding: 10px; width: 0px; background: %s' % (layout.get_color("border"), layout.get_color("background"))
        } )


        script_path = my.options.get("script_path")
        class_name = my.options.get("detail_class_name")

        if script_path:
            layout.add_behavior( {
            'type': 'smart_click_up',
            'bvr_match_class': 'spt_thumb_script_path',
            'script_path': script_path,
            'cbjs_action': '''
            var script = spt.CustomProject.get_script_by_path(bvr.script_path);
            spt.CustomProject.exec_script(script);
            '''
            } )

        else:
            layout.add_behavior( {
            'type': 'smart_click_up',
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



            layout.add_behavior( {
            'type': 'smart_click_up',
            'bvr_match_class': 'spt_thumb_href',
            'class_name': class_name,
            'cbjs_action': '''
            var link = bvr.src_el.getAttribute("spt_href");
            window.open(link);
            '''
            } )
        
 
        #if False:
        #if my.layout_wdg.kwargs.get("icon_generate_refresh") != False \
        if my.layout_wdg and my.layout_wdg.kwargs.get('temp') != True:
            #unique_id = my.layout_wdg.get_unique_id()
            unique_id = my.layout_wdg.get_table_id()
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
 


    def preprocess(my):
        my.is_preprocess_run = True

        if my.get_option('filename') == 'true':
            my.show_filename_flag = True
        if my.get_option('file_type') == 'true':
            my.show_file_type = True
        if my.get_option('original') == 'true':
            my.show_orig_icon = True
        if my.get_option('versionless') == 'true':
            my.show_versionless = True

        if my.get_option('latest_icon') == 'true':
            my.show_latest_icon = True
        context = my.get_option('icon_context')

        if not context and my.sobjects:
            sobject = my.sobjects[0]
            assert(sobject)
            if sobject:     # protect agains it being None
                context = sobject.get_icon_context(my.context)


        if context:
            my.context = context
        
        if not my.image_link_order:
            order = my.get_option('image_link_order')
            if order:
                order = order.split('|')
            my.set_image_link_order(order)
        
        # preselect all of the snapshots (don't do this for redirect right now)
        redirect = my.get_option("redirect")
        redirect_expr = my.get_option("redirect_expr")

        if not redirect and not redirect_expr and my.sobjects:
            if not my.sobjects[0]:
                # retired
                return

            snapshots = []
            # if it is snapshot, there is no need to search for it again
            # and we dont' try to to look for publish context icons for it to save time
            if isinstance(my.sobjects[0], Snapshot):
                
                snapshots = my.sobjects
            else:
                if my.show_latest_icon:
                    icon_context = None
                else:
                    icon_context = my.sobjects[0].get_icon_context(my.context)
                try:
                    if my.version == None:
                        my.data = Snapshot.get_by_sobjects(my.sobjects, icon_context, is_latest=True, return_dict=True)
                        # verify if we get icon for all
                        if len(my.data) < len(my.sobjects):
                            publish_data =  Snapshot.get_by_sobjects(my.sobjects, my.DEFAULT_CONTEXT, is_latest=True, return_dict=True)
                            my._update_data(publish_data)

                        # verify if we get icon for all
                        if len(my.data) < len(my.sobjects):
                            publish_data =  Snapshot.get_by_sobjects(my.sobjects, process=my.DEFAULT_PROCESS, is_latest=True, return_dict=True)
                            my._update_data(publish_data)


                        # verify if we get icon for all
                        if len(my.data) < len(my.sobjects):
                            publish_data =  Snapshot.get_by_sobjects(my.sobjects, is_latest=True, return_dict=True)
                            my._update_data(publish_data)





                    else:
                        my.data = Snapshot.get_by_sobjects(my.sobjects, icon_context, version=my.version, return_dict=True)

                        # verify if we get icon for all
                        if len(my.data) < len(my.sobjects):
                            publish_data =  Snapshot.get_by_sobjects(my.sobjects, my.DEFAULT_CONTEXT, version=my.version, return_dict=True)
                            my._update_data(publish_data)

                        # verify if we get icon for all
                        if len(my.data) < len(my.sobjects):
                            publish_data =  Snapshot.get_by_sobjects(my.sobjects, process=my.DEFAULT_PROCESS, version=my.version, return_dict=True)
                            my._update_data(publish_data)

                        # verify if we get icon for all
                        if len(my.data) < len(my.sobjects):
                            publish_data =  Snapshot.get_by_sobjects(my.sobjects, version=my.version, return_dict=True)
                            my._update_data(publish_data)




 

                except SqlException, e:
                    my.SQL_ERROR = True 
                    DbContainer.abort_thread_sql()
                    return


                snapshots = my.data.values()

                


            # get all of the file objects
            file_objects = File.get_by_snapshots(snapshots)
            for file_object in file_objects:
                file_code = file_object.get_code()
                my.file_objects[file_code] = file_object



    def _update_data(my, publish_data):
        '''update my.data with 2nd choice publish context data to display an icon'''
        publish_data.update(my.data)
        my.data = publish_data


    def get_title(my):
        return super(ThumbWdg,my).get_title();

    #def is_editable(my):
    #    sobject = my.get_current_sobject()
    #    if sobject and sobject.get_id() == -1:
    #        return False
    #    else:
    #        return True
    def is_editable(my):
        return False



    def get_info(my):
        # FIXME: temporary fix to make flash_swf_view_wdg.py work
        return my.info


    def handle_th(my, th, cell_idx):
        if not my.width:
            th.add_style("width", "30px")
        else:
            th.add_style("width: %s" % my.width)


    def handle_td(my, td):
        td.set_attr('spt_input_type', 'upload')
        td.set_style("width: 1px")


    def set_icon_size(my, size):
        my.icon_size = str(size)
    

    def get_icon_size(my):
        ICON_SIZE = 120
        if not my.icon_size:
            my.icon_size = 120

        if type(my.icon_size) in types.StringTypes and my.icon_size.endswith("%"):
            return my.icon_size

        icon_size = int(my.icon_size)

        icon_mult = PrefSetting.get_value_by_key("thumb_multiplier")
        if not icon_mult:
            icon_mult = 1
        else:
            icon_mult = float(icon_mult)

        if not icon_size:
            size = int(ICON_SIZE * icon_mult)
        else:
            size = int(icon_size * icon_mult)

        # cap the size to 15
        if size < 15:
            size = 15

        return size

    def set_aspect(my, aspect):
        my.aspect = aspect

    def set_show_filename(my, flag):
        my.show_filename_flag = flag

    def set_show_clipboard(my, flag):
        my.show_clipboard_flag = flag

    def set_show_orig_icon(my, flag):
        my.show_orig_icon = flag

    def set_show_latest_icon(my, flag):
        my.show_latest_icon = flag

    def set_show_file_type(my, flag):
        my.show_file_type = flag

    def set_has_img_link(my, show):
        my.has_img_link = show

    def set_icon_type(my, icon_type):
        my.icon_type = icon_type


    def set_image_link_order(my, order):
        if order:
            my.image_link_order = order

    def set_context(my, context):
        ''' if set externally, the sobject's icon_context will be ignored '''
        my.context = context

    def set_version(my, version):
        my.version = version


    def get_no_icon_wdg(my, missing=False):
        sobject = my.get_current_sobject()
        if not sobject:
            return ''

        div = my.top
        div.add_style("position: relative")

        div.set_id( "thumb_%s" %  sobject.get_search_key() )
        icon_size = my.get_icon_size()

        if icon_size:
            div.add_style("%s: %s" % (my.aspect, icon_size) )

        if missing:
            img = HtmlElement.img(ThumbWdg.get_missing_image())
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
        if my.SQL_ERROR:
            warning_div = DivWdg('<i>-- preprocess error --</i>')
            warning_div.add_styles('position: absolute; z-index: 100; float: left; top: 0; left: 0; font-size: smaller;')
            div.add_style('position: relative')
            div.add(warning_div)

        search_key = SearchKey.get_by_sobject(sobject)
        code = sobject.get_code()
       
        
        detail = my.get_option("detail")
        if detail != 'false':
            my.add_icon_behavior(div, sobject)

        if type(icon_size) == types.StringType and icon_size.endswith("%"):
            img.add_style("%s: 100%%" % my.aspect )
        else:
            img.add_style("%s: %spx" % (my.aspect, my.get_icon_size()) )
        img.add_style("min-%s: 15px" % my.aspect)

        return div


    def is_simple_viewable(my):
        return False

    def add_style(my, name, value=None):
        my.top.add_style(name, value)


    def get_display(my):

        my.aspect = my.get_option('aspect')
        if not my.aspect:
            my.aspect = "width"

        search_key = my.get_option('search_key')
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            my.set_sobject(sobject)

        if not my.is_preprocess_run:
            my.preprocess()

 
  
        # get the set size
        icon_size = my.get_option("icon_size")
        if icon_size:
            my.set_icon_size(icon_size)
        # get the real size
        icon_size = my.get_icon_size()


        min_size = my.get_option("min_icon_size")
        if not min_size:
            min_size = 45 


        sobject = my.get_current_sobject()
        # get it from the web container
        if not sobject:
            web = WebContainer.get_web()
            search_type = web.get_form_value("search_type")
            search_code = web.get_form_value("search_code")
            search_id = web.get_form_value("search_id")
            icon_size = web.get_form_value("icon_size")
            if icon_size:
                my.icon_size = icon_size
            if search_type and search_code:
                sobject = Search.get_by_code(search_type, search_code)
                my.set_sobject(sobject)
            elif search_type and search_id:
                sobject = Search.get_by_id(search_type, search_id)
                my.set_sobject(sobject)
            else:
                return my.get_no_icon_wdg()
        elif sobject.get_id() == -1:
            div = DivWdg()
            div.add("&nbsp;")
            div.add_style("text-align: center")
            return div



        # if there is a redirect to the sobject (a relation), use that
        redirect = my.get_option("redirect")
        redirect_expr = my.get_option("redirect_expr")
        parser = ExpressionParser()
        
        if redirect and sobject:
            if redirect == "true":
                # use search_type and search_id pair
                # FIXME: go up a maximum of 2 .. this is not so stable as
                # the parent may have a similar relationship
                for i in range(0,2):
                    if not sobject:
                        return my.get_no_icon_wdg()

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
                    return my.get_no_icon_wdg()

        elif redirect_expr and sobject:
            redirect_sobject = parser.eval(redirect_expr, sobjects=[sobject], single=True)
            if redirect_sobject:
                sobject = redirect_sobject
            else:
                return my.get_no_icon_wdg()

        # get the icon context from the sobject
        icon_context = my.get_option("icon_context")
        if not icon_context:
            icon_context = sobject.get_icon_context(my.context)

        # try to get an icon first
        if isinstance(sobject, Snapshot):
            snapshot = sobject
            # check if the sobject actually exists
            try:
                snapshot.get_sobject()
            except SObjectNotFoundException, e:
                return IconWdg('sobject n/a for snapshot code[%s]' %snapshot.get_code(), icon=IconWdg.ERROR)
            except SearchException, e:
                return IconWdg('parent for snapshot [%s] not found' %snapshot.get_code(), icon=IconWdg.ERROR)
       
        else:
            # this is to limit unnecessary queries
            snapshot = None
            if my.data:
                search_key = SearchKey.get_by_sobject(sobject, use_id=False)
                snapshot = my.data.get(search_key)
            elif my.is_ajax(check_name=False) or redirect or redirect_expr:
                if my.show_latest_icon:
                    icon_context = None
                    
                snapshot = Snapshot.get_latest_by_sobject(sobject, icon_context, show_retired=False)

                # get the latest icon period
                if not snapshot and icon_context == 'icon':
                    snapshot = Snapshot.get_latest_by_sobject(sobject, show_retired=False)


        if not snapshot:
            icon = my.get_no_icon_wdg()
            return icon


        xml = snapshot.get_xml_value("snapshot")
        
        # data structure to store my.info
        my.info = {}
        # get the file objects if they have not already been cached
        if not my.file_objects:
            file_objects = {}
            snapshot_file_objects = File.get_by_snapshot(snapshot)
            
            for file_object in snapshot_file_objects:
                file_objects[file_object.get_code()] = file_object
        else:
            file_objects = my.file_objects

        # go through the nodes and try to find appropriate paths
        my.info = ThumbWdg.get_file_info(xml, file_objects, sobject, snapshot, my.show_versionless) 
        # find the link that will be used when clicking on the icon
        link_path = ThumbWdg.get_link_path(my.info, image_link_order=my.image_link_order)

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
            my.info = ThumbWdg.get_file_info(xml, file_objects, sobject, snapshot, my.show_versionless) 
            link_path = ThumbWdg.get_link_path(my.info, image_link_order=my.image_link_order)
          
        # define a div
        div = my.top

        div.force_default_context_menu()
 
      
        # if no link path is found, display the no icon image
        if link_path == None:
            return my.get_no_icon_wdg()


        repo_path = ThumbWdg.get_link_path(my.info['_repo'], image_link_order=my.image_link_order)
        #if repo_path and repo_path.startswith("//"):
        if False:
            # PERFORCE
            # FIXME: need a better check the this.  This is test code
            # for viewing perforce images when running perforce web server
            version = snapshot.get_value("version")
            link_path = "http://localhost:8080%s&rev=%s" % (link_path, version)

        elif not repo_path or not os.path.exists(repo_path):
            return my.get_no_icon_wdg(missing=True)

        if my.icon_type == 'default':
            # fix template icon_size=100% icon_type which always loads web version
            if type(icon_size) == types.StringType and icon_size.endswith("%"):
               icon_size_check = int(icon_size[0:-1])
            else:
               icon_size_check = icon_size
	
            if icon_size_check > 120:    
                icon_type = 'web'
            else:
                icon_type = 'icon'
        else:
            icon_type = my.icon_type

        icon_info = my.get_icon_info(link_path, repo_path=repo_path, icon_type=icon_type)
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
        div.add_style("%s: %s" % (my.aspect, icon_size) )
        div.add_style("min-%s: %s" % (my.aspect, min_size) )
        div.set_box_shadow("0px 0px 5px")
        div.add_border()

        div.add_style("text-align: left" )

        if icon_missing:
            missing_div = DivWdg()
            div.add(missing_div)
            missing_icon = IconWdg("Missing files", IconWdg.ERROR, width='12px')
            missing_div.add(missing_icon)

            missing_div.add_style("margin-top: 0px")
            missing_div.add_style("position: absolute")



        img = HtmlElement.img(icon_link)
        img.add_class("spt_image")

        # TODO: make this a preference
        img.add_style("background: #ccc")

        if type(icon_size) == types.StringType and icon_size.endswith("%"):
	    img.add_style("%s: 100%%" % my.aspect)
        else:
	    img.add_style("%s: %spx" % (my.aspect, icon_size) )


        detail = my.get_option("detail")
        protocol = my.get_option("protocol")
        if not protocol:
            from pyasm.prod.biz import ProdSetting
            protocol = ProdSetting.get_value_by_key('thumbnail_protocol')

        if detail == "false":
            if my.has_img_link:

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
                        #href.set_attr("target", "_blank" )
                        href.add_class("spt_thumb_href")
                        href.add_attr("spt_href", link_path)



                    
                div.add(href)

            else:
                div.add(img)
        else:
            div.add(img)
            div.add_class("hand")

            my.add_icon_behavior(div, sobject)


        
        # add an optional source/original file icon
        if my.show_orig_icon:
            # make sure main is first
            link_order = ['main', 'web'] 
            link_path = ThumbWdg.get_link_path(my.info, link_order)
            img = IconWdg("source file", icon= IconWdg.IMAGE)
            
            href = HtmlElement.href(img, link_path)
            href.add_style('float: left')
            href.set_attr("spt_href", link_path)
            href.add_class("spt_thumb_href")
            
            div.add(HtmlElement.br(clear="all"))
            div.add(href)

        # add an optional text link
        if my.show_filename_flag:
            text_link = ThumbWdg.get_link_path(my.info, my.image_link_order)
            my.set_text_link(div, div, text_link)

        if my.show_file_type:
            links_list = ThumbWdg.get_file_info_list(xml, file_objects, sobject, snapshot, my.show_versionless)
            my.set_type_link(div, links_list) 
             
        return div



    def add_icon_behavior(my, widget, sobject):
        search_key = SearchKey.get_by_sobject(sobject)
        code = sobject.get_code()

        widget.add_attr("spt_search_key", search_key)
        widget.add_attr("spt_code", code)

        script_path = my.options.get("script_path")
        class_name = my.options.get("detail_class_name")

        if script_path:
            widget.add_class("spt_thumb_script_path")
        else:
            widget.add_class("spt_thumb_detail_class_name")


        return

        """
        if script_path:
            widget.add_behavior( {
            'type': 'click_up',
            'script_path': script_path,
            'cbjs_action': '''
            var script = spt.CustomProject.get_script_by_path(bvr.script_path);
            spt.CustomProject.exec_script(script);
            '''
            } )

        else:
            widget.add_behavior( {
            'type': 'click_up',
            'class_name': class_name,
            'search_key': search_key,
            'code': code,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = bvr.class_name;
            if ( ! class_name )
                class_name = 'tactic.ui.tools.SObjectDetailWdg';

            var kwargs = {
                search_key: bvr.search_key
            };
            var element_name = "detail_"+bvr.code;
            var title = "Detail ["+bvr.code+"]";
            spt.tab.add_new(element_name, title, class_name, kwargs);
            '''
            } )
        """






    
    def set_type_link(my, widget, link_path_list):
        ''' set the format of the file type links '''
        type_div = DivWdg()
        for type, link_path in link_path_list:
            href = HtmlElement.href(type, link_path)
            href.add_color('color','color')
            href.set_attr("target", "_blank")
            href.add_tip('Right-click and choose [Save Link As..] to save to disk') 
            type_div.add(SpanWdg(href, 'small'))

        widget.add(type_div)
    
    def set_text_link(my, widget, div, link_path):
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
        if not my.show_orig_icon:
            div.add(HtmlElement.br(2))
        widget.add(href)




    def get_link_path( info, image_link_order=None):
        ''' get the link for the thumbnail '''
        image_link = None

        #default_image_link_order = ['web', 'main', '.swf', 'maya', 'anim', 'houdini', \
        default_image_link_order = ['web', 'main', '.swf']
        
        if image_link_order:
            default_image_link_order = image_link_order


        for item in default_image_link_order:
            if info.has_key(item):
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


    def get_icon_info(my, image_link, repo_path=None, icon_type='icon'):
        ''' if no icon is specified then get the icon based on the main file,
        otherwise use the specified icon '''

        icon_info = {}

        icon_size = my.get_icon_size()
        icon_link = None
        if my.info.has_key(icon_type):
            icon_link = my.info[icon_type]

            if not os.path.exists(repo_path):
                icon_link = ThumbWdg.get_no_image()
                icon_info['icon_missing'] = True

            # HACK for pdf icons
            if image_link.endswith(".pdf"):
                if icon_size.endswith("%"):
                    icon_size = float(icon_size[0:-1])
                    icon_size = int( 80.0 / 120.0 * float(icon_size) )
                    icon_size = '%s%%' %icon_size
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
            icon = "gnome-application-vnd.ms-excel.png"
        elif ext in ["ppt", "pptx"]:
            icon = "gnome-application-vnd.ms-excel.png"
        elif ext == "mp3" or ext == "wav":
            icon = "mp3_and_wav.jpg"
        elif ext == "aif" or ext == 'aiff':
            icon = "gnome-audio-x-aiff.png"
        elif ext == "mpg":
            icon = "gnome-video-mpeg.png"
        elif ext in ["mov"]:
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
        elif ext in ["obj", "mtl"]:
            icon = "3d_obj.png"
        elif ext == "rdc":
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
        elif ext in File.VIDEO_EXT:
            #icon = "general_video.png"
            icon = "indicator_snake.gif"
        elif ext in File.IMAGE_EXT:
            icon = "indicator_snake.gif"
        else:
            icon = "default_doc.png"

        if base:
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




    def get_file_info(xml, file_objects, sobject, snapshot, show_versionless=False, is_list=False):
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

            if isinstance(info, dict):
                info[type] = path
                lib_dir = sobject.get_lib_dir(snapshot, file_object=file_object)
                repo_info[type] = "%s/%s" % (lib_dir, file_name)
            else:
                info.append((type, path))

        return info

    get_file_info = staticmethod(get_file_info)

    def get_refresh_script(sobject, icon_size=None, show_progress=True):
        print "DEPRECATED: Snapshot.get_refresh_script!"

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



class ThumbCmd(Command):

    def get_path(my):
        return my.path

    def execute(my):

        search_keys  = my.kwargs.get("search_keys")

        for search_key in search_keys:
            my.generate_icon(search_key)


        my.info = {
            'search_keys': search_keys
        }
        my.add_description('Generate Thumbnail with ThumbCmd')

    def generate_icon(my, search_key):

        sobject = Search.get_by_search_key(search_key)
        search_code = sobject.get_code()
        search_type = sobject.get_search_type()
        base_search_type = sobject.get_base_search_type()


        if base_search_type == 'sthpw/snapshot':
            snapshot_code = sobject.get_code()

            file_type = "main"
            path = sobject.get_lib_path_by_type(file_type)

            #To check if it is a sequence checkin
            all_snapshots=sobject.get_all_file_objects()
            for single_snapshot in all_snapshots:
                if single_snapshot.get('base_type') == 'sequence':
                    return

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

            icon_creator = IconCreator(path)
            icon_creator.execute()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()
            if web_path and icon_path:
                sub_file_paths = [path, web_path, icon_path]
                sub_file_types = [path, 'web', 'icon']

                from pyasm.checkin import FileCheckin
                checkin = FileCheckin(sobject, sub_file_paths, sub_file_types, context='icon', mode="copy")
                checkin.execute()
                snapshot = checkin.get_snapshot()

            # need the actual sobject to get the path to replace the icon
            # in the ui
            #snapshot = Search.get_by_search_key(snapshot.get("__search_key__"))


        my.path = snapshot.get_web_path_by_type("icon")







class FileInfoWdg(BaseTableElementWdg):

    def get_title(my):
        return "File Info"


    def get_display(my):
        sobject = my.get_current_sobject()

        if my.name == None:
            my.name = "snapshot"

        xml = sobject.get_xml_value(my.name)

        images = xml.get_values("snapshot/file/@name")
        if len(images) != 3:
            return "No images"
        file_codes = xml.get_values("snapshot/file/@file_code")

        html = Html()
        for i in range(0, len(images)):
            html.writeln("%0.10d : %s<br/>" % (int(file_codes[i]), images[i]) )

        return html.getvalue()

