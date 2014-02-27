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
from pyasm.widget import IconWdg, TextWdg, CheckboxWdg, RadioWdg, TextAreaWdg, HiddenWdg
from pyasm.command import Command
from pyasm.search import SearchType, Search
from pyasm.biz import File, Project
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import DialogWdg
from tactic.ui.widget import IconButtonWdg

from tactic.ui.input import UploadButtonWdg, TextInputWdg
from tactic.ui.widget import ActionButtonWdg

from tactic_client_lib import TacticServerStub

import os

__all__ = ['IngestUploadWdg', 'IngestUploadCmd']


class IngestUploadWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'search_type': 'Search Type to ingest into',
        'parent_key': 'Parent search key to relate create sobject to',
        'extra_data': 'Extra data (JSON) to be added to created sobjects'
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


        title_div = DivWdg()
        div.add(title_div)
        title_div.add("Ingest Files")
        title_div.add_style("font-size: 14px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 10px")
        title_div.add_color("background", "background3")
        title_div.add_border()

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

            title_div.add_style("margin: -20px -21px 5px -21px")
        else:
            title_div.add_style("margin: -20px -21px 15px -21px")


        div.add("<b>Add or drag/drop files to be ingested</b>")
        div.add("<br/>"*2)


        data_div = my.get_data_wdg()
        data_div.add_style("float: left")
        data_div.add_style("float: left")
        div.add(data_div)

        # create the help button
        help_button_wdg = DivWdg()
        div.add(help_button_wdg)
        help_button_wdg.add_style("margin-top: -3px")
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
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_upload_files");

	    var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                for (var i = 0; i < files.length; i++) {
                    spt.drag.show_file(files[i], files_el, 0, true);
                }
	    }

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


        files_div = DivWdg()
        files_div.add_style("position: relative")
        files_div.add_class("spt_to_ingest_files")
        div.add(files_div)
        files_div.add_style("max-height: 300px")
        files_div.add_style("height: 300px")
        files_div.add_style("overflow-y: auto")
        files_div.add_border()
        files_div.add_style("padding: 3px")
        files_div.add_color("background", "background3")
        #files_div.add_style("display: none")

        bgcolor = div.get_color("background3")
        bgcolor2 = div.get_color("background3", -3)

        files_div.add_behavior( {
            'type': 'mouseenter',
            'bgcolor': bgcolor2,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor)
            '''
        } )

        files_div.add_behavior( {
            'type': 'mouseout',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor)
            '''
        } )


        background = DivWdg()
        background.add_class("spt_files_background")
        files_div.add(background)
        background.add_style("font-size: 4.0em")
        background.add_style("font-weight: bold")
        background.add_style("opacity: 0.1")
        background.add_style("position: absolute")
        background.add_style("left: 50%")
        background.add_style("top: 100px")
        background.add_border()
        inner_background = DivWdg("Drag Files Here")
        background.add(inner_background)
        inner_background.set_style("position: absolute")
        inner_background.set_style("margin-left: -50%")



        # Test drag and drop files
        files_div.add_attr("ondragenter", "return false")
        files_div.add_attr("ondragover", "return false")
        files_div.add_attr("ondrop", "spt.drag.noop(event, this)")
        files_div.add_behavior( {
        'type': 'load',
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
                if (icon) {
                    var loadingImage = loadImage(
                        file,
                        function (img) {
                            thumb_el.appendChild(img);
                        },
                        {maxWidth: 80, maxHeight: 60, canvas: true, contain: true}
                    );
                }
                else {
                    var img = $(document.createElement("div"));
                    img.setStyle("width", "60");
                    img.setStyle("height", "40");
                    //img.innerHTML = "MP4";
                    img.setStyle("border", "solid 1px black")
                    thumb_el.appendChild(img);
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
            for (var i = 0; i < files.length; i++) {
                var size = files[i].size;
                if (size >= 10*1024*1024) {
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
        var server = TacticServerStub.get();
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


        on_complete = '''
        var top = bvr.src_el.getParent(".spt_ingest_top");
        var update_data_top = top.getElement(".spt_edit_top");
        var progress_el = top.getElement(".spt_upload_progress");
        progress_el.innerHTML = "100%";
        progress_el.setStyle("width", "100%");

        var info_el = top.getElement(".spt_upload_info");
        
        var search_type = bvr.kwargs.search_type;
        var relative_dir = bvr.kwargs.relative_dir;

        var filenames = [];
        for (var i = 0; i != files.length;i++) {
            var name = files[i].name;
            filenames.push(name);
        }

        var key = spt.message.generate_key();
        var values = spt.api.get_input_values(top);
        //var category = values.category[0];
        //var keywords = values.keywords[0];

        //var extra_data = values.extra_data[0];
        
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
            //extra_data: extra_data,
            update_data: update_data,
            process: process,
            convert: convert,
        }
        on_complete = function() {

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

            

            spt.table.run_search();

        };

        var class_name = bvr.action_handler;
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
                'relative_dir': relative_dir
            },
            'cbjs_action': '''

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


        button = IconButtonWdg(title="Fill in Data", icon=IconWdg.EDIT)
        buttons.add_cell(button)


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

        ingest_insert_view = my.kwargs.get('ingest_insert_view')

        ingest_insert_view = 'edit'
        from tactic.ui.panel import EditWdg

        sobject = SearchType.create(my.search_type)
        edit = EditWdg(search_key =sobject.get_search_key(), mode='view', view=ingest_insert_view )
        
        dialog_data_div.add(edit)
        hidden = HiddenWdg(name="parent_key")
        dialog_data_div.add(hidden)
        hidden.add_class("spt_parent_key")
        parent_key = my.kwargs.get("parent_key") or ""
        if parent_key:
            hidden.set_value(parent_key)




        """
 
        dialog_data_div.add("Keywords:<br/>")
        dialog.add(dialog_data_div)
        text = TextAreaWdg(name="keywords")
        dialog_data_div.add(text)
        text.add_class("spt_keywords")
        text.add_style("padding: 1px")


        dialog_data_div.add("<br/>"*2)
    

        extra_data = my.kwargs.get("extra_data")
        if not isinstance(extra_data, basestring):
            extra_data = jsondumps(extra_data)

        dialog_data_div.add("Extra Data (JSON):<br/>")
        text = TextAreaWdg(name="extra_data")
        dialog_data_div.add(text)
        if extra_data != "null":
            text.set_value(extra_data)
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
        
        for count, filename in enumerate(filenames):

            # first see if this sobjects still exists
            search = Search(search_type)
            search.add_filter("name", filename)
            if relative_dir and search.column_exists("relative_dir"):
                search.add_filter("relative_dir", relative_dir)
            sobject = search.get_sobject()

            # else create a new one
            if not sobject:
                sobject = SearchType.create(search_type)
                sobject.set_value("name", filename)
                if relative_dir and sobject.column_exists("relative_dir"):
                    sobject.set_value("relative_dir", relative_dir)



            # extract metadata
            #file_path = "%s/%s" % (base_dir, File.get_filesystem_name(filename))
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

            for key, value in extra_data.items():
                if SearchType.column_exists(search_type, key):
                    sobject.set_value(key, value)
            """

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
                context = "%s/%s" % (process, filename)
            

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



