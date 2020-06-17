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
__all__ = [ 'SimpleUploadWdg', 'UploadWdg', 'UploadProgressWdg' ]


import os, shutil, string, types

from pyasm.common import Container
from pyasm.web import HtmlElement, DivWdg, SpanWdg, WebContainer, Widget, Table, WebContainer, StringWdg
from pyasm.widget import BaseInputWdg, HiddenWdg, TextWdg, SwapDisplayWdg, HintWdg, CheckboxWdg, TextAreaWdg, ProdIconButtonWdg, SelectWdg
from pyasm.search import SearchKey
from tactic.ui.common import BaseRefreshWdg




class SimpleUploadWdg(BaseInputWdg):

    def __init__(self, **kwargs):
        name = kwargs.get("key")
        self.kwargs = kwargs

        super(SimpleUploadWdg,self).__init__(name, "upload")
        
    ARGS_KEYS = {

        "context": {
            'description': "a single context for check-in. If not specified, the icon_context for this SType is used.",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Optional'
        },
        "client_action": {
            'description': "the client side action to take on uploading. For server side action in Edit Panel, choose empty.",
            'type': 'SelectWdg',
            'values' : 'icon_checkin|submission',
            'order': 1,
            'category': 'Optional'
        }
        }
 
    def get_info_wdg(self):
        widget = Widget()
        context_input = HiddenWdg("%s|context" % self.get_input_name(), self.context)
        context_input.add_class('spt_upload_context')

        widget.add(context_input)


        # override the column
        column = self.get_option("column")
        if column != "":
            column_input = HiddenWdg("%s|column" % self.get_input_name(), column)
            widget.add(column_input)

        return widget

    def add_style(self, style):
        self.browse.add_style(style)

    def init(self):

        from tactic.ui.input import UploadButtonWdg 
        on_complete = '''
        var files = spt.html5upload.get_file();
        var top = bvr.src_el.getParent(".spt_simple_upload_top");
        var hidden = top.getElement(".spt_upload_hidden");
        var ticket_hidden = top.getElement(".spt_upload_ticket");
        var files_el = top.getElement(".spt_upload_files");

        ticket = spt.Environment.get().get_ticket();
        var html = "";
        html += "Uploaded: " + files.name;
        files_el.innerHTML = html;
        
        if (files) {
            hidden.value = files.name;
            ticket_hidden.value = ticket;
        }
        '''
        self.browse = UploadButtonWdg(title="Browse", on_complete=on_complete)

    def add_behavior(self, bvr):
        '''add extra bvr to the Browse button post upload'''
        self.browse.add_behavior(bvr)

    def add_action(self):
        action = self.kwargs.get('client_action')
        cbjs_action = ''
        # these are client side action applicable for editing, not insert
        if action =='icon_checkin':
            cbjs_action = '''
        var tbody = bvr.src_el.getParent(".spt_table_tbody");
        var top = spt.get_parent(bvr.src_el, ".spt_upload_top");
        var hidden = top.getElement(".spt_upload_hidden");
        var files_el = top.getElement(".spt_upload_files");
        var file_name = hidden.value;
        if (!file_name) {
            alert('No file selected');
            return;
        }
        // use full path for simple check-in, it takes care of everything
        //file_name = spt.path.get_basename(file_name);
        var search_key = tbody.getAttribute("spt_search_key");


        var server = TacticServerStub.get();
        var option = {'mode': 'uploaded'};

        // check in the uploaded file 
        try {
        server.simple_checkin(search_key, '%s',
            file_name, option);
        } catch(e) {
            var error_str = spt.exception.handler(e);
            alert( "Checkin Error: " + error_str );
            files_el.innerHTML = '';
            hidden.value = '';
            return;
        }

        // update stats message
        //var stats_msg = instance.file_list.length + " file/s queued";
        //upload_stats.innerHTML = stats_msg;
        spt.named_events.fire_event('update|' + search_key, {});
        '''%self.context
        
            self.add_behavior({'type':'click_up',
                        'cbjs_action': cbjs_action})

        elif action == 'submission':
            
            bvr = {
                'type': 'listen',
                'event_name': 'submit_pressed',
                'cbjs_action': "spt.Upload.submit_complete(bvr)",
                'start_transaction': True
            }
            self.add_behavior(bvr)


    
            


        
    def get_display(self):
        top = DivWdg()
        top.add_color("color", "color")
        #top.add_color("background", "background")
        top.add_class("spt_simple_upload_top")
        
        top.add(self.browse)
       

        hidden = HiddenWdg( "%s|path" %  self.get_input_name() )
        hidden.add_class("spt_upload_hidden")
        top.add(hidden)


        # this can be used for some other transaction that picks up this file to checkin
        hidden = HiddenWdg( "%s|ticket" %  self.get_input_name() )
        hidden.add_class("spt_upload_ticket")
        top.add(hidden)

        # if not specified, get the sobject's icon context 
        self.context = self.kwargs.get("context")
        if not self.context:
            current = self.get_current_sobject()
            if current:
                self.context = current.get_icon_context()
            else:
                from pyasm.biz import Snapshot
                self.context = Snapshot.get_default_context()

        top.add_attr("spt_context", self.context)

        top.add( self.get_info_wdg() )


        files_div = DivWdg()
        top.add(files_div)
        files_div.add_class("spt_upload_files")
        files_div.add_style("font-size: 11px")
        files_div.add_style("margin-top: 10px")

        self.add_action()

        return top





