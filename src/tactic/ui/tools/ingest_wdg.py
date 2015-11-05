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
        'ingest_data_view': 'Specify a ingest data view, defaults to edit',
        'extra_data': 'Extra data (JSON) to be added to created sobjects',
        'oncomplete_script_path': 'Script to be run on a finished ingest',
        'update_mode': 'Takes values "true" or "false".  When true, uploaded files will update existing file iff exactly one file exists already with the same name.'
    }


    def get_display(my):

        relative_dir = my.kwargs.get("relative_dir")
        my.relative_dir = relative_dir

        div = DivWdg()
        div.add_class("spt_ingest_top")
        div.add_style("width: 100%px")
        div.add_style("min-width: 500px")
        div.add_style("padding: 20px")
        div.add_color("background", "background")
        
        my.search_type = my.kwargs.get("search_type")
        if not my.search_type:
            div.add("No search type specfied")
            return div

        if relative_dir:
            folder_div = DivWdg()
            div.add(folder_div)
            folder_div.add("Folder: %s" % relative_dir)
            folder_div.add_style("opacity: 0.5")
            folder_div.add_style("font-style: italic")
            folder_div.add_style("margin-bottom: 10px")



        data_div = my.get_data_wdg()
        data_div.add_style("float: left")
        data_div.add_style("float: left")
        div.add(data_div)

        # create the help button
        help_button_wdg = DivWdg()
        div.add(help_button_wdg)
        help_button_wdg.add_style("float: right")
        help_button = ActionButtonWdg(title="?", tip="Ingestion Widget Help", size='s')
        help_button_wdg.add(help_button)

        help_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''spt.help.load_alias("ingestion_widget")'''
        } )

        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        div.add(upload)


        button = ActionButtonWdg(title="Add")
        button.add_style("float: right")
        button.add_style("margin-top: -3px")
        div.add(button)
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

         '''
         } )




        div.add("<br clear='all'/>")
        div.add("<br clear='all'/>")

        border_color_light = div.get_color("background2", 8)
        border_color_dark = div.get_color("background2", -15)
        background_mouseout = div.get_color("background3", 10)
        background_mouseenter = div.get_color("background3", 8)


        files_div = DivWdg()
        files_div.add_style("position: relative")
        files_div.add_class("spt_to_ingest_files")
        div.add(files_div)
        files_div.add_style("max-height: 300px")
        files_div.add_style("height: 300px")
        files_div.add_style("overflow-y: auto")
        files_div.add_style("padding: 3px")
        files_div.add_color("background", background_mouseout)
        files_div.add_style("border: 3px dashed %s" % border_color_light)
        files_div.add_style("border-radius: 20px 20px 20px 20px")
        files_div.add_style("z-index: 1")
        #files_div.add_style("display: none")

        bgcolor = div.get_color("background3")
        bgcolor2 = div.get_color("background3", -3)

        #style_text = "text-align: center; margin-top: 100px; color: #A0A0A0; font-size: 3.0em; z-index: 10;"

        background = DivWdg()
        background.add_class("spt_files_background")
        files_div.add(background)

        background.add_style("text-align: center")
        background.add_style("margin-top: 100px")
        background.add_style("opacity: 0.65")
        background.add_style("font-size: 3.0em")
        background.add_style("z-index: 10")

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

            if (!background) {
                background = top.getElement(".spt_files_background");
                if (background)
                    background.setStyle("display", "none");
            }
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
            var top = bvr.src_el.getParent(".spt_upload_file");
            spt.behavior.destroy_element(top);
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
        name_div.add_style("width: 150px")



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
        icon = IconButtonWdg(title="Remove", icon=IconWdg.DELETE)
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
        progress_div.add_style("width: 100%")
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
        
        var update_mode_select = top.getElement(".spt_update_mode_select");
        var update_mode = update_mode_select.value;

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
            convert: convert,
            update_mode: update_mode,
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


        upload_div = DivWdg()
        div.add(upload_div)
        #button = UploadButtonWdg(**kwargs)
        button = ActionButtonWdg(title="Ingest")
        upload_div.add(button)
        button.add_style("float: right")
        upload_div.add_style("margin-bottom: 15px")
        upload_div.add("<br clear='all'/>")


        action_handler = my.kwargs.get("action_handler")
        if not action_handler:
            action_handler = 'tactic.ui.tools.IngestUploadCmd';
 
        button.add_behavior( {
            'type': 'click_up',
            'action_handler': action_handler,
            'kwargs': {
                'search_type': my.search_type,
                'relative_dir': relative_dir,
                'script_found': script_found,
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

        ingest_data_view = my.kwargs.get('ingest_data_view')

        from tactic.ui.panel import EditWdg

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

        """
 
        dialog_data_div.add("Keywords:<br/>")
        dialog.add(dialog_data_div)
        text = TextAreaWdg(name="keywords")
        dialog_data_div.add(text)
        text.add_class("spt_keywords")
        text.add_style("padding: 1px")


        dialog_data_div.add("<br/>"*2)
    

       
        text.add_class("spt_extra_data")
        text.add_style("padding: 1px")

        """

        #### TEST Image options
        """
        button = IconButtonWdg(title="Resize", icon=IconWdg.FILM)
        buttons.add_cell(button)

        dialog = DialogWdg(display="false", show_title=False)
        div.add(dialog)
        dialog.set_as_activator(button, offset={'x':-10,'y':10})

        try:
            from spt.tools.convert import ConvertOptionsWdg
            convert_div = DivWdg()
            dialog.add(convert_div)
            convert_div.add_style("padding: 20px")
            convert_div.add_color("background", "background")
            convert_div.add_class("spt_image_convert")

            convert = ConvertOptionsWdg()
            convert_div.add(convert)
        except:
            pass
        """


        # use base name for name
        """
        name_div = DivWdg()
        dialog_data_div.add(name_div)
        name_div.add_style("margin: 15px 0px")


        checkbox = CheckboxWdg("use_file_name")
        name_div.add(checkbox)
        name_div.add(" Use name of file for name")

        name_div.add("<br/>")

        checkbox = CheckboxWdg("use_base_name")
        name_div.add(checkbox)
        name_div.add(" Remove extension")


        name_div.add("<br/>")

        checkbox = CheckboxWdg("file_keywords")
        name_div.add(checkbox)
        name_div.add(" Use file name for keywords")
        """


        return div




class IngestUploadCmd(Command):

    def execute(my):

        filenames = my.kwargs.get("filenames")

        upload_dir = Environment.get_upload_dir()
        base_dir = upload_dir

        update_mode = my.kwargs.get("update_mode")
        search_type = my.kwargs.get("search_type")
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

        if not SearchType.column_exists(search_type, "name"):
            raise TacticException('The Ingestion puts the file name into the name column which is the minimal requirement. Please first create a "name" column for this sType.')

        input_prefix = update_data.get('input_prefix')
        non_seq_filenames = []

        # For sequence mode, take all filenames, and regenerate the filenames based on the function "find_sequences"
        if update_mode == "sequence":
            results = my.find_sequences(filenames)

            # non_seq_filenames is a list of filenames that are stored in the None key,
            # which are the filenames that are not part of a sequence, or does not contain
            # a sequence pattern.
            non_seq_filenames = results[None]
            
            # delete the None key from list so filenames can be used in the latter for loop
            del results[None]
            filenames = results.keys()
            if filenames == []:
                raise TacticException('No sequences are found in files.')

        for count, filename in enumerate(filenames):
        # Check if files should be updated. 
        # If so, attempt to find one to update.
        # If more than one is found, do not update.
            if update_mode in ["true", "True"]:
                # first see if this sobjects still exists
                search = Search(search_type)
                search.add_filter("name", filename)
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
                search.add_filter("name", filename)

                if relative_dir and search.column_exists("relative_dir"):
                    search.add_filter("relative_dir", relative_dir)
                sobjects = search.get_sobjects()
                if sobjects:
                    sobject = sobjects[0]
                else:
                    sobject = None

            else:
                sobject = None 

            # Create a new file
            if not sobject:
                sobject = SearchType.create(search_type)
                sobject.set_value("name", filename)
                if relative_dir and sobject.column_exists("relative_dir"):
                    sobject.set_value("relative_dir", relative_dir)



            # extract metadata
            #file_path = "%s/%s" % (base_dir, File.get_filesystem_name(filename))
            if update_mode == "sequence":
                first_filename = results.get(filename)[0]
                last_filename = results.get(filename)[-1]
                file_path = "%s/%s" % (base_dir, first_filename)
            else:
                file_path = "%s/%s" % (base_dir, filename)

            # TEST: convert on upload
            try:
                convert = my.kwargs.get("convert")
                if convert:
                    message_key = "IngestConvert001"
                    cmd = ConvertCbk(**convert)
                    cmd.execute()
            except Exception, e:
                print "WARNING: ", e


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

            if parent_key:
                parent = Search.get_by_search_key(parent_key)
                if parent:
                    sobject.set_sobject_value(sobject)

            for key, value in update_data.items():
                if input_prefix:
                    key = key.replace('%s|'%input_prefix, '')
                if SearchType.column_exists(search_type, key):
                    if value:
                        sobject.set_value(key, value)
            """
            if SearchType.column_exists(search_type, "keywords"):
                if keywords:
                    sobject.set_value("keywords", keywords)

            """
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

            if process == "icon":
                context = "icon"
            else:
                context = "%s/%s" % (process, filename.lower())
            
            if update_mode == "sequence":
                count_digits = re.findall('\d+', first_filename)
                # if count_digits[-1] is only one digit, meaning filetypes: mp3, mp4 ...etc
                if len(count_digits[-1]) < 2:
                    seq_digit_length = len(count_digits[-2])
                else:
                    seq_digit_length = len(count_digits[-1])

                expr = re.compile('^([^0]*)(\d+)([^\d]*)$')
                # using matches.groups() to find the first and last filename's pattern,
                # to find the file range

                
                pattern_expr = re.compile('^(.*)(\d{%d})(\..*)$'%seq_digit_length)
                
                m_first = re.match(pattern_expr, first_filename)
                m_last = re.match(pattern_expr, last_filename)
                # for files without extension
                if not m_first: 
                    pattern_expr = re.compile('^(.*)(\d{%d})([^\d]*)$'%seq_digit_length)
                    m_first = re.match(pattern_expr, first_filename)
                    m_last = re.match(pattern_expr, last_filename)

                # using second last index , to grab the set right before file type
                range_start = int(m_first.groups()[-2])
                
                range_end = int(m_last.groups()[-2])

                file_range = '%s-%s' % (range_start, range_end)

                file_path = "%s/%s" % (base_dir, filename)
                server.group_checkin(search_key, context, file_path, file_range, mode='uploaded')
            else: 
                server.simple_checkin(search_key, context, filename, mode='uploaded')
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
            if len(count) <= 1:
                raise TacticException('Please modify sequence naming to have at least three digits.')
            if not count:
                raise TacticException("Please ingest sequences only.")
            # if count[-1] is only one digit, meaning filetypes: mp3, mp4 ...etc
            if len(count[-1]) <= 2:
                seq_digit_length = len(count[-2])
            else:
                seq_digit_length = len(count[-1])

            try: 
                #pattern_expr = re.compile('^(.*)(\d{%d})([^\d]*)$'%len(count[-1]))
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
            basename      = os.path.basename(filename)

            pattern_match = pattern_expr.match(basename)
            if not pattern_match:
                pattern_expr = re.compile('^(.*)(\d{%d})([^\d]*)$'%seq_digit_length)
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

        return sequences
