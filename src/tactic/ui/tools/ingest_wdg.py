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


from pyasm.web import DivWdg
from pyasm.widget import IconWdg, TextWdg
from pyasm.command import Command
from pyasm.search import SearchType, Search
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import DialogWdg
from tactic.ui.widget import IconButtonWdg

from tactic.ui.input import UploadButtonWdg, TextInputWdg
from tactic.ui.widget import ActionButtonWdg

from tactic_client_lib import TacticServerStub

__all__ = ['IngestUploadWdg', 'IngestUploadCmd']


class IngestUploadWdg(BaseRefreshWdg):

    def get_display(my):
        div = DivWdg()
        div.add_class("spt_ingest_top")
        div.add_style("width: 500px")
        div.add_style("padding: 20px")
        div.add_color("background", "background")


        title_div = DivWdg()
        div.add(title_div)
        title_div.add("Ingest Files")
        title_div.add_style("font-size: 14px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 10px")
        title_div.add_style("margin: -20px -21px 15px -21px")
        title_div.add_color("background", "background3")
        title_div.add_border()

        search_type = my.kwargs.get("search_type")
        if not search_type:
            div.add("No search type specfied")
            return div



        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        div.add(upload)
        button = ActionButtonWdg(title="Add")
        button.add_style("float: right")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_upload_files");

	    var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                for (var i = 0; i < files.length; i++) {
                    spt.drag.show_file(files[i], files_el);
                }
	    }

            spt.html5upload.set_form( top );
            spt.html5upload.select_file( onchange );

         '''
         } )



        button = ActionButtonWdg(title="Clear")
        button.add_style("float: right")
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



        div.add("Select files or drag/drop files to be uploaded and ingested:")
        div.add("<br/>"*2)



        files_div = DivWdg()
        files_div.add_class("spt_upload_files")
        div.add(files_div)
        files_div.add_style("max-height: 300px")
        files_div.add_style("height: 300px")
        files_div.add_style("overflow-y: auto")
        files_div.add_border()
        files_div.add_style("padding: 3px")
        files_div.add_color("background", "background3")
        #files_div.add_style("display: none")


        # Test drag and drop files
        files_div.add_attr("ondragenter", "return false")
        files_div.add_attr("ondragover", "return false")
        files_div.add_attr("ondrop", "spt.drag.noop(event, this)")
        files_div.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.drag = {}

        spt.drag.show_file = function(file, top, delay) {
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

            if (true) {

                //var loadingImage = loadImage(
                setTimeout( function() {
                    var loadingImage = loadImage(
                        file,
                        function (img) {
                            thumb_el.appendChild(img);
                        },
                        {maxWidth: 80, maxHeight: 60, canvas: true, contain: true}
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
            }
         
            clone.getElement(".spt_name").innerHTML = file.name;
            clone.getElement(".spt_size").innerHTML = size + " KB";
            clone.inject(top);
        }

        spt.drag.noop = function(evt, el) {
            var top = $(el).getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_upload_files");
            evt.stopPropagation();
            evt.preventDefault();
            evt.dataTransfer.dropEffect = 'copy';
            var files = evt.dataTransfer.files;

            var delay = 0;
            var skip = false;
            for (var i = 0; i < files.length; i++) {
                var size = files[i].size;

                if (size >= 10*1024*1024) continue

                spt.drag.show_file(files[i], files_el, delay);

                if (size < 100*1024)       delay += 50;
                else if (size < 1024*1024) delay += 500;
                else if (size < 10*1024*1024) delay += 1000;

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


        dialog = DialogWdg(display="false", show_title=False)
        info_div.add(dialog)
        dialog.set_as_activator(info_div, offset={'x':0,'y':10})

        dialog_data_div = DivWdg()
        dialog_data_div.add_color("background", "background")
        dialog_data_div.add_style("padding", "10px")

        dialog.add(dialog_data_div)
        dialog_data_div.add("Category:")
        text = TextInputWdg(name="category")
        dialog_data_div.add(text)
        text.add_class("spt_category")
        text.add_style("padding: 1px")

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
        var categories = values.category;
        categories.shift();


        var kwargs = {
            search_type: search_type,
            relative_dir: relative_dir,
            filenames: filenames,
            key: key,
            categories: categories,
        }
        on_complete = function() {
            spt.info("Ingest complete");
            server.finish();
            spt.message.stop_interval(key);
        };

        var class_name = 'tactic.ui.tools.IngestUploadCmd';

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

        relative_dir = my.kwargs.get("relative_dir")

        button.add_behavior( {
            'type': 'click_up',
            'kwargs': {
                'search_type': search_type,
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
                alert("No files selected");
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

            %s

            spt.html5upload.upload_file(upload_file_kwargs);

            ''' % (upload_progress, on_complete, upload_init)
        } )


        return div




class IngestUploadCmd(Command):

    def execute(my):

        filenames = my.kwargs.get("filenames")
        search_type = my.kwargs.get("search_type")
        key = my.kwargs.get("key")
        relative_dir = my.kwargs.get("relative_dir")

        server = TacticServerStub.get()

        categories = my.kwargs.get("categories")
        if not categories:
            categories = []

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


            if len(categories) >= count:
                category = categories[count]
                if category:

                    if SearchType.column_exists(search_type, "category"):
                        sobject.set_value("category", category)

                    if SearchType.column_exists(search_type, "keywords"):
                        sobject.set_value("keywords", category)


            sobject.commit()

            search_key = sobject.get_search_key()

            # use API
            server.simple_checkin(search_key, "publish", filename, mode='uploaded')
            percent = int((float(count)+1) / len(filenames)*100)
            print filename, percent

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