class UploadWdg(SimpleUploadWdg):

    
    def __init__(self, **kwargs):
        # by default the Upload button is hidden in EditWdg
        super(UploadWdg, self).__init__(**kwargs)
        self.show_upload = False

    ARGS_KEYS = {

        "context": {
            'description': "context dropdown list for check-in. e.g. icon|publish|special",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Optional'
        },
        "client_action": {
            'description': "For server side action in Edit Panel, choose empty and set 'UplaodAction' in the action field",
            'type': 'SelectWdg',
            'values' : 'icon_checkin|submission',
            'order': 1,
            'category': 'Optional'
        }
    }

    def get_display_old(self):
        '''This is NOT used, just used as a reference for the old method'''
        icon_id = 'upload_div'
        div = DivWdg()

        if self.get_option('upload_type') == 'arbitrary':
            counter = HiddenWdg('upload_counter','0')
            div.add(counter)
            icon = IconButtonWdg('add upload', icon=IconWdg.ADD)
            icon.set_id(icon_id)
            icon.add_event('onclick', "Common.add_upload_input('%s','%s','upload_counter')" \
                %(icon_id, self.get_input_name()))
            div.add(icon)
        
        table = Table()
        table.set_class("minimal")
        table.add_style("font-size: 0.8em")

        names = self.get_option('names')
        required = self.get_option('required')
        if not names:
            self.add_upload(table, self.name)
        else:
            names = names.split('|')
            if required:
                required = required.split('|')
                if len(required) != len(names):
                    raise TacticException('required needs to match the number of names if defined in the config file.')
            # check for uniqueness in upload_names
            if len(set(names)) != len(names):
                raise TacticException('[names] in the config file must be unique')
            
            for idx, name in enumerate(names):
                 if required:
                     is_required = required[idx] == 'true'
                 else:
                     is_required = False
                 self.add_upload(table, name, is_required)

        table.add_row()
        
    def get_info_wdg(self):

        widget = Widget()

        table = Table()
        table.set_class("minimal")
        table.add_style("font-size: 0.8em")

        context_option = self.kwargs.get('context')
        context_expr_option = self.kwargs.get('context_expr')
        
        pipeline_option = self.kwargs.get('pipeline') in ['true', True, 'True']
        setting_option = self.kwargs.get('setting')
        context_name = "%s|context" % self.get_input_name()
        text = None 
        span1 = SpanWdg("Context", id='context_mode')
        span2 = SpanWdg("Context<br/>/Subcontext", id='subcontext_mode')
        span2.add_style('display','none')
        table.add_cell(span1)
        table.add_data(span2)
        if context_expr_option or context_option or setting_option:
            # add swap display for subcontext only if there is setting or context option
            swap = SwapDisplayWdg()
            table.add_data(SpanWdg(swap, css='small'))
            swap.set_display_widgets(StringWdg('[+]'), StringWdg('[-]'))
            subcontext_name = "%s|subcontext" % self.get_input_name()
            subcontext = SpanWdg('/ ', css='small')
            subcontext.add(TextWdg(subcontext_name))
            subcontext.add_style('display','none')
            subcontext.set_id(subcontext_name)
            on_script = "set_display_on('%s');swap_display('subcontext_mode','context_mode')"%subcontext_name
            off_script = "set_display_off('%s');get_elements('%s').set_value(''); "\
                "swap_display('context_mode','subcontext_mode')"%(subcontext_name, subcontext_name)
            swap.add_action_script(on_script, off_script)
            text = SelectWdg(context_name)
            if self.sobjects:
                text.set_sobject(self.sobjects[0])
            if context_expr_option:
                text.set_option('values_expr', context_expr_option)
            elif context_option:
                text.set_option('values', context_option)
            elif setting_option:
                text.set_option('setting', setting_option)
                    

            td = table.add_cell(text)
            
            table.add_data(subcontext)
            
        elif pipeline_option:
            from pyasm.biz import Pipeline
            sobject = self.sobjects[0]
            pipeline = Pipeline.get_by_sobject(sobject)
            context_names = []
            process_names = pipeline.get_process_names(recurse=True)
            for process in process_names:
                context_names.append(pipeline.get_output_contexts(process))
            text = SelectWdg(context_name)
            text.set_option('values', process_names)
            table.add_cell(text)
            
        else:
            text = TextWdg(context_name)
            table.add_cell(text)
            hint = HintWdg('If not specified, the default is [publish]')
            table.add_data(hint)
      
        revision_cb = CheckboxWdg('%s|is_revision' %self.get_input_name(),\
            label='is revision', css='med')
        table.add_data(revision_cb)
        table.add_row()
        table.add_cell("Comment")
        textarea = TextAreaWdg("%s|description"% self.get_input_name())
        table.add_cell(textarea)
        widget.add(table)

        return widget





