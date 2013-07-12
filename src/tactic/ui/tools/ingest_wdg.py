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
from pyasm.widget import IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonWdg

from tactic.ui.input import UploadButtonWdg
from tactic.ui.widget import ActionButtonWdg

__all__ = ['IngestUploadWdg']


class IngestUploadWdg(BaseRefreshWdg):

    def get_display(my):
        div = DivWdg()
        div.add_class("spt_uploadx_top")
        div.add_style("width: 500px")
        div.add_style("height: 400px")
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



        div.add("Select files or drag/drop files to be uploaded and ingested:")
        div.add("<br/>"*2)



        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        div.add(upload)
        button = IconButtonWdg(title="Test", icon=IconWdg.ADD)
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_uploadx_top");
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

        spt.drag.show_file = function(file, top) {
            var template = top.getElement(".spt_upload_file_template");
            var clone = spt.behavior.clone(template);
            clone.removeClass("spt_upload_file_template");
            clone.addClass("spt_upload_file");
            clone.setStyle("display", "");

            // remember the file handle
            clone.file = file;

            var name = file.name;
            var size = parseInt(file.size / 1024 * 10) / 10;

            var thumb_el = clone.getElement(".spt_thumb");

            if (true) {
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
            }
         
            clone.getElement(".spt_name").innerHTML = file.name;
            clone.getElement(".spt_size").innerHTML = size + " KB";
            clone.inject(top);
        }

        spt.drag.noop = function(evt, el) {
            var top = $(el).getParent(".spt_uploadx_top");
            var files_el = top.getElement(".spt_upload_files");
            evt.stopPropagation();
            evt.preventDefault();
            evt.dataTransfer.dropEffect = 'copy';
            var files = evt.dataTransfer.files;

            for (var i = 0; i < files.length; i++) {
                spt.drag.show_file(files[i], files_el);
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


        name_div = DivWdg()
        name_div.add_class("spt_name")
        file_template.add(name_div)
        name_div.add("image001.jpg")
        name_div.add_style("float: left")
        name_div.add_style("width: 150px")

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




        progress_div = DivWdg()
        progress_div.add_class("spt_upload_progress_top")
        div.add(progress_div)
        progress_div.add_style("width: 100%")
        progress_div.add_style("height: 15px")
        progress_div.add_border()
        progress_div.add_style("display: none")

        progress = DivWdg()
        progress_div.add(progress)
        progress.add_class("spt_upload_progress")
        progress.add_style("width: 0px")
        progress.add_style("height: 100%")
        progress.add_style("background-color: red")
        progress.add_style("text-align: right")





        div.add("<br/>"*2)




        upload_init = '''
        var server = TacticServerStub.get();
        server.start( {description: "Upload and check-in of ["+files.length+"] files"} );
        '''

        upload_progress = '''
        var top = bvr.src_el.getParent(".spt_uploadx_top");
        progress_el = top.getElement(".spt_upload_progress");
        progress_el.setStyle("width", 300);
        progress_el.innerHTML = "100%";
        
        '''


        on_complete = '''
        var top = bvr.src_el.getParent(".spt_uploadx_top");
        progress_el = top.getElement(".spt_upload_progress");
        progress_el.setStyle("width", 300);
        progress_el.innerHTML = "100%";
        
        var server = TacticServerStub.get();

        var search_type = bvr.kwargs.search_type;

        for (var i = 0; i != files.length;i++) {
            var name = files[i].name;
            sobject = server.insert(search_type, { name: name });
            console.log(sobject);
            console.log(files[i]);
            server.simple_checkin(sobject.__search_key__, "publish", name, {mode:'uploaded'});
            percent = parseInt((i+1) / files.length*100);
            progress_el.setStyle("width", 300*percent/100);
            progress_el.innerHTML = "Check-in: " + percent + "%";
        }
        server.finish();
        '''


        upload_div = DivWdg()
        div.add(upload_div)
        upload_div.add_border()

        button = ActionButtonWdg(title="Ingest")
        button.add_behavior( {
            'type': 'click_up',
            'kwargs': {
                'search_type': search_type
            },
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_uploadx_top");
            var file_els = top.getElements(".spt_upload_file");

            // retrieved the stored file handles
            var files = [];
            for (var i = 0; i < file_els.length; i++) {
                files.push( file_els[i].file );
            }
            if (files.length == 0) {
                alert("No files selcted");
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

            spt.html5upload.upload_file(upload_file_kwargs);
            ''' % (upload_progress, on_complete)
        } )


        #button = UploadButtonWdg(**kwargs)
        upload_div.add(button)
        button.add_style("float: right")


        return div

