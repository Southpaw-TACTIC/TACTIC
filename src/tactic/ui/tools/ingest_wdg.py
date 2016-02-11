###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

from pyasm.common import Environment, jsonloads, jsondumps, TacticException
from pyasm.web import DivWdg, Table
from pyasm.widget import IconWdg, TextWdg, SelectWdg, CheckboxWdg, RadioWdg, TextAreaWdg, HiddenWdg
from pyasm.command import Command
from pyasm.search import SearchType, Search
from pyasm.biz import File, Project, FileGroup
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import DialogWdg
from tactic.ui.widget import IconButtonWdg

from tactic.ui.input import UploadButtonWdg, TextInputWdg
from tactic.ui.widget import ActionButtonWdg

from tactic_client_lib import TacticServerStub

import os
import os.path
import re
__all__ = ['IngestUploadWdg', 'IngestUploadCmd']


class IngestUploadWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'search_type': 'Search Type to ingest into',
        'parent_key': 'Parent search key to relate create sobject to',
        'process': 'The default process to ingest into',
        'context': 'Fixed context to ingest into',
        'ingest_data_view': 'Specify a ingest data view, defaults to edit',
        'extra_data': 'Extra data (JSON) to be added to created sobjects',
        'oncomplete_script_path': 'Script to be run on a finished ingest',
        'update_mode': 'Takes values "true" or "false".  When true, uploaded files will update existing file iff exactly one file exists already with the same name.',
        'context_mode': 'Set or remove context case sensitivity.',
        'hidden_options': 'Comma separated list of hidden settings i.e. "process,context_mode"'
    }


    def get_display(my):

        top = my.top
        top.add_class("spt_ingest_top")

        table = Table()
        top.add(table)
        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")

        middle = table.add_cell()
        middle.add_style("height: 10") # not sure why we need this height
        middle.add_style("padding: 30px 20px")
        line = DivWdg()
        middle.add(line)
        line.add_style("height: 100%")
        line.add_style("border-style: solid")
        line.add_style("border-width: 0px 0px 0px 1px")
        line.add_style("border-color: #DDD")
        line.add(" ")

        left.add( my.get_content_wdg() )


        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add( my.get_settings_wdg() )

        show_settings = my.kwargs.get("show_settings")
        if show_settings in [False, 'false']:
            right.add_style("display: none")

        return top



    def get_settings_wdg(my):

        div = DivWdg()
        div.add_style("width: 400px")
        div.add_style("padding: 20px")
        
        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Ingest Settings")
        title_wdg.add_style("font-size: 25px")

        div.add("<hr/>")

        # Build list of process names
        process_names = set()
        from pyasm.biz import Pipeline
        from pyasm.widget import SelectWdg
        search_type_obj = SearchType.get(my.search_type)
        base_type = search_type_obj.get_base_key()

        pipeline_search = Search("sthpw/pipeline")
        pipeline_search.add_filter("search_type", base_type)
        pipelines = pipeline_search.get_sobjects()
        for pipeline in pipelines:
            process_names.update(pipeline.get_process_names())
  
        selected_process = my.kwargs.get("process")
        if selected_process:
            process_names.add(selected_process) 
        
        if process_names:
            process_names = list(process_names)
            process_names.sort()
        else:
            process_names = []

        process_names.append("---")
        process_names.append("publish")
        process_names.append("icon")


        hidden_options = my.kwargs.get("hidden_options").split(',')

        if "process" not in hidden_options:
            title_wdg = DivWdg()
            div.add(title_wdg)
            title_wdg.add("Process")
            title_wdg.add_style("margin-top: 20px")
            title_wdg.add_style("font-size: 16px")

            div.add("<br/>")

            select = SelectWdg("process")
            div.add(select)
            process_names.append("---")
            process_names.append("publish")
            process_names.append("icon")
            select.set_option("values", process_names)
            select.add_empty_option("- Select Ingest Process -")
            if selected_process:
                select.set_option("default", selected_process)

            div.add("<br/>")
            div.add("<hr/>")

        # Metadata
        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Metadata")
        title_wdg.add_style("margin-top: 20px")
        title_wdg.add_style("font-size: 16px")

        desc_wdg = DivWdg("This extra metaadata will be added to each new item")
        div.add(desc_wdg)

        from tactic.ui.panel import EditWdg

        ingest_data_view = my.kwargs.get('ingest_data_view')

        sobject = SearchType.create(my.search_type)
        edit = EditWdg(
                search_key=sobject.get_search_key(),
                mode='view',
                view=ingest_data_view,
                show_header=False,
                width="auto",
        )
        
        div.add(edit)
        hidden = HiddenWdg(name="parent_key")
        div.add(hidden)
        hidden.add_class("spt_parent_key")
        parent_key = my.kwargs.get("parent_key") or ""
        if parent_key:
            hidden.set_value(parent_key)





        div.add("<br/>")
        div.add("<hr/>")


        # options


        # update mode
        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Mapping Files to Items")
        title_wdg.add_style("margin-top: 20px")
        title_wdg.add_style("font-size: 16px")
        desc_wdg = DivWdg("Determines how the file name matches up to a particular entry")

        #desc_wdg = DivWdg("When update mode is 'Update', if a file shares the name of one other file in the asset library, the file will update on ingest. If more than one file shares the name of an ingested asset, a new asset is created.  If sequence mode is selected, the system will update the sobject on ingest if a file sequence sharing the same name already exists.")
        div.add(desc_wdg)

        div.add("<br/>")


        update_mode_option = my.kwargs.get("update_mode")
        if not update_mode_option:
            update_mode_option = "true"
        update_mode = SelectWdg(name="update mode")
        update_mode.add_class("spt_update_mode_select")
        update_mode.set_option("values", ["false", "true", "sequence"])
        update_mode.set_option("labels", ["Always insert a new item", "Update duplicate items", "Update as a sequence"])
        update_mode.set_option("default", update_mode_option)
        update_mode.add_style("margin-top: -3px")
        update_mode.add_style("margin-right: 5px")
        div.add(update_mode)


        label_div = DivWdg()
        label_div.add("Ignore File Extension")
        div.add(label_div)
        label_div.add_style("margin-top: 10px")
        label_div.add_style("margin-bottom: 5px")

        ignore_ext_option = my.kwargs.get("ignore_ext")
        if not ignore_ext_option:
            ignore_ext_option = "false"
        ignore_ext = SelectWdg(name="update mode")
        ignore_ext.add_class("spt_ignore_ext_select")
        ignore_ext.set_option("values", ["true", "false"])
        ignore_ext.set_option("labels", ["Yes", "No"])
        ignore_ext.set_option("default", ignore_ext_option)
        ignore_ext.add_style("margin-top: -3px")
        ignore_ext.add_style("margin-right: 5px")
        div.add(ignore_ext)



        label_div = DivWdg()
        label_div.add("Map file name to column:")
        div.add(label_div)
        label_div.add_style("margin-top: 10px")
        label_div.add_style("margin-bottom: 5px")

        column_option = my.kwargs.get("column")
        if not column_option:
            column_option = "name"
        column_select = SelectWdg(name="update mode")
        column_select.add_class("spt_column_select")
        column_select.set_option("values", ["name", "code"])
        column_select.set_option("labels", ["Name", "Code"])
        column_select.set_option("default", column_option)
        column_select.add_style("margin-top: -3px")
        column_select.add_style("margin-right: 5px")
        div.add(column_select)



        if "context_mode" not in hidden_options:
            div.add("<br/>")
            div.add("<hr/>")

            title_wdg = DivWdg()
            div.add(title_wdg)
            title_wdg.add("Context Mode")
            title_wdg.add_style("font-size: 16px")

            div.add("<br/>")

            context_mode_option = my.kwargs.get("context_mode")
            if not context_mode_option:
                context_mode_option = "case_insensitive"
            context_mode = SelectWdg(name="context_mode")
            context_mode.add_class("spt_context_mode_select")
            context_mode.set_option("values", "case_insensitive|case_sensitive")
            context_mode.set_option("labels", "Case Insensitive|Case Sensitive")
            context_mode.set_option("default", context_mode_option)
            context_mode.add_style("margin-top: -3px")
            context_mode.add_style("margin-right: 5px")
            div.add(context_mode)
                


        extra_data = my.kwargs.get("extra_data")
        if not isinstance(extra_data, basestring):
            extra_data = jsondumps(extra_data)

        if extra_data and extra_data != "null":
            # it needs a TextArea instead of Hidden because of JSON data
            text = TextAreaWdg(name="extra_data")
            text.add_style('display: none')
            text.set_value(extra_data)
            div.add(text)



        return div





    def get_content_wdg(my):

        relative_dir = my.kwargs.get("relative_dir")
        my.relative_dir = relative_dir

        div = DivWdg()
        div.add_style("width: auto")
        div.add_style("min-width: 600px")
        div.add_style("padding: 20px")
        div.add_color("background", "background")

        header_div = DivWdg()
        div.add(header_div)
       
        title_wdg = DivWdg()
        header_div.add(title_wdg)
        title_wdg.add("<span style='font-size: 25px'>Ingest Files</span>")
        title_wdg.add("<br/>")
        title_wdg.add("Drag files into the box or click 'Add Files'")
        title_wdg.add_style("display", "inline-block")

        # create the help button
        help_button_wdg = DivWdg()
        header_div.add(help_button_wdg)
        help_button_wdg.add_styles("float: right; margin-top: 11px;")
        help_button = ActionButtonWdg(title="?", tip="Ingestion Widget Help", size='s')
        help_button_wdg.add(help_button)

        help_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''spt.help.load_alias("ingestion_widget")'''
        } )

        div.add("<hr style='margin-right: 4px'/>")

        shelf_div = DivWdg()
        div.add(shelf_div)
        shelf_div.add_style("margin-bottom: 10px")

        my.search_key = my.kwargs.get("search_key")
        if my.search_key:
            my.sobject = Search.get_by_search_key(my.search_key)
            my.search_type = my.sobject.get_search_type()
        else: 
            my.search_type = my.kwargs.get("search_type")
            my.sobject = None
            my.search_key = None

        if my.search_key:
            div.add("<input class='spt_input' type='hidden' name='search_key' value='%s'/>" % my.search_key)
        else:
            div.add("<input class='spt_input' type='hidden' name='search_key' value=''/>")


        if not my.search_type:
            div.add("No search type specfied")
            return div

        if relative_dir:
            folder_div = DivWdg()
            shelf_div.add(folder_div)
            folder_div.add("Folder: %s" % relative_dir)
            folder_div.add_style("opacity: 0.5")
            folder_div.add_style("font-style: italic")
            folder_div.add_style("margin-bottom: 10px")


        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        shelf_div.add(upload)

        button = ActionButtonWdg(title="Clear")
        button.add_style("float: right")
        button.add_style("margin-top: -3px")
        shelf_div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingest_top");
            var file_els = top.getElements(".spt_upload_file");
            for ( var i = 0; i < file_els.length; i++) {
                spt.behavior.destroy( file_els[i] );
            };

            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "");

            var button = top.getElement(".spt_upload_file_button");
            button.setStyle("display", "none");
         '''
         } )

        button = ActionButtonWdg(title="Add Files")
        button.add_style("float: right")
        button.add_style("margin-top: -3px")
        shelf_div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'normal_ext': File.NORMAL_EXT,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');
        
            //clear upload progress
            var upload_bar = top.getElement('.spt_upload_progress');
            if (upload_bar) {
                upload_bar.setStyle('width','0%');
                upload_bar.innerHTML = '';
            }
            var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                var delay = 0; 
                for (var i = 0; i < files.length; i++) {
                    var size = files[i].size;
                    var file_name = files[i].name;
                    var is_normal = regex.test(file_name);
                    if (size >= 10*1024*1024 || is_normal) {
                        spt.drag.show_file(files[i], files_el, 0, false);
                    }
                    else {
                        spt.drag.show_file(files[i], files_el, delay, true);

                        if (size < 100*1024)       delay += 50;
                        else if (size < 1024*1024) delay += 500;
                        else if (size < 10*1024*1024) delay += 1000;
                    }
                }
            }

            spt.html5upload.clear();
            spt.html5upload.set_form( top );
            spt.html5upload.select_file( onchange );

         '''
         } )



        upload_div = DivWdg()
        shelf_div.add(upload_div)
        upload_div.add_class("spt_upload_file_button")
        button = ActionButtonWdg(title="Ingest Files", width=200, color="primary")
        upload_div.add(button)
        upload_div.add_style("display: none")

        shelf_div.add("<br clear='all'/>")

        border_color_light = div.get_color("background2", 8)
        border_color_dark = div.get_color("background2", -15)
        background_mouseout = div.get_color("background", 10)
        background_mouseenter = div.get_color("background", 8)


        files_div = DivWdg()
        files_div.add_style("position: relative")
        files_div.add_class("spt_to_ingest_files")
        div.add(files_div)
        files_div.add_style("max-height: 400px")
        files_div.add_style("height: 400px")
        files_div.add_style("overflow-y: auto")
        files_div.add_style("padding: 3px")
        files_div.add_color("background", background_mouseout)
        files_div.add_style("border: 3px dashed %s" % border_color_light)
        #files_div.add_style("border-radius: 20px 20px 20px 20px")
        files_div.add_style("z-index: 1")
        files_div.add_style("width", "586px")
        #files_div.add_style("display: none")

        bgcolor = div.get_color("background")
        bgcolor2 = div.get_color("background", -3)

        #style_text = "text-align: center; margin-top: 100px; color: #A0A0A0; font-size: 3.0em; z-index: 10;"

        background = DivWdg()
        background.add_class("spt_files_background")
        files_div.add(background)

        background.add_style("text-align: center")
        background.add_style("margin-top: 75px")
        background.add_style("font-size: 3.0em")
        background.add_style("z-index: 10")
        background.add_color("color", "color", 70)


        icon = "<i class='fa fa-cloud-upload' style='font-size: 150px'> </i>"
        background.add(icon)


        background_text = DivWdg("<p>Drag Files Here</p>")

        background.add(background_text)

        files_div.add_behavior( {
            'type': 'mouseover',
            'cbjs_action': '''
            bvr.src_el.setStyle("border","3px dashed %s")
            bvr.src_el.setStyle("background","%s")
            ''' % (border_color_dark, background_mouseenter)
        } )

        files_div.add_behavior( {
            'type': 'mouseout',
            'cbjs_action': '''
            bvr.src_el.setStyle("border", "3px dashed %s")
            bvr.src_el.setStyle("background","%s")
            ''' % (border_color_light, background_mouseout)
        } ) 


        background.add( my.get_select_files_button() )






        # Test drag and drop files
        files_div.add_attr("ondragenter", "return false")
        files_div.add_attr("ondragover", "return false")
        files_div.add_attr("ondrop", "spt.drag.noop(event, this)")
        files_div.add_behavior( {
        'type': 'load',
        'normal_ext': File.NORMAL_EXT,
        'cbjs_action': '''
        spt.drag = {}
        var background;

        spt.drag.show_file = function(file, top, delay, icon) {

            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "none");


            var template = top.getElement(".spt_upload_file_template");
            var clone = spt.behavior.clone(template);

            clone.removeClass("spt_upload_file_template");
            clone.addClass("spt_upload_file");
            clone.setStyle("display", "");

            if (typeof(delay) == 'undefined') {
                delay = 0;
            }

            // remember the file handle
            clone.file = file;

            var name = file.name;
            var size = parseInt(file.size / 1024 * 10) / 10;

            var thumb_el = clone.getElement(".spt_thumb");
            var date_label_el = clone.getElement(".spt_date_label");
            var date_el = clone.getElement(".spt_date");

            //var loadingImage = loadImage(
            setTimeout( function() {
                var draw_empty_icon = function() {
                        var img = $(document.createElement("div"));
                        img.setStyle("width", "58");
                        img.setStyle("height", "34");
                        //img.innerHTML = "MP4";
                        img.setStyle("border", "1px dotted #222")
                        thumb_el.appendChild(img);
                    };
                if (icon) {
                        var loadingImage = loadImage(
                            file,
                            function (img) {
                            if (img.width)
                                thumb_el.appendChild(img);
                            else
                                draw_empty_icon();
                                
                            },
                            {maxWidth: 80, maxHeight: 60, canvas: true, contain: true}
                        );
                        
                }
                else {
                    draw_empty_icon();
                }


                loadImage.parseMetaData(
                    file,
                    function(data) {
                        if (data.exif) {
                            var date = data.exif.get('DateTimeOriginal');
                            if (date) {
                                date_label_el.innerHTML = date;
                                if (date_el) {
                                    date_el.value = date;
                                }
                            }
                        }

                    }
                );

            }, delay );

            /*
            var reader = new FileReader();
            reader.thumb_el = thumb_el;
            reader.onload = function(e) {
                this.thumb_el.innerHTML = [
                    '<img class="thumb" src="',
                    e.target.result,
                    '" title="', escape(name),
                    '" width="60px"',
                    '" padding="5px"',
                    '"/>'
                ].join('');
            }
            reader.readAsDataURL(file);
            */
         
            clone.getElement(".spt_name").innerHTML = file.name;
            clone.getElement(".spt_size").innerHTML = size + " KB";
            clone.inject(top);
        }

        spt.drag.noop = function(evt, el) {
            var top = $(el).getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            evt.stopPropagation();
            evt.preventDefault();
            evt.dataTransfer.dropEffect = 'copy';
            var files = evt.dataTransfer.files;

            var delay = 0;
            var skip = false;
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');
            for (var i = 0; i < files.length; i++) {
                var size = files[i].size;
                var file_name = files[i].name;
                var is_normal = regex.test(file_name);
                if (size >= 10*1024*1024 || is_normal) {
                    spt.drag.show_file(files[i], files_el, 0, false);
                }
                else {
                    spt.drag.show_file(files[i], files_el, delay, true);

                    if (size < 100*1024)       delay += 50;
                    else if (size < 1024*1024) delay += 500;
                    else if (size < 10*1024*1024) delay += 1000;
                }

            }
        }
        '''
        } )

        # create a template that will be filled in for each file
        files_div.add_relay_behavior( {
            'type': 'mouseenter',
            'color': files_div.get_color("background3", -5),
            'bvr_match_class': 'spt_upload_file',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.color);
            '''
        } )
        files_div.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_upload_file',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )
        files_div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_remove',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingest_top");

            var el = bvr.src_el.getParent(".spt_upload_file");
            spt.behavior.destroy_element(el);

            var els = top.getElements(".spt_upload_file");

            if (els.length == 0) {
                var background = top.getElement(".spt_files_background");
                background.setStyle("display", "");
            }

            '''
        } )


        """
        metadata_view = "test/wizard/metadata"
        files_div.add_relay_behavior( {
            'type': 'mouseup',
            'view': metadata_view,
            'bvr_match_class': 'spt_upload_file',
            'cbjs_action': '''
            var class_name = 'tactic.ui.panel.CustomLayoutWdg';
            var kwargs = {
                view: bvr.view
            }
            spt.app_busy.show("Loading Metadata");
            spt.panel.load_popup("Metadata", class_name, kwargs);
            spt.app_busy.hide();
            '''
        } )
        """



        # template for each file item
        file_template = DivWdg()
        file_template.add_class("spt_upload_file_template")
        files_div.add(file_template)
        file_template.add_style("margin-bottom: 3px")
        file_template.add_style("padding: 3px")
        file_template.add_style("height: 40px")
        file_template.add_style("display: none")

        thumb_div = DivWdg()
        file_template.add(thumb_div)
        thumb_div.add_style("float: left")
        thumb_div.add_style("width: 60");
        thumb_div.add_style("height: 40");
        thumb_div.add_style("overflow: hidden");
        thumb_div.add_style("margin: 3 10 3 0");
        thumb_div.add_class("spt_thumb")


        info_div = DivWdg()
        file_template.add(info_div)
        info_div.add_style("float: left")

        name_div = DivWdg()
        name_div.add_class("spt_name")
        info_div.add(name_div)
        name_div.add("image001.jpg")
        name_div.add_style("width: 225px")
        name_div.add_style("overflow-x: hidden")
        name_div.add_style("text-overflow: ellipsis")



        """
        dialog = DialogWdg(display="false", show_title=False)
        info_div.add(dialog)
        dialog.set_as_activator(info_div, offset={'x':0,'y':10})

        dialog_data_div = DivWdg()
        dialog_data_div.add_color("background", "background")
        dialog_data_div.add_style("padding", "10px")

        dialog.add(dialog_data_div)
        dialog_data_div.add("Category: ")
        text = TextInputWdg(name="category")
        dialog_data_div.add(text)
        text.add_class("spt_category")
        text.add_style("padding: 1px")
        """

        date_div = DivWdg()
        date_div.add_class("spt_date_label")
        info_div.add(date_div)
        date_div.add("")
        date_div.add_style("opacity: 0.5")
        date_div.add_style("font-size: 0.8em")
        date_div.add_style("font-style: italic")
        date_div.add_style("margin-top: 3px")

        hidden_date_div = HiddenWdg("date")
        hidden_date_div.add_class("spt_date")
        info_div.add(date_div)




        size_div = DivWdg()
        size_div.add_class("spt_size")
        file_template.add(size_div)
        size_div.add("433Mb")
        size_div.add_style("float: left")
        size_div.add_style("width: 150px")
        size_div.add_style("text-align: right")

        remove_div = DivWdg()
        remove_div.add_class("spt_remove")
        file_template.add(remove_div)
        icon = IconButtonWdg(title="Remove", icon="BS_REMOVE")
        icon.add_style("float: right")
        remove_div.add(icon)
        #remove_div.add_style("text-align: right")


        div.add("<br/>")



        info = DivWdg()
        div.add(info)
        info.add_class("spt_upload_info")


        progress_div = DivWdg()
        progress_div.add_class("spt_upload_progress_top")
        div.add(progress_div)
        progress_div.add_style("width: 595px")
        progress_div.add_style("height: 15px")
        progress_div.add_style("margin-bottom: 10px")
        progress_div.add_border()
        #progress_div.add_style("display: none")

        progress = DivWdg()
        progress_div.add(progress)
        progress.add_class("spt_upload_progress")
        progress.add_style("width: 0px")
        progress.add_style("height: 100%")
        progress.add_gradient("background", "background3", -10)
        progress.add_style("text-align: right")
        progress.add_style("overflow: hidden")
        progress.add_style("padding-right: 3px")

        from tactic.ui.app import MessageWdg
        progress.add_behavior( {
            'type': 'load',
            'cbjs_action': MessageWdg.get_onload_js()
        } )



        # NOTE: files variable is passed in automatically

        upload_init = '''
        server.start( {description: "Upload and check-in of ["+files.length+"] files"} );
        var info_el = top.getElement(".spt_upload_info");
        info_el.innerHTML = "Uploading ...";
        '''

        upload_progress = '''
        var top = bvr.src_el.getParent(".spt_ingest_top");
        progress_el = top.getElement(".spt_upload_progress");
        var percent = Math.round(evt.loaded * 100 / evt.total);
        progress_el.setStyle("width", percent + "%");
        progress_el.innerHTML = String(percent) + "%";


        '''
        
        oncomplete_script_path = my.kwargs.get("oncomplete_script_path")
        oncomplete_script = ''
        if oncomplete_script_path:
            script_folder, script_title = oncomplete_script_path.split("/")
            oncomplete_script_expr = "@GET(config/custom_script['folder','%s']['title','%s'].script)" %(script_folder,script_title)    
            server = TacticServerStub.get()
            oncomplete_script_ret = server.eval(oncomplete_script_expr, single=True)
            
            if oncomplete_script_ret:
                oncomplete_script = '''var top = bvr.src_el.getParent(".spt_ingest_top");
                var file_els = top.getElements(".spt_upload_file");
                for ( var i = 0; i < file_els.length; i++) {
                spt.behavior.destroy( file_els[i] );
                };''' + oncomplete_script_ret
                script_found = True
            else:
                script_found = False
                oncomplete_script = "alert('Error: oncomplete script not found');"

        if not oncomplete_script:
            oncomplete_script = '''
            var click_action = function() {
                var fade = true;
                var pop = spt.popup.get_popup(top)
                spt.popup.close(pop, fade); 
            }
            spt.info("Ingest Completed", {click: click_action});
            server.finish();

            var file_els = top.getElements(".spt_upload_file");
            for ( var i = 0; i < file_els.length; i++) {
                spt.behavior.destroy( file_els[i] );
            };
            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "");

            spt.message.stop_interval(key);

            var info_el = top.getElement(".spt_upload_info");
            info_el.innerHTML = ''; 

            if (spt.table)
            {
                spt.table.run_search();
            }
            
            spt.panel.refresh(top);
            '''
            script_found = True
        
        on_complete = '''
        var top = bvr.src_el.getParent(".spt_ingest_top");
        var update_data_top = top.getElement(".spt_edit_top");
        var progress_el = top.getElement(".spt_upload_progress");
        progress_el.innerHTML = "100%";
        progress_el.setStyle("width", "100%");

        var info_el = top.getElement(".spt_upload_info");
        
        var search_type = bvr.kwargs.search_type;
        var relative_dir = bvr.kwargs.relative_dir;
        var context = bvr.kwargs.context;

        // Data comes from Ingest Settings
        var context_mode_select = top.getElement(".spt_context_mode_select");
        var context_mode = context_mode_select ? context_mode_select.value : bvr.kwargs.context_mode;
 
        var update_mode_select = top.getElement(".spt_update_mode_select");
        var update_mode = update_mode_select.value;

        var ignore_ext_select = top.getElement(".spt_ignore_ext_select");
        var ignore_ext = ignore_ext_select.value;

        var column_select = top.getElement(".spt_column_select");
        var column = column_select.value;


        var filenames = [];
        for (var i = 0; i != files.length;i++) {
            var name = files[i].name;
            filenames.push(name);
        }

        var key = spt.message.generate_key();
        var values = spt.api.get_input_values(top);
        //var category = values.category[0];
        //var keywords = values.keywords[0];

        var extra_data = values.extra_data ? values.extra_data[0]: {};
        var parent_key = values.parent_key[0];
        var search_key = values.search_key[0];

        var convert_el = top.getElement(".spt_image_convert")
        var convert = spt.api.get_input_values(convert_el);

        var processes = values.process;
        if (processes) {
            process = processes[0];
            if (!process) {
                process = null;
            }
        }
        else {
            process = null;
        }

        var return_array = false;
        var update_data = spt.api.get_input_values(update_data_top, null, return_array);

        var kwargs = {
            search_key: search_key,
            search_type: search_type,
            relative_dir: relative_dir,
            filenames: filenames,
            key: key,
            parent_key: parent_key,
            //category: category,
            //keywords: keywords,
            extra_data: extra_data,
            update_data: update_data,
            process: process,
            context: context,
            convert: convert,
            update_mode: update_mode,
            ignore_ext: ignore_ext,
            column: column,
            context_mode: context_mode
        }
        on_complete = function(rtn_data) {

        ''' + oncomplete_script + '''

        };

        var class_name = bvr.action_handler;
        // TODO: make the async_callback return throw an e so we can run 
        // server.abort
        server.execute_cmd(class_name, kwargs, null, {on_complete:on_complete});
        
        
        on_progress = function(message) {
            msg = JSON.parse(message.message);
            var percent = msg.progress;
            var description = msg.description;
            info_el.innerHTML = description;

            progress_el.setStyle("width", percent+"%");
            progress_el.innerHTML = percent + "%";
        }
        spt.message.set_interval(key, on_progress, 2000);

        '''


        button = ActionButtonWdg(title="Clear")
        button.add_style("float: right")
        button.add_style("margin-top: -3px")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingest_top");
            var file_els = top.getElements(".spt_upload_file");
            for ( var i = 0; i < file_els.length; i++) {
                spt.behavior.destroy( file_els[i] );
            };

            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "");

         '''
         } )

        upload_div = DivWdg()
        div.add(upload_div)
        button = ActionButtonWdg(title="Ingest Files", width=200, color="primary")
        upload_div.add(button)
        button.add_style("float: right")
        upload_div.add_style("margin-bottom: 15px")



        upload_div.add("<br clear='all'/>")


        action_handler = my.kwargs.get("action_handler")
        if not action_handler:
            action_handler = 'tactic.ui.tools.IngestUploadCmd';

        context = my.kwargs.get("context")
        context_mode = my.kwargs.get("context_mode")
 
        button.add_behavior( {
            'type': 'click_up',
            'action_handler': action_handler,
            'kwargs': {
                'search_type': my.search_type,
                'relative_dir': relative_dir,
                'script_found': script_found,
                'context': context,
                'context_mode': context_mode
            },
            'cbjs_action': '''

            if (bvr.kwargs.script_found != true)
            {
                spt.alert("Error: provided on_complete script not found");
                return;
            }

            var top = bvr.src_el.getParent(".spt_ingest_top");
           
            var file_els = top.getElements(".spt_upload_file");

            // get the server that will be used in the callbacks
            var server = TacticServerStub.get();

            // retrieved the stored file handles
            var files = [];
            for (var i = 0; i < file_els.length; i++) {
                files.push( file_els[i].file );
            }
            if (files.length == 0) {
                alert("Either click 'Add' or drag some files over to ingest.");
                return;
            }


            // defined the callbacks
            var upload_start = function(evt) {
            }

            var upload_progress = function(evt) {
            %s;
            }

            var upload_complete = function(evt) {
            %s;
            spt.app_busy.hide();
            }


            var upload_file_kwargs =  {
                files: files,
                upload_start: upload_start,
                upload_complete: upload_complete,
                upload_progress: upload_progress
            };
            if (bvr.ticket)
               upload_file_kwargs['ticket'] = bvr.ticket; 

            %s;

            spt.html5upload.set_form( top );
            spt.html5upload.upload_file(upload_file_kwargs);

            ''' % (upload_progress, on_complete, upload_init)
        } )


        return div


    def get_data_wdg(my):
        div = DivWdg()

        from pyasm.biz import Pipeline
        from pyasm.widget import SelectWdg
        search_type_obj = SearchType.get(my.search_type)
        base_type = search_type_obj.get_base_key()
        search = Search("sthpw/pipeline")
        search.add_filter("search_type", base_type)
        pipelines = search.get_sobjects()
        if pipelines:
            pipeline = pipelines[0]

            process_names = pipeline.get_process_names()
            if process_names:
                table = Table()
                div.add(table)
                table.add_row()
                table.add_cell("Process: ")
                select = SelectWdg("process")
                table.add_cell(select)
                process_names.append("---")
                process_names.append("publish")
                process_names.append("icon")
                select.set_option("values", process_names)
        


        ####
        buttons = Table()
        div.add(buttons)
        buttons.add_row()


        #button = IconButtonWdg(title="Fill in Data", icon=IconWdg.EDIT)
        button = ActionButtonWdg(title="Metadata")
        button.add_style("float: left")
        button.add_style("margin-top: -3px")
        buttons.add_cell(button)

        select_label = DivWdg("Update mode");
        select_label.add_style("float: left")
        select_label.add_style("margin-top: -3px")
        select_label.add_style("margin-left: 20px")
        buttons.add_cell(select_label)
        
        update_mode_option = my.kwargs.get("update_mode")
        if not update_mode_option:
            update_mode_option = "true"
        update_mode = SelectWdg(name="update mode")
        update_mode.add_class("spt_update_mode_select")
        update_mode.set_option("values", ["false", "true", "sequence"])
        update_mode.set_option("labels", ["Off", "On", "Sequence"])
        update_mode.set_option("default", update_mode_option)
        update_mode.add_style("float: left")
        update_mode.add_style("margin-top: -3px")
        update_mode.add_style("margin-left: 5px")
        update_mode.add_style("margin-right: 5px")
        buttons.add_cell(update_mode)

        update_info = DivWdg()
        update_info.add_class("glyphicon")
        update_info.add_class("glyphicon-info-sign")
        update_info.add_style("float: left")
        update_info.add_style("margin-top: -3px")
        update_info.add_style("margin-left: 10px")
        update_info.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.info("When update mode is on, if a file shares the name of one other file in the asset library, the file will update on ingest. If more than one file shares the name of an ingested asset, a new asset is created.<br> If sequence mode is selected, the system will update the sobject on ingest if a file sequence sharing the same name already exists.", {type: 'html'});
            '''
        } )
        buttons.add_cell(update_info);
 
        dialog = DialogWdg(display="false", show_title=False)
        div.add(dialog)
        dialog.set_as_activator(button, offset={'x':-10,'y':10})

        dialog_data_div = DivWdg()
        dialog_data_div.add_color("background", "background")
        dialog_data_div.add_style("padding", "20px")
        dialog.add(dialog_data_div)


        # Order folders by date
        name_div = DivWdg()
        dialog_data_div.add(name_div)
        name_div.add_style("margin: 15px 0px")

        if SearchType.column_exists(my.search_type, "relative_dir"):

            category_div = DivWdg()
            name_div.add(category_div)
            checkbox = RadioWdg("category")
            checkbox.set_option("value", "none")
            category_div.add(checkbox)
            category_div.add(" No categories")
            category_div.add_style("margin-bottom: 5px")
            checkbox.set_option("checked", "true")


            category_div = DivWdg()
            name_div.add(category_div)
            checkbox = RadioWdg("category")
            checkbox.set_option("value", "by_day")
            category_div.add(checkbox)
            category_div.add(" Categorize files by Day")
            category_div.add_style("margin-bottom: 5px")


            category_div = DivWdg()
            name_div.add(category_div)
            checkbox = RadioWdg("category")
            checkbox.set_option("value", "by_week")
            category_div.add(checkbox)
            category_div.add(" Categorize files by Week")
            category_div.add_style("margin-bottom: 5px")


            category_div = DivWdg()
            name_div.add(category_div)
            checkbox = RadioWdg("category")
            checkbox.set_option("value", "by_year")
            category_div.add(checkbox)
            category_div.add(" Categorize files by Year")
            category_div.add_style("margin-bottom: 5px")


            """
            checkbox = RadioWdg("category")
            checkbox.set_option("value", "custom")
            name_div.add(checkbox)
            name_div.add(" Custom")
            """

            name_div.add("<br/>")



        # edit
        from tactic.ui.panel import EditWdg

        ingest_data_view = my.kwargs.get('ingest_data_view')

        sobject = SearchType.create(my.search_type)
        edit = EditWdg(search_key =sobject.get_search_key(), mode='view', view=ingest_data_view )
        
        dialog_data_div.add(edit)
        hidden = HiddenWdg(name="parent_key")
        dialog_data_div.add(hidden)
        hidden.add_class("spt_parent_key")
        parent_key = my.kwargs.get("parent_key") or ""
        if parent_key:
            hidden.set_value(parent_key)


        extra_data = my.kwargs.get("extra_data")
        if not isinstance(extra_data, basestring):
            extra_data = jsondumps(extra_data)

        if extra_data and extra_data != "null":
            # it needs a TextArea instead of Hidden because of JSON data
            text = TextAreaWdg(name="extra_data")
            text.add_style('display: none')
            text.set_value(extra_data)
            dialog_data_div.add(text)



        return div




    def get_select_files_button(my):


        button = ActionButtonWdg(title="Add Files")

        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        button.add(upload)


        button.add_style("margin: 30px auto")

        button.add_behavior( {
            'type': 'click_up',
            'normal_ext': File.NORMAL_EXT,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');
        
            //clear upload progress
            var upload_bar = top.getElement('.spt_upload_progress');
            if (upload_bar) {
                upload_bar.setStyle('width','0%');
                upload_bar.innerHTML = '';
            }
        var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                var delay = 0; 
                for (var i = 0; i < files.length; i++) {
                    var size = files[i].size;
                    var file_name = files[i].name;
                    var is_normal = regex.test(file_name);
                    if (size >= 10*1024*1024 || is_normal) {
                        spt.drag.show_file(files[i], files_el, 0, false);
                    }
                    else {
                        spt.drag.show_file(files[i], files_el, delay, true);

                        if (size < 100*1024)       delay += 50;
                        else if (size < 1024*1024) delay += 500;
                        else if (size < 10*1024*1024) delay += 1000;
                    }
                }
        }

            spt.html5upload.clear();
            spt.html5upload.set_form( top );
            spt.html5upload.select_file( onchange );

         '''
        } )

        return button