class UploadProgressWdg(Widget):

    def get_display(self):
        div = DivWdg()
        #div.add_style("div: solid 1px black")
        div.add_style("margin: 5px")

        # add the progress meter
        progress_div = DivWdg()
        progress_div.add_style("font-size: 0.8em")
        progress_div.add_class("spt_upload_progress")

        progress_info = DivWdg()
        progress_info.add_class("spt_upload_info")
        progress_div.add(progress_info)

        progress_bar = DivWdg()
        progress_bar.add_class("spt_upload_bar")
        progress_bar.add_style("width: 0px")
        progress_bar.add_style("height: 5px")
        progress_bar.add_style("background: red")
        progress_bar.add_style("margin: 2px")
        progress_div.add(progress_bar)

        div.add(progress_div)

        return div
        




#-----------------------
# TEST TEST TEST
# Yet another uploader ... sigh

from .button_new_wdg import ActionButtonWdg
__all__.extend(["AppletUploader", "HtmlUploader"])


class AppletUploader(BaseRefreshWdg):
    def get_display(self):
        top = self.top

        return top


    def get_browse_button(self):
        button = ActionButtonWdg(title="Browse")
        button_div.add(button)
        button.add_style("float: left")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var applet = spt.Applet.get();
        var files = applet.open_file_browser();

        var top = bvr.src_el.getParent(".spt_uploader_top");
        var drop_area = top.getElement(".spt_uploader_drop");
        alert(drop_area);

        var file_objs = [];
        for (var i = 0; i < files.length; i++ ) {
            var file_obj = {};
            file_objs.push(file_obj);

            var file_path = files[i];
            file_obj.fileName = spt.path.get_basename(file_path);

        }

        spt.uploader.traverse_files(drop_area, file_objs);

        '''
        } )

        return button


    def get_upload_button(self):
        button = ActionButtonWdg(title="Upload")
        button_div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_uploader_top");
        var files = top.files;
        var applet = spt.Applet.get();
        for ( var i = 0; i < files.length; i++ ) {
            applet.upload_file(files[i]);
            
        }
        '''
        } )
        return upload



class HtmlUploader(BaseRefreshWdg):

    def get_display(self):

        width = self.kwargs.get("width")
        if not width:
            width = 300
        height = self.kwargs.get("height")
        if not height:
            height = 100

        top = self.top
        top.add_class("spt_uploader_top")

        inner = DivWdg()
        top.add(inner)
        inner.add_style("scroll: auto")
        inner.add_style("padding: 3px")
        inner.add_behavior( {
        'type': 'load',
        'cbjs_action': self.get_onload_js()
        } )

        drop_wdg = DivWdg()
        inner.add(drop_wdg)
        drop_wdg.add_class("spt_uploader_drop")
        drop_wdg.add_border()
        drop_wdg.add_style("width: %s" % width)
        drop_wdg.add_style("height: %s" % height)

        drop_wdg.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        var drop_area = bvr.src_el;
        spt.uploader.init_drop_area(drop_area);
        '''
        } )


        button_div = DivWdg()
        top.add(button_div)

        #top.add('''<input id="files-upload" type="file" multiple=""/>''')

        return top




    def get_onload_js(self):
        return '''

spt.uploader = {};


spt.uploader.init_drop_area = function(drop_area)
{
    drop_area.addEventListener("dragleave", function (evt) {
        var target = evt.target;
     
        if (target && target === drop_area) {
            this.className = "";
        }
        evt.preventDefault();
        evt.stopPropagation();
    }, false);


    drop_area.addEventListener("dragenter", function(evt) {
        this.className = "over";
        evt.preventDefault();
        evt.stopPropagation();
    }, false);
     
    drop_area.addEventListener("dragover", function (evt) {
        evt.preventDefault();
        evt.stopPropagation();
    }, false);
     
    drop_area.addEventListener("drop", function (evt) {
        this.className = "";
        evt.preventDefault();
        evt.stopPropagation();
        spt.uploader.traverse_files(this, evt.dataTransfer.files);
    }, false);

}