class IngestUploadCmd(Command):

    def execute(my):

        filenames = my.kwargs.get("filenames")

        base_dir = my.kwargs.get("base_dir")
        if not base_dir:
            upload_dir = Environment.get_upload_dir()
            base_dir = upload_dir

        context_mode = my.kwargs.get("context_mode")
        if not context_mode:
            context_mode = "case_insensitive"
        update_mode = my.kwargs.get("update_mode")
        ignore_ext = my.kwargs.get("ignore_ext")
        column = my.kwargs.get("column")
        if not column:
            column = "name"


        search_key = my.kwargs.get("search_key")
        if search_key:
            my.sobject = Search.get_by_search_key(search_key)
            search_type = my.sobject.get_search_key()
        else:
            search_type = my.kwargs.get("search_type")
            my.sobject = None


        key = my.kwargs.get("key")
        relative_dir = my.kwargs.get("relative_dir")
        if not relative_dir:
            project_code = Project.get_project_code()
            search_type_obj = SearchType.get(search_type)
            table = search_type_obj.get_table()
            relative_dir = "%s/%s" % (project_code, table)

        server = TacticServerStub.get()

        parent_key = my.kwargs.get("parent_key")
        category = my.kwargs.get("category")
        keywords = my.kwargs.get("keywords")
        update_data = my.kwargs.get("update_data")
        extra_data = my.kwargs.get("extra_data")
        if extra_data:
            extra_data = jsonloads(extra_data)
        else:
            extra_data = {}

        # TODO: use this to generate a category
        category_script_path = my.kwargs.get("category_script_path")
        """
        ie:
            from pyasm.checkin import ExifMetadataParser
            parser = ExifMetadataParser(path=file_path)
            tags = parser.get_metadata()

            date = tags.get("EXIF DateTimeOriginal")
            return date.split(" ")[0]
        """

        if not SearchType.column_exists(search_type, column):
            raise TacticException('The Ingestion puts the file name into the "%s" column which is the minimal requirement. Please first create a "%s" column for this sType.' % (column, column))

        input_prefix = update_data.get('input_prefix')
        non_seq_filenames = []

        # For sequence mode, take all filenames, and regenerate the filenames based on the function "find_sequences"
        if update_mode == "sequence":
            
            non_seq_filenames_dict, seq_digit_length = my.find_sequences(filenames)
            # non_seq_filenames is a list of filenames that are stored in the None key,
            # which are the filenames that are not part of a sequence, or does not contain
            # a sequence pattern.
            non_seq_filenames = non_seq_filenames_dict[None]
            
            # delete the None key from list so filenames can be used in the latter for loop
            del non_seq_filenames_dict[None]
            filenames = non_seq_filenames_dict.keys()
            if filenames == []:
                raise TacticException('No sequences are found in files. Please follow the pattern of [filename] + [digits] + [file extension (optional)]. Examples: [abc_1001.png, abc_1002.png] [abc.1001.mp3, abc.1002.mp3] [abc_100_1001.png, abc_100_1002.png]')

        for count, filename in enumerate(filenames):
        # Check if files should be updated. 
        # If so, attempt to find one to update.
        # If more than one is found, do not update.

            if filename.endswith(".zip"):
                from pyasm.common import ZipUtil

                unzip_dir = "/tmp/xxx"
                if not os.path.exists(unzip_dir):
                    os.makedirs(unzip_dir)

                zip_path = "%s/%s" % (base_dir, filename)
                ZipUtil.extract(zip_path, base_dir=unzip_dir)

                paths = ZipUtil.get_file_paths(zip_path)


                new_kwargs = my.kwargs.copy()
                new_kwargs['filenames'] = paths
                new_kwargs['base_dir'] = unzip_dir
                ingest = IngestUploadCmd(**new_kwargs)
                ingest.execute()

                continue



            if my.sobject:
                sobject = my.sobject

            elif update_mode in ["true", True]:
                # first see if this sobjects still exists
                search = Search(search_type)
                search.add_filter(column, filename)
                if relative_dir and search.column_exists("relative_dir"):
                    search.add_filter("relative_dir", relative_dir)
                sobjects = search.get_sobjects()
                if len(sobjects) > 1:
                    sobject = None
                elif len(sobjects) == 1:
                    sobject = sobjects[0]
                else:
                    sobject = None

            elif update_mode == "sequence":
                if not FileGroup.is_sequence(filename):
                    raise TacticException('Please modify sequence naming to have at least three digits.')
                search = Search(search_type)
                search.add_filter(column, filename)

                if relative_dir and search.column_exists("relative_dir"):
                    search.add_filter("relative_dir", relative_dir)
                sobjects = search.get_sobjects()
                if sobjects:
                    sobject = sobjects[0]
                else:
                    sobject = None

            else:
                sobject = None 


            # Create a new entry
            if not sobject:
                sobject = SearchType.create(search_type)

                if ignore_ext in ['true', True]:
                    name, ext = os.path.splitext(filename)
                else:
                    name = filename

                # if the name contains a path, the only take basename
                name = os.path.basename(name)

                sobject.set_value(column, name)
                if relative_dir and sobject.column_exists("relative_dir"):
                    sobject.set_value("relative_dir", relative_dir)


            relative_dir = my.kwargs.get("relative_dir")
            if relative_dir:
                path = "%s/%s" % (relative_dir, filename)
            else:
                path = filename

            # extract keywords from filename
            file_keywords = my.get_keywords_from_path(path)
            file_keywords.append(filename.lower())
            file_keywords = " ".join(file_keywords)

            if SearchType.column_exists(search_type, "keywords"):
                if keywords:
                    file_keywords = "%s %s " % (keywords, file_keywords)

                if file_keywords:
                    sobject.set_value("keywords", file_keywords)


            if sobject.column_exists("keywords_data"):
                data = sobject.get_json_value("keywords_data", {})
                data['path'] = file_keywords.split(" ")
                sobject.set_json_value("keywords_data", data)




            # extract metadata
            #file_path = "%s/%s" % (base_dir, File.get_filesystem_name(filename))
            if update_mode == "sequence":
                first_filename = non_seq_filenames_dict.get(filename)[0]
                last_filename = non_seq_filenames_dict.get(filename)[-1]
                file_path = "%s/%s" % (base_dir, first_filename)
            else:
                file_path = "%s/%s" % (base_dir, filename)


            """
            # TEST: convert on upload
            try:
                convert = my.kwargs.get("convert")
                if convert:
                    message_key = "IngestConvert001"
                    cmd = ConvertCbk(**convert)
                    cmd.execute()
            except Exception, e:
                print "WARNING: ", e
            """


            if not os.path.exists(file_path):
                raise Exception("Path [%s] does not exist" % file_path)

            # get the metadata from this image
            if SearchType.column_exists(search_type, "relative_dir"):
                if category and category not in ['none', None]:
                    from pyasm.checkin import ExifMetadataParser
                    parser = ExifMetadataParser(path=file_path)
                    tags = parser.get_metadata()

                    date = tags.get("EXIF DateTimeOriginal")
                    if not date:
                        date_str = "No-Date"
                    else:
                        date_str = str(date)
                        # this can't be parsed correctly by dateutils
                        parts = date_str.split(" ")
                        date_str = parts[0].replace(":", "-")
                        date_str = "%s %s" % (date_str, parts[1])

                        from dateutil import parser 
                        orig_date = parser.parse(date_str)

                        if category == "by_day":
                            date_str = orig_date.strftime("%Y/%Y-%m-%d")
                        elif category == "by_month":
                            date_str = orig_date.strftime("%Y-%m")
                        elif category == "by_week":
                            date_str = orig_date.strftime("%Y/Week-%U")

                    full_relative_dir = "%s/%s" % (relative_dir, date_str)
                    sobject.set_value("relative_dir", full_relative_dir)
           
            # Add parent sObject
            if parent_key:
                parent = Search.get_by_search_key(parent_key)
                if parent:
                    try:
                        sobject.set_sobject_value(parent)
                    except:
                        pass

            for key, value in update_data.items():
                if input_prefix:
                    key = key.replace('%s|'%input_prefix, '')
                if SearchType.column_exists(search_type, key):
                    if value:
                        sobject.set_value(key, value)



            for key, value in extra_data.items():
                if SearchType.column_exists(search_type, key):
                    sobject.set_value(key, value)


            """
            if category:

                if SearchType.column_exists(search_type, "category"):
                    sobject.set_value("category", category)


                if SearchType.column_exists(search_type, "relative_dir"):
                    full_relative_dir = "%s/%s" % (relative_dir, category)
                    sobject.set_value("relative_dir", category)
            """

            sobject.commit()
            search_key = sobject.get_search_key()

            # use API to check in file

            process = my.kwargs.get("process")
            if not process:
                process = "publish"


            context = my.kwargs.get("context")
            if not context:
                context = process

            if process == "icon":
                context = "icon"
            else:
                context = "%s/%s" % (context, filename)

            if context_mode == "case_insensitive":
                context = context.lower()                
            
            if update_mode == "sequence":

                pattern_expr = re.compile('^.*(\d{%d})\..*$'%seq_digit_length)
                
                m_first = re.match(pattern_expr, first_filename)
                m_last = re.match(pattern_expr, last_filename)
                # for files without extension
                # abc_1001, abc.1123_1001
                if not m_first: 
                    no_ext_expr = re.compile('^.*(\d{%d})$'%seq_digit_length)
                    m_first = re.match(no_ext_expr, first_filename)
                    m_last = re.match(no_ext_expr, last_filename)

                # using second last index , to grab the set right before file type
                groups_first = m_first.groups()
                if groups_first:
                    range_start = int(m_first.groups()[0])
                    
                groups_last = m_last.groups()
                if groups_last:
                    range_end = int(m_last.groups()[0])

                file_range = '%s-%s' % (range_start, range_end)

                file_path = "%s/%s" % (base_dir, filename)
                server.group_checkin(search_key, context, file_path, file_range, mode='uploaded')
            else: 
                if my.kwargs.get("base_dir"):
                    from pyasm.checkin import FileCheckin
                    checkin = FileCheckin(sobject, file_path, context=context, process=process)
                    checkin.execute()
                else:
                    server.simple_checkin(search_key, context, filename, process=process, mode='uploaded')


            percent = int((float(count)+1) / len(filenames)*100)
            print "checking in: ", filename, percent

            msg = {
                'progress': percent,
                'description': 'Checking in file [%s]' % filename,
            }

            server.log_message(key, msg, status="in progress")






        msg = {
            'progress': '100',
            'description': 'Check-ins complete'
        }
        server.log_message(key, msg, status="complete")

        my.info = non_seq_filenames
        return non_seq_filenames


    def get_keywords_from_path(cls, rel_path):

        # delimiters
        P_delimiters = re.compile("[- _\.]")
        # special characters
        P_special_chars = re.compile("[\[\]{}\(\)\,]")
        # camel case
        P_camel_case = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


        #parts = rel_path.split("/")
        parts =  re.split(r'/|\\', rel_path)
        keywords = set()

        for item in parts:
            item = P_camel_case.sub(r'_\1', item)
            parts2 = re.split(P_delimiters, item)
            for item2 in parts2:
                if not item2:
                    continue

                item2 = re.sub(P_special_chars, "", item2)

                # skip 1 letter keywords
                if len(item2) == 1:
                    continue

                try:
                    int(item2)
                    continue
                except:
                    pass


                #print "item: ", item2
                item2 = item2.lower()

                keywords.add(item2)

        keywords_list = list(keywords)
        keywords_list.sort()
        return keywords_list

    get_keywords_from_path = classmethod(get_keywords_from_path)










    def natural_sort(my,l):
        '''
        natural sort will makesure a list of names passed in is 
        sorted in an order of 1000 to be after 999 instead of right after 101
        '''
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(l, key = alphanum_key)

    def find_sequences(my, filenames):
        '''
        Parse a list of filenames into a dictionary of sequences.  Filenames not
        part of a sequence are returned in the None key

        :param      filenames | [<str>, ..]

        :return     {<str> sequence: [<str> filename, ..], ..}
        '''
        local_filenames   = filenames[:]
        sequence_patterns = {}
        sequences         = {None: []}

        # sort the files (by natural order) so we always generate a pattern
        # based on the first potential file in a sequence

        local_filenames = my.natural_sort(local_filenames)

        for filename in local_filenames:
            count = re.findall('\d+', filename)

            if not count:
                raise TacticException("Please ingest sequences only.")
            
            base, file_ext = os.path.splitext(filename)

            if file_ext:
                file_ext = file_ext[1:]

            # if last set of digits is not a file extension, and is less than 3 digits
            # because common.get_dir_info only works with 3 of more digits
            if len(count[-1]) <= 1 and file_ext.isalpha():
                raise TacticException('Please modify sequence naming to have at least three digits.')
            
            
            # if file extension found, and contains a number in the extension (but also not completely numbers)
            # grab the second last set of digits
            # ie. .mp3, .mp4, .23p

            if file_ext and not file_ext.isalpha() and not file_ext.isdigit():
                seq_digit_length = len(count[-2])
            else:
                seq_digit_length = len(count[-1])



            # if file_ext is empty, or if file_ext[1] is all numbers, use expression below
            # abc0001, abc.0001 ...etc
            if not file_ext or file_ext.isdigit():
                try:
                    pattern_expr = re.compile('^(.*)(\d{%d})([^\d]*)$'%seq_digit_length)
                except:
                    sequences[None].append(filename)
                    continue
            
            # then for regular filenames, try grabbing filenames by looking at the digits before the last dot
            # for files with extensions:
            # abc.0001.png, abc.0001.mp3, abc0001.mp3, 
            else:
                try:
                    pattern_expr = re.compile('^(.*)(\d{%d})(\..*)$'%seq_digit_length)
                except:
                    sequences[None].append(filename)
                    continue

            
            pound_length = seq_digit_length
            pounds = "#" * pound_length

            # first, check to see if this filename matches a sequence
            found = False

            for key, pattern in sequence_patterns.items():
                match = pattern.match(filename)
                if not match:
                    continue

                sequences[key].append(filename)
                found = True
                break

            # if we've already been matched, then continue on
            if found:
                continue

            # next, see if this filename should start a new sequence
            basename = os.path.basename(filename)

            pattern_match = pattern_expr.match(basename)

            if pattern_match:
                opts = (pattern_match.group(1), pattern_match.group(3))
                key  = '%s%s%s' % (opts[0], pounds, opts[1])

                # create a new pattern based on the filename
                sequence_pattern = re.compile('^%s\d+%s$' % opts)

                sequence_patterns[key] = sequence_pattern
                sequences[key] = [filename]
                continue

            # otherwise, add it to the list of non-sequences
            sequences[None].append(filename)

        # now that we have grouped everything, we'll merge back filenames
        # that were potential sequences, but only contain a single file to the
        # non-sequential list
        for key, filenames in sequences.items():
            if ( key is None or len(filenames) > 1 ):
                continue

            sequences.pop(key)
            sequences[None] += filenames

        return sequences, seq_digit_length