spt.uploader.traverse_files = function(drop_area, files) {
    var top = bvr.src_el.getParent(".spt_uploader_top");
    if (typeof files !== "undefined") {
        for (var i=0, l=files.length; i<l; i++) {
            //spt.uploader.upload_file(files[i]);
            //console.log(files[i]);
            var file_name = files[i].fileName + " ("+files[i].fileSize+")";
            drop_area.innerHTML = drop_area.innerHTML + file_name + "<br/>";
            top.files = files;
        }
    }
    else {
        fileList.innerHTML = "No support for the File API in this web browser";
    }
}


spt.uploader.upload_file = function(file) {
    xhr = new XMLHttpRequest();

    xhr.addEventListener("progress", function (evt) {
        //console.log("evt: " + evt.lengthComputable);
        if (evt.lengthComputable) {
            //progressBar.style.width = (evt.loaded / evt.total) * 100 + "%";
            //console.log((evt.loaded / evt.total) * 100 + "%");
        }
        else {
            // No data to calculate on
        }
    }, false);

    server_url = "/tactic/default/UploadServer/";
    xhr.open("post", server_url, true);

    // Send the file
    var boundary = '---------------------------';
    boundary += Math.floor(Math.random()*32768);
    boundary += Math.floor(Math.random()*32768);
    boundary += Math.floor(Math.random()*32768);
    xhr.setRequestHeader("Content-Type", 'multipart/form-data; boundary=' + boundary);
    // Set appropriate headers
    xhr.setRequestHeader("X-File-Name", file.fileName);
    xhr.setRequestHeader("X-File-Size", file.fileSize);
    xhr.setRequestHeader("X-File-Type", file.type);

    var CRLF = "\\r\\n";
    var body = '';
    body += "--" + boundary + CRLF;
    body += 'Content-Disposition: form-data; name=';
    body += '"file"; filename="'+ file.fileName + '"';
    body += CRLF;
    body += 'Content-type: ' + file.type;
    body += CRLF + CRLF;
    body += file.getAsBinary()
    body += CRLF;
    body += "--" + boundary + '--';
    body += CRLF + CRLF;
    xhr.setRequestHeader("Content-Length", body.length);
    xhr.sendAsBinary(body); 
    //xhr.send(body); 
}

    '''





# DEPRECATED
"""
class GlobalUploadWdg(BaseRefreshWdg):
    def get_args_keys(self):
        return {
        'key': 'the key to the this upload widget'
        }
        
    def get_display(self):
        key = self.kwargs.get("key")


        div = DivWdg()

        # create the button that will be replace by the swf element
        yet_another_div = DivWdg()
        yet_another_div.add_style("border", "solid blue 2px")
        yet_another_div.set_id("cow_button")
        yet_another_div.add_class("spt_upload")
        yet_another_div.add_style("position: absolute")
        yet_another_div.add_style("margin-left: -1000px")
        yet_another_div.add_attr("spt_key", key)

        # the button div that will get replaced by the swf
        button_div = DivWdg()
        yet_another_div.add(button_div)
        div.add(yet_another_div)

        button_id = "%sButton" % key
        button_div.set_id(button_id)
        button_div.add_class("spt_upload_button")
        button_div.add_style("display: block")

        

        # add the onload behavior for this widget to initialize the swf
        #load_div = DivWdg()
        #behavior = {
        #    'type': 'load',
        #    'cbfn_action': "spt.Upload.setup_cbk",
        #    'key': key,
        #    'settings': {
        #        'upload_complete_handler':  'spt.Upload.icon_complete',
        #        'file_queued_handler':  'spt.Upload.icon_file_queued',
        #    }
        #}
        #load_div.add_behavior(behavior)
        #div.add(load_div)
        

        # add a listener to upload this file
        behavior = {
            'type': 'listen',
            'event_name': 'edit_pressed',
            'cbjs_action': "spt.Upload.upload_cbk(bvr)"
        }
        div.add_behavior(behavior)

        # add a listener to upload this file
        behavior = {
            'type': 'listen',
            'event_name': 'upload',
            'cbjs_action': "spt.Upload.upload_cbk(bvr)"
        }
        div.add_behavior(behavior)


        # test
        span = SpanWdg(css="hand")
        span.add("Test")
        behavior = {
            'type': 'click_up',
            'cbjs_action': "spt.Upload.clone_upload()",
        }
        span.add_behavior(behavior)
        div.add(span)


        return div
"""


